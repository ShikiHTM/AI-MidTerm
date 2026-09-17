import heapq
from SearchStrategy import SearchStrategy
from map import State, Map

class UCS(SearchStrategy):
    def search(self, m: Map, initial_state: State):
        init_priority = 0
        seq = 0

        pq = [(init_priority, 0, initial_state, [])] # priority, cost, state, path
        visited = set()

        while pq:
            priority, _, state, path = heapq.heappop(pq)

            if state.boxes_pos == m.goals:
                return priority, path

            if state in visited:
                continue

            visited.add(state)

            for next_state, action, step_cost in self.get_successor(m, state):
                if next_state not in visited:
                    new_path = path + [action]
                    new_cost = priority + step_cost
                    seq += 1
                    heapq.heappush(pq, (new_cost, seq, next_state, new_path))

        return int('inf'), []
