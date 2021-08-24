from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
# from django.http.response import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from tespy.networks import Network
from tespy.components import (
    Sink, Source, Splitter, Compressor, Condenser, Pump, HeatExchangerSimple,
    Valve, Drum, HeatExchanger, CycleCloser
)
from tespy.connections import Connection, Ref
from tespy.tools.characteristics import CharLine
from tespy.tools.characteristics import load_default_char as ldc
from tespy.tools import document_model

from simulations_app.models import SimParameters
# from .migrations import *

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class PrepareSimulation(CreateAPIView):
    def post(self, request, format=None):
        # print(request)
        # print(request.data)
        # print(request.POST)
        all_user_inputs = request.data
        # print(all_user_inputs)
        upper_terminal_temperature_difference_condenser = all_user_inputs['ttd_condenser']
        lower_terminal_temperature_difference_evaporator  = all_user_inputs['ttd_evaporator']
        water_pump_efficiency = all_user_inputs['water_pump_eff']
        district_heating_pump_efficiency  = all_user_inputs['dh_pump_eff']
        evaporator_pump_efficiency = all_user_inputs['evap_pump_eff']
        compressor_efficiency = all_user_inputs['compressor_eff']
        temp_district_heat_return = all_user_inputs['dh_return_temp']
        pressure_in_bar_dh = all_user_inputs['pressure_bar_dh']
        dh_supply_temp = all_user_inputs['dh_supply_temp']
        wasted_heat_design_temperature = all_user_inputs['waste_design_temp']
        pressure_in_bar_waste_heat_fluid = all_user_inputs['waste_design_pressure']
        return_pressure_from_heat_pump = all_user_inputs['return_pressure_from_hp']
        return_temperature_from_heat_pump  = all_user_inputs['return_temperature_from_hp']
        dh_heat_demand_in_watts = all_user_inputs['dh_demand_watts']
        # print(dh_heat_demand_in_watts)
        # print(district_heating_pump_efficiency)
        SimParameters.objects.create(
        upper_terminal_temperature_difference_condenser=upper_terminal_temperature_difference_condenser,
        lower_terminal_temperature_difference_evaporator=lower_terminal_temperature_difference_evaporator,
        water_pump_efficiency=water_pump_efficiency,
        district_heating_pump_efficiency=district_heating_pump_efficiency,
        evaporator_pump_efficiency=evaporator_pump_efficiency,
        compressor_efficiency=compressor_efficiency,
        temp_district_heat_return=temp_district_heat_return,
        pressure_in_bar_dh=pressure_in_bar_dh,
        dh_supply_temp=dh_supply_temp,
        wasted_heat_design_temperature=wasted_heat_design_temperature,
        pressure_in_bar_waste_heat_fluid=pressure_in_bar_waste_heat_fluid,
        return_pressure_from_heat_pump=return_pressure_from_heat_pump,
        return_temperature_from_heat_pump=return_temperature_from_heat_pump,
        dh_heat_demand_in_watts=dh_heat_demand_in_watts,
        )
        stuff = SimParameters.objects.last()#this means row id

        # print(stuff)
        # print(stuff.id)
        # print(stuff.pk)
        return Response(stuff.id)
        # return RunSimulation.get(self, request, dh_supply_temp)
class RunSimulation(APIView):
    def get(self, request, pk, format=None):
        sim_parameters = get_object_or_404(SimParameters, id=self.kwargs['pk'])
        # %% network
        #Water is used for the cold side of the heat exchanger, for the consumer and for the hot side of the environmental temperature.
        #Ammonia is used as coolant within the heat pump circuit.
        nw = Network(
            fluids=['water', 'NH3'], T_unit='C', p_unit='bar', h_unit='kJ / kg',
            m_unit='kg / s'
        )

        # %% components

        # sources & sinks
        cc1 = CycleCloser('coolant cycle closer1')#CycleCloser component makes sure, the fluid properties pressure and enthalpy are identical at the inlet and the outlet. 
        # cc2 = CycleCloser('coolant cycle closer2')#add later for heat pump 2
        cc_cons = CycleCloser('consumer cycle closer')
        electra_therm_rejected_heat = Source('source heat from electratherm')
        # exit_heat_from_condenser1 = Source('source heat from condenser1 exit')#added by trial and error
        # exit_heat_from_evaporator1 = Sink('exit_heat_from_evaporator1')#added by trial and error
        sink_electratherm_cooling_reservoir= Sink('sink cool water')
        pu = Pump('pump')#pumps source heat from ElectraTherm rejected heat reservoir

        # consumer system

        condenser_1 = Condenser('condenser 1')#closest to cooling reservoir
        district_heating_pump = Pump('district heating pump')#feeds the first condenser 
        cons_1 = HeatExchangerSimple('consumer 1')#exits the first condenser, enters the second condenser

        ves1 = Valve('valve 1')
        dr1 = Drum('drum 1')
        ev1 = HeatExchanger('evaporator 1')
        erp1 = Pump('evaporator recirculation pump 1')

        # compressor-system(s)

        compressor1 = Compressor('compressor 1')

        # %% connections

        # consumer system

        c_in_condenser_1 = Connection(cc1, 'out1', condenser_1, 'in1')#cyclecloser to condenser 1, see https://tespy.readthedocs.io/en/main/tutorials_examples.html#cop-of-a-heat-pump

        cb_district_heating_pump = Connection(cc_cons, 'out1', district_heating_pump, 'in1')#return from DH
        district_heating_pump_condenser_1 = Connection(district_heating_pump, 'out1', condenser_1, 'in2')#DH pump feeds condenser 1 (return from DH)
        condenser1_cons = Connection(condenser_1, 'out2', cons_1, 'in1')
        cons_cf = Connection(cons_1, 'out1', cc_cons, 'in1')#out to consumer DH network with cycle closer for enthalpy and pressure match

        nw.add_conns(c_in_condenser_1, cb_district_heating_pump, district_heating_pump_condenser_1, condenser1_cons, cons_cf)

        # connection condenser - evaporator system

        condenser1_ves = Connection(condenser_1, 'out1', ves1, 'in1')#condeser to expansion valve

        nw.add_conns(condenser1_ves)

        ves1_dr1 = Connection(ves1, 'out1', dr1, 'in1')#valve connects to drum at inlet
        dr1_erp1 = Connection(dr1, 'out1', erp1, 'in1')#drum outlet to evaporator recirculation pump inlet
        erp1_ev1 = Connection(erp1, 'out1', ev1, 'in2')#pump outlet to evaporator inlet
        ev1_dr1 = Connection(ev1, 'out2', dr1, 'in2')#evaporator outlet to drum inlet

        nw.add_conns(ves1_dr1, dr1_erp1, erp1_ev1, ev1_dr1)#add all the connections above to the network, Connections is a class, add_conns is the function that takes them in

        rejected_heat_to_pump = Connection(electra_therm_rejected_heat, 'out1', pu, 'in1')
        p_ev1 = Connection(pu, 'out1', ev1, 'in1')#pump to evaporator1
        ev1_sink = Connection(ev1, 'out1', sink_electratherm_cooling_reservoir, 'in1')#exit to cooling reservoir

        nw.add_conns(rejected_heat_to_pump, p_ev1, ev1_sink)

        # connection evaporator system - compressor system

        dr1_compressor1 = Connection(dr1, 'out2', compressor1, 'in1')#drum outlet2 to compressor1

        nw.add_conns(dr1_compressor1)

        compressor1_c_out = Connection(compressor1, 'out1', cc1, 'in1')

        nw.add_conns(compressor1_c_out)

        # %% component parametrization
        # ttd_u=sim_parameters.upper_terminal_temperature_difference_condenser
        # print(ttd_u)
        # print(type(ttd_u))
        # print(type(sim_parameters.wasted_heat_design_temperature))
        # print(type(sim_parameters.dh_heat_demand_in_watts))
        # print(type(sim_parameters.district_heating_pump_efficiency))
        # print(type(sim_parameters.pressure_in_bar_waste_heat_fluid))
        # print(type(sim_parameters.evaporator_pump_efficiency))
        # condenser system
        condenser_1.set_attr(pr1=0.99, pr2=0.99, ttd_u=sim_parameters.upper_terminal_temperature_difference_condenser, design=['pr2', 'ttd_u'], #upper terminal temperature difference as design parameter, pressure ratios
                    offdesign=['zeta2', 'kA_char'])#kA_char is area independent heat transfer coefficient characteristic
        district_heating_pump.set_attr(eta_s=sim_parameters.district_heating_pump_efficiency, design=['eta_s'], offdesign=['eta_s_char'])#efficiency of the district heating pump set to 80%
        cons_1.set_attr(pr=0.99, design=['pr'], offdesign=['zeta'])#In offdesign calculation the consumer’s pressure ratio will be a function of the mass flow, thus as offdesign parameter we select zeta

        # water pump

        pu.set_attr(eta_s=sim_parameters.water_pump_efficiency, design=['eta_s'], offdesign=['eta_s_char'])#this is for a 75% pump efficiency

        # evaporator system

        kA_char1 = ldc('heat exchanger', 'kA_char1', 'DEFAULT', CharLine)#Characteristic line for hot side heat transfer coefficient. heat transfer coefficient multiplied by the area of HEX, Charline is the linear interpolation equation of the x, y; DEFAULT HEX function is charted here https://tespy.readthedocs.io/en/main/api/tespy.data.html?highlight=DEFAULT#default-characteristics
        kA_char2 = ldc('heat exchanger', 'kA_char2', 'EVAPORATING FLUID', CharLine)#Characteristic line for cold side heat transfer coefficient (ammonia in this case for Mandaree)

        ev1.set_attr(pr1=0.98, pr2=0.99, ttd_l=sim_parameters.lower_terminal_temperature_difference_evaporator, #pressure_ratio1, pressure_ratio2, terminal_temperature_difference1(terminal temperature difference at the evaporator’s cold side inlet)
                    kA_char1=kA_char1, kA_char2=kA_char2,
                    design=['pr1', 'ttd_l'], offdesign=['zeta1', 'kA_char'])
        erp1.set_attr(eta_s=sim_parameters.evaporator_pump_efficiency, design=['eta_s'], offdesign=['eta_s_char'])#eta_s is the Isentropic (adiabatic) efficiency of the process

        # compressor system

        compressor1.set_attr(eta_s=sim_parameters.compressor_efficiency, design=['eta_s'], offdesign=['eta_s_char'])#docs say not to set compressor 1 pressure ratio for parallel, if adding another compressor later remove pressure ratio, #pressure ratio 3:1 outlet:inlet

        # %% connection parametrization

        # condenser system

        c_in_condenser_1.set_attr(fluid={'NH3': 1, 'water': 0})
        cb_district_heating_pump.set_attr(T=sim_parameters.temp_district_heat_return, p=sim_parameters.pressure_in_bar_dh, fluid={'NH3': 0, 'water': 1})
        condenser1_cons.set_attr(T=sim_parameters.dh_supply_temp)#temperature feeding the DH network

        # evaporator system cold side

        erp1_ev1.set_attr(m=Ref(ves1_dr1, 1.25, 0), p0=5)#pump outlet to evaporator1 Ref(ref_obj, factor, delta)

        # evaporator system hot side (from ElectraTherm rejection)

        # pumping at constant rate in partial load
        rejected_heat_to_pump.set_attr(T=sim_parameters.wasted_heat_design_temperature, p=sim_parameters.pressure_in_bar_waste_heat_fluid, fluid={'NH3': 0, 'water': 1},
                    offdesign=['v'])#here I assume we are maintaining 2 bar in the partial load condition from rejected heat reservoir from generators at 38C
        ev1_sink.set_attr(p=sim_parameters.return_pressure_from_heat_pump, T=sim_parameters.return_temperature_from_heat_pump, design=['T'])#this would be the return temperature to the cooling reservoir from the heat pump

        # %% key paramter (consumer demand)

        cons_1.set_attr(Q=-sim_parameters.dh_heat_demand_in_watts) #4MW demand, demand unit in watts, this value should be negative to represent a demand on the system

        # %% Calculation and document output
        #from TESPy Issue #281 and https://tespy.readthedocs.io/en/main/tespy_modules.html#automatic-model-documentation
        # fmt = {
        #     'latex_body': True,  # adds LaTeX body to compile report out of the box
        #     'include_results': True,  # include parameter specification and results
        #     'HeatExchanger': {  # for components of class HeatExchanger
        #         'params': ['Q', 'ttd_l', 'ttd_u', 'pr1', 'pr2']},  # change columns displayed
        #     'Condenser': {  # for components of class HeatExchanger
        #         'params': ['Q', 'ttd_l', 'ttd_u', 'pr1', 'pr2'],
        #         'float_fmt': '{:,.2f}'},  # change float format of data
        #     'Connection': {  # for Connection instances
        #         'p': {'float_fmt': '{:,.4f}'},  # change float format of pressure
        #         's': {'float_fmt': '{:,.4f}'},
        #         'h': {'float_fmt': '{:,.2f}'},
        #         'params': ['m', 'p', 'h', 's'],  # list results of mass flow, ...
        #         'fluid': {'include_results': False}  # exclude results of fluid composition
        #     },
        #     'include_results': True,  # include results
        #     'draft': False  # disable draft mode
        # }
        # path = { '*/report/'}

        nw.solve('design', max_iter=5)#network solve    
        # nw.print_results()
        
        nw.save('heat_pump_water')#added in max iterations because of the 30sec limit on Heroku app processing times. May result in errant eta_s solutions...
        # document_model(nw, filename='report_water_design.tex', fmt=fmt)#output network model to latex report
        # offdesign test
        nw.solve('offdesign', design_path='heat_pump_water', max_iter=5)#solve the offdesign values for the network (other projected outcomes)
        # document_model(nw, filename='report_water_offdesign.tex', fmt=fmt)#print these alternatives to a latex report
        # #the following comments are from fwitte
        T_range = [sim_parameters.wasted_heat_design_temperature-6, sim_parameters.wasted_heat_design_temperature-3, sim_parameters.wasted_heat_design_temperature, sim_parameters.wasted_heat_design_temperature+3, sim_parameters.wasted_heat_design_temperature+6][::-1]#inverted the temperature and heat provision ranges to always start near the design point specifications rather than further away.
        Q_range = np.array([np.round(sim_parameters.dh_heat_demand_in_watts*.60), np.round(sim_parameters.dh_heat_demand_in_watts*.80), np.round(sim_parameters.dh_heat_demand_in_watts), np.round(sim_parameters.dh_heat_demand_in_watts*1.2), np.round(sim_parameters.dh_heat_demand_in_watts*1.4)])[::-1]#Only after restarting from full load after modifying the temperature I read the initial values from the design specs, all other simulations start at the previous solution of the model which is always near the current case.
        # print(Q_range)
        # df2 = pd.DataFrame(columns=Q_range / -cons_1.Q.val)
        # print(df2)
        df = pd.DataFrame(columns=Q_range / -cons_1.Q.val)
        #In the full load and 35 °C waste heat temperature case, the outlet temperature of the water after the evaporator will be below the minimum temperature limit of the fluid property database, therefore no solution can be found.
        # parser = argparse.ArgumentParser()
        # parser.add_argument("report", type=Path)
        # p = parser.parse_args()

        # TeX source filename
        # tex_filename = '/report/report_water_design.tex'
        # filename, ext = os.path.splitext(tex_filename)
        # # the corresponding PDF filename
        # pdf_filename = filename + '.pdf'

        # # compile TeX file
        # subprocess.run(['pdflatex', '-interaction=nonstopmode', tex_filename])

        # # check if PDF is successfully generated
        # if not os.path.exists(pdf_filename):
        #     raise RuntimeError('PDF output not found')

        # # open PDF with platform-specific command
        # if platform.system().lower() == 'darwin':
        #     subprocess.run(['open', pdf_filename])
        # elif platform.system().lower() == 'windows':
        #     os.startfile(pdf_filename)
        # elif platform.system().lower() == 'linux':
        #     subprocess.run(['xdg-open', pdf_filename])
        # else:
        #     raise RuntimeError('Unknown operating system "{}"'.format(platform.system()))

        for T in T_range:
            rejected_heat_to_pump.set_attr(T=T)
            eps = []

            for Q in Q_range:
                cons_1.set_attr(Q=-Q)
                nw.solve('offdesign', design_path='heat_pump_water', max_iter=5)

                if nw.lin_dep:
                    eps += [np.nan]
                else:
                    eps += [
                        abs(condenser_1.Q.val) / (compressor1.P.val + erp1.P.val + pu.P.val)
                    ]

            df.loc[T] = eps
            # df2.loc[T] = eps
        result = df.to_json()
        # print(df)
        df.plot.line()
        plt.legend(['1.4 times design demand', '1.2 times design demand', '<<design load>>', '0.8 times design demand', '0.6 times design demand'])
        plt.title("Heat Pump for District Energy")
        plt.ylabel("Coefficient of Performance")
        plt.xlabel("Waste Heat Source Temperature (C)")
        plt.savefig("static/lines.png", format="png")
        # df.plot(x="Name", y="Age", kind="bar")
        # sns.lineplot()
        # csv_result = df.to_csv()
        # simulation = SimParameters.objects.create(id=id, )
        return Response(result)
        #make a function here, collect variables into it.

