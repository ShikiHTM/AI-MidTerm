import sys
import os
import random
from typing import Tuple

from Solver.EntityDataType import Coord
from Solver.map import Map
from Adversarial.agent import Agent
import random
from datetime import datetime

class CompetitiveEnvironment:
    def __init__(self, map_path: str, max_steps: int, algo1: type, algo2: type):
        self.map_path = map_path
        self.max_steps = max_steps
        
        # 1. Load the shared map
        self.shared_map = Map(map_path)
        
        # 2. Extract both agent positions manually (since Map only stores the last 'A')
        self.agent_positions = []
        with open(map_path) as f:
            lines = f.readlines()
        for y, line in enumerate(lines):
            line = line.rstrip('\n')
            for x, char in enumerate(line):
                if char == 'A':
                    self.agent_positions.append(Coord(x, y))
                    
        if len(self.agent_positions) < 2:
            raise ValueError("The map must contain exactly 2 'A's to run a competitive match.")
            
        self.agent1_pos = self.agent_positions[0]
        self.agent2_pos = self.agent_positions[1]
        
        self.boxes = self.shared_map.boxes_pos.copy()
        
        self.agent1 = Agent("Agent 1", algo1, self.shared_map)
        self.agent2 = Agent("Agent 2", algo2, self.shared_map)
        
        # Track box ownership (score goes to the last agent to push a box onto a goal)
        self.box_owners = {} # Mapping: goal_coord -> agent_id
        
        self.current_step = 0
        self.game_over = False
        self.winner = None

    def resolve_action(self, pos: Coord, action: str) -> Coord:
        directions = {
            "North": (0, -1),
            "South": (0, 1),
            "West": (-1, 0),
            "East": (1, 0),
            "Stay": (0, 0)
        }
        dx, dy = directions.get(action, (0, 0))
        return Coord(pos.x + dx, pos.y + dy)

    def step(self):
        if self.current_step >= self.max_steps or self.is_all_boxes_on_goal():
            self.end_game()
            return
            
        # 1. Get simultaneous actions from both agents
        # (This will trigger their SearchStrategy to plan paths if needed)
        print(f"--- Step {self.current_step + 1} ---")
        print(f"Agent 1 planning...")
        action1 = self.agent1.get_next_action(self.agent1_pos, self.boxes, self.agent2_pos)
        print(f"Agent 2 planning...")
        action2 = self.agent2.get_next_action(self.agent2_pos, self.boxes, self.agent1_pos)
        
        print(f"Agent 1 attempts: {action1}")
        print(f"Agent 2 attempts: {action2}")
        
        # 2. Determine target coordinates
        next1 = self.resolve_action(self.agent1_pos, action1)
        next2 = self.resolve_action(self.agent2_pos, action2)
        
        push1_target = self.resolve_action(next1, action1) if next1 in self.boxes else None
        push2_target = self.resolve_action(next2, action2) if next2 in self.boxes else None
        
        conflict1, conflict2 = self.check_conflicts(next1, next2, push1_target, push2_target)
        
        # 3. Apply moves
        new_pos1 = self.agent1_pos if conflict1 else next1
        new_pos2 = self.agent2_pos if conflict2 else next2
        
        if conflict1 and action1 != "Stay":
            print("Agent 1 action blocked by conflict.")
        if conflict2 and action2 != "Stay":
            print("Agent 2 action blocked by conflict.")
            
        # 4. Handle box movements and ownership
        new_boxes = set(self.boxes)
        
        if push1_target and not conflict1:
            new_boxes.remove(next1)
            new_boxes.add(push1_target)
            if push1_target in self.shared_map.goals:
                self.box_owners[push1_target] = self.agent1.id
            if next1 in self.box_owners:
                del self.box_owners[next1]
                
        if push2_target and not conflict2:
            new_boxes.remove(next2)
            new_boxes.add(push2_target)
            if push2_target in self.shared_map.goals:
                self.box_owners[push2_target] = self.agent2.id
            if next2 in self.box_owners:
                del self.box_owners[next2]
                
        self.agent1_pos = new_pos1
        self.agent2_pos = new_pos2
        self.boxes = new_boxes
        self.current_step += 1
        
        self.print_state()
        
    def check_conflicts(self, next1: Coord, next2: Coord, push1_target: Coord, push2_target: Coord) -> Tuple[bool, bool]:
        random.seed(datetime.now().second)
        conflict1 = False
        conflict2 = False
        
        # Swapping positions
        if next1 == self.agent2_pos and next2 == self.agent1_pos:
            return True, True
            
        # Moving to same square
        if next1 == next2 and next1 != self.agent1_pos and next2 != self.agent2_pos:
            if random.choice([True, False]):
                conflict2 = True # Agent 1 gets the square
            else:
                conflict1 = True # Agent 2 gets the square
            
        # Walls
        if next1 in self.shared_map.walls or (push1_target and push1_target in self.shared_map.walls):
            conflict1 = True
        if next2 in self.shared_map.walls or (push2_target and push2_target in self.shared_map.walls):
            conflict2 = True
            
        # Both push same box
        if push1_target and push2_target and next1 == next2:
            return True, True
            
        # Push box into other agent
        if push1_target == self.agent2_pos and next2 == self.agent2_pos:
            conflict1 = True
        if push2_target == self.agent1_pos and next1 == self.agent1_pos:
            conflict2 = True
            
        # Push box into other agent's next pos
        if push1_target == next2:
            conflict1 = True
            conflict2 = True
        if push2_target == next1:
            conflict1 = True
            conflict2 = True
            
        # Push two different boxes into same square
        if push1_target and push2_target and push1_target == push2_target:
            if random.choice([True, False]):
                return False, True # Agent 1 wins the push
            else:
                return True, False # Agent 2 wins the push
            
        # Push box into another static box
        if push1_target in self.boxes and push1_target != next2:
            conflict1 = True
        if push2_target in self.boxes and push2_target != next1:
            conflict2 = True
            
        return conflict1, conflict2

    def is_all_boxes_on_goal(self) -> bool:
        return self.boxes.issubset(self.shared_map.goals)
        
    def end_game(self):
        self.game_over = True
        print("\n=== Game Over ===")
        score1 = list(self.box_owners.values()).count(self.agent1.id)
        score2 = list(self.box_owners.values()).count(self.agent2.id)
        print(f"Agent 1 Score: {score1}")
        print(f"Agent 2 Score: {score2}")
        
        if score1 > score2:
            print("Winner: Agent 1!")
        elif score2 > score1:
            print("Winner: Agent 2!")
        else:
            print("Draw!")
            
    def print_state(self):
        print(f"Agent 1 Pos: ({self.agent1_pos.x}, {self.agent1_pos.y}) | Agent 2 Pos: ({self.agent2_pos.x}, {self.agent2_pos.y})")
        score1 = list(self.box_owners.values()).count(self.agent1.id)
        score2 = list(self.box_owners.values()).count(self.agent2.id)
        print(f"Scores -> Agent 1: {score1} | Agent 2: {score2}")
        
    def run(self):
        self.print_state()
        while not self.game_over:
            self.step()
