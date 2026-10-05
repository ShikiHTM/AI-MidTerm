import time
import tracemalloc
from Solver.EntityDataType import GoalState

def benchmark(strategy_class, map_obj, initial_state, display=True):
    solver = strategy_class(map_obj, initial_state)
    
    tracemalloc.start() # checks for ram usage for space complexity
    start_time = time.perf_counter()
    
    result: GoalState = solver.search()
    
    end_time = time.perf_counter()

    current_mem, peak_mem = tracemalloc.get_traced_memory() 
    tracemalloc.stop() # ends mem tracing
    
    execution_time = end_time - start_time
    
    if display:
        print("=" * 40)
        print(f"BENCHMARK RESULT FOR: {strategy_class.__name__}")
        print("=" * 40)
        print(f"Status        : {'Success (Found)' if result.cost != -1 else 'Failed (No Path)'}")
        print(f"Path Cost     : {result.cost}")
        print(f"Path Length   : {len(result.path) if result.path else 0} actions")
        print(f"Node Created: {solver.nodes} nodes")
        print(f"Execution Time: {execution_time:.6f} seconds")
        print("=" * 40)
    
    return {
        "nodes": solver.nodes,
        "cost": result.cost,
        "path": result.path,
        "time": execution_time,
        "p_mem": peak_mem
    }