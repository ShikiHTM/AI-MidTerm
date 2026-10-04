from dataclasses import dataclass
from Solver.EntityDataType import Coord
from typing import NamedTuple

class EndGameState(NamedTuple):
    first_agent_score: int
    second_agent_score: int

@dataclass
class AgentProps:
    position: Coord
    action: str

@dataclass
class Step:
    at: int
    primary_agent: AgentProps
    secondary_agent: AgentProps
    box_positions: frozenset[Coord]