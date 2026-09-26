from __future__ import annotations  # <-- Add this line at the absolute top

from Solver.EntityDataType import Coord
from Solver.map import Map

class State:
    def __init__(self, agent_position: Coord, box_positions: list[Coord]):
        self.agent_position: Coord = agent_position
        self.box_positions: frozenset[Coord] = frozenset(box_positions)

    def __eq__(self, other: State):
        return self.agent_position == other.agent_position and self.box_positions == other.box_positions

    def __hash__(self):
        return hash((self.agent_position, self.box_positions))