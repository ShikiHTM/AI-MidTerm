import argparse
import os
import sys
from Solver.map import Map
from Solver.state import State
from Solver.SearchStrategy import UCS, Astar
from Solver.benchmark import benchmark

parser = argparse.ArgumentParser(
    description="Benchmark Sokoban search strategies.")
default_map = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), "input.txt")
parser.add_argument("input_file", nargs="?", default=default_map,
                    help="path to the Sokoban map file")
args = parser.parse_args()

static_map = Map(args.input_file)
print(static_map)
initial_state = State(static_map.agent_pos, static_map.boxes_pos)

benchmark(Astar, static_map, initial_state)
benchmark(UCS, static_map, initial_state)
