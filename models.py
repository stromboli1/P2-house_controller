# Import modules
from typing import Self, Type
from datetime import datetime, timedelta
from numpy.polynomial.polynomial import polyval
from numpy.random import default_rng, Generator

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
            appliances: list[Type[Appliance]]
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
            appliances (Type[Appliance]): The appliances of the house

        Returns:
            None:
        """

        # Set given parameters
        self.energy_label: str = energy_label.lower()
        self.sq_meters: float = sq_meters
        self.height_meter: float = height_meter
        self.active_days: int = active_days
        self.appliances: list[Type[Appliance]]

        # Set temperature
        self.current_temperature: float = start_temperature

        # Set the time
        self.current_time: int = start_time

        # Calculate the cubic meters of the house
        self.cubic_meters: float = self.sq_meters * self.height_meter

        # Calculate kg of the air inside the house
        self.kg_air: float = self.cubic_meters * 1.219

        if not self.LIMIT_VALUES.get(self.energy_label, None):
            raise ValueError("Energy Label is invalid")

        self.limit_value: tuple[int, int] = self.LIMIT_VALUES.get(self.energy_label)
        
    def _kj2celsius(self, kj: float) -> float:
        """Convert kj to celsius.

        Args:
            kj (float): kj

        Returns:
            float: celsius
        """

        return kj*(1.005 * self.kg_air)

    def calculate_heat_loss(self: Self, minutes: int) -> float:
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
        kwh_minute_loss: float = kwh_year_loss/(self.active_days*24*60)

        # Convert to kj
        kj_minute_loss: float = kwh_minute_loss*3600

        # Calculate celsius change
        celsius_minute_loss: float = self._kj2celsius(kj_minute_loss)

        # Return the celsius scaled to the minutes
        return celsius_minute_loss * minutes

    def calculate_heat_gain(self: Self, kwh: float) -> float:
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

    def tick(self: Self, minutes: int) -> None:
        """Tick the household.

        Args:
            self (Self): self.
            minutes (int): duration of tick.

        Returns:
            None:
        """

        # TODO: Calculate the kwh
        kwh = 0 # DELETE ME!!
        delta_temperature: float = self.calculate_heat_gain(kwh) - \
            self.calculate_heat_loss(minutes)

        self.current_temperature += delta_temperature

class Appliance():

    # TODO List:
    #
    # Make a generised power usage calculation
    # Make variables reset between days
    #
    # Make all subclasses use the newly general functions

    # The state of the appliance
    power_state: bool = False
    _power_lock: bool = False

    # Datetime object to track the start of a cycle
    cycle_end_time: Optional[datetime] = None

    # Keep track of how many times the appliance has been cycled
    cycle_count: int = 0

    def __init__(
            self: Self,
            controllable: bool,
            state_coeffs: list[float],
            allowed_cycles: int,
            cycle_time_range: tuple[int, int]
            ) -> None:
        """Initialize the appliance.

        Args:
            self (Self): self
            controllable (bool): Is the appliance controllable
            state_coeffs (list[float]): The coefficients of the state over time polynomial
            allowed_cycles (int): How many times are the appliance allowed to have a cycle in a day (0 and less is infinite)
            cycle_time_range (tuple[int, int]): Range to pick cycle time from (in minutes)

        Returns:
            None:
        """

        self.controllable: bool = controllable
        self.state_coeffs: list[float] = state_coeffs
        self.allowed_cycles: int = allowed_cycles
        self.cycle_time_range: tuple[int, int] = cycle_time_range

        # Make a randomness generator
        self._rng: Generator = default_rng()

    def power_locker(self: Self, lock: bool) -> None:
        if not self.controllable:
            raise RuntimeWarning("Appliance is not controllable")
            return

        self._power_lock: bool = lock
        if self._power_lock:
            self.power_state: bool = False

    def calculate_state(self: Self, date: datetime) -> None:

        # Check if we are already in a cycle
        if date < self.cycle_end_time:
            # Check if it is locked, dont do anything
            if self._power_lock:
                return

            self.power_state: bool = True
            return
        else:
            # Turn it off if it isnt in a cycle
            self.power_state: bool = False

        # Check if it should be turned on
        if not self.power_state:
            # Make sure that it has more allowed cycles
            if self.cycle_count < self.allowed_cycles and not self.allowed_cycles <= 0:
                return

            # Sample a probability polynomial
            sample_point: float = date.hour + (date.minute/60)

            if self._rng.uniform() <= polyval(sample_point, self.state_coeffs):
                self.power_state: bool = True
                self.cycle_count += 1
                self.cycle_end_time: datetime = date + \
                        timedelta(minutes=self._rng.integers(
                            self.cycle_time_range[0], self.cycle_time_range[1]))

    def tick(self: Self, minutes: int, date: datetime) -> tuple[bool, float]:
        """Tick the appliance and get the state and kwh draw.

        Args:
            self (Self): self
            minutes (int): duration of tick.

        Returns:
            tuple[bool, float]: state and kwh draw
        """

        self.calculate_state(date)

        kwh_draw: float = 0
        if self.power_state:
            # TODO: Calculate power draw
            pass

        return kwh_draw

class Heatpump(Appliance):

    def __init__(self: Self,
                 averkwh: float,
                 variance: float,
                 ) -> None:
        """Initiazalize the heatpump.

        Args:
            self (Self): self

        Returns:
            None:
        """
        self.variables: float = variance
        self.averkwh: float = averkwh
        self.kwh_min: float = self.averkwh/24/60

        super().__init__(controllable=True)

    def tick(self: Self, minutes: int, date: datetime, temperature: float) -> float:
        """Tick the heatpump and get the kwh draw.

        Args:
            self (Self): self
            minutes (int): duration of the tick

        Returns:
            float: kwh draw
        """

        kws_swing = self.kwh_min * self.rng.uniform(-self.variance, self.variance)
        kwh_used = (self.kwh_min + kws_swing)*minutes

        #check if the heatpump has been on
        if  heating.temp <= 19:
            return self.kwh_used

        return super().tick(minutes), kwh_used

    def heating(self: Self, minutes: int) -> float:
        """Get the heating effect.

        Args:
            self (Self): self
            minutes (int): duration to the the effect of

        Returns:
            float: effect in kwh
        """
        kj_gain: float = self.kwh_used
        celsius_gain = self._kj2celsius(kj_gain)
        if self.on_state:
            # TODO: stuff
            pass

        return celsius_gain 

class Dryer(Appliance):
    """Dryer class for simulating a dryer."""

    def __init__(self: Self, power_usage) -> None:
        """Initialise the dryer.

        Args:
            self (Self): self

        Returns:
            None:
        """

        # The amount of power used by the dryer in one drying cycle.
        self.power_usage = power_usage

        
        super().__init__(controllable=False)

    def check(self, time_of_day: int):
        """Check if the dryer will be turned on.

        Args:
            time_of_day (int): The time of day given in seconds.
        """
        on_chance_level = self.dryer_dictionary[(time_of_day//3600)]

        # The dryer check only happens once per hour (at random).
        chance_per_hour = self.rng.integers(0,3600)
        on_chance = self.rng.random()

        if chance_per_hour == 0 and on_chance <= on_chance_level and self.flag == 0:
            return 1
        elif self.flag == 1:
            return 2
        else:
            return 0

    def consumption_calc(self, time_of_day: int):
        """Calculate the consumption if dryer is used.

        Args:
            time_of_day (int): Time of day in seconds.
        """
        consumption = float(self.power_usage)
        fluctuation = float(self.rng.integers(-2, 5)/100)
        consumption += fluctuation
        self.flag = 1
        self.flag_time = time_of_day
        self.flag_consumption = consumption
        return consumption

    def tick(self: Self, minutes: int, time_of_day: int) -> float:
        """Tick the dryer and get the kwh draw.

        Args:
            self (Self): self
            minutes (int): duration of the tick
            time_of_day (int): Time of day in seconds

        Returns:
            float: kwh draw
        """

        tick_consumption = 0

        f
        if tick_consumption > 0:
            tick_consumption = tick_consumption/(minutes*60)

        return tick_consumption

    def reset(self):
        """Resets key variables. Should be used when a new day starts."""

        self.flag = 0
        self.flag_consumption = 0
        self.flag_time = 0
        self.cycle_time = self.rng.integers(3400,7200)

class Oven(Appliance):
    """Oven class for simulating a oven."""

    def __init__(self: Self, power_usage) -> None:
        """Initialise the oven.

        Args:
            self (Self): self

        Returns:
            None:
        """

        # The amount of power used by the oven in one cycle.
        self.power_usage = power_usage

        # Flag indicating whether or not the dryer has been used.
        
        super().__init__(controllable=False)

    def check(self, time_of_day: int):
        """Check if the oven will be turned on.

        Args:
            time_of_day (int): The time of day given in seconds.
        """
        on_chance_level = self.oven_dictionary[(time_of_day//3600)]

        # The oven check only happens once per hour (at random).
        chance_per_hour = self.rng.integers(0,3600)
        on_chance = self.rng.random()

        if chance_per_hour == 0 and on_chance <= on_chance_level and self.flag == 0:
            return 1
        elif self.flag == 1:
            return 2
        else:
            return 0

    def consumption_calc(self, time_of_day: int):
        """Calculate the consumption if oven is used.

        Args:
            time_of_day (int): Time of day in seconds.
        """
        consumption = float(self.power_usage)
        fluctuation = float(self.rng.integers(-2, 5)/100)
        consumption += fluctuation
        self.flag = 1
        self.flag_time = time_of_day
        self.flag_consumption = consumption
        return consumption

    def tick(self: Self, minutes: int, time_of_day: int) -> float:
        """Tick the oven and get the kwh draw.

        Args:
            self (Self): self
            minutes (int): duration of the tick
            time_of_day (int): Time of day in seconds

        Returns:
            float: kwh draw
        """

        
        if tick_consumption > 0:
            tick_consumption = tick_consumption/(minutes*60)

        return tick_consumption

    def reset(self):
        """Resets key variables. Should be used when a new day starts."""

        self.flag = 0
        self.flag_consumption = 0
        self.flag_time = 0
        self.cycle_time = self.rng.integers(3600,7200)

class background_power_consumption(Appliance):
    """Used for simulating background power consumption."""

    def __init__(self: Self) -> None:
        """Initialise background power consumption.

        Args:
            self (Self): self

        Returns:
            None:
        """


        # Dictionary with level of background power being used.
        self.background_dict = {0: 0.30,
                                1: 0.30,
                                2: 0.30,
                                3: 0.30,
                                4: 0.30,
                                5: 0.30,
                                6: 0.32,
                                7: 0.36,
                                8: 0.38,
                                9: 0.35,
                                10: 0.32,
                                11: 0.32,
                                12: 0.35,
                                13: 0.38,
                                14: 0.38,
                                15: 0.40,
                                16: 0.45,
                                17: 0.48,
                                18: 0.51,
                                19: 0.51,
                                20: 0.51,
                                21: 0.45,
                                22: 0.40,
                                23: 0.30}

        super().__init__(controllable=False)

    def tick(self, minutes:int, time_of_day: int):
        """Tick the background power consumption and get the kwh draw.

        Args:
            self (Self): self
            minutes (int): duration of the tick
            time_of_day (int): Time of day in seconds

        Returns:
            float: kwh draw
        """
        tick_consumption = 0
        for seconds in range(minutes*60):
            tick_consumption += self.rng.uniform(-0.05, 0.05)
            time = time_of_day+seconds
            tick_consumption += self.background_dict[(time)//3600]
        return tick_consumption/60
