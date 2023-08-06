from typing import *


Node = NewType('Node', object)


PropertyValue = Union[int, float, str]
PropertyValueArray = Sequence[PropertyValue]