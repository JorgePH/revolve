from xml.etree.ElementTree import ElementTree
from .rmevo_module import RMEvoModule
from enum import Enum


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

    def parse_inertia(self, module, inertia_tree):
        None

    def parse_collision(self, module, inertia_tree):
        None

    def parse_visual(self, module, visual_tree):
        None
        #for child in visual_tree:
        #    if child.tag == 'geometry':

    def parse_link(self, module, link_tree):
        module.SDF = link_tree
        for child in link_tree:
            if child.tag == 'inertial':
                self.parse_inertia(module, child)
            elif child.tag == 'collision':
                self.parse_collision(module, child)
            elif child.tag == 'visual':
                self.parse_visual(module, child)

    def parse_model(self, module, model_tree):
        module.TYPE = model_tree.attrib
        for child in model_tree:
            if child.tag == 'link':
                self.parse_link(module, child)
            else:
                print('Input file has wrong structure: error in link')

    def import_module_from_sdf(self, file):
        """
        Import module from SDF
        """

        new_module = RMEvoModule()
        sdf_tree = ElementTree()
        sdf_tree.parse(file)
        root = sdf_tree.getroot()

        if not root.tag == 'sdf':
            print('Input file is not a valid sdf')
        else:
            version = root.attrib
            for child in root:
                if child.tag == 'model':
                    self.parse_model(new_module, child)
                else:
                    print('Input file has wrong structure: error in model')

        self.modules_list.append(new_module)
