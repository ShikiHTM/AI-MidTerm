from dataclasses import dataclass
from typing import NamedTuple

class Coord(NamedTuple):
    x: int
    y: int

class Agent(NamedTuple):
    position: Coord
    is_max: bool | None = None

@dataclass
class GoalState:
    cost: int
    path: list[str]