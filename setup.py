#!/usr/bin/env python
from distutils.core import setup

setup(name='revolve',
      version=0.1,
      description='Revolve: robot evolution framework',
      author='Elte Hupkes',
      author_email='elte@hupkes.org',
      url='https://github.com/ElteHupkes/revolve',
      packages=['revolve', 'revolve.analyze', 'revolve.build', 'revolve.build.sdf',
                'revolve.convert', 'revolve.generate', 'revolve.spec', 'revolve.angle'],
      install_requires=['PyYAML', 'pygazebo', 'protobuf', 'sdfbuilder']
      )
