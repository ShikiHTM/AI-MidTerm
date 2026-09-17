import heapq
from SearchStrategy import SearchStrategy
from map import State, Map

class UCS(SearchStrategy):
    def search(self, m: Map, initial_state: State):
        init_priority = 0
        pq = [(init_priority, 0, initial_state, [])] # priority, cost, state, path

        visited = set()

        while pq:
            priority, cost, state, path = heapq.heappop(pq)

            if state.boxes_pos == m.goals:
                return cost, path

            if state in visited:
                continue

            visited.add(state)
