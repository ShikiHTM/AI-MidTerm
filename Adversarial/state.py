from Adversarial.EntityDataType import Coord, Agent
from Adversarial.map import Map

class State:
    def __init__(self, agent_positions: list[Agent], box_positions: list[Coord], is_max_turn=True):
        self.agents: list[Agent] = agent_positions
        self.box_positions: frozenset[Coord] = frozenset(box_positions)
        self.is_max_turn = is_max_turn

    def __eq__(self, other):
        return self.agents == other and self.box_positions == other.box_positions

    def __hash__(self):
        return hash((self.agents, self.box_positions, self.is_max_turn))

    def is_game_over(self, map: Map) -> bool:
        return self.box_positions == map.goals