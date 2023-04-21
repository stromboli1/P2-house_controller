# import modules
from typing import Self
import random

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
            active_days: int
            ) -> None:
        """Initialize Household.

        Args:
            self (Self): self
            energy_label (str): The energy label of the house
            sq_meters (float): The square meters floor space
            height_meter (float): The height of the walls

        Returns:
            None:
        """

        # Set given parameters
        self.energy_label: str = energy_label.lower()
        self.sq_meters: float = sq_meters
        self.height_meter: float = height_meter
        self.active_days: int = active_days

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

    def _kj2celsius(kj: float) -> float:
        """Convert kj to celsius.

        Args:
            kj (float): kj

        Returns:
            float: celsius
        """

        return kj*(1.005 * (self.kg_air))

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

    # The state of the appliance
    on_state: bool = False

    def __init__(self: Self, 
                 controllable: bool,
                 ) -> None:
        """Initialize the appliance.

        Args:
            self (Self): self
            controllable (bool): Is the appliance controllable

        Returns:
            None:
        """

        self.controllable: bool = controllable

    def tick(self: Self, minutes: int) -> float:
        """Tick the appliance and get the kwh draw.

        Args:
            self (Self): self
            minutes (int): duration of tick.

        Returns:
            float: kwh draw
        Raises:
            NotImplementedError: The appliance doesn't have a tick
        """

        kwh_draw: float = 0
        if self.on_state:
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

    def tick(self: Self, minutes: int) -> float:
        """Tick the heatpump and get the kwh draw.

        Args:
            self (Self): self
            minutes (int): duration of the tick

        Returns:
            float: kwh draw
        """
        
        kws_swing = self.kwh_min * random.uniform(-self.variance, self.variance)
        self.kwh_used = (self.kwh_min + kws_swing)*minutes

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
        cellsiuscellsius_gain = self._kj2celsius(kj_gain)
        if self.on_state:
            # TODO: stuff
            pass

        return cellsius_gain 

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

        # Flag indicating whether or not the dryer has been used.
        self.flag = 0

        # Time at which the dryer_flag was raised.
        self.flag_time = 0

        # Consumption level from when the flag was raised.
        self.flag_consumption = 0

        # Amount of time the dryer is turned on.
        self.cycle_time = random.randint(3400, 7200)

        # Dictionary with chance of the dryer being used.
        self.dryer_dictionary = {0: 0.02,
                                1: 0.01,
                                2: 0.01,
                                3: 0.01,
                                4: 0.01,
                                5: 0.01,
                                6: 0.03,
                                7: 0.05,
                                8: 0.04,
                                9: 0.03,
                                10: 0.02,
                                11: 0.02,
                                12: 0.02,
                                13: 0.03,
                                14: 0.06,
                                15: 0.15,
                                16: 0.16,
                                17: 0.23,
                                18: 0.32,
                                19: 0.38,
                                20: 0.40,
                                21: 0.30,
                                22: 0.15,
                                23: 0.08}
        
        super().__init__(controllable=False)

    def check(self, time_of_day: int):
        """Check if the dryer will be turned on.

        Args:
            time_of_day (int): The time of day given in seconds.
        """
        on_chance_level = self.dryer_dictionary[(time_of_day//3600)]

        # The dryer check only happens once per hour (at random).
        chance_per_hour = random.randint(0,3600)
        on_chance = random.random()

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
        fluctuation = float(random.randint(-2, 5)/100)
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

        for seconds in range(int(minutes*60)):
            check_sum = self.check(time_of_day+seconds)
            if check_sum == 0:
                tick_consumption += 0
            elif check_sum == 1:
                tick_consumption += self.consumption_calc(time_of_day+seconds)
            elif check_sum == 2:
                flag_time_diff = (time_of_day + seconds) - self.flag_time
                if flag_time_diff < self.cycle_time:
                    return self.flag_consumption
                else:
                    return(0)

        if tick_consumption > 0:
            tick_consumption = tick_consumption/(minutes*60)
        
        return tick_consumption

    def reset(self):
        """Resets key variables. Should be used when a new day starts."""

        self.flag = 0
        self.flag_consumption = 0
        self.flag_time = 0
        self.cycle_time = random.randint(3400,7200)

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
        self.flag = 0

        # Time at which the flag was raised.
        self.flag_time = 0

        # Consumption level from when the flag was raised.
        self.flag_consumption = 0

        # Amount of time the oven is turned on.
        self.cycle_time = random.randint(3400, 7200)

        # Dictionary with chance of the oven being used.
        self.oven_dictionary = {0: 0.03,
                                1: 0.02,
                                2: 0.02,
                                3: 0.02,
                                4: 0.03,
                                5: 0.04,
                                6: 0.05,
                                7: 0.07,
                                8: 0.06,
                                9: 0.02,
                                10: 0.02,
                                11: 0.02,
                                12: 0.02,
                                13: 0.04,
                                14: 0.06,
                                15: 0.15,
                                16: 0.30,
                                17: 0.35,
                                18: 0.30,
                                19: 0.30,
                                20: 0.10,
                                21: 0.08,
                                22: 0.06,
                                23: 0.04}
        
        super().__init__(controllable=False)

    def check(self, time_of_day: int):
        """Check if the oven will be turned on.

        Args:
            time_of_day (int): The time of day given in seconds.
        """
        on_chance_level = self.oven_dictionary[(time_of_day//3600)]

        # The oven check only happens once per hour (at random).
        chance_per_hour = random.randint(0,3600)
        on_chance = random.random()

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
        fluctuation = float(random.randint(-2, 5)/100)
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
        
        tick_consumption = 0

        for seconds in range(int(minutes*60)):
            check_sum = self.check(time_of_day+seconds)
            if check_sum == 0:
                tick_consumption += 0
            elif check_sum == 1:
                tick_consumption += self.consumption_calc(time_of_day+seconds)
            elif check_sum == 2:
                flag_time_diff = (time_of_day + seconds) - self.flag_time
                if flag_time_diff < self.cycle_time:
                    return self.flag_consumption
                else:
                    return(0)

        if tick_consumption > 0:
            tick_consumption = tick_consumption/(minutes*60)
        
        return tick_consumption

    def reset(self):
        """Resets key variables. Should be used when a new day starts."""

        self.flag = 0
        self.flag_consumption = 0
        self.flag_time = 0
        self.cycle_time = random.randint(3600,7200)

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
            tick_consumption += random.uniform(-0.05, 0.05)
            time = time_of_day+seconds
            tick_consumption += self.background_dict[(time)//3600]
        return tick_consumption/60
