""" The house_model module is used for creating a house model for 
simulating heating and heat loss.

"""

class House:
    """ The House class is used to create a house object, which can be used
    in the simulations of heating and heat loss.

    As input, the class takes energy label, square meters and wall height in meters.

    Example:
    >>> house_1 = House('A', 100, 3)
    >>> print(house_1.heat_loss())
    0.004452054794520548

    >>> weight = house_1.kg_m3_to_kg()
    >>> print(weight)
    365.70000000000005

    >>> kJ = house_1.heating_kJ(18, 21, weight)
    >>> print(kJ)
    1102.5855000000001

    >>> kWh = house_1.heating_kWh(kJ)
    >>> print(kWh)
    0.30627375
                                    
    """

    def __init__(self, energy_label, sq_meters, wall_height) -> None:
        self.energy_label = energy_label
        self.sq_meters = sq_meters
        self.wall_height = wall_height
        self.cubic_meters = sq_meters * wall_height

    def heat_loss(self):
        if self.energy_label == 'A':
           year = 29+(1000/self.sq_meters)
           hour = year/(365*24)
           return(hour)
        elif self.energy_label == 'B':
           year = 69+(2200/self.sq_meters)
           hour = year/(365*24)
           return(hour)
        elif self.energy_label == 'C':
            year = 109+(3200/self.sq_meters)
            hour = year/(365*24)
            return(hour)
        
    def kg_m3_to_kg(self):
        """ The kg_m3_to_kg function returns the weight of the air inside the 
        house.
        
        """

        return(self.cubic_meters * 1.219)
    
    def heating_kJ(self, start_temp, end_temp, kg):
        """ The heating_kJ function is used to calculate the amount of 
        energy needed to change the temperature in the house from the start 
        temperature to the end temperature.

        The function returns the energy amount given in kJ.

        """
        delta_temp = end_temp-start_temp
        return(1.005 * kg * delta_temp)
    
    def heating_kWh(self, kJ):
        """ The heating_kWh function is used for turning the amount of kJ 
        into kWh.

        """
        return(kJ/3600)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
