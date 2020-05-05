#!/usr/bin/env python3
import asyncio
import os
import sys
from pyrevolve.util.supervisor.supervisor_multi import DynamicSimSupervisor
from pyrevolve import parser

here = os.path.dirname(os.path.abspath(__file__))
rvpath = os.path.abspath(os.path.join(here, '..', 'revolve'))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pyrevolve.gazebo.manage import WorldManager as World
from pyrevolve.sdfbuilder import Model, Link, SDF
from pyrevolve.sdfbuilder.math import Vector3


async def run():
	# Start Simulator
    settings = parser.parse_args()
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

    world = await World.create()
    if world:
        print("Connected to the simulator world.")
    
    model = Model(
            name='sdf_model',
            static=True,
    )
    model.set_position(position=Vector3(0, 0, 1))
    link = Link('sdf_link')
    link.make_sphere(
            mass=10e10,
            radius=0.5,
    )
    link.make_color(0.7, 0.2, 0.0, 1.0)
    
    model.add_element(link)
    sdf_model = SDF(elements=[model])
    
    await world.insert_model(sdf_model)
    await world.pause(True)
    
    while True:
        await asyncio.sleep(10.0)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())


if __name__ == "__main__":
    main()
