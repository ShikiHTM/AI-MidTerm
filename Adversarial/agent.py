from Solver.EntityDataType import Coord
from Solver.SearchStrategy import SearchStrategy
from Solver.map import Map
from Solver.state import State
import copy

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

        best_path = []
        
        unsolved_boxes = [b for b in box_positions if b not in self.static_map.goals]
        
        for target_box in unsolved_boxes:
            for target_goal in self.static_map.goals:
                if target_goal in box_positions: 
                    continue
                    
                fake_map = copy.copy(self.static_map)
                fake_map.goals = {target_goal}
                
                fake_state = State(agent_position=current_pos, box_positions=frozenset({target_box}))
                
                search_solver = self.search_strategy(fake_map, fake_state)
                goal_state = search_solver.search()
                
                if goal_state and goal_state.path:
                    if not best_path or len(goal_state.path) < len(best_path):
                        best_path = goal_state.path

        if is_opponent_added:
            self.static_map.walls.remove(opponent_pos)

        self._expected_box_positions = set(box_positions)
        
        if best_path:
            self.current_path = best_path
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