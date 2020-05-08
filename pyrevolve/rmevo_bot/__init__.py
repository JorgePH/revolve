# Adds OrderedDict as possible yaml input
import yaml
from collections import OrderedDict

from .rmevo_bot import RMEvoBot
from .rmevo_module import RMEvoModule, BoxSlot
from .factory import Factory


def represent_ordereddict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)

yaml.add_representer(OrderedDict, represent_ordereddict)
