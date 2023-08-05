"""
Evaluation function of an individual

"""
from __future__ import division

import numpy as np
import pandas as pd

import cea.inputlocator
from cea.constants import HOURS_IN_YEAR
from cea.optimization.master import cost_model
from cea.optimization.master import master_to_slave as master
from cea.optimization.master.generation import individual_to_barcode
from cea.optimization.master.performance_aggregation import summarize_results_individual
from cea.optimization.slave import cooling_main
from cea.optimization.slave import electricity_main
from cea.optimization.slave import heating_main


# +++++++++++++++++++++++++++++++++++++
# Main objective function evaluation
# ++++++++++++++++++++++++++++++++++++++

def evaluation_main(individual, building_names_all, locator, network_features, config, prices, lca,
                    ind_num, gen, column_names_individual,
                    column_names_buildings_heating,
                    column_names_buildings_cooling,
                    building_names_heating,
                    building_names_cooling,
                    building_names_electricity,
                    district_heating_network,
                    district_cooling_network,
                    ):
    """
    This function evaluates an individual

    :param individual: list with values of the individual
    :param column_names_buildings_all: list with names of buildings
    :param cea.inputlocator.InputLocator locator: locator class
    :param solar_features: solar features call to class
    :param network_features: network features call to class
    :param optimization_constants: class containing constants used in optimization
    :param config: configuration file
    :param prices: class of prices used in optimization
    :type individual: list
    :type column_names_buildings_all: list
    :type solar_features: class
    :type network_features: class
    :type optimization_constants: class
    :type config: class
    :type prices: class
    :return: Resulting values of the objective function. costs, CO2, prim
    :rtype: tuple

    """

    # CREATE THE INDIVIDUAL BARCODE AND INDIVIDUAL WITH HER COLUMN NAME AS A DICT
    DHN_barcode, DCN_barcode, individual_with_name_dict, building_connectivity_dict = individual_to_barcode(individual,
                                                                                                            building_names_all,
                                                                                                            building_names_heating,
                                                                                                            building_names_cooling,
                                                                                                            column_names_individual,
                                                                                                            column_names_buildings_heating,
                                                                                                            column_names_buildings_cooling)

    print("EVALUATING THE NEXT SYSTEM OPTION/INDIVIDUAL")
    print(individual_with_name_dict)

    # CREATE CLASS AND PASS KEY CHARACTERISTICS OF INDIVIDUAL
    # THIS CLASS SHOULD CONTAIN ALL VARIABLES THAT MAKE AN INDIVIDUAL CONFIGURATION
    master_to_slave_vars = master.export_data_to_master_to_slave_class(locator,
                                                                       gen,
                                                                       ind_num,
                                                                       individual_with_name_dict,
                                                                       building_names_all,
                                                                       building_names_heating,
                                                                       building_names_cooling,
                                                                       building_names_electricity,
                                                                       DHN_barcode,
                                                                       DCN_barcode,
                                                                       district_heating_network,
                                                                       district_cooling_network)
    # INITIALIZE DICTS STORING PERFORMANCE DATA
    district_heating_fixed_costs = {}
    district_heating_generation_dispatch = {}
    district_cooling_fixed_costs = {}
    district_cooling_generation_dispatch = {}
    district_heating_capacity_installed = {}
    district_cooling_capacity_installed = {}
    # DISTRICT HEATING NETWORK
    if master_to_slave_vars.DHN_exists:
        print("DISTRICT HEATING OPERATION")
        district_heating_fixed_costs, \
        district_heating_generation_dispatch, \
        district_heating_electricity_requirements_dispatch, \
        district_heating_fuel_requirements_dispatch, \
        district_heating_capacity_installed = heating_main.district_heating_network(locator,
                                                                                    master_to_slave_vars,
                                                                                    config,
                                                                                    prices,
                                                                                    lca,
                                                                                    network_features,
                                                                                    )
    else:
        district_heating_electricity_requirements_dispatch = {
            # ENERGY REQUIREMENTS
            # Electricity
            "E_Storage_charging_req_W": np.zeros(HOURS_IN_YEAR),
            "E_Storage_discharging_req_W": np.zeros(HOURS_IN_YEAR),
            "E_DHN_req_W": np.zeros(HOURS_IN_YEAR),
            "E_HP_SC_FP_req_W": np.zeros(HOURS_IN_YEAR),
            "E_HP_SC_ET_req_W": np.zeros(HOURS_IN_YEAR),
            "E_HP_PVT_req_W": np.zeros(HOURS_IN_YEAR),
            "E_HP_Server_req_W": np.zeros(HOURS_IN_YEAR),
            "E_HP_Sew_req_W": np.zeros(HOURS_IN_YEAR),
            "E_HP_Lake_req_W": np.zeros(HOURS_IN_YEAR),
            "E_GHP_req_W": np.zeros(HOURS_IN_YEAR),
            "E_BaseBoiler_req_W": np.zeros(HOURS_IN_YEAR),
            "E_PeakBoiler_req_W": np.zeros(HOURS_IN_YEAR),
            "E_BackupBoiler_req_W": np.zeros(HOURS_IN_YEAR),
        }
        district_heating_fuel_requirements_dispatch = {
            "NG_CHP_req_W": np.zeros(HOURS_IN_YEAR),
            "NG_BaseBoiler_req_W": np.zeros(HOURS_IN_YEAR),
            "NG_PeakBoiler_req_W": np.zeros(HOURS_IN_YEAR),
            "NG_BackupBoiler_req_W": np.zeros(HOURS_IN_YEAR),
            "WB_Furnace_req_W": np.zeros(HOURS_IN_YEAR),
            "DB_Furnace_req_W": np.zeros(HOURS_IN_YEAR),
        }

    # DISTRICT COOLING NETWORK:
    if master_to_slave_vars.DCN_exists:
        print("DISTRICT COOLING OPERATION")
        district_cooling_fixed_costs, \
        district_cooling_generation_dispatch, \
        district_cooling_electricity_requirements_dispatch, \
        district_cooling_fuel_requirements_dispatch, \
        district_cooling_capacity_installed = cooling_main.district_cooling_network(locator,
                                                                                    master_to_slave_vars,
                                                                                    config,
                                                                                    prices,
                                                                                    network_features)
    else:
        district_cooling_electricity_requirements_dispatch = {
            # ENERGY REQUIREMENTS
            # Electricity
            "E_DCN_req_W": np.zeros(HOURS_IN_YEAR),
            "E_BaseVCC_WS_req_W": np.zeros(HOURS_IN_YEAR),
            "E_PeakVCC_WS_req_W": np.zeros(HOURS_IN_YEAR),
            "E_BaseVCC_AS_req_W": np.zeros(HOURS_IN_YEAR),
            "E_PeakVCC_AS_req_W": np.zeros(HOURS_IN_YEAR),
            "E_BackupVCC_AS_req_W": np.zeros(HOURS_IN_YEAR),
        }
        district_cooling_fuel_requirements_dispatch = {
            "NG_Trigen_req_W": np.zeros(HOURS_IN_YEAR)
        }

    # ELECTRICITY CONSUMPTION CALCULATIONS
    print("DISTRICT ELECTRICITY GRID OPERATION")
    district_electricity_fixed_costs, \
    district_electricity_dispatch, \
    district_electricity_demands, \
    district_electricity_capacity_installed = electricity_main.electricity_calculations_of_all_buildings(locator,
                                                                                                         master_to_slave_vars,
                                                                                                         district_heating_generation_dispatch,
                                                                                                         district_heating_electricity_requirements_dispatch,
                                                                                                         district_cooling_generation_dispatch,
                                                                                                         district_cooling_electricity_requirements_dispatch)

    # print("DISTRICT NATURAL GAS / BIOMASS GRID OPERATION")
    # electricity_main.extract_fuels_demand_buildings(master_to_slave_vars, building_names_all, locator)

    print("DISTRICT ENERGY SYSTEM - COSTS, PRIMARY ENERGY AND EMISSIONS OF CONNECTED BUILDINGS")
    buildings_connected_costs, \
    buildings_connected_emissions = cost_model.buildings_connected_costs_and_emissions(district_heating_fixed_costs,
                                                                                       district_cooling_fixed_costs,
                                                                                       district_electricity_fixed_costs,
                                                                                       district_electricity_dispatch,
                                                                                       district_heating_fuel_requirements_dispatch,
                                                                                       district_cooling_fuel_requirements_dispatch,
                                                                                       district_electricity_demands,
                                                                                       prices,
                                                                                       lca)

    print("DISTRICT ENERGY SYSTEM - COSTS, PRIMARY ENERGY AND EMISSIONS OF DISCONNECTED BUILDINGS")
    buildings_disconnected_costs, \
    buildings_disconnected_emissions, \
    buildings_disconnected_heating_capacities, \
    buildings_disconnected_cooling_capacities = cost_model.buildings_disconnected_costs_and_emissions(
        building_names_heating,
        building_names_cooling,
        locator,
        master_to_slave_vars)

    print("AGGREGATING RESULTS")
    TAC_sys_USD, GHG_sys_tonCO2, PEN_sys_MJoil, performance_totals = summarize_results_individual(master_to_slave_vars,
                                                                                                  buildings_connected_costs,
                                                                                                  buildings_connected_emissions,
                                                                                                  buildings_disconnected_costs,
                                                                                                  buildings_disconnected_emissions)

    print("SAVING RESULTS TO DISK")
    save_results(master_to_slave_vars,
                 locator,
                 buildings_connected_costs,
                 buildings_connected_emissions,
                 buildings_disconnected_costs,
                 buildings_disconnected_emissions,
                 district_heating_generation_dispatch,
                 district_cooling_generation_dispatch,
                 district_electricity_dispatch,
                 district_electricity_demands,
                 performance_totals,
                 building_connectivity_dict,
                 district_heating_capacity_installed,
                 district_cooling_capacity_installed,
                 district_electricity_capacity_installed,
                 buildings_disconnected_heating_capacities,
                 buildings_disconnected_cooling_capacities
                 )

    # Converting costs into float64 to avoid longer values
    print ('Total TAC in USD = ' + str(TAC_sys_USD))
    print ('Total GHG emissions in tonCO2-eq = ' + str(GHG_sys_tonCO2))
    print ('Total PEN non-renewable in MJoil ' + str(PEN_sys_MJoil) + "\n")

    return TAC_sys_USD, GHG_sys_tonCO2, PEN_sys_MJoil


def save_results(master_to_slave_vars,
                 locator,
                 buildings_connected_costs,
                 buildings_connected_emissions,
                 buildings_disconnected_costs,
                 buildings_disconnected_emissions,
                 heating_dispatch,
                 cooling_dispatch,
                 electricity_dispatch,
                 electricity_requirements,
                 performance_totals_dict,
                 building_connectivity_dict,
                 district_heating_capacity_installed_dict,
                 district_cooling_capacity_installed_dict,
                 district_electricity_capacity_installed_dict,
                 buildings_disconnected_heating_capacities,
                 buildings_disconnected_cooling_capacities
                 ):
    # local variables
    individual = master_to_slave_vars.individual_number
    generation = master_to_slave_vars.generation_number

    # SAVE INDIVIDUAL DISTRICT HEATING INSTALLED CAPACITIES
    pd.DataFrame(district_heating_capacity_installed_dict, index =[0]).to_csv(locator.get_optimization_connected_heating_capacity(individual,
                                                                                                                                  generation),
                                                                              index=False, float_format='%.3f')
    pd.DataFrame(district_cooling_capacity_installed_dict, index =[0]).to_csv(locator.get_optimization_connected_cooling_capacity(individual,
                                                                                                                                  generation),
                                                                              index=False, float_format='%.3f')
    pd.DataFrame(district_electricity_capacity_installed_dict, index =[0]).to_csv(locator.get_optimization_connected_electricity_capacity(individual,
                                                                                                                                          generation),
                                                                                  index=False, float_format='%.3f')

    buildings_disconnected_heating_capacities.to_csv(locator.get_optimization_disconnected_heating_capacity(individual,
                                                                                                        generation),
                                                     index=False, float_format='%.3f')

    buildings_disconnected_cooling_capacities.to_csv(locator.get_optimization_disconnected_cooling_capacity(individual,
                                                                                                        generation),
                                                     index=False, float_format='%.3f')

    # SAVE BUILDING CONNECTIVITY
    pd.DataFrame(building_connectivity_dict).to_csv(locator.get_optimization_slave_building_connectivity(individual,
                                                                                                         generation),
                                                    index=False, float_format='%.3f')

    # SAVE PERFORMANCE RELATED FILES
    # export all including performance heating and performance cooling since we changed them
    performance_disconnected_dict = dict(buildings_disconnected_costs, **buildings_disconnected_emissions)
    pd.DataFrame(performance_disconnected_dict, index =[0]).to_csv(locator.get_optimization_slave_disconnected_performance(individual,
                                                                                                          generation),
                                                  index=False, float_format='%.3f')

    performance_connected_dict = dict(buildings_connected_costs, **buildings_connected_emissions)
    pd.DataFrame(performance_connected_dict, index =[0]).to_csv(locator.get_optimization_slave_connected_performance(individual,
                                                                                                    generation),
                                               index=False, float_format='%.3f')

    pd.DataFrame(performance_totals_dict, index =[0]).to_csv(locator.get_optimization_slave_total_performance(individual,
                                                                                                              generation),
                                                             index=False, float_format='%.3f')

    # add date and plot
    DATE = master_to_slave_vars.date
    electricity_dispatch['DATE'] = DATE
    cooling_dispatch['DATE'] = DATE
    heating_dispatch['DATE'] = DATE
    electricity_requirements['DATE'] = DATE

    pd.DataFrame(electricity_requirements).to_csv(
        locator.get_optimization_slave_electricity_requirements_data(individual,
                                                                     generation), index=False, float_format='%.3f')

    pd.DataFrame(electricity_dispatch).to_csv(locator.get_optimization_slave_electricity_activation_pattern(individual,
                                                                                                            generation),
                                              index=False, float_format='%.3f')

    pd.DataFrame(cooling_dispatch).to_csv(locator.get_optimization_slave_cooling_activation_pattern(individual,
                                                                                                    generation),
                                          index=False, float_format='%.3f')

    pd.DataFrame(heating_dispatch).to_csv(locator.get_optimization_slave_heating_activation_pattern(individual,
                                                                                                    generation),
                                          index=False, float_format='%.3f')
