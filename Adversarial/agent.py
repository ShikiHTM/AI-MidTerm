from Solver.EntityDataType import Coord
from Solver.SearchStrategy import SearchStrategy
from Solver.map import Map
from Solver.state import State

class Agent:
    def __init__(self, id: str, search_strategy: type['SearchStrategy'], static_map: Map):
        self.id: str = id
        self.search_strategy: type[SearchStrategy] = search_strategy
        self.static_map: Map = static_map
        self.current_path: list[str] = []
        self._expected_box_positions: set[Coord] = set()

    def get_next_action(self, current_pos: Coord, box_positions: set[Coord], opponent_pos: Coord) -> str:
        if self.is_valid_path(current_pos, box_positions, opponent_pos):
            return self.current_path.pop(0)
        return self.plan_new_path(current_pos, box_positions, opponent_pos)

    def plan_new_path(self, current_pos: Coord, box_positions: set[Coord], opponent_pos: Coord) -> str:
        is_opponent_added = False
        if opponent_pos not in self.static_map.walls:
            self.static_map.walls.add(opponent_pos)
            is_opponent_added = True

        initial_state = State(agent_position=current_pos, box_positions=frozenset(box_positions))
        search_solver = self.search_strategy(self.static_map, initial_state)

        self._expected_box_positions = set(box_positions)
        goal_state = search_solver.search()

        if is_opponent_added:
            self.static_map.walls.remove(opponent_pos)

        if goal_state.path:
            self.current_path = goal_state.path
            return self.current_path.pop(0)
        else:
            return "Stay"

    def is_valid_path(self, current_pos: Coord, box_positions: set[Coord], opponent_pos: Coord) -> bool:
        if not self.current_path:
            return False

        next_action = self.current_path[0]
        directions = {
            "North": (0, -1),
            "South": (0, 1),
            "West": (-1, 0),
            "East": (1, 0)
        }

        dx, dy = directions[next_action]
        next_pos = Coord(current_pos.x + dx, current_pos.y + dy)

        if next_pos == opponent_pos:
            self.current_path = []
            return False

        if box_positions != self._expected_box_positions:
            self.current_path = []
            self.plan_new_path(current_pos, box_positions, opponent_pos)
            return False

        return True