import time
from Solver.EntityDataType import GoalState

def benchmark(strategy_class, map_obj, initial_state):
    # Khởi tạo thuật toán
    solver = strategy_class(map_obj, initial_state)
    
    # Đo thời gian bắt đầu
    start_time = time.perf_counter()
    
    # Chạy thuật toán (giả sử hàm search trả về (cost, path))
    result: GoalState = solver.search()
    
    # Đo thời gian kết thúc
    end_time = time.perf_counter()
    
    execution_time = end_time - start_time
    
    # In kết quả benchmark ra màn hình
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
        "cost": result.cost,
        "path": result.path,
        "time": execution_time
    }