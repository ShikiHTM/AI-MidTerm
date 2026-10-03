from dataclasses import dataclass
from Solver.state import State

@dataclass
class Successor:
    action: str
    cost: int
    state: State