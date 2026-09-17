import heapq
from SearchStrategy import SearchStrategy
from map import State, Map

class UCS(SearchStrategy):
    def __init__(self, m: Map):
        super().__init__()

    def search(self, m: Map, initial_state: State):
        init_g = 0
        seq = 0 # This will prevent the crash if cost between state is the same

        pq = [(init_g, seq, initial_state, [])]
        visited = set()

        while pq:
            g, _, state, path = heapq.heappop(pq)

            if state.boxes_pos == m.goals:
                return g, path

            if state in visited:
                continue

            visited.add(state)

            for next_state, action, step_cost in self.get_successor(m, state):
                if next_state not in visited:
                    new_path = path + [action]
                    new_g = g + step_cost
                    seq +=  1
                    heapq.heappush(pq, (new_g, seq, next_state, new_path))

        return int('inf'), []
