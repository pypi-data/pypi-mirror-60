from dataclasses import dataclass
from typing import List, TypeVar, Generic


@dataclass
class Entity:
    pass


T = TypeVar("T")


@dataclass
class PaginatedResult(Generic[T]):
    results: List[T]
    next: str
