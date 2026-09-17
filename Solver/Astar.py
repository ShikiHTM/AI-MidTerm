from SearchStrategy import SearchStrategy
from map import Map, State
import heapq
from collections import deque

class Astar(SearchStrategy):
    def __init__(self, m: Map):
        super().__init__()
        self.H = {} # Heuristic function
        self.H_cache = {}

        self.get_lookup_table(m)

    # Tbh, this is just a modified UCS by adding heuristic, iykyk :)
    def search(self, m: Map, initial_state: State):
        init_g = 0
        init_h = self.get_heuristic(initial_state, m)
        init_f = init_g + init_h
        best_g = {initial_state: 0}
        seq = 0 # This will prevent the crash if cost between state is the same

        pq = [(init_f, init_g, seq, initial_state, [])]
        visited = set()

        while pq:
            f, g, _, state, path = heapq.heappop(pq)

            if state.boxes_pos == m.goals:
                return g, path

            if state in visited:
                continue

            visited.add(state)

            for next_state, action, step_cost in self.get_successor(m, state):
                new_g = g + step_cost
                if next_state not in visited and new_g < best_g.get(next_state, float('inf')):
                    best_g[next_state] = new_g
                    new_h = self.get_heuristic(next_state, m)
                    new_f = new_g + new_h

                    new_path = path + [action]
                    seq += 1
                    heapq.heappush(pq, (new_f, new_g, seq, next_state, new_path))

        return float('inf'), []

    # We're using BFS to preprocess a lookup table since the forbidden of Manhattan distance and Euclidean, then get the max value of H(n) since we will simplifier the problem with easier rules
    # BFS will answer "How many steps I needs to get any box in the map reach to the specific goal"
    # E.g: {(2, 3): {(3, 4): 4, ...}}
    def get_distance_by_goal(self, goal, m: Map):
        direction = [
            (0, 1), # Down
            (0, -1), # Up
            (-1, 0), # Left
            (1, 0) # Right
        ]

        queue = deque([goal])
        distances = {goal: 0}

        while queue:
            fx, fy = queue.popleft()
            curr_dist = distances[(fx, fy)]

            for dx, dy in direction:
                nx, ny = fx + dx, fy + dy

                # Not hitting the wall and haven't reached yet
                if (nx, ny) not in m.walls and (nx, ny) not in distances:
                    distances[(nx, ny)] = curr_dist + 1
                    queue.append((nx, ny))

        return distances

    def get_lookup_table(self, m: Map):
        for g in m.goals:
            self.H[g] = self.get_distance_by_goal(g, m)

    def get_heuristic(self, state: State, m: Map):
        if state.boxes_pos in self.H_cache:
            return self.H_cache[state.boxes_pos]

        total_h = 0
        for box in state.boxes_pos:
            min_dist = min(self.H[goal].get(box, float('inf')) for goal in self.H)
            total_h += min_dist
        self.H_cache[state.boxes_pos] = total_h
        return total_h