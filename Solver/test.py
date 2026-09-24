from Solver.map import Map
from Solver.state import State
from Solver.SearchStrategy import UCS, Astar
from Solver.benchmark import benchmark

static_map = Map("Solver/input.txt")
print(static_map)
initial_state = State(static_map.agent_pos, static_map.boxes_pos)

benchmark(Astar, static_map, initial_state)
benchmark(UCS, static_map, initial_state)