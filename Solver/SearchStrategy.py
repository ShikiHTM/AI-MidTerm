from Solver.map import Map
from Solver.EntityDataType import Coord, GoalState
from Solver.successor_type import Successor
from Solver.state import State
from Solver.heuristic import HeuristicTable
from collections import deque
import heapq

class SearchStrategy:
    def __init__(self, static_map: Map, initial_state: State):
        self.nodes = 0
        self.static_map = static_map
        self.initial_state = initial_state

    def search(self) -> GoalState:
        return GoalState(cost=-1, path=[])

    def __is_in_corner(self, box_pos: Coord):
        if box_pos in self.static_map.goals:
            return False

        up = Coord(box_pos.x, box_pos.y-1) in self.static_map.walls
        down = Coord(box_pos.x, box_pos.y+1) in self.static_map.walls
        left = Coord(box_pos.x-1, box_pos.y) in self.static_map.walls
        right = Coord(box_pos.x+1, box_pos.y) in self.static_map.walls
        return (up or down) and (left or right)

    def get_successor(self, current_state: State) -> list[Successor]:
        """
        Generate a list of successors from current state.

        Args:
            current_state (State): Information of the state

        Returns:
            List[Successor]: A list of valid moves. Each Successor object packaged a new State, Moved and Cost
        """
        successors: list[Successor] = []

        directions = {
            "North": (0, -1),
            "South": (0, 1),
            "West": (-1, 0),
            "East": (1, 0)
        }

        for action, (dx, dy) in directions.items():
            # P'
            next_agent_pos: Coord = Coord(current_state.agent_position.x + dx, current_state.agent_position.y + dy)

            # If P' is a wall, do nothing
            if next_agent_pos in self.static_map.walls:
                continue

            # If P' is a Box
            if next_agent_pos in current_state.box_positions:
                # P''
                next_box_pos: Coord = Coord(next_agent_pos.x + dx, next_agent_pos.y + dy)

                # If P'' is a wall, do nothing
                if next_box_pos in self.static_map.walls:
                    continue

                # If P'' is a box, do nothing
                if next_box_pos in current_state.box_positions:
                    continue

                if self.__is_in_corner(next_box_pos):
                    continue

                # Remove old specific box and add new position
                new_box_pos = set(current_state.box_positions)
                new_box_pos.remove(next_agent_pos)
                new_box_pos.add(next_box_pos)
            else:
                new_box_pos = current_state.box_positions

            next_state: State = State(next_agent_pos, frozenset(new_box_pos))
            successors.append(Successor(action=action, cost=1, state=next_state))

        return successors

class UCS(SearchStrategy):
    def __init__(self, static_map: Map, initial_state: State):
        super().__init__(static_map, initial_state)

    def search(self) -> GoalState:
        seq = 0 # Since all moves cost 1 Cost Unit. Hence, we need another variable for heapq to not crash out

        pq = [(0, seq, self.initial_state, [])]
        visited = set()

        while pq:
            curr_cost, _, curr_state, curr_path = heapq.heappop(pq)

            if curr_state.box_positions == self.static_map.goals:
                return GoalState(curr_cost, curr_path)

            if curr_state in visited:
                continue

            visited.add(curr_state)

            for successor in self.get_successor(curr_state):
                next_state = successor.state

                if next_state not in visited:
                    seq += 1
                    new_cost = curr_cost + successor.cost
                    new_path = curr_path + [successor.action]
                    self.nodes += 1
                    heapq.heappush(pq, (new_cost, seq, next_state, new_path))

        return GoalState(cost=-1, path=[])

class Astar(SearchStrategy):
    def __init__(self, static_map: Map, initial_state: State):
        super().__init__(static_map, initial_state)
        self.H: HeuristicTable = HeuristicTable()
        self.H_cached = {}
        self.__build_heuristic_data()

    def search(self) -> GoalState:
        init_f = self.__get_heuristic(self.initial_state.box_positions)
        init_g = 0
        seq = 0

        visited = set()

        pq = [(init_f, seq, init_g, self.initial_state, [])]
        best_g = {self.initial_state: 0}

        while pq:
            f, _, g, state, path = heapq.heappop(pq)

            if state in visited:
                continue

            visited.add(state)

            if state.box_positions == self.static_map.goals:
                return GoalState(g, path)

            for successor in self.get_successor(state):
                next_state = successor.state
                new_g = successor.cost + g

                if next_state not in visited and new_g < best_g.get(next_state, float('inf')):
                    new_h = self.__get_heuristic(next_state.box_positions)
                    new_f = new_g + new_h
                    seq += 1
                    new_path = path + [successor.action]
                    best_g[next_state] = new_g
                    self.nodes += 1
                    heapq.heappush(pq, (new_f, seq, new_g, next_state, new_path))

        return GoalState(cost=-1, path=[])

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

                # hitting wall
                if next_cell in self.static_map.walls:
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

    def __get_heuristic(self, box_positions: frozenset[Coord]) -> float:
        if box_positions in self.H_cached:
            return self.H_cached[box_positions]

        total_h = 0
        for box in box_positions:
            min_dist = min((self.H.get_distance(goal, box) for goal in self.static_map.goals), default=float('inf'))
            total_h = total_h + min_dist

        self.H_cached[box_positions] = total_h
        return total_h
