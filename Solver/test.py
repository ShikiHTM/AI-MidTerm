from map import Map, State
from UCS import UCS

m = Map('./Solver/input.txt')
m.print()

init_state = State(m.agent_pos, m.boxes_pos)

strategy = UCS()
result = strategy.search(m, init_state)

print(result)
print("Node created: %d"%strategy.nodes)