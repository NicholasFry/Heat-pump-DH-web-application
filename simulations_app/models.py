from django.db import models


class SimParameters(models.Model):
    # name = models.CharField(max_length=100, default='user_simulation')
    # id = models.PositiveIntegerField(primary_key=True, db_column='id')
    upper_terminal_temperature_difference_condenser = models.IntegerField(default=5)
    lower_terminal_temperature_difference_evaporator = models.IntegerField(default=5)
    # water_pump_efficiency = models.DecimalField(max_digits=2, decimal_places=2, default=.75)#pass as decimal, maybe FloatField is better?
    # district_heating_pump_efficiency = models.DecimalField(max_digits=2, decimal_places=2, default=.75)#pass as decimal
    # evaporator_pump_efficiency = models.DecimalField(max_digits=2, decimal_places=2, default=.85)
    # compressor_efficiency = models.DecimalField(max_digits=2, decimal_places=2, default=.85)
    water_pump_efficiency = models.FloatField(default=.75)#TESPy does not like using the DecimalField in the components.py
    district_heating_pump_efficiency = models.FloatField(default=.75)#pass as decimal
    evaporator_pump_efficiency = models.FloatField(default=.85)
    compressor_efficiency = models.FloatField(default=.85)
    temp_district_heat_return = models.IntegerField(default=50)
    pressure_in_bar_dh = models.IntegerField(default=10)
    dh_supply_temp = models.IntegerField(default=70)
    wasted_heat_design_temperature=models.IntegerField(default=35)
    # offdesign1_wasted_heat_design_temperature = wasted_heat_design_temperature-6#this will have to go in views.py
    # offdesign2_wasted_heat_design_temperature = wasted_heat_design_temperature-3
    # offdesign3_wasted_heat_design_temperature = wasted_heat_design_temperature+3
    # offdesign4_wasted_heat_design_temperature = wasted_heat_design_temperature+6
    pressure_in_bar_waste_heat_fluid=models.IntegerField(default=2)
    return_pressure_from_heat_pump=models.IntegerField(default=2)
    return_temperature_from_heat_pump=models.IntegerField(default=15)
    dh_heat_demand_in_watts=(models.IntegerField(default=4000000))#consider edge cases like user inputs that are negative
    # offdesign1_dh_heat_demand_in_watts = dh_heat_demand_in_watts*.60
    # offdesign2_dh_heat_demand_in_watts = dh_heat_demand_in_watts*.80
    # offdesign3_dh_heat_demand_in_watts = dh_heat_demand_in_watts*1.2
    # offdesign4_dh_heat_demand_in_watts = dh_heat_demand_in_watts*1.4

    def __str__(self):#if you ever print params, if you don't have then you get a memory location
        return f'this object is {self.id}'