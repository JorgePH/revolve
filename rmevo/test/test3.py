#!/usr/bin/env python3

"""
This file is a test that tries to implement the evolution api over a factory of imported modules
"""


import asyncio

from pyrevolve import parser
from pyrevolve.evolution import fitness
from pyrevolve.evolution.selection import multiple_selection, tournament_selection
from pyrevolve.evolution.population import Population, PopulationConfig
from pyrevolve.evolution.pop_management.steady_state import steady_state_population_management
from pyrevolve.experiment_management import ExperimentManagement
from pyrevolve.genotype.plasticoding.crossover.crossover import CrossoverConfig
from pyrevolve.genotype.plasticoding.crossover import rmevo_crossovers
from pyrevolve.genotype.plasticoding.initialization import random_initialization
from pyrevolve.genotype.plasticoding.initialization import rmevo_random_initialization
from pyrevolve.genotype.plasticoding.mutation.mutation import MutationConfig
from pyrevolve.genotype.plasticoding.mutation.rmevo_mutations import standard_mutation
from pyrevolve.genotype.plasticoding.plasticoding import PlasticodingConfig
from pyrevolve.util.supervisor.analyzer_queue import AnalyzerQueue
from pyrevolve.util.supervisor.simulator_queue import SimulatorQueue
from pyrevolve.custom_logging.logger import logger
from pyrevolve import rmevo_bot


async def run():
    """
    The main coroutine, which is started below.
    """

    # Load modules from files
    logger.info("Starting Factory.")
    factory = rmevo_bot.Factory()
    logger.info("Importing module.")
    module_file_dir = 'rmevo/test/modules/basic'
    factory.import_modules_from_dir(module_file_dir)

    # experiment params #
    num_generations = 1
    population_size = 30
    offspring_size = 1

    genotype_conf = PlasticodingConfig(
        max_structural_modules=5,
        factory=factory,
        axiom_w='Body',
    )

    mutation_conf = MutationConfig(
        mutation_prob=1,
        genotype_conf=genotype_conf,
    )

    crossover_conf = CrossoverConfig(
        crossover_prob=0,
    )
    # experiment params #

    # Parse command line / file input arguments
    settings = parser.parse_args()
    settings.recovery_enabled = False
    settings.evaluation_time = 1

    experiment_management = ExperimentManagement(settings)
    do_recovery = settings.recovery_enabled and not experiment_management.experiment_is_new()

    logger.info('Activated run '+settings.run+' of experiment '+settings.experiment_name)

    if do_recovery:
        gen_num, has_offspring, next_robot_id = experiment_management.read_recovery_state(population_size, offspring_size)

        if gen_num == num_generations-1:
            logger.info('Experiment is already complete.')
            return
    else:
        gen_num = 0
        next_robot_id = 1

    population_conf = PopulationConfig(
        population_size=population_size,
        genotype_constructor=rmevo_random_initialization,
        #genotype_constructor=random_initialization,
        genotype_conf=genotype_conf,
        fitness_function=fitness.maximum_weight,
        mutation_operator=standard_mutation,
        mutation_conf=mutation_conf,
        #crossover_operator=rmevo_crossovers.standard_crossover,
        crossover_operator=None,
        crossover_conf=crossover_conf,
        selection=lambda individuals: tournament_selection(individuals, 2),
        parent_selection=lambda individuals: multiple_selection(individuals, 2, tournament_selection),
        population_management=steady_state_population_management,
        population_management_selector=tournament_selection,
        evaluation_time=settings.evaluation_time,
        offspring_size=offspring_size,
        experiment_name=settings.experiment_name,
        experiment_management=experiment_management,
    )

    n_cores = settings.n_cores

    settings.output_directory = 'file'
    settings.simulator_cmd = 'gazebo'
    settings.world = 'worlds/plane.realtime.world'
    simulator_queue = SimulatorQueue(n_cores, settings, settings.port_start)
    await simulator_queue.start()

    analyzer_queue = AnalyzerQueue(1, settings, settings.port_start+n_cores)
    await analyzer_queue.start()

    population = Population(population_conf, simulator_queue, analyzer_queue, next_robot_id)

    if do_recovery:
        # loading a previous state of the experiment
        await population.load_snapshot(gen_num)
        if gen_num >= 0:
            logger.info('Recovered snapshot '+str(gen_num)+', pop with ' + str(len(population.individuals))+' individuals')
        if has_offspring:
            individuals = await population.load_offspring(gen_num, population_size, offspring_size, next_robot_id)
            gen_num += 1
            logger.info('Recovered unfinished offspring '+str(gen_num))

            if gen_num == 0:
                await population.init_pop(individuals)
            else:
                population = await population.next_gen(gen_num, individuals)

            experiment_management.export_snapshots(population.individuals, gen_num)
    else:
        # starting a new experiment
        experiment_management.create_exp_folders()
        await population.init_pop()
        experiment_management.export_snapshots(population.individuals, gen_num)

    while gen_num < num_generations-1:
        gen_num += 1
        population = await population.next_gen(gen_num)
        experiment_management.export_snapshots(population.individuals, gen_num)

    # output result after completing all generations...
