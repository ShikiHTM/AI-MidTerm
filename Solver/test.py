from map import Map, State
from SearchStrategy import SearchStrategy

m = Map('input.txt')
m.print()

init_state = State(m.agent_pos, m.boxes_pos)

search = SearchStrategy()

successors = search.get_successor(m, init_state)

for i, (next_state, action, cost) in enumerate(successors):
    print(f"Action: {action}, cost: ${cost}")
    print(f"Agent Pos: {next_state.agent_pos}")
    print(f"Boxes Pos: {next_state.boxes_pos}")
    print()