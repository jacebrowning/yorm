"""Custom YAML representers."""

from collections import OrderedDict

import yaml


class LiteralString(str):
    """Custom type for strings which should be dumped in the literal style."""


def represent_literalstring(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data,
                                   style='|' if data else '')


def represent_ordereddict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode('tag:yaml.org,2002:map', value)


yaml.add_representer(OrderedDict, represent_ordereddict)
yaml.add_representer(LiteralString, represent_literalstring)
