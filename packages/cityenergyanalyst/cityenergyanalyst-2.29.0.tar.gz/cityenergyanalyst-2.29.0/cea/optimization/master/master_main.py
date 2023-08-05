from __future__ import division

import copy
import json
import multiprocessing
import random
import warnings
from itertools import repeat, izip
from math import factorial

import numpy as np
import pandas as pd
from deap import algorithms
from deap import tools, creator, base
from math import sqrt

from cea.optimization.constants import DH_CONVERSION_TECHNOLOGIES_SHARE, DC_CONVERSION_TECHNOLOGIES_SHARE, DH_ACRONYM, \
    DC_ACRONYM
from cea.optimization.master import evaluation
from cea.optimization.master.generation import generate_main
from cea.optimization.master.generation import individual_to_barcode
from cea.optimization.master.mutations import mutation_main
from cea.optimization.master.crossover import crossover_main
from cea.optimization.master.normalization import scaler_for_normalization, normalize_fitnesses

__author__ = "Sreepathi Bhargava Krishna"
__copyright__ = "Copyright 2015, Architecture and Building Systems - ETH Zurich"
__credits__ = ["Sreepathi Bhargava Krishna"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daren Thomas"
__email__ = "thomas@arch.ethz.ch"
__status__ = "Production"

warnings.filterwarnings("ignore")
NOBJ = 3  # number of objectives
creator.create("FitnessMin", base.Fitness, weights=(-1.0,) * NOBJ)
creator.create("Individual", list, typecode='d', fitness=creator.FitnessMin)


def objective_function(individual,
                       individual_number,
                       generation,
                       building_names_all,
                       column_names_buildings_heating,
                       column_names_buildings_cooling,
                       building_names_heating,
                       building_names_cooling,
                       building_names_electricity,
                       locator,
                       network_features,
                       config,
                       prices,
                       lca,
                       district_heating_network,
                       district_cooling_network,
                       column_names):
    """
    Objective function is used to calculate the costs, CO2, primary energy and the variables corresponding to the
    individual
    :param individual: Input individual
    :type individual: list
    :return: returns costs, CO2, primary energy and the master_to_slave_vars
    """
    print('cea optimization progress: individual ' + str(individual_number) + ' and generation ' + str(
        generation) + '/' + str(config.optimization.number_of_generations))
    costs_USD, CO2_ton, prim_MJ = evaluation.evaluation_main(individual,
                                                             building_names_all,
                                                             locator,
                                                             network_features,
                                                             config,
                                                             prices, lca,
                                                             individual_number,
                                                             generation,
                                                             column_names,
                                                             column_names_buildings_heating,
                                                             column_names_buildings_cooling,
                                                             building_names_heating,
                                                             building_names_cooling,
                                                             building_names_electricity,
                                                             district_heating_network,
                                                             district_cooling_network,
                                                             )
    return costs_USD, CO2_ton, prim_MJ


def objective_function_wrapper(args):
    """
    Wrap arguments because multiprocessing only accepts one argument for the function"""
    return objective_function(*args)


def calc_dictionary_of_all_individuals_tested(dictionary_individuals, gen, invalid_ind):
    dictionary_individuals['generation'].extend([gen] * len(invalid_ind))
    dictionary_individuals['individual_id'].extend(range(len(invalid_ind)))
    dictionary_individuals['individual_code'].extend(invalid_ind)
    return dictionary_individuals


def non_dominated_sorting_genetic_algorithm(locator,
                                            building_names_all,
                                            district_heating_network,
                                            district_cooling_network,
                                            building_names_heating,
                                            building_names_cooling,
                                            building_names_electricity,
                                            network_features,
                                            config,
                                            prices,
                                            lca):

    # LOCAL VARIABLES
    NGEN = config.optimization.number_of_generations  # number of generations
    MU = config.optimization.population_size  # int(H + (4 - H % 4)) # number of individuals to select
    RANDOM_SEED = config.optimization.random_seed
    CXPB = config.optimization.crossover_prob
    MUTPB = config.optimization.mutation_prob

    # SET-UP EVOLUTIONARY ALGORITHM
    # Hyperparameters
    NOBJ = 3  # number of objectives
    P = 12
    ref_points = tools.uniform_reference_points(NOBJ, P)
    if MU == None:
        H = factorial(NOBJ + P - 1) / (factorial(P) * factorial(NOBJ - 1))
        MU = int(H + (4 - H % 4))
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    # SET-UP INDIVIDUAL STRUCTURE INCLUIDING HOW EVERY POINT IS CALLED (COLUM_NAMES)
    column_names, \
    heating_unit_names_share, \
    cooling_unit_names_share, \
    column_names_buildings_heating, \
    column_names_buildings_cooling = get_column_names_individual(district_heating_network,
                                                                 district_cooling_network,
                                                                 building_names_heating,
                                                                 building_names_cooling,
                                                                 )
    individual_with_names_dict = create_empty_individual(column_names,
                                                         column_names_buildings_heating,
                                                         column_names_buildings_cooling,
                                                         district_heating_network,
                                                         district_cooling_network)

    # DEAP LIBRARY REFERENCE_POINT CLASSES AND TOOLS
    # reference points
    toolbox = base.Toolbox()
    toolbox.register("generate",
                     generate_main,
                     individual_with_names_dict=individual_with_names_dict,
                     column_names=column_names,
                     column_names_buildings_heating=column_names_buildings_heating,
                     column_names_buildings_cooling=column_names_buildings_cooling,
                     district_heating_network=district_heating_network,
                     district_cooling_network=district_cooling_network)
    toolbox.register("individual",
                     tools.initIterate,
                     creator.Individual,
                     toolbox.generate)
    toolbox.register("population",
                     tools.initRepeat,
                     list,
                     toolbox.individual)
    toolbox.register("mate",
                     crossover_main,
                     indpb=CXPB,
                     column_names=column_names,
                     heating_unit_names_share=heating_unit_names_share,
                     cooling_unit_names_share=cooling_unit_names_share,
                     column_names_buildings_heating=column_names_buildings_heating,
                     column_names_buildings_cooling=column_names_buildings_cooling,
                     district_heating_network=district_heating_network,
                     district_cooling_network=district_cooling_network)
    toolbox.register("mutate",
                     mutation_main,
                     indpb=MUTPB,
                     column_names=column_names,
                     heating_unit_names_share=heating_unit_names_share,
                     cooling_unit_names_share=cooling_unit_names_share,
                     column_names_buildings_heating=column_names_buildings_heating,
                     column_names_buildings_cooling=column_names_buildings_cooling,
                     district_heating_network=district_heating_network,
                     district_cooling_network=district_cooling_network)
    toolbox.register("evaluate",
                     objective_function_wrapper)
    toolbox.register("select",
                     tools.selNSGA3WithMemory(ref_points))

    # configure multiprocessing
    if config.multiprocessing:
        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        toolbox.register("map", pool.map)

    # Initialize statistics object
    paretofrontier = tools.ParetoFront()
    halloffame = tools.HallOfFame(MU)
    generational_distances = []
    difference_generational_distances = []
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean, axis=0)
    stats.register("std", np.std, axis=0)
    stats.register("min", np.min, axis=0)
    stats.register("max", np.max, axis=0)

    logbook = tools.Logbook()
    logbook.header = "gen", "evals", "std", "min", "avg", "max"

    pop = toolbox.population(n=MU)

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, izip(invalid_ind, range(len(invalid_ind)), repeat(0, len(invalid_ind)),
                                                   repeat(building_names_all, len(invalid_ind)),
                                                   repeat(column_names_buildings_heating, len(invalid_ind)),
                                                   repeat(column_names_buildings_cooling, len(invalid_ind)),
                                                   repeat(building_names_heating, len(invalid_ind)),
                                                   repeat(building_names_cooling, len(invalid_ind)),
                                                   repeat(building_names_electricity, len(invalid_ind)),
                                                   repeat(locator, len(invalid_ind)),
                                                   repeat(network_features, len(invalid_ind)),
                                                   repeat(config, len(invalid_ind)),
                                                   repeat(prices, len(invalid_ind)),
                                                   repeat(lca, len(invalid_ind)),
                                                   repeat(district_heating_network, len(invalid_ind)),
                                                   repeat(district_cooling_network, len(invalid_ind)),
                                                   repeat(column_names, len(invalid_ind))))

    # normalization of the first generation
    scaler_dict = scaler_for_normalization(NOBJ, fitnesses)
    fitnesses = normalize_fitnesses(scaler_dict, fitnesses)

    # add fitnesses to population individuals
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # Compile statistics about the population
    record = stats.compile(pop)
    paretofrontier.update(pop)
    halloffame.update(pop)
    performance_metrics = calc_performance_metrics(0.0, paretofrontier)
    generational_distances.append(performance_metrics[0])
    difference_generational_distances.append(performance_metrics[1])
    logbook.record(gen=0, evals=len(invalid_ind), **record)

    # create a dictionary to store which individuals that are being calculated
    record_individuals_tested = {'generation': [], "individual_id": [], "individual_code": []}
    record_individuals_tested = calc_dictionary_of_all_individuals_tested(record_individuals_tested, gen=0,
                                                                          invalid_ind=invalid_ind)
    print(logbook.stream)

    # Begin the generational process
    # Initialization of variables
    for gen in range(1, NGEN + 1):
        print ("Evaluating Generation %s of %s generations" % (gen, NGEN + 1))
        # Select and clone the next generation individuals
        offspring = algorithms.varAnd(pop, toolbox, CXPB, MUTPB)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        invalid_ind = [ind for ind in invalid_ind if ind not in pop]
        fitnesses = toolbox.map(toolbox.evaluate,
                                izip(invalid_ind, range(len(invalid_ind)), repeat(gen, len(invalid_ind)),
                                     repeat(building_names_all, len(invalid_ind)),
                                     repeat(column_names_buildings_heating, len(invalid_ind)),
                                     repeat(column_names_buildings_cooling, len(invalid_ind)),
                                     repeat(building_names_heating, len(invalid_ind)),
                                     repeat(building_names_cooling, len(invalid_ind)),
                                     repeat(building_names_electricity, len(invalid_ind)),
                                     repeat(locator, len(invalid_ind)),
                                     repeat(network_features, len(invalid_ind)),
                                     repeat(config, len(invalid_ind)),
                                     repeat(prices, len(invalid_ind)),
                                     repeat(lca, len(invalid_ind)),
                                     repeat(district_heating_network, len(invalid_ind)),
                                     repeat(district_cooling_network, len(invalid_ind)),
                                     repeat(column_names, len(invalid_ind))))
        # normalization of the second generation on
        fitnesses = normalize_fitnesses(scaler_dict, fitnesses)

        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Select the next generation population from parents and offspring
        pop = toolbox.select(pop + invalid_ind, MU)

        # get paretofront and update dictionary of individuals evaluated
        paretofrontier.update(pop)
        halloffame.update(pop)

        record_individuals_tested = calc_dictionary_of_all_individuals_tested(record_individuals_tested, gen=gen,
                                                                              invalid_ind=invalid_ind)

        # Compile statistics about the new population
        record = stats.compile(pop)
        performance_metrics = calc_performance_metrics(generational_distances[-1], paretofrontier)
        generational_distances.append(performance_metrics[0])
        difference_generational_distances.append(performance_metrics[1])
        logbook.record(gen=gen, evals=len(invalid_ind), **record)
        print(logbook.stream)

        DHN_network_list_tested = []
        DCN_network_list_tested = []
        for individual in invalid_ind:
            DHN_barcode, DCN_barcode, individual_with_name_dict, _ = individual_to_barcode(individual,
                                                                                           building_names_all,
                                                                                           building_names_heating,
                                                                                           building_names_cooling,
                                                                                           column_names,
                                                                                           column_names_buildings_heating,
                                                                                           column_names_buildings_cooling)
            DCN_network_list_tested.append(DCN_barcode)
            DHN_network_list_tested.append(DHN_barcode)

        print "Saving results for generation", gen, "\n"
        save_generation_dataframes(gen, invalid_ind, locator, DCN_network_list_tested, DHN_network_list_tested)
        save_generation_individuals(column_names, gen, invalid_ind, locator)
        save_generation_pareto_individuals(locator, gen, record_individuals_tested, paretofrontier)
        save_generation_halloffame_individuals(locator, gen, record_individuals_tested, halloffame)

        # Create Checkpoint if necessary
        print "Creating CheckPoint", gen, "\n"
        with open(locator.get_optimization_checkpoint(gen), "wb") as fp:
            cp = dict(generation = gen,
                      selected_population=pop,
                      tested_population=invalid_ind,
                      generational_distances=generational_distances,
                      difference_generational_distances = difference_generational_distances)
            json.dump(cp, fp)
    if config.multiprocessing:
        pool.close()

    return pop, logbook


def save_generation_pareto_individuals(locator, generation, record_individuals_tested, paretofrontier):
    performance_totals_pareto = pd.DataFrame()
    individual_list = []
    generation_list = []
    for i, record in enumerate(record_individuals_tested['individual_code']):
        if record in paretofrontier:
            ind = record_individuals_tested['individual_id'][i]
            gen = record_individuals_tested['generation'][i]
            individual_list.append(ind)
            generation_list.append(gen)
            performance_totals_pareto = pd.concat([performance_totals_pareto,
                                                   pd.read_csv(
                                                       locator.get_optimization_slave_total_performance(ind, gen))],
                                                  ignore_index=True)

    individual_name_list = ["Sys " + str(y) + "-" + str(x) for x, y in zip(individual_list, generation_list)]
    performance_totals_pareto['individual'] = individual_list
    performance_totals_pareto['individual_name'] = individual_name_list
    performance_totals_pareto['generation'] = generation_list
    performance_totals_pareto.to_csv(locator.get_optimization_generation_total_performance_pareto(generation))

def save_generation_halloffame_individuals(locator, generation, record_individuals_tested, hall_of_fame):
    performance_totals_halloffame = pd.DataFrame()
    individual_list = []
    generation_list = []
    for i, record in enumerate(record_individuals_tested['individual_code']):
        if record in hall_of_fame:
            ind = record_individuals_tested['individual_id'][i]
            gen = record_individuals_tested['generation'][i]
            individual_list.append(ind)
            generation_list.append(gen)
            performance_totals_halloffame = pd.concat([performance_totals_halloffame,
                                                   pd.read_csv(
                                                       locator.get_optimization_slave_total_performance(ind, gen))],
                                                  ignore_index=True)

    individual_name_list = ["Sys " + str(y) + "-" + str(x) for x, y in zip(individual_list, generation_list)]
    performance_totals_halloffame['individual'] = individual_list
    performance_totals_halloffame['individual_name'] = individual_name_list
    performance_totals_halloffame['generation'] = generation_list
    performance_totals_halloffame.to_csv(locator.get_optimization_generation_total_performance_halloffame(generation))

def save_generation_dataframes(generation,
                               slected_individuals,
                               locator,
                               DCN_network_list_selected,
                               DHN_network_list_selected):
    individual_list = range(len(slected_individuals))
    individual_name_list = ["Sys " + str(generation) + "-" + str(x) for x in individual_list]
    performance_disconnected = pd.DataFrame()
    performance_connected = pd.DataFrame()
    performance_totals = pd.DataFrame()
    for ind, DCN_barcode, DHN_barcode in zip(individual_list, DCN_network_list_selected, DHN_network_list_selected):
        performance_connected = pd.concat([performance_connected,
                                           pd.read_csv(
                                               locator.get_optimization_slave_connected_performance(ind, generation))],
                                          ignore_index=True)

        performance_disconnected = pd.concat([performance_disconnected, pd.read_csv(
            locator.get_optimization_slave_disconnected_performance(ind, generation))], ignore_index=True)
        performance_totals = pd.concat([performance_totals,
                                        pd.read_csv(
                                            locator.get_optimization_slave_total_performance(ind, generation))],
                                       ignore_index=True)

    performance_disconnected['individual'] = individual_list
    performance_connected['individual'] = individual_list
    performance_totals['individual'] = individual_list
    performance_disconnected['individual_name'] = individual_name_list
    performance_connected['individual_name'] = individual_name_list
    performance_totals['individual_name'] = individual_name_list
    performance_disconnected['generation'] = generation
    performance_connected['generation'] = generation
    performance_totals['generation'] = generation

    # save all results to disk
    performance_disconnected.to_csv(locator.get_optimization_generation_disconnected_performance(generation))
    performance_connected.to_csv(locator.get_optimization_generation_connected_performance(generation))
    performance_totals.to_csv(locator.get_optimization_generation_total_performance(generation))


def save_generation_individuals(columns_of_saved_files, generation, invalid_ind, locator):
    # now get information about individuals and save to disk
    individual_list = range(len(invalid_ind))
    individuals_info = pd.DataFrame()
    for ind in invalid_ind:
        infividual_dict = pd.DataFrame(dict(zip(columns_of_saved_files, [[x] for x in ind])))
        individuals_info = pd.concat([infividual_dict, individuals_info], ignore_index=True)

    individuals_info['individual'] = individual_list
    individuals_info['generation'] = generation
    individuals_info.to_csv(locator.get_optimization_individuals_in_generation(generation))


def convergence_metric(old_front, new_front, normalization):
    #  This function calculates the metrics corresponding to a Pareto-front
    #  combined_euclidean_distance calculates the euclidean distance between the current front and the previous one
    #  it is done by locating the choosing a point on current front and the closest point in the previous front and
    #  calculating normalized euclidean distance

    #  Spread discusses on the spread of the Pareto-front, i.e. how evenly the Pareto front is spaced. This is calculated
    #  by identifying the closest neighbour to a point on the Pareto-front. Distance to each closest neighbour is then
    #  subtracted by the mean distance for all the points on the Pareto-front (i.e. closest neighbors for all points).
    #  The ideal value for this is to be 'zero'

    combined_euclidean_distance = 0

    for indNew in new_front:

        (aNew, bNew, cNew) = indNew.fitness.values
        distance = []
        for i, indOld in enumerate(old_front):
            (aOld, bOld, cOld) = indOld.fitness.values
            distance_mix = ((aNew - aOld) / normalization[0]) ** 2 + ((bNew - bOld) / normalization[1]) ** 2 + (
                    (cNew - cOld) / normalization[2]) ** 2
            distance_mix = round(distance_mix, 5)
            distance.append(np.sqrt(distance_mix))

        combined_euclidean_distance = combined_euclidean_distance + min(distance)

    combined_euclidean_distance = (combined_euclidean_distance) / (len(new_front))

    spread = []
    nearest_neighbor = []

    for i, ind_i in enumerate(new_front):
        spread_i = []
        (cost_i, co2_i, eprim_i) = ind_i.fitness.values
        for j, ind_j in enumerate(new_front):
            (cost_j, co2_j, eprim_j) = ind_j.fitness.values
            if i != j:
                spread_mix = ((cost_i - cost_j) / normalization[0]) ** 2 + ((co2_i - co2_j) / normalization[1]) ** 2 + (
                        (eprim_i - eprim_j) / normalization[2]) ** 2
                spread_mix = round(spread_mix, 5)
                spread.append(np.sqrt(spread_mix))
                spread_i.append(np.sqrt(spread_mix))

        nearest_neighbor.append(min(spread_i))
    average_spread = np.mean(spread)

    nearest_neighbor = [abs(x - average_spread) for x in nearest_neighbor]

    spread_final = np.sum(nearest_neighbor)

    print ('combined euclidean distance = ' + str(combined_euclidean_distance))
    print ('spread = ' + str(spread_final))

    return combined_euclidean_distance, spread_final


def create_empty_individual(column_names, column_names_buildings_heating, column_names_buildings_cooling,
                            district_heating_network, district_cooling_network):
    # local variables
    heating_unit_names_share = [x[0] for x in DH_CONVERSION_TECHNOLOGIES_SHARE]
    cooling_unit_names_share = [x[0] for x in DC_CONVERSION_TECHNOLOGIES_SHARE]

    heating_unit_share_float = [0.0] * len(heating_unit_names_share)
    cooling_unit_share_float = [0.0] * len(cooling_unit_names_share)

    DH_buildings_connected_int = [0] * len(column_names_buildings_heating)
    DC_buildings_connected_int = [0] * len(column_names_buildings_cooling)

    # 3 cases are possible
    if district_heating_network and district_cooling_network:
        # combine both strings and calculate the ranges of each part of the individual
        individual = heating_unit_share_float + \
                     DH_buildings_connected_int + \
                     cooling_unit_share_float + \
                     DC_buildings_connected_int

    elif district_heating_network:
        individual = heating_unit_share_float + \
                     DH_buildings_connected_int

    elif district_cooling_network:
        individual = cooling_unit_share_float + \
                     DC_buildings_connected_int

    individual_with_names_dict = dict(zip(column_names, individual))

    return individual_with_names_dict


def get_column_names_individual(district_heating_network,
                                district_cooling_network,
                                building_names_heating,
                                building_names_cooling,
                                ):
    # 3 cases are possible
    if district_heating_network and district_cooling_network:
        # local variables
        heating_unit_names_share = [x for x, y in DH_CONVERSION_TECHNOLOGIES_SHARE.iteritems()]
        cooling_unit_names_share = [x for x, y in DC_CONVERSION_TECHNOLOGIES_SHARE.iteritems()]
        column_names_buildings_heating = [x + "_" + DH_ACRONYM for x in building_names_heating]
        column_names_buildings_cooling = [x + "_" + DC_ACRONYM for x in building_names_cooling]
        # combine both strings and calculate the ranges of each part of the individual
        column_names = heating_unit_names_share + \
                       column_names_buildings_heating + \
                       cooling_unit_names_share + \
                       column_names_buildings_cooling

    elif district_heating_network:
        # local variables
        heating_unit_names_share = [x for x, y in DH_CONVERSION_TECHNOLOGIES_SHARE.iteritems()]
        column_names_buildings_heating = [x + "_" + DH_ACRONYM for x in building_names_heating]
        cooling_unit_names_share = []
        column_names_buildings_cooling = []
        column_names = heating_unit_names_share + \
                       column_names_buildings_heating
    elif district_cooling_network:
        # local variables
        cooling_unit_names_share = [x for x, y in DC_CONVERSION_TECHNOLOGIES_SHARE.iteritems()]
        column_names_buildings_cooling = [x + "_" + DC_ACRONYM for x in building_names_cooling]
        heating_unit_names_share = []
        column_names_buildings_heating = []
        column_names = cooling_unit_names_share + \
                       column_names_buildings_cooling

    return column_names, \
           heating_unit_names_share, \
           cooling_unit_names_share, \
           column_names_buildings_heating, \
           column_names_buildings_cooling

def calc_euclidean_distance(x2, y2, z2):
    x1, y1, z1 = 0.0, 0.0, 0.0
    euclidean_distance = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
    return euclidean_distance

def calc_gd(n, X2, Y2, Z2):
    gd = 1 / n * sqrt(sum([calc_euclidean_distance(x2, y2, z2) for x2, y2, z2 in zip(X2, Y2, Z2)]))
    return gd

def calc_performance_metrics(generational_distance_n_minus_1, paretofrontier):
    number_of_individuals = len([paretofrontier])
    X2 = [paretofrontier[x].fitness.values[0] for x in range(number_of_individuals)]
    Y2 = [paretofrontier[x].fitness.values[1] for x in range(number_of_individuals)]
    Z2 = [paretofrontier[x].fitness.values[2] for x in range(number_of_individuals)]

    generational_distance = calc_gd(number_of_individuals, X2, Y2, Z2)
    difference_generational_distance = abs(generational_distance_n_minus_1-generational_distance)

    return generational_distance, difference_generational_distance,

if __name__ == "__main__":
    x = 'no_testing_todo'
