"""

"""
from typing import Dict

try:
    from rv import commands
except ImportError:
    from dummyrv import commands

from .properties import *
from .typehint import *
from .constants import *


__all__ = [
    'to_node',
    'create_node',
    'input_nodes',
    'output_nodes',
    'view_node',
    'source_groups',
    'nodes_of_type',
    'Node',

]


CACHED_NODES = dict()


def to_node(node_name: str):
    """

    Args:
        node_name:

    Returns:
        Node:
    """
    global CACHED_NODES

    if not commands.nodeExists(node_name):
        raise NameError('Node not found')

    if node_name in CACHED_NODES:
        return CACHED_NODES[node_name]

    node_type = commands.nodeType(node_name)
    try:
        node = eval(node_type)(node_name)
    except NameError:
        node = Node(node_name)

    CACHED_NODES[node_name] = node

    return node


def create_node(node_type, node_name=None):
    try:
        if not isinstance(node_type, type):
            node_type = eval(node_type)
    except NameError:
        raise NameError('Invalid node type:')

    node_name = commands.newNode(node_type.__name__, node_name)

    return to_node(node_name)





def _input_node_names(node_name, traverse_groups=False):
    return commands.nodeConnections(node_name, traverse_groups)[0]


def _output_node_names(node_name, traverse_groups=False):
    return commands.nodeConnections(node_name, traverse_groups)[1]


def input_nodes(node_name, traverse_groups=False):
    return [to_node(n) for n in _input_node_names(node_name, traverse_groups=traverse_groups)]


def output_nodes(node_name, traverse_groups=False):
    return [to_node(n) for n in _output_node_names(node_name, traverse_groups=traverse_groups)]


def connected_nodes(root_node, node_type=None, traverse_groups=False):
    ledger = list()

    def _connected_nodes(_root_node, _node_type, _traverse_groups, _ledger):
        if _node_type:
            if isinstance(_root_node, _node_type) and _root_node not in _ledger:
                _ledger.append(_root_node)
        else:
            if _root_node not in _ledger:
                _ledger.append(_root_node)

        for _node in _root_node.input_nodes(traverse_groups=traverse_groups):
            _connected_nodes(_node, _node_type, _traverse_groups, _ledger)

    for node in root_node.input_nodes(traverse_groups=traverse_groups):
        _connected_nodes(node, node_type, traverse_groups, ledger)

    return ledger


def view_node():
    return to_node(commands.viewNode())


def source_groups(context=SESSION):
    pass


def nodes_of_type(node_type, context=SESSION):
    if isinstance(node_type, Node):
        node_type = node_type.__class__.__name__
    elif issubclass(node_type, Node):
        node_type = node_type.__name__

    node_names = commands.nodesOfType(node_type)
    return [to_node(node_name) for node_name in node_names]


class Node(object):

    def __init__(self, name: str):
        self._name = str(name)
        self._type = self.__class__.__name__
        self._property_groups = dict()

    def __getattr__(self, item):
        if item not in self._property_groups:
            self._property_groups[item] = PropertyGroup(self, item)
        return self._property_groups[item]

    def property_groups(self):
        pass

    def properties(self):
        pass

    def node_name(self):
        pass

    def node_type(self):
        pass

    def properties_dict(self) -> Dict[str: PropertyValueArray]:
        pass

    def get_values(self, property_fullname: str) -> PropertyValueArray:
        pass

    def get_value(self, property_fullname: str, index: int = 0) -> PropertyValue:
        pass
    
    def set_values(self, property_fullname: str, *values: PropertyValueArray):
        pass

    def set_value(self, property_fullname: str, value: PropertyValue):
        pass

    def insert_value(self, property_fullname: str, index: int, value: PropertyValue):
        pass

    def insert_values(self, property_fullname: str, index: int, *values: PropertyValueArray):
        pass

    def input_nodes(self, traverse_groups=False):
        return input_nodes(self.node_name(), traverse_groups=traverse_groups)

    def output_nodes(self):
        pass

    def top_level_group(self):
        pass


class LUT(Node):
    pass


class Source(Node):

    def media_paths(self):
        pass


class RVSession(Node):
    pass


class RVFileSource(Source):
    pass


class RVImageSource(Source):
    pass


class RVCacheLUT(LUT):
    pass


class RVFormat(Node):
    pass


class RVChannelMap(Node):
    pass


class RVCache(Node):
    pass


class RVLinearize(Node):
    pass


class RVLensWarp(Node):
    pass


class RVPaint(Node):
    pass


class RVOverlay(Node):
    pass


class RVColor(Node):
    pass


class RVLookLUT(LUT):
    pass


class RVSourceStereo(Node):
    pass


class RVTransform2D(Node):
    pass


class RVRetime(Node):
    pass


class RVSequence(Node):
    pass


class RVStack(Node):
    pass


class RVSoundTrack(Node):
    pass


class RVDispTransform2D(Node):
    pass


class RVDisplayStereo(Node):
    pass


class RVDisplayColor(Node):
    pass


class RVCDL(Node):
    pass


class RVPrimaryConvert(Node):
    pass


class RVSwitch(Node):
    pass


# OCIO nodes
class OCIONode(Node):
    pass


class OCIOFile(OCIONode):
    pass


class OCIOLook(OCIONode):
    pass


class OCIODisplay(OCIONode):
    pass


# Group nodes
class Group(Node):

    def member_nodes(self):
        pass


class RVSourceGroup(Group):

    def source_node(self):
        pass

    def linearize_pipeline_group(self):
        pass

    def color_pipeline_group(self):
        pass

    def look_pipeline_group(self):
        pass


class RVSequenceGroup(Group):
    pass


class RVStackGroup(Group):
    pass


class RVLayoutGroup(Group):
    pass


class RVViewGroup(Group):

    def view_pipeline_group(self):
        pass


class RVDisplayGroup(Group):

    def display_pipeline_group(self):
        pass


class RVOutputGroup(Group):
    pass


class RVRetimeGroup(Group):
    pass


class RVFolderGroup(Group):
    pass


class RVSwitchGroup(Group):
    pass


# Pipeline Groups
class PipelineGroup(Group):

    def pipeline_nodes(self):
        pass

    def append_pipeline_node(self, node: Node):
        pass

    def insert_pipeline_node(self, node: Node, index: int = 0):
        pass

    def remove_pipeline_node(self, index: int = 0):
        pass

    def clear_pipeline_nodes(self):
        pass


class RVLinearizePipelineGroup(PipelineGroup):
    pass


class RVColorPipelineGroup(PipelineGroup):
    pass


class RVLookPipelineGroup(PipelineGroup):
    pass


class RVViewPipelineGroup(PipelineGroup):
    pass


class RVDisplayPipelineGroup(PipelineGroup):
    pass



