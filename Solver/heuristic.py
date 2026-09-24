from dataclasses import dataclass, field
from Solver.EntityDataType import Coord
from collections import deque

@dataclass
class HeuristicTable:
    table: dict[Coord, dict[Coord, int]] = field(default_factory=dict)

    def add_distance(self, goal: Coord, box: Coord, distance: int):
        if goal not in self.table:
            self.table[goal] = {}

        self.table[goal][box] = distance

    def get_distance(self, goal: Coord, box: Coord) -> int:
        return self.table.get(goal, {}).get(box, float('inf'))