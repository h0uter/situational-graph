from dataclasses import dataclass
import sys
from uuid import uuid4


size_of_int = sys.getsizeof(5)


@dataclass
class IntClass:
    id: int


@dataclass
class UUIDClass:
    id: uuid4


size_of_int_dataclass = sys.getsizeof(IntClass(id=5))

size_of_uuid = sys.getsizeof(uuid4())
size_of_uuid_dataclass = sys.getsizeof(UUIDClass(id=uuid4()))

print(f"size of int: {size_of_int}")
print(f"size of dataclass: {size_of_int_dataclass}")
print(f"size of uuid: {size_of_uuid}")
print(f"size of uuid class: {size_of_uuid_dataclass}")


size_of_int_edge = sys.getsizeof((5, 6, 1))
size_of_uuid_edge = sys.getsizeof((uuid4(), uuid4(), uuid4()))

print(f"size of int edge: {size_of_int_edge}")
print(f"size of uuid edge: {size_of_uuid_edge}")