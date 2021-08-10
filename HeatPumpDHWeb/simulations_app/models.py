from django.db import models


class SimParameters(models.Model):
    upper_terminal_temperature_difference_condenser = models.IntegerField(max_length=2, default=5)
    lower_terminal_temperature_difference_evaporator = models.IntegerField(max_length=2, default=5)
    water_pump_efficiency = models.DecimalField(max_digits=3, decimal_places=2, default=.75)#pass as decimal, maybe FloatField is better?
    district_heating_pump_efficiency = models.DecimalField(max_digits=3, decimal_places=2, default=.75)#pass as decimal
    evaporator_pump_efficiency = models.DecimalField(max_digits=3, decimal_places=2, default=.85)
    compressor_efficiency = models.DecimalField(max_digits=3, decimal_places=2, default=.85)
    temp_district_heat_return = models.IntegerField(max_length=3, default=50)
    pressure_in_bar_dh = models.IntegerField(max_length=2, default=10)
    dh_supply_temp = models.IntegerField(max_length=3, default=70)
    wasted_heat_design_temperature=models.IntegerField(max_length=3, default=30)
    offdesign1_wasted_heat_design_temperature = wasted_heat_design_temperature-6
    offdesign2_wasted_heat_design_temperature = wasted_heat_design_temperature-3
    offdesign3_wasted_heat_design_temperature = wasted_heat_design_temperature+3
    offdesign4_wasted_heat_design_temperature = wasted_heat_design_temperature+6
    pressure_in_bar_waste_heat_fluid=models.IntegerField(max_length=2, default=2)
    return_pressure_from_heat_pump=models.IntegerField(max_length=2, default=2)
    return_temperature_from_heat_pump=models.IntegerField(max_length=3, default=30)
    dh_heat_demand_in_watts=(-models.IntegerField(max_length=8, default=4000000))#consider edge cases like user inputs that are negative
    offdesign1_dh_heat_demand_in_watts = dh_heat_demand_in_watts*.60
    offdesign2_dh_heat_demand_in_watts = dh_heat_demand_in_watts*.80
    offdesign3_dh_heat_demand_in_watts = dh_heat_demand_in_watts*1.2
    offdesign4_dh_heat_demand_in_watts = dh_heat_demand_in_watts*1.4

    def __str__(self):#if you ever print params, if you don't have then you get a memory location
        return self.dh_supply_temp