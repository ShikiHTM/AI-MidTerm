from Solver.map import Map
from Solver.EntityDataType import Coord, GoalState
from Solver.successor_type import Successor
from Solver.state import State
from Solver.heuristic_table import HeuristicUtility
from collections import deque
import heapq
import math
from utils import log_execution_time


class SearchStrategy:
    # @log_execution_time
    def __init__(self, static_map: Map, initial_state: State):
        self.nodes = 0
        self.static_map = static_map
        self.initial_state = initial_state
        self.H: HeuristicUtility = HeuristicUtility(static_map)

    @log_execution_time
    def search(self) -> GoalState:
        return GoalState(cost=-1, path=[])

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
            next_agent_pos: Coord = Coord(
                current_state.agent_position.x + dx, current_state.agent_position.y + dy)

            # If P' is a wall, do nothing
            if next_agent_pos in self.static_map.walls:
                continue

            # If P' is a Box
            if next_agent_pos in current_state.box_positions:
                # P''
                next_box_pos: Coord = Coord(
                    next_agent_pos.x + dx, next_agent_pos.y + dy)

                # If P'' is a wall, do nothing
                if next_box_pos in self.static_map.walls:
                    continue

                # If P'' is a box, do nothing
                if next_box_pos in current_state.box_positions:
                    continue

                if self.H.is_dead_square[next_box_pos.y][next_box_pos.x]:
                    continue

                # Remove old specific box and add new position
                new_box_pos = set(current_state.box_positions)
                new_box_pos.remove(next_agent_pos)
                new_box_pos.add(next_box_pos)
            else:
                new_box_pos = current_state.box_positions

            next_state: State = State(next_agent_pos, frozenset(new_box_pos))
            successors.append(
                Successor(action=action, cost=1, state=next_state))

        return successors

    def _depth_limited_search(self, depth_limit: int) -> GoalState:
        if self.initial_state.box_positions == self.static_map.goals:
            return GoalState(cost=0, path=[])

        frontier = deque([(self.initial_state, 0)])
        discovered_depth = {self.initial_state: 0}
        parent = {self.initial_state: (None, None)}

        while frontier:
            state, depth = frontier.pop()
            if depth != discovered_depth[state]:
                continue

            for successor in self.get_successor(state):
                next_state = successor.state
                next_depth = depth + 1
                previous_depth = discovered_depth.get(next_state)
                if previous_depth is not None and previous_depth <= next_depth:
                    continue

                discovered_depth[next_state] = next_depth
                parent[next_state] = (state, successor.action)
                self.nodes += 1

                if next_state.box_positions == self.static_map.goals:
                    path = []
                    curr, action = next_state, successor.action

                    while curr is not None:
                        path.append(action)
                        curr, action = parent[curr]

                    path.reverse()

                    return GoalState(cost=len(path), path=path)

                if next_depth < depth_limit:
                    frontier.append((next_state, next_depth))

        return GoalState(cost=-1, path=[])


class BFS(SearchStrategy):
    def search(self) -> GoalState:
        if self.initial_state.box_positions == self.static_map.goals:
            return GoalState(cost=0, path=[])

        frontier = deque([self.initial_state])
        discovered = []

        parent = {self.initial_state: (None, None)}

        while frontier:
            state = frontier.popleft()
            discovered.append(state)

            for successor in self.get_successor(state):
                next_state = successor.state

                if next_state in discovered or next_state in frontier:
                    continue

                parent[next_state] = (state, successor.action)

                if next_state.box_positions == self.static_map.goals:
                    path = []
                    curr, action = next_state, successor.action

                    while curr is not None:
                        path.append(action)
                        curr, action = parent[curr]

                    path.reverse()

                    return GoalState(cost=len(path), path=path)

                self.nodes += 1
                frontier.append(next_state)

        return GoalState(cost=-1, path=[])


class DFS(SearchStrategy):
    def search(self) -> GoalState:
        if self.initial_state.box_positions == self.static_map.goals:
            return GoalState(cost=0, path=[])

        frontier = deque([self.initial_state])
        discovered = []

        parent = {self.initial_state: (None, None)}

        while frontier:
            state = frontier.pop()
            discovered.append(state)

            for successor in self.get_successor(state):
                next_state = successor.state

                if next_state in discovered or next_state in frontier:
                    continue

                parent[next_state] = (state, successor.action)

                if next_state.box_positions == self.static_map.goals:
                    path = []
                    curr, action = next_state, successor.action

                    while curr is not None:
                        path.append(action)
                        curr, action = parent[curr]

                    path.reverse()

                    return GoalState(cost=len(path), path=path)

                self.nodes += 1
                frontier.append(next_state)

        return GoalState(cost=-1, path=[])


class DLS(SearchStrategy):
    def __init__(
        self,
        static_map: Map,
        initial_state: State,
        depth_limit: int = 100,
    ):
        if depth_limit < 0:
            raise ValueError("depth_limit must be non-negative")
        super().__init__(static_map, initial_state)
        self.depth_limit = depth_limit

    def search(self) -> GoalState:
        return self._depth_limited_search(self.depth_limit)


class IDS(SearchStrategy):
    def __init__(
        self,
        static_map: Map,
        initial_state: State,
        max_depth: int = 100,
        step: int = 5,
    ):
        if max_depth < 0:
            raise ValueError("max_depth must be non-negative")
        super().__init__(static_map, initial_state)
        self.max_depth = max_depth
        self.step = step

    def search(self) -> GoalState:
        for depth_limit in range(self.max_depth + self.step):
            result = self._depth_limited_search(depth_limit)
            if result.cost != -1:
                return result
        return GoalState(cost=-1, path=[])


class GBFS(SearchStrategy):
    def search(self) -> GoalState:
        initial_h = self.H.get_heuristic(self.initial_state.box_positions)
        if math.isinf(initial_h):
            return GoalState(cost=-1, path=[])

        seq = 0
        frontier = [(initial_h, seq, self.initial_state, [])]
        discovered = {self.initial_state}

        while frontier:
            _, _, state, path = heapq.heappop(frontier)
            if state.box_positions == self.static_map.goals:
                return GoalState(cost=len(path), path=path)

            for successor in self.get_successor(state):
                next_state = successor.state
                if next_state in discovered:
                    continue

                heuristic = self.H.get_heuristic(next_state.box_positions)
                if math.isinf(heuristic):
                    continue

                discovered.add(next_state)
                self.nodes += 1
                seq += 1
                heapq.heappush(
                    frontier,
                    (heuristic, seq, next_state, path + [successor.action]),
                )

        return GoalState(cost=-1, path=[])


class UCS(SearchStrategy):
    def __init__(self, static_map: Map, initial_state: State):
        super().__init__(static_map, initial_state)

    def search(self) -> GoalState:
        seq = 0  # Since all moves cost 1 Cost Unit. Hence, we need another variable for heapq to not crash out

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

    def search(self) -> GoalState:
        init_f = self.H.get_heuristic(self.initial_state.box_positions)
        if math.isinf(init_f):
            return GoalState(cost=-1, path=[])
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
                    new_h = self.H.get_heuristic(next_state.box_positions)
                    if math.isinf(new_h):
                        continue

                    new_f = new_g + new_h
                    seq += 1
                    new_path = path + [successor.action]
                    best_g[next_state] = new_g
                    self.nodes += 1
                    heapq.heappush(
                        pq, (new_f, seq, new_g, next_state, new_path))

        return GoalState(cost=-1, path=[])
