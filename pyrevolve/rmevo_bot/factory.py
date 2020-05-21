from xml.etree.ElementTree import ElementTree
from .rmevo_module import FactoryModule
from enum import Enum

import copy

from pyrevolve.custom_logging.logger import logger

from ..SDF.geometry import Visual, Collision


class Box:
    size = [1, 1, 1]


class Cylinder:
    radius = 1
    length = 1


class Sphere:
    radius = 1


class Mesh:
    uri = None
    scale = [1, 1, 1]


class Geometry(Enum):
    Box = 1
    Cylinder = 2
    Sphere = 3
    Mesh = 4


class Factory:
    def __init__(self):
        self.modules_list = []

    def parse_sdf_attribute(self, tree, attribute):
        value = tree.get(attribute)

        if value is not None:
            value = value.split()
            value = [float(i) for i in value]

        return value

    def parse_inertia(self, module, inertia_tree):
        module.SDF_INERTIA = inertia_tree
        module.MASS = float(inertia_tree.find('mass').text)
        module.SDF_COLLISION.mass = module.MASS

    def parse_collision(self, module, collision_tree):
        module.SDF_COLLISION = Collision(collision_tree.get('name'), 0.0)
        module.SDF_COLLISION.copy_from_tree(collision_tree)


    def parse_visual(self, module, visual_tree):
        module.SDF_VISUAL = Visual(visual_tree.get('name'))
        module.SDF_VISUAL.copy_from_tree(visual_tree)

    def parse_link(self, module, link_tree):
        module.SDF = link_tree

        if link_tree.find('collision') is not None:
            self.parse_collision(module, link_tree.find('collision'))
        else:
            raise RuntimeError('Collision tag not found in link')

        if link_tree.find('inertial') is not None:
            self.parse_inertia(module, link_tree.find('inertial'))
        else:
            raise RuntimeError('Inertial tag not found in link')

        if link_tree.find('visual') is not None:
            self.parse_visual(module, link_tree.find('visual'))
        else:
            raise RuntimeError('Visual tag not found in link')

    def parse_rmevo(self, module, rmevo_tree):
        for child in rmevo_tree:
            if child.tag == 'slots':
                module.SLOT_COORDINATES[0] = self.parse_sdf_attribute(child, 'x')
                module.SLOT_COORDINATES[1] = self.parse_sdf_attribute(child, 'y')
                module.SLOT_COORDINATES[2] = self.parse_sdf_attribute(child, 'z')

    def parse_model(self, module, model_tree):
        module.TYPE = model_tree.attrib['name']
        for child in model_tree:
            if child.tag == 'link':
                self.parse_link(module, child)
            elif child.tag == 'rmevo':
                self.parse_rmevo(module, child)
            else:
                logger.error("Input file has wrong structure: error in link")

    def import_module_from_sdf(self, file):
        """
        Import module from SDF
        """

        new_module = FactoryModule()
        sdf_tree = ElementTree()
        sdf_tree.parse(file)
        root = sdf_tree.getroot()

        logger.info("Importing file.")

        if not root.tag == 'sdf':
            logger.error("Input file is not a valid sdf")
        else:
            version = root.attrib
            for child in root:
                if child.tag == 'model':
                    self.parse_model(new_module, child)
                else:
                    logger.error("Input file has wrong structure: error in model")

        self.modules_list.append(new_module)

    def import_modules_from_dir(self, dir_path):
        import os
        import fnmatch
        # List all files the given directory and select the .sdf
        for entry in os.listdir(dir_path):
            file_path = os.path.join(dir_path, entry)
            if os.path.isfile(file_path):
                if fnmatch.fnmatch(file_path, '*.sdf'):
                    self.import_module_from_sdf(file_path)

