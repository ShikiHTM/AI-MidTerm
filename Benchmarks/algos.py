from Solver.map import Map
from Solver.state import State
from Solver.SearchStrategy import UCS, Astar
from Solver.benchmark import benchmark
from pathlib import Path

import tracemalloc

from matplotlib import pyplot as plt
import numpy as np


maps = []  # logs the maps in an array, could be of use later

static_map: Map
initial_state: State

A_perf = []  # stores the time and space performance of each run of A star on the 5 maps
UCS_perf = []

A_run = []  # perf benchmark of the A star run on current map
UCS_run = []

count = 0

maps_dir = Path(__file__).resolve().parent.parent / "maps"
map_files = sorted(
    (path for path in maps_dir.iterdir() if path.is_file()),
    key=lambda path: path.name,
)
for file in map_files:
    # if count == 3:
    #     break
    # count += 1

    with open(file, "r") as f:
        m = f.read()
        maps.append(m)

    static_map = Map(file)
    initial_state = State(static_map.agent_pos, static_map.boxes_pos)

    # A_run = benchmark(Astar, static_map, initial_state, display=False)
    # UCS_run = benchmark(UCS, static_map, initial_state, display=False)

    A_perf.append(benchmark(Astar, static_map, initial_state, display=False))
    UCS_perf.append(benchmark(UCS, static_map, initial_state, display=False))

    # print(f"{A_perf[-1]}\n{UCS_perf[-1]}\n")

node_ratio = 0
time_ratio = 0
mem_ratio = 0

for i in range(len(A_perf)):
    node_ratio += A_perf[i]['nodes'] / UCS_perf[i]['nodes']
    time_ratio += A_perf[i]['time'] / UCS_perf[i]['time']
    mem_ratio += A_perf[i]['p_mem'] / UCS_perf[i]['p_mem']

node_ratio /= len(A_perf)
time_ratio /= len(A_perf)
mem_ratio /= len(A_perf)

with open("perf_record.txt", "w") as f:
    f.write("Astar:\n\n")
    for i in range(len(A_perf)):
        f.write(
            f"Map {i + 1}:\n - Amount of nodes generated: {A_perf[i]["nodes"]}\n - Execution time: {A_perf[i]["time"]}\n - Ram used (MB): {A_perf[i]["p_mem"]/1000000.0}\n\n"
        )

    f.write("UCS:\n\n")
    for i in range(len(UCS_perf)):
        f.write(
            f"Map {i + 1}:\n - Amount of nodes generated: {UCS_perf[i]["nodes"]}\n - Execution time: {UCS_perf[i]["time"]}\n - Ram used (MB): {UCS_perf[i]["p_mem"]/1000000.0}\n\n"
        )

    f.write("--- Averages ---\n\n")
    f.write(
        f" - Average ratio of the number of nodes generated between Astar and UCS: {node_ratio}\n")
    f.write(
        f" - Average ratio of execution time between Astar and UCS: {time_ratio}\n")
    f.write(f" - Average ratio of memory between Astar and UCS: {mem_ratio}\n")

# plotting

plot_dir = Path(__file__).resolve().parent / "plots"
plot_dir.mkdir(parents=True, exist_ok=True)

map_names = [f"Map {i}" for i in range(1, len(A_perf) + 1)]

x = np.arange(len(map_names))
width = 0.35  # bar width

A_mem = [i['p_mem']/1000000.0 for i in A_perf]
UCS_mem = [i['p_mem']/1000000.0 for i in UCS_perf]

# plots memory used (most correlated to space complexity)

A_bar = plt.bar(x - width/2, A_mem, width, label='A*', color='#4f81bd')
UCS_bar = plt.bar(x + width/2, UCS_mem, width, label='UCS', color='#c0504d')

plt.bar_label(A_bar, padding=3, fontsize=9)
plt.bar_label(UCS_bar, padding=3, fontsize=9)

plt.xlabel('Maps')
plt.ylabel('Memory used (MB)')
plt.title('Comparison of memory used (space complexity)')

plt.xticks(x, map_names)
plt.yscale('log')
plt.legend()

plt.margins(y=0.3)
plt.tight_layout()
plt.savefig(plot_dir / "memory_usage.png")
plt.close()

# plots time

A_time = [i['time'] for i in A_perf]
UCS_time = [i['time'] for i in UCS_perf]

A_bar = plt.bar(x - width/2, A_time, width, label='A*', color='#4f81bd')
UCS_bar = plt.bar(x + width/2, UCS_time, width, label='UCS', color='#c0504d')

plt.bar_label(A_bar, padding=3, fontsize=9)
plt.bar_label(UCS_bar, padding=3, fontsize=9)

plt.xlabel('Maps')
plt.ylabel('Time')
plt.title('Comparison of execution time')

plt.xticks(x, map_names)
plt.yscale('log')
plt.legend()

plt.margins(y=0.3)
plt.tight_layout()
plt.savefig(plot_dir / "execution_time.png")
plt.close()

# plots nodes

A_nodes = [i['nodes'] for i in A_perf]
UCS_nodes = [i['nodes'] for i in UCS_perf]

A_bar = plt.bar(x - width/2, A_nodes, width, label='A*', color='#4f81bd')
UCS_bar = plt.bar(x + width/2, UCS_nodes, width, label='UCS', color='#c0504d')

plt.bar_label(A_bar, padding=3, fontsize=9)
plt.bar_label(UCS_bar, padding=3, fontsize=9)

plt.xlabel('Maps')
plt.ylabel('Nodes')
plt.title('Comparison of the number of nodes generated')

plt.xticks(x, map_names)
plt.yscale('log')
plt.legend()

plt.margins(y=0.3)
plt.tight_layout()
plt.savefig(plot_dir / "generated_nodes.png")
plt.close()
