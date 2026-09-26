import os
import sys
import time
import pygame

# ddd project root to sys.path, fixes import bugs i dont know why imports run relative to the dir path in the terminal 
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root not in sys.path:
    sys.path.insert(0, root)

from Solver.map import Map
from Solver.state import State
from Solver.EntityDataType import Coord
from Solver.SearchStrategy import UCS, Astar
from GUI.Grid import Camera, Grid
from GUI.Selector import UIPanel

# direction vectors for each named action
DIRECTIONS = {
    "North": (0, -1),
    "South": (0,  1),
    "West":  (-1, 0),
    "East":  (1,  0),
}


def state_to_matrix(state, static_map):
    matrix = []
    for y in range(static_map.height):
        row = []
        for x in range(static_map.width):
            pos = Coord(x, y)
            if pos in static_map.walls:
                row.append('%')
            elif pos == state.agent_position:
                # Agent standing on a goal shows 'E', otherwise 'A'
                row.append('E' if pos in static_map.goals else 'A')
            elif pos in state.box_positions:
                # Box on a goal shows 'C', otherwise 'B'
                row.append('C' if pos in static_map.goals else 'B')
            elif pos in static_map.goals:
                row.append('D')
            else:
                row.append(' ')
        matrix.append(row)
    return matrix


def build_history(init_state, static_map, path):
    history = [state_to_matrix(init_state, static_map)]
    current = init_state

    for action in path:
        dx, dy = DIRECTIONS[action]
        new_agent = Coord(current.agent_position.x + dx,
                          current.agent_position.y + dy)
        boxes = set(current.box_positions)

        # If the agent walks into a box, push it one cell further
        if new_agent in boxes:
            boxes.remove(new_agent)
            boxes.add(Coord(new_agent.x + dx, new_agent.y + dy))

        current = State(new_agent, frozenset(boxes))
        history.append(state_to_matrix(current, static_map))

    return history


class SokobanGame:
    def __init__(self, map_path, width=1100, height=700):
        pygame.init()
        pygame.display.set_caption("Sokoban Solver")
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()

        panel_w = 300
        board_rect = pygame.Rect(0, 0, width - panel_w, height)
        panel_rect = pygame.Rect(width - panel_w, 0, panel_w, height)

        self.map_obj    = Map(map_path)
        self.init_state = State(self.map_obj.agent_pos, self.map_obj.boxes_pos)

        self.camera = Camera(board_rect, cell_size=60)
        self.grid   = Grid()
        self.panel  = UIPanel(panel_rect)

        self.algorithm  = ""       # "UCS" or "Astar"
        self.states     = []       # list of matrices, one per step
        self.path       = []       # list of action names
        self.step       = 0        # current playback index
        self.cost       = 0
        self.nodes      = 0
        self.time_spent = 0.0

        # Playback
        self.playing    = False
        self.step_delay = 0.22     # seconds between auto-play steps
        self.timer      = 0.0

        self.grid.set_matrix(state_to_matrix(self.init_state, self.map_obj))
        self.camera.center(self.grid.rows, self.grid.cols)


    def solve(self, algo_name):
        """Run the chosen search algorithm and store the result."""
        self.algorithm = algo_name
        self.playing = False

        solver = (UCS if algo_name == "UCS" else Astar)(self.map_obj, self.init_state)
        result = solver.search()

        self.nodes  = solver.nodes
        self.cost   = result.cost
        self.path   = result.path or []
        self.states = build_history(self.init_state, self.map_obj, self.path)
        self.step   = 0
        self.grid.set_matrix(self.states[0])

    def step_forward(self):
        if self.states and self.step < len(self.states) - 1:
            self.step += 1
            self.grid.set_matrix(self.states[self.step])

    def step_backward(self):
        if self.states and self.step > 0:
            self.step -= 1
            self.grid.set_matrix(self.states[self.step])

    def toggle_play(self):
        if not self.states:
            return
        if self.step >= len(self.states) - 1:
            self.step = 0
            self.grid.set_matrix(self.states[0])
            self.playing = True
        else:
            self.playing = not self.playing
        self.timer = 0.0

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if self.camera.handle_event(event):
                    continue

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.solve("UCS")
                    elif event.key == pygame.K_2:
                        self.solve("Astar")
                    elif event.key == pygame.K_SPACE:
                        self.toggle_play()
                    elif event.key == pygame.K_RIGHT:
                        self.playing = False
                        self.step_forward()
                    elif event.key == pygame.K_LEFT:
                        self.playing = False
                        self.step_backward()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

            if self.playing and self.states:
                self.timer += dt
                if self.timer >= self.step_delay:
                    self.timer = 0.0
                    if self.step < len(self.states) - 1:
                        self.step_forward()
                    else:
                        self.playing = False     # reached the end

            self.grid.draw(self.screen, self.camera)
            self.panel.draw(self.screen, self.algorithm, self.step, len(self.path))
            pygame.display.flip()


if __name__ == "__main__":
    map_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "input.txt")
    SokobanGame(map_file).run()
