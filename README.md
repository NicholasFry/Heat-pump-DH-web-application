# PDX Code Guild Capstone Proposal

## Title: Low-carbon District Heating Assessments
Uses TESPy to run simulations of heat pump driven district heating from a web application. 


## Project Overview
There is a need to rapidly assess the feasibility of various waste heat sources (geothermal, steel making, data centers, etc.) for their direct application in industrial, commercial, and residential heat networks. Heat networks have the potential to decarbonize up to 40% of primary energy consumption in North America. One application in these heat networks are centralized heat pumps. 
A useful web-application may be one interfacing with the Thermal Engineering Systems Python (TESPy) library, where a programmer can put together various configurations of heat pumps and energy networks. Simplifying the network design and isolating the energy efficiency from various waste heat sources is the goal of this project. 
TESPy runs simulations that can take up to 25 seconds each. The off-design values specified by a user will each incur a new simulation run. Since the duration of each round of simulations varies with inputs there is likely a need to develop a Vue-Django interface that can idle while awaiting results. 
## Features
This project will model a simple ammonia (NH3), single-stage heat pump coupled to a water (H20) district heating network. In the web application the user should be able to state the design demand load of the district heating network in Watts, various temperatures in Celsius for the supply and return pipelines, and the inlet and outlet temperatures from a waste heat source. 
A user knowing the exit temperature of their waste heat source should be able to easily enter parameters for temperature and design demand loads to assess the system efficiency of a heat pump without having any programming skills. This will enable data center operators, power plant operators, and oil & gas field operators to quickly understand the economic and energetic potential of their otherwise wasted heat.
## Data Model
There will be a model – HeatPump – for the heat pump and district heating network simulation. There will also be a model – Results – for the results from the simulation.
- 27August – Complete with presentation	
- 21August – Continue refinements
- 20August – Minimum Viable Product
- 16August – Refine the user interface
- 13August – Develop the user interface
- 12August – Develop the simulation

## Minimum Viable Product milestones
* Essential – Static text print out of simulation report to user.
* Really great to have – Static visualization charts of simulation in plotly, matplotlib, seaborn, etc. 
* Nice-to-have – Compiled report in pdf form and dashboard of simulation charts. Least likely because of .tex compiler variations on the backend.
