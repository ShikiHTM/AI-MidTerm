from Solver.EntityDataType import Coord
from Solver.map import Map

class State:
    def __init__(self, agent_position: Coord, box_positions: list[Coord]):
        self.agent_position: Coord = agent_position
        self.box_positions: frozenset[Coord] = frozenset(box_positions)

    def __eq__(self, other):
        return self.agent_position == other.agent_position and self.box_positions == other.box_positions

    def __hash__(self):
        return hash((self.agent_position, self.box_positions))