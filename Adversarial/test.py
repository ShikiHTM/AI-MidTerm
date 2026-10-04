import argparse
import os
import sys
import time
import pygame

# Add project root to sys.path
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root not in sys.path:
    sys.path.insert(0, root)

from Solver.map import Map
from Solver.EntityDataType import Coord
from Solver.SearchStrategy import UCS, Astar
from GUI.Grid import Camera, Grid
from Adversarial.Selector import UIPanel
from Adversarial.game_state import Step, AgentProps, EndGameState
from Adversarial.game import CompetitiveEnvironment

# Direction vectors for each named action
DIRECTIONS = {
    "North": (0, -1),
    "South": (0,  1),
    "West":  (-1, 0),
    "East":  (1,  0),
}


def step_to_matrix(step: Step, static_map: Map):
    matrix = []

    agent_a = step.primary_agent
    agent_b = step.secondary_agent

    pushed_boxes = step.box_pushed
    pushed_pos: list[Coord] = []
    if len(pushed_boxes) > 0:
        pushed_pos = [b.box_position for b in pushed_boxes]

    for y in range(static_map.height):
        matrix.append([' '] * static_map.width)
        for x in range(static_map.width):
            pos = Coord(x, y)
            if pos in static_map.walls:
                matrix[y][x] = "%"
            elif (pos == agent_a.position) or (pos == agent_b.position):
                matrix[y][x] = 'A'
            elif pos in pushed_pos:
                continue
            elif pos in step.box_positions:
                # Box on a goal shows 'C', otherwise 'B'
                matrix[y][x] = 'C' if pos in static_map.goals else 'B'
            elif pos in static_map.goals:
                matrix[y][x] = 'D'

    if len(pushed_pos) > 0:
        for b in pushed_boxes:
            if b.agent_id in ("Agent_1", "Agent 1", 1):
                matrix[b.box_position.y][b.box_position.x] = "B_1"
            else:
                matrix[b.box_position.y][b.box_position.x] = "B_2"

    return matrix


class AdversarialSokobanGame:
    def __init__(self, map_path, max_steps=100, width=1100, height=700):
        pygame.init()
        pygame.display.set_caption("2-Agent Adversarial Sokoban")
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()

        panel_w = 300
        board_rect = pygame.Rect(0, 0, width - panel_w, height)
        panel_rect = pygame.Rect(width - panel_w, 0, panel_w, height)

        self.map_path   = map_path
        self.max_steps  = max_steps
        self.actions_input = str(max_steps)
        self.map_obj    = Map(map_path)

        self.camera = Camera(board_rect, cell_size=40)
        self.grid   = Grid()
        self.panel  = UIPanel(panel_rect)

        # Selected algorithms for Agent 1 and Agent 2
        self.algo1 = Astar
        self.algo1_name = "Astar"
        self.algo2 = UCS
        self.algo2_name = "UCS"

        # Live environment reference
        self.env = None

        # Playback & state tracking
        self.playing      = False
        self.step_delay   = 0.22     # seconds between live steps
        self.timer        = 0.0
        self.game_started = False
        self.is_game_over = False

        # Extract initial agent positions
        agent_positions = []
        with open(map_path) as f:
            for y, line in enumerate(f):
                for x, char in enumerate(line.rstrip('\n')):
                    if char == 'A':
                        agent_positions.append(Coord(x, y))

        p1 = agent_positions[0] if len(agent_positions) > 0 else (self.map_obj.agent_pos or Coord(0, 0))
        p2 = agent_positions[1] if len(agent_positions) > 1 else p1

        self.init_step = Step(
            at=0,
            primary_agent=AgentProps(position=p1, action="Stay"),
            secondary_agent=AgentProps(position=p2, action="Stay"),
            box_positions=frozenset(self.map_obj.boxes_pos),
            box_pushed=[]
        )

        self.states       = [step_to_matrix(self.init_step, self.map_obj)]
        self.step_objs    = [self.init_step]
        self.scores       = [(0, 0)]
        self.step_times   = [None]   # Execution time for each step
        self.final_scores = (0, 0)
        self.step         = 0

        self.grid.set_matrix(self.states[0])
        self.camera.center(self.grid.rows, self.grid.cols)

    def reset_match_state(self):
        """Reset match state when algorithms or max actions are adjusted."""
        self.env = None
        self.game_started = False
        self.is_game_over = False
        self.playing = False
        self.step = 0
        self.states = [step_to_matrix(self.init_step, self.map_obj)]
        self.step_objs = [self.init_step]
        self.scores = [(0, 0)]
        self.step_times = [None]
        self.final_scores = (0, 0)
        self.grid.set_matrix(self.states[0])
        pygame.display.set_caption(f"2-Agent Sokoban - Ready ({self.algo1_name} vs {self.algo2_name})")

    def select_algo(self, agent_num, algo_type, algo_name):
        """Set algorithm choice and prepare for new simulation."""
        if agent_num == 1:
            self.algo1 = algo_type
            self.algo1_name = algo_name
        else:
            self.algo2 = algo_type
            self.algo2_name = algo_name

        self.reset_match_state()

    def start_live_match(self):
        """Initialize the competitive environment for real-time live stepping."""
        if not self.actions_input or int(self.actions_input) <= 0:
            self.actions_input = "100"
            self.max_steps = 100
        else:
            self.max_steps = int(self.actions_input)

        label = f"{self.algo1_name} vs {self.algo2_name}"
        pygame.display.set_caption(f"2-Agent Sokoban - Live ({label})")

        self.env = CompetitiveEnvironment(self.map_path, self.max_steps, self.algo1, self.algo2)
        self.states = [step_to_matrix(self.init_step, self.map_obj)]
        self.step_objs = [self.init_step]
        self.scores = [(0, 0)]
        self.step_times = [None]
        self.final_scores = (0, 0)
        self.step = 0
        self.game_started = True
        self.is_game_over = False
        self.playing = True
        self.timer = 0.0

    def advance_step(self):
        """Execute the next live turn, or step forward if viewing past history."""
        if not self.game_started:
            self.start_live_match()
            return

        # If viewing past rewound history, walk forward through recorded frames
        if self.step < len(self.states) - 1:
            self.step += 1
            self.grid.set_matrix(self.states[self.step])
            return

        if self.is_game_over or self.env is None:
            self.playing = False
            return

        # Execute next step live in the environment and measure execution time
        t0 = time.perf_counter()
        res = self.env.step()
        elapsed = time.perf_counter() - t0

        if res is None:
            self.is_game_over = True
            self.playing = False
            return

        if isinstance(res, EndGameState):
            self.is_game_over = True
            self.playing = False
            self.final_scores = (res.first_agent_score, res.second_agent_score)
            caption = f"2-Agent Sokoban - Finished | Agent 1: {res.first_agent_score}, Agent 2: {res.second_agent_score}"
            pygame.display.set_caption(caption)
            return

        # Step successfully produced
        self.step_objs.append(res)
        self.states.append(step_to_matrix(res, self.map_obj))
        self.step_times.append(elapsed)
        s1 = list(self.env.box_owners.values()).count(self.env.agent1.id)
        s2 = list(self.env.box_owners.values()).count(self.env.agent2.id)
        self.scores.append((s1, s2))
        self.step += 1
        self.grid.set_matrix(self.states[self.step])

    def step_backward(self):
        """Step backward in recorded history."""
        if self.step > 0:
            self.step -= 1
            self.grid.set_matrix(self.states[self.step])

    def toggle_play(self):
        """Toggle live playback pause/resume or restart match."""
        if not self.game_started:
            self.start_live_match()
            return
        if self.is_game_over and self.step >= len(self.states) - 1:
            self.start_live_match()
            return

        self.playing = not self.playing
        self.timer = 0.0

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.camera.handle_event(event):
                    continue

                if event.type == pygame.KEYDOWN:
                    # Agent 1 algorithm selection (Z = UCS, X = Astar)
                    if event.key == pygame.K_z:
                        self.select_algo(1, UCS, "UCS")
                    elif event.key == pygame.K_x:
                        self.select_algo(1, Astar, "Astar")

                    # Agent 2 algorithm selection (C = UCS, V = Astar)
                    elif event.key == pygame.K_c:
                        self.select_algo(2, UCS, "UCS")
                    elif event.key == pygame.K_v:
                        self.select_algo(2, Astar, "Astar")

                    # Number input for max actions in real time
                    elif event.unicode.isdigit():
                        if self.actions_input == "0":
                            self.actions_input = event.unicode
                        else:
                            if len(self.actions_input) < 5:
                                self.actions_input += event.unicode
                        if self.actions_input and int(self.actions_input) > 0:
                            self.max_steps = int(self.actions_input)
                        self.reset_match_state()

                    # Backspace to remove digits from action input
                    elif event.key == pygame.K_BACKSPACE:
                        self.actions_input = self.actions_input[:-1]
                        if self.actions_input and int(self.actions_input) > 0:
                            self.max_steps = int(self.actions_input)
                        self.reset_match_state()

                    # Start / Pause live execution
                    elif event.key == pygame.K_SPACE:
                        self.toggle_play()

                    # Step forward manually
                    elif event.key == pygame.K_RIGHT:
                        self.playing = False
                        self.advance_step()

                    # Step backward in history
                    elif event.key == pygame.K_LEFT:
                        self.playing = False
                        self.step_backward()

                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            # Advance live turns at fixed interval
            if self.playing and not self.is_game_over:
                self.timer += dt
                if self.timer >= self.step_delay:
                    self.timer = 0.0
                    self.advance_step()

            self.grid.draw(self.screen, self.camera)

            total_steps = max(0, len(self.states) - 1) if self.states else 0
            is_game_over_now = self.is_game_over and (self.step >= len(self.states) - 1 and len(self.states) > 1)

            if is_game_over_now:
                cur_s1, cur_s2 = self.final_scores
            elif self.scores and self.step < len(self.scores):
                cur_s1, cur_s2 = self.scores[self.step]
            else:
                cur_s1, cur_s2 = (0, 0)

            cur_time = None
            if self.step_times and 0 <= self.step < len(self.step_times):
                cur_time = self.step_times[self.step]

            self.panel.draw(
                self.screen,
                self.algo1_name,
                self.algo2_name,
                self.step,
                total_steps,
                cur_s1,
                cur_s2,
                is_game_over_now,
                self.game_started,
                max_actions_str=self.actions_input,
                step_time=cur_time
            )
            pygame.display.flip()


def main():
    parser = argparse.ArgumentParser(description="Run the 2-Agent Adversarial Sokoban GUI.")
    default_map = os.path.join(root, "tiny.txt")
    parser.add_argument("input_file", nargs="?", default=default_map,
                        help="path to the Sokoban map file (default: tiny.txt)")
    parser.add_argument("--steps", "-n", type=int, default=100,
                        help="maximum number of steps (default: 100)")
    args = parser.parse_args()

    map_file = args.input_file
    if not os.path.exists(map_file):
        candidate = os.path.join(root, map_file)
        if os.path.exists(candidate):
            map_file = candidate
        else:
            print(f"Map {map_file} not found.")
            return

    AdversarialSokobanGame(map_file, max_steps=args.steps).run()


if __name__ == "__main__":
    main()
