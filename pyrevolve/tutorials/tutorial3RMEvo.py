#!/usr/bin/env python3
"""
This script loads a robot.yaml file and inserts it into the simulator.
"""

import os
import sys
import asyncio
from pyrevolve.SDF.math import Vector3
from pyrevolve import rmevo_bot, parser
from pyrevolve.tol.manage import World
from pyrevolve.util.supervisor.supervisor_multi import DynamicSimSupervisor
from pyrevolve.evolution import fitness

from pyrevolve.custom_logging.logger import logger


async def run():
    """
    The main coroutine, which is started below.
    """
    #robot_file_path = "rmevo/test/basic.yaml"
    robot_file_path = "rmevo/test/twomodules.yaml"
    #robot_file_path = "experiments/examples/yaml/spider.yaml"
    module_file_path = 'rmevo/test/module.sdf'
    sdf_file_path = 'rmevo/test/robot.sdf'

    # Parse command line / file input arguments
    settings = parser.parse_args()

    # Start Simulator
    if settings.simulator_cmd != 'debug':
        simulator_supervisor = DynamicSimSupervisor(
            world_file=settings.world,
            simulator_cmd=settings.simulator_cmd,
            simulator_args=["--verbose"],
            plugins_dir_path=os.path.join('.', 'build', 'lib'),
            models_dir_path=os.path.join('.', 'models'),
            simulator_name='gazebo'
        )
        await simulator_supervisor.launch_simulator(port=settings.port_start)
        await asyncio.sleep(0.1)

    # Load modules from files
    logger.info("Starting Factory.")
    factory = rmevo_bot.Factory()
    logger.info("Importing module.")
    factory.import_module_from_sdf(module_file_path)

    # Load a robot from yaml
    robot = rmevo_bot.RMEvoBot(self_factory=factory)
    logger.info("Loading Robot.")
    robot.load_file(robot_file_path)
    robot.update_substrate()

    # Print robot to sdf file
    logger.info("Parsing robot to model.")
    sdf_model = robot.to_sdf()
    robot_sdf_file = open(sdf_file_path, 'w')
    robot_sdf_file.write(sdf_model)
    robot_sdf_file.close()

    # robot._brain = BrainRLPowerSplines()

    # Connect to the simulator and pause
    connection = await World.create(settings, world_address=('127.0.0.1', settings.port_start))
    await asyncio.sleep(1)

    # Starts the simulation
    await connection.pause(False)

    # Insert the robot in the simulator
    # robot_manager = await connection.insert_robot(robot, Vector3(0, 0, settings.z_start))

    # Start a run loop to do some stuff
    while True:
        # Print robot fitness every second
        #status = 'dead' if robot_manager.dead else 'alive'
        #print(f"Robot fitness ({status}) is: {fitness.displacement(robot_manager, robot)} \n")
        await asyncio.sleep(1.0)
