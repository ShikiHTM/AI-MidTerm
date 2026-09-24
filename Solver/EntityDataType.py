from dataclasses import dataclass

@dataclass
class Coord():
    x: int
    y: int

    def __hash__(self):
        return hash((self.x, self.y))

@dataclass
class GoalState:
    cost: int
    path: list[str]