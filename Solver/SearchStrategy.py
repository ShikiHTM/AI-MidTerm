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
