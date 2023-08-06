

from .typehint import *


try:
    from rv import rvtypes, commands
except ImportError:
    from dummyrv import rvtypes, commands


__all__ = [
    'PropertyGroup',
    'Property',
]


PROPERTY_MAPPING = {
    str: {
        'get': commands.getStringProperty,
        'set': commands.setStringProperty,
        'insert': commands.insertStringProperty,
    },
    int: {
        'get': commands.getIntProperty,
        'set': commands.setIntProperty,
        'insert': commands.insertIntProperty,
    },
    float: {
        'get': commands.getFloatProperty,
        'set': commands.setFloatProperty,
        'insert': commands.insertFloatProperty,
    },
}


class PropertyGroup(object):
    def __init__(self, parent_node, group_name):
        self._parent_node = parent_node
        self._name = group_name

    def __getattr__(self, property_name):
        return Property(self._parent_node, self._group_name, property_name)

    @property
    def full_name(self):
        return '.'.join([self._parent_node.full_name(), self._name])


class Property(object):
    def __init__(self, parent_node, property_group, property_name):
        self._parent_node = parent_node
        self._property_group = property_group
        self._name = property_name

    @property
    def full_name(self) -> str:
        return '.'.join([self._property_group.full_name(), self._name])

    def set_value(self, value):
        pass

    def set_values(self, *values: PropertyValueArray):
        pass

    def value(self, index=0) -> PropertyValue:
        """

        Args:
            index:

        Returns:
            PropertyValue:
        """
        pass

    def values(self) -> PropertyValueArray:
        """

        Returns:
            PropertyValueArray:
        """
        return

    def insert_value(self, index, value):
        pass

    def insert_values(self, index, *values):
        pass

    def append_value(self, value):
        pass

    def append_values(self, *values):
        pass



