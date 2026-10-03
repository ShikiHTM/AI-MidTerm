from dataclasses import dataclass, field
from Solver.EntityDataType import Coord
from collections import deque
from Solver.map import Map

@dataclass
class HeuristicTable:
    table: dict[Coord, dict[Coord, int]] = field(default_factory=dict)

    def add_distance(self, goal: Coord, box: Coord, distance: int):
        if goal not in self.table:
            self.table[goal] = {}

        self.table[goal][box] = distance

    def get_distance(self, goal: Coord, box: Coord) -> int:
        return self.table.get(goal, {}).get(box, float('inf'))

class HeuristicUtility:
    def __init__(self, map: Map):
        self.static_map = map
        self.H: HeuristicTable = HeuristicTable()
        self.H_cached = {}
        self.__build_heuristic_data()

    def __get_distance_by_goal(self, goal: Coord) -> dict:
        directions = [
            (-1, 0),
            (1, 0),
            (0, 1),
            (0, -1)
        ]

        queue = deque([goal])
        distance = {goal: 0}

        self.H.add_distance(goal, goal, 0)

        while queue:
            curr_cell = queue.popleft()
            curr_dist = distance[curr_cell]

            for dx, dy in directions:
                next_cell = Coord(curr_cell.x + dx, curr_cell.y + dy)
                next_agent = Coord(next_cell.x + dx, next_cell.y + dy)

                # hitting wall
                if (next_cell in self.static_map.walls or next_agent in self.static_map.walls):
                    continue

                # already has a distance
                if next_cell in distance:
                    continue

                distance[next_cell] = curr_dist + 1
                queue.append(next_cell)

        return distance

    def __build_heuristic_data(self):
        for goal in self.static_map.goals:
            distance = self.__get_distance_by_goal(goal)
            for box_pos, dist in distance.items():
                self.H.add_distance(goal, box_pos, dist)

    def get_heuristic(self, box_positions: frozenset[Coord]) -> float:
        """
        Compute the heuristic using the Hungarian Algorithm (O(n³)).
        Finds the minimum-cost perfect matching between boxes and goals,
        giving a tighter (but still admissible) lower bound than greedy min.
        """
        if box_positions in self.H_cached:
            return self.H_cached[box_positions]

        boxes = list(box_positions)
        goals = list(self.static_map.goals)
        n = len(boxes)

        if n == 0:
            self.H_cached[box_positions] = 0
            return 0

        INF = float('inf')

        # Build cost matrix: cost[i][j] = distance from boxes[i] to goals[j]
        # 1-indexed for the algorithm, so cost[0][*] is unused
        cost = [[0] * (n + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                cost[i][j] = self.H.get_distance(goals[j - 1], boxes[i - 1])
                if cost[i][j] == INF:
                    # Box can't reach this goal — use a large finite value
                    cost[i][j] = 10**9

        # Hungarian Algorithm (O(n³) from cp-algorithms)
        # u[i] = potential for row i, v[j] = potential for column j
        # p[j] = row assigned to column j (0 = unassigned)
        u = [0] * (n + 1)
        v = [0] * (n + 1)
        p = [0] * (n + 1)
        way = [0] * (n + 1)

        for i in range(1, n + 1):
            p[0] = i
            j0 = 0
            minv = [INF] * (n + 1)
            used = [False] * (n + 1)

            while True:
                used[j0] = True
                i0 = p[j0]
                delta = INF
                j1 = -1

                for j in range(1, n + 1):
                    if not used[j]:
                        cur = cost[i0][j] - u[i0] - v[j]
                        if cur < minv[j]:
                            minv[j] = cur
                            way[j] = j0
                        if minv[j] < delta:
                            delta = minv[j]
                            j1 = j

                for j in range(n + 1):
                    if used[j]:
                        u[p[j]] += delta
                        v[j] -= delta
                    else:
                        minv[j] -= delta

                j0 = j1

                if p[j0] == 0:
                    break

            # Unroll augmenting path
            while j0:
                j1 = way[j0]
                p[j0] = p[j1]
                j0 = j1

        # The optimal cost is -v[0]
        total_h = -v[0]

        self.H_cached[box_positions] = total_h
        return total_h