from typing import Union
from uuid import UUID
# Node = Union[str, int]
Node = UUID
# Edge = tuple[Union[str, int], Union[str, int]]
# Edge = tuple[Union[str, int], Union[str, int], int]
Edge = tuple[UUID, UUID, UUID]
