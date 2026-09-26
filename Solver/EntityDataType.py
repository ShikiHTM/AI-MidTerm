from dataclasses import dataclass
from typing import NamedTuple

class Coord(NamedTuple):
    x: int
    y: int

@dataclass
class GoalState:
    cost: int
    path: list[str]