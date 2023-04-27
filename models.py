# Import modules
from typing import Self, Type, Optional, Union
from numpy.polynomial.polynomial import polyval
from numpy.random import default_rng, Generator
from numpy import linspace

# TODO:
#
# * Add some way for the time to run along
#   * Per tick or Continuos?
# * Calculate polynomials for all appliances
#   * In a config file or over the control protocol

# Base Model of an Appliance
class Appliance():

    # The state of the appliance
    power_state: bool = False
    _power_lock: bool = False

    # Datetime object to track the start of a cycle
    cycle_end_time: Optional[int] = None

    # Keep track of how many times the appliance has been cycled
    cycle_count: int = 0

    def __init__(
            self: Self,
            power_usage: float,
            power_fluctuation: float,
            controllable: bool,
            state_coeffs: list[float],
            allowed_cycles: int,
            cycle_time_range: tuple[int, int],
            ) -> None:
        """Initialize the appliance.

        Args:
            self (Self): self
            power_usage (float): The power usage of the device in kW
            power_fluctuation (float): The amount of power can fluctuate in percent
            controllable (bool): Is the appliance controllable
            state_coeffs (list[float]): The coefficients of the state over time polynomial
            allowed_cycles (int): How many times are the appliance allowed to have a cycle in a day (0 and less is infinite)
            cycle_time_range (tuple[int, int]): Range to pick cycle time from (in minutes)

        Returns:
            None:
        """

        # Set given parameters
        self.controllable: bool = controllable
        self._power_usage: float = power_usage
        self._power_fluctuation: float = power_fluctuation
        self._state_coeffs: list[float] = state_coeffs
        self._allowed_cycles: int = allowed_cycles
        self._cycle_time_range: tuple[int, int] = cycle_time_range

        # Make a randomness generator
        self._rng: Generator = default_rng()

    def power_locker(self: Self, lock: bool) -> None:
        """Lock (or unlock) the power on the appliance.

        Args:
            self (Self): self
            lock (bool): lock or unlock

        Returns:
            None:
        """

        # Check if we are able to control the appliance
        if not self.controllable:
            raise RuntimeWarning("Appliance is not controllable")

        # Lock the appliance
        self._power_lock: bool = lock
        if self._power_lock:
            self.power_state: bool = False

    def _calculate_state(self: Self, time: int) -> None:
        """Calculate the power state.

        Args:
            self (Self): self
            time (int): The unix time

        Returns:
            None:
        """

        # Check if we are already in a cycle
        if self.cycle_end_time and time < self.cycle_end_time:
            # Check if it is locked, dont do anything
            if self._power_lock:
                return

            self.power_state: bool = True
            return

        # Turn it off if it isnt in a cycle
        self.power_state: bool = False

        # Check if it should be turned on
        # Make sure that it has more allowed cycles
        if self._allowed_cycles <= self.cycle_count and not self._allowed_cycles <= 0:
            return

        # Sample a probability polynomial
        sample_point: float = time / 3600

        if self._rng.uniform() <= polyval(sample_point, self._state_coeffs):
            self.power_state: bool = True
            self.cycle_count += 1
            self.cycle_end_time: int = time + \
                    (self._rng.integers(
                            self._cycle_time_range[0],
                            self._cycle_time_range[1]
                            ) * 60
                    )

    def tick(
            self: Self,
            last_tick: int,
            time: int,
            ) -> tuple[bool, float, float]:
        """Tick the appliance and get the power state, kwh draw and heating effect

        Args:
            self (Self): self
            last_tick (datetime): Unix timestamp of last tick
            date (datetime): Unix timestamp

        Returns:
            tuple[bool, float, float]: power state, kWh draw and heating effect
        """

        # Calculate the minutes between ticks
        minutes = (time - last_tick)/60.0

        # Make sure that we dont have a past date
        if minutes < 0:
            raise RuntimeError("No time travel allowed")

        # Check if a new day has begun
        if last_tick // 86400 < time // 86400:
            self._reset_variables()

        # Calculate the power state
        self._calculate_state(time)

        kwh_draw: float = 0.0
        if self.power_state:
            # Calculate the power draw in kWh
            kwh_draw: float = self._power_usage * \
                    (1 + self._rng.uniform(
                        -self._power_fluctuation,
                        self._power_fluctuation
                        )
                    )

        return self.power_state, kwh_draw, 0.0

    def _reset_variables(self: Self) -> None:
        """Reset variables keeping track of limits.

        Args:
            self (Self): self

        Returns:
            None:
        """

        self.cycle_count: int = 0


class Heatpump(Appliance):

    def __init__(
            self: Self,
            power_usage: float,
            power_fluctuation: float,
            controllable: bool,
            heating_multiplier: float,
            heating_fluctuation: float,
            min_temperature: float,
            max_temperature: float
            ) -> None:
        """Initialize the heatpump.

        Args:
            self (Self): self
            power_usage (float): The power usage of the device in kW
            power_fluctuation (float): The amount of power can fluctuate in percent
            controllable (bool): Is the appliance controllable
            heating_multiplier (float): How much more does it heat then it uses
            heating_fluctuation (float): Fluctuation of heating in percent
            min_temperature (float): The minimum temperature
            max_temperature (float): The maximum temperature

        Returns:
            None:
        """

        self._heating_multiplier = heating_multiplier
        self._heating_fluctuation = heating_fluctuation
        self._min_temperature = min_temperature
        self._max_temperature = max_temperature

        super().__init__(
                power_usage,
                power_fluctuation,
                controllable,
                [0],
                0,
                [0, 0]
                )

    def _calculate_state(self: Self, time: int) -> None:
        if self._power_lock:
            return

        if self._temperature >= self._max_temperature:
            self.power_state = False
            return

        if self._temperature <= self._min_temperature:
            self.power_state = True
            return

    def tick(
            self: Self,
            last_tick: int,
            time: int,
            temperature: float
            ) -> tuple[bool, float, float]:
        """Tick the appliance and get the power state, kwh draw and heating effect

        Args:
            self (Self): self
            last_tick (int): Unix timestamp of last tick
            time (int): Unix timestamp

        Returns:
            tuple[bool, float, float]: power state, kWh draw and heating effect
        """

        # Set the temperature (workaround till I get a better idea)
        self._temperature = temperature

        # Call the super tick
        _, kwh_draw, _ = super().tick(last_tick, time)

        # Calculate heating effect
        heating_effect = kwh_draw * self._heating_multiplier * \
                (1 + self._rng.uniform(
                    -self._heating_fluctuation,
                    self._heating_fluctuation
                    )
                )

        return self.power_state, kwh_draw, heating_effect


class Dryer(Appliance):

    def __init__(
            self: Self,
            power_usage: float,
            power_fluctuation: float,
            controllable: bool,
            state_coeffs: list[float],
            allowed_cycles: int,
            cycle_time_range: tuple[int, int],
            ) -> None:
        """Initialize the dryer.

        Args:
            self (Self): self
            power_usage (float): The power usage of the device in kW
            power_fluctuation (float): The amount of power can fluctuate in percent
            controllable (bool): Is the appliance controllable
            state_coeffs (list[float]): The coefficients of the state over time polynomial
            allowed_cycles (int): How many times are the appliance allowed to have a cycle in a day (0 and less is infinite)
            cycle_time_range (tuple[int, int]): Range to pick cycle time from (in minutes)

        Returns:
            None:
        """

        super().__init__(
                power_usage,
                power_fluctuation,
                controllable,
                state_coeffs,
                allowed_cycles,
                cycle_time_range,
                )


class Oven(Appliance):

    def __init__(
            self: Self,
            power_usage: float,
            power_fluctuation: float,
            controllable: bool,
            state_coeffs: list[float],
            allowed_cycles: int,
            cycle_time_range: tuple[int, int],
            ) -> None:
        """Initialize the oven.

        Args:
            self (Self): self
            power_usage (float): The power usage of the device in kW
            power_fluctuation (float): The amount of power can fluctuate in percent
            controllable (bool): Is the appliance controllable
            state_coeffs (list[float]): The coefficients of the state over time polynomial
            allowed_cycles (int): How many times are the appliance allowed to have a cycle in a day (0 and less is infinite)
            cycle_time_range (tuple[int, int]): Range to pick cycle time from (in minutes)

        Returns:
            None:
        """

        super().__init__(
                power_usage,
                power_fluctuation,
                controllable,
                state_coeffs,
                allowed_cycles,
                cycle_time_range,
                )


# Model of a Household
class House():
    """Model of a household.
    """

    # Set the limit values
    LIMIT_VALUES: dict = {
        'a': (29, 1000),
        'b': (69, 2200),
        'c': (109, 3200),
        'd': (149, 4200),
        'e': (189, 5200),
        'f': (239, 6500)
    }

    def __init__(
            self: Self,
            energy_label: str,
            sq_meters: float,
            height_meter: float,
            start_temperature: float,
            start_time: int,
            active_days: int,
            appliances: list[Type[Appliance]],
            bg_power_coeffs: list[float],
            bg_power_fluctuation: float,
            random_heat_loss_chance: float
            ) -> None:
        """Initialize Household.

        Args:
            self (Self): self
            energy_label (str): The energy label of the house
            sq_meters (float): The square meters floor space
            height_meter (float): The height of the walls
            start_temperature (float): The starting temperature
            start_time (int): The starting time in unix time
            active_days (int): The days that the house is active
            appliances (list[Type[Appliance]]): The appliances of the house
            bg_power_coeffs (list[float]): Coefficients for background power usage
            bg_power_fluctuation (float): Fluctuation in background power usage (in percent)

        Returns:
            None:
        """

        # Set given parameters
        self.energy_label: str = energy_label.lower()
        self.sq_meters: float = sq_meters
        self.height_meter: float = height_meter
        self._active_days: int = active_days
        self._appliances: list[Type[Appliance]] = appliances
        self._bg_power_coeffs: list[float] = bg_power_coeffs
        self._bg_power_fluctuation: float = bg_power_fluctuation
        self.random_heat_loss_chance: float = random_heat_loss_chance

        # Set temperature
        self.current_temperature: float = start_temperature

        # Set the time
        self.time: int = start_time

        # Set last tick to start date
        self.last_tick: int = self.time

        # Calculate the cubic meters of the house
        self.cubic_meters: float = self.sq_meters * self.height_meter

        # Calculate kg of the air inside the house
        self._kg_air: float = self.cubic_meters * 1.219

        # Make randomness generator
        self._rng = default_rng()

        # Make sure that the energy_label exists
        if not self.LIMIT_VALUES.get(self.energy_label, None):
            raise ValueError("Energy Label is invalid")

        # Get limit values
        self.limit_value: tuple[int, int] = self.LIMIT_VALUES.get(self.energy_label)

    def _kj2celsius(self: Self, kj: float) -> float:
        """Convert kj to celsius.

        Args:
            self (Self): self
            kj (float): kj

        Returns:
            float: celsius
        """

        return kj/(1.005 * self._kg_air)

    def _calculate_heat_loss(self: Self, minutes: float) -> float:
        """Calculate the total heatloss in the given minute interval.

        Args:
            self (Self): self
            minutes (int): Minutes to calculate loss for.

        Returns:
            float: Loss in celsius.
        """

        # Calculate the yearly loss in kwh
        kwh_year_loss: float = self.limit_value[0] + \
                (self.limit_value[1]/self.sq_meters)

        # Convert it to minutely
        kwh_minute_loss: float = kwh_year_loss/(self._active_days*24*60)

        # Convert to kj
        kj_minute_loss: float = kwh_minute_loss*3600

        # Calculate celsius change
        celsius_minute_loss: float = self._kj2celsius(kj_minute_loss)

        # Return the celsius scaled to the minutes
        return celsius_minute_loss * minutes

    def _calculate_heat_gain(self: Self, kw: float, minutes: int) -> float:
        """Calculate the gained celsius by the given kwh.

        Args:
            self (Self): self
            kwh (float): The added kwh to the system

        Returns:
            float: Gain in celsius
        """

        # Convert kwh to kj
        kj_gain: float = kw * (minutes*60)

        # Calculate the gain in celsius
        celsius_gain: float = self._kj2celsius(kj_gain)

        # Return the celsius gained
        return celsius_gain

    def update_time(self: Self, delta_time: int) -> None:
        """Update the time.

        Args:
            self (Self): self
            delta_time (int): Change in seconds

        Returns:
            None:
        """

        self.time += delta_time

    def set_time(self: Self, unix_time: int) -> None:
        """Set the time on the house.

        Args:
            self (Self): self
            unix_time (int): New time in unix format

        Returns:
            None:
        """

        self.time = unix_time

    def tick(self: Self) -> tuple[list[bool], float, float, int]:
        """Tick the household, and return the device power states, total kWh draw, temperature and unix time.

        Args:
            self (Self): self

        Returns:
            tuple[list[bool], float, float, int]: Device states, total kWh draw, temperature and unix time
        """

        # Calculate the amount of minutes since last tick
        minutes: float = (self.time - self.last_tick)/60.0

        # Variables to hold the data
        power_states: list[bool] = []
        total_kwh_draw: float = 0.0
        total_heating_kwh: float = 0.0

        # Loop over all appliances
        for appliance in self._appliances:
            # Call tick on appliance
            if type(appliance) == Heatpump:
                power_state, kwh_draw, heating_kwh = appliance.tick(
                        self.last_tick,
                        self.time,
                        self.current_temperature
                        )
            else:
                power_state, kwh_draw, heating_kwh = appliance.tick(
                        self.last_tick,
                        self.time
                        )

            # Add the values to the variables
            power_states.append(power_state)
            total_kwh_draw += kwh_draw
            total_heating_kwh += heating_kwh

        # Calculate the new temperature
        self.current_temperature += self._calculate_heat_gain(total_heating_kwh, minutes) - \
            self._calculate_heat_loss(minutes)
        # Add random heat loss from open doors ect.
        if self._rng.random() < self.random_heat_loss_chance:
            self.current_temperature -= self._rng.random()

        # Get sample points for background power

        sample_points: list[float] = []

        # some edge case that 24/0 hours
        last_tick_clamped = (self.last_tick // 86400) * 86400
        time_clamped = (self.time // 86400) * 86400

        if last_tick_clamped < time_clamped:
            # We have sample points for two days
            sample_points.extend(
                    linspace(
                        (self.last_tick / 3600) % 24,
                        ((time_clamped-1) / 3600) % 24,
                        int(time_clamped-1 - self.last_tick)
                        )
                    )

            sample_points.extend(
                    linspace(
                        (time_clamped / 3600) % 24,
                        (self.time / 3600) % 24,
                        int(self.time - time_clamped)
                        )
                    )

        else:
            sample_points.extend(
                    linspace(
                        (self.last_tick / 3600) % 24,
                        (self.time / 3600) % 24,
                        int(minutes*60)
                        )
                    )

        # Add the background power to the total power draw
        bg_kwh_draw = sum(polyval(sample_points, self._bg_power_coeffs)) / \
                (minutes*60) * \
                (1 + self._rng.uniform(
                    -self._bg_power_fluctuation,
                    self._bg_power_fluctuation
                    )
                )

        total_kwh_draw += bg_kwh_draw

        # Update the last_tick date
        self.last_tick: int = self.time

        return power_states, total_kwh_draw, self.current_temperature, self.time

