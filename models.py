# import modules
from typing import Self

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

    def __init__(self: Self,
        energy_label: str,
        sq_meters: float,
        height_meter: float,
        start_temperature: float,
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

        return kj*(1.005*self.kg_air)

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

    def __init__(self: Self, controllable: bool) -> None:
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
        raise NotImplementedError("Tick is not implemented")

class Heatpump(Appliance):

    def __init__(self: Self) -> None:
        """Initiazalize the heatpump.

        Args:
            self (Self): self

        Returns:
            None:
        """

        super().__init__(controllable=True)

    def tick(self: Self, minutes: int) -> float:
        """Tick the heatpump and get the kwh draw.

        Args:
            self (Self): self
            minutes (int): duration of the tick

        Returns:
            float: kwh draw
        """

        kwh_draw: float = 0
        if on_state:
            # TODO: stuff
            pass

        return kwh_draw

    def heating(self: Self, minutes: int) -> float:
        """Get the heating effect.

        Args:
            self (Self): self
            minutes (int): duration to the the effect of

        Returns:
            float: effect in kwh
        """

        kwh_heating: float = 0
        if on_state:
            # TODO: stuff
            pass

        return kwh_heating
