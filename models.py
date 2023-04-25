# Import modules
from typing import Self, Type, Optional, Union
from datetime import datetime, timedelta
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
    cycle_end_time: Optional[datetime] = None

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

    def _dates2minutes(self: Self, date1: datetime, date2: datetime) -> float:
        """Convert to dates to minute difference.

        Args:
            self (Self): self
            date1 (datetime): First date
            date2 (datetime): Second date

        Returns:
            float: minutes
        """

        return (date1 - date2).total_seconds()/60.0

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

    def _calculate_state(
            self: Self,
            date: datetime,
            ) -> None:
        """Calculate the power state.

        Args:
            self (Self): self
            date (datetime): The date
            override (Optional[bool]): Override of state

        Returns:
            None:
        """

        # Check if we are already in a cycle
        if self.cycle_end_time and date < self.cycle_end_time:
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
        sample_point: float = date.hour + (date.minute/60)

        if self._rng.uniform() <= polyval(sample_point, self._state_coeffs):
            self.power_state: bool = True
            self.cycle_count += 1
            self.cycle_end_time: datetime = date + \
                    timedelta(
                            minutes=int(self._rng.integers(
                                self._cycle_time_range[0],
                                self._cycle_time_range[1]
                                ))
                            )

    def tick(
            self: Self,
            last_tick: datetime,
            date: datetime,
            ) -> tuple[bool, float, float]:
        """Tick the appliance and get the power state, kwh draw and heating effect

        Args:
            self (Self): self
            last_tick (datetime): Date and time of the last tick
            date (datetime): The date and time
            state_override (Optional[bool]): Override for the state

        Returns:
            tuple[bool, float, float]: power state, kWh draw and heating effect
        """

        # Calculate the minutes between ticks
        minutes = self._dates2minutes(date, last_tick)

        # Make sure that we dont have a past date
        if minutes < 0:
            raise RuntimeError("No time travel allowed")

        # Check if a new day has begun
        if last_tick.date() < date.date():
            self._reset_variables()

        # Calculate the power state
        self._calculate_state(date)

        kwh_draw: float = 0.0
        if self.power_state:
            # Calculate the power draw in kWh
            kwh_draw: float = self._power_usage * \
                    (1 + self._rng.uniform(
                        -self._power_fluctuation,
                        self._power_fluctuation
                        )
                    ) * (minutes/60)

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
            state_coeffs (list[float]): The coefficients of the state over time polynomial
            allowed_cycles (int): How many times are the appliance allowed to have a cycle in a day (0 and less is infinite)
            cycle_time_range (tuple[int, int]): Range to pick cycle time from (in minutes)
            continuos (bool): Does the appliance run continuosly?
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

    def _calculate_state(self: Self, date: datetime) -> None:
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
            last_tick: datetime,
            date: datetime,
            temperature: float
            ) -> tuple[bool, float, float]:
        """Tick the appliance and get the power state, kwh draw and heating effect

        Args:
            self (Self): self
            last_tick (datetime): Date and time of the last tick
            date (datetime): The date and time

        Returns:
            tuple[bool, float, float]: power state, kWh draw and heating effect
        """

        # Set the temperature (workaround till I get a better idea)
        self._temperature = temperature

        # Call the super tick
        _, kwh_draw, _ = super().tick(last_tick, date, override)

        # Calculate heating effect
        heating_effect = kwh_draw * self._heating_multiplier * \
                (1 + self._rng.uniform(
                    -self.heating_fluctuation,
                    self.heating_fluctuation
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
            continuos (bool): Does the appliance run continuosly?

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
            continuos (bool): Does the appliance run continuosly?

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
        'e': (189, 5200)
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
            bg_power_fluctuation: float
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

        # Set temperature
        self.current_temperature: float = start_temperature

        # Set the time
        self.date: datetime = datetime.fromtimestamp(start_time)

        # Set last tick to start date
        self.last_tick: datetime = self.date

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

    def _kj2celsius(self, kj: float) -> float:
        """Convert kj to celsius.

        Args:
            kj (float): kj

        Returns:
            float: celsius
        """

        return kj/(1.005 * self._kg_air)

    def _dates2minutes(self: Self, date1: datetime, date2: datetime) -> float:
        """Convert to dates to minute difference.

        Args:
            self (Self): self
            date1 (datetime): First date
            date2 (datetime): Second date

        Returns:
            float: minutes
        """

        return (date1 - date2).total_seconds()/60.0

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

    def _calculate_heat_gain(self: Self, kwh: float) -> float:
        """Calculate the gained celsius by the given kwh.

        Args:
            self (Self): self
            kwh (float): The added kwh to the system

        Returns:
            float: Gain in celsius
        """

        # Convert kwh to kj
        kj_gain: float = kwh*3600

        # Calculate the gain in celsius
        celsius_gain: float = self._kj2celsius(kj_gain)

        # Return the celsius gained
        return celsius_gain

    def update_time(self: Self, delta_time: float) -> None:
        """Update the time.

        Args:
            self (Self): self
            delta_time (float): Change in seconds

        Returns:
            None:
        """

        self.date += timedelta(seconds=delta_time)

    def set_time(self: Self, unix_time: int) -> None:
        """Set the time on the house.

        Args:
            self (Self): self
            unix_time (int): New time in unix format

        Returns:
            None:
        """

        self.date = datetime.fromtimestamp(unix_time)

    def tick(self: Self) -> tuple[list[bool], float, float]:
        """Tick the household, and return the device power states, total kWh draw and temperature.

        Args:
            self (Self): self

        Returns:
            tuple[list[bool], float, float]: Device states, total kWh draw and temperature
        """

        # Calculate the amount of minutes since last tick
        minutes: float = self._dates2minutes(self.date, self.last_tick)

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
                        self.date,
                        self.current_temperature
                        )
            else:
                power_state, kwh_draw, heating_kwh = appliance.tick(
                        self.last_tick,
                        self.date
                        )

            # Add the values to the variables
            power_states.append(power_state)
            total_kwh_draw += kwh_draw
            total_heating_kwh += heating_kwh

        # Calculate the new temperature
        self.current_temperature += self._calculate_heat_gain(total_heating_kwh) - \
            self._calculate_heat_loss(minutes)

        # Get sample points for background power
        sample_points: list[float] = linspace(
                self.last_tick.hour + (self.last_tick.minute/60),
                self.date.hour + (self.date.minute/60)
                )

        # Add the background power to the total power draw
        total_kwh_draw += sum(polyval(sample_points, self._bg_power_coeffs)) * \
                (1 + self._rng.uniform(
                    -self._bg_power_fluctuation,
                    self._bg_power_fluctuation
                    )
                )

        # Update the last_tick date
        self.last_tick: datetime = self.date

        return power_states, total_kwh_draw, self.current_temperature

