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

        """
        Q. What are you thinking? __is_dead_square have nothing to do in HeuristicUtility
        A. ikik, but I just want to reuse the BFS function so stfu
        """
        self.is_dead_square: list[list[bool]] = [
            [True] * map.width for _ in range(map.height)]
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

        while queue:
            curr_cell = queue.popleft()
            curr_dist = distance[curr_cell]
            if 0 <= curr_cell.y < len(self.is_dead_square) and 0 <= curr_cell.x < len(self.is_dead_square[0]):
                self.is_dead_square[curr_cell.y][curr_cell.x] = False

            for dx, dy in directions:
                next_cell = Coord(curr_cell.x + dx, curr_cell.y + dy)
                next_agent = Coord(next_cell.x + dx, next_cell.y + dy)

                if not (0 <= next_cell.x < self.static_map.width and 0 <= next_cell.y < self.static_map.height):
                    continue

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
        if box_positions in self.H_cached:
            return self.H_cached[box_positions]

        for box in box_positions:
            if self.is_dead_square[box.y][box.x]:
                self.H_cached[box_positions] = float('inf')
                return float('inf')

        total_h = 0
        for box in box_positions:
            min_dist = min((self.H.get_distance(goal, box) for goal in self.static_map.goals), default=float('inf'))
            total_h = total_h + min_dist

        self.H_cached[box_positions] = total_h
        return total_h
