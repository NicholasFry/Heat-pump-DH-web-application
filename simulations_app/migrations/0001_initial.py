# Generated by Django 3.2.6 on 2021-08-12 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SimParameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upper_terminal_temperature_difference_condenser', models.IntegerField(default=5, max_length=2)),
                ('lower_terminal_temperature_difference_evaporator', models.IntegerField(default=5, max_length=2)),
                ('water_pump_efficiency', models.DecimalField(decimal_places=2, default=0.75, max_digits=3)),
                ('district_heating_pump_efficiency', models.DecimalField(decimal_places=2, default=0.75, max_digits=3)),
                ('evaporator_pump_efficiency', models.DecimalField(decimal_places=2, default=0.85, max_digits=3)),
                ('compressor_efficiency', models.DecimalField(decimal_places=2, default=0.85, max_digits=3)),
                ('temp_district_heat_return', models.IntegerField(default=50, max_length=3)),
                ('pressure_in_bar_dh', models.IntegerField(default=10, max_length=2)),
                ('dh_supply_temp', models.IntegerField(default=70, max_length=3)),
                ('wasted_heat_design_temperature', models.IntegerField(default=30, max_length=3)),
                ('pressure_in_bar_waste_heat_fluid', models.IntegerField(default=2, max_length=2)),
                ('return_pressure_from_heat_pump', models.IntegerField(default=2, max_length=2)),
                ('return_temperature_from_heat_pump', models.IntegerField(default=30, max_length=3)),
                ('dh_heat_demand_in_watts', models.IntegerField(default=4000000, max_length=8)),
            ],
        ),
    ]