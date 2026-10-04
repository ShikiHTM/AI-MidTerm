from Solver.map import Map
from Solver.state import State
from Solver.SearchStrategy import UCS, Astar
from Solver.benchmark import benchmark
from pathlib import Path
import numpy as np
import pandas as pd

maps = []

static_map: Map
initial_state: State

A_perf = [] # stores the time and space performance of each run of A star on the 5 maps
UCS_perf = [] 

A_run = [] # perf benchmark of the A star run on current map
UCS_run = []

count = 0

dir = Path("./maps")
for file in dir.iterdir():    
    # if count == 3:
    #     break
    # count += 1

    with open(file, "r") as f:
        m = f.read()
        maps.append(m)

    static_map = Map(file)
    initial_state = State(static_map.agent_pos, static_map.boxes_pos)

    A_run = benchmark(Astar, static_map, initial_state, display=False)
    UCS_run = benchmark(UCS, static_map, initial_state, display=False)

    A_perf.append(benchmark(Astar, static_map, initial_state, display=False))
    UCS_perf.append(benchmark(UCS, static_map, initial_state, display=False))

    # print(f"{A_perf[-1]}\n{UCS_perf[-1]}\n")

with open("perf_record.txt", "w") as f:
    f.write("Astar:\n\n")
    for i in range(len(A_perf)):
        f.write(
            f"Map {i}:\n - Amount of nodes generated: {A_perf[i]["nodes"]}\n - Execution time: {A_perf[i]["time"]}\n\n"
            )

    f.write("UCS:\n\n")
    for i in range(len(UCS_perf)):
        f.write(
            f"Map {i}:\n - Amount of nodes generated: {UCS_perf[i]["nodes"]}\n - Execution time: {UCS_perf[i]["time"]}\n\n"
            )
