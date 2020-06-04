from xml.etree.ElementTree import ElementTree
from .rmevo_module import FactoryModule

from .. import SDF
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

    def parse_sdf_text(self, tag):
        value = tag.text

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
        if module.SDF_VISUAL is None:
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
        from .rmevo_module import BoxSlot, Orientation

        slots_tag = rmevo_tree.find('slots')
        if slots_tag is not None:
            module.SLOT_DATA = []
            module.children = []
            for child in slots_tag:
                new_slot = BoxSlot([[0, 0], [1, 0], [0, 0]], orientation=Orientation.SOUTH)
                new_slot.pos = SDF.math.Vector3(self.parse_sdf_text(child.find('pos')))
                new_slot.normal = SDF.math.Vector3(self.parse_sdf_text(child.find('norm')))
                new_slot.tangent = SDF.math.Vector3(self.parse_sdf_text(child.find('tan')))
                module.SLOT_DATA.append(new_slot)
                module.children.append(None)
        else:
            assert AttributeError("Tag free_slots not found in module %s, using default", module.TYPE)

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

class Alphabet(Enum):
    # MorphologyMountingCommands
    ADD_RIGHT = 'addr'
    ADD_FRONT = 'addf'
    ADD_LEFT = 'addl'

    # MorphologyMovingCommands
    MOVE_RIGHT = 'mover'
    MOVE_FRONT = 'movef'
    MOVE_LEFT = 'movel'
    MOVE_BACK = 'moveb'

    # ControllerChangingCommands
    ADD_EDGE = 'brainedge'
    MUTATE_EDGE = 'brainperturb'
    LOOP = 'brainloop'
    MUTATE_AMP = 'brainampperturb'
    MUTATE_PER = 'brainperperturb'
    MUTATE_OFF = 'brainoffperturb'

    # ControllerMovingCommands
    MOVE_REF_S = 'brainmoveFTS'
    MOVE_REF_O = 'brainmoveTTS'

    @staticmethod
    def modules(factory):
        modules = []
        for module in factory.modules_list:
            modules.append([module.TYPE, []])

        return modules

    @staticmethod
    def morphology_mounting_commands():
        return [
            [Alphabet.ADD_RIGHT, []],
            [Alphabet.ADD_FRONT, []],
            [Alphabet.ADD_LEFT, []]
        ]

    @staticmethod
    def morphology_moving_commands():
        return [
            [Alphabet.MOVE_RIGHT, []],
            [Alphabet.MOVE_FRONT, []],
            [Alphabet.MOVE_LEFT, []],
            [Alphabet.MOVE_BACK, []]
        ]
