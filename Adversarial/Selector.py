import pygame

PANEL_BG = (244, 245, 247)   # BG
TEXT     = (40, 44, 52)      # WALL color

class UIPanel:
    def __init__(self, rect):
        self.rect = rect
        self.x = rect.x + 15 # left edge with padding for the text

        self.title_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.big_font   = pygame.font.SysFont("Arial", 20, bold=True)
        self.font       = pygame.font.SysFont("Arial", 17)
        self.small_font = pygame.font.SysFont("Arial", 15)

    def draw(self, surface, algo1, algo2, step, total_steps, score1=0, score2=0, is_game_over=False, game_started=False, max_actions_str="100", step_time=None):
        # draws panel background
        pygame.draw.rect(surface, PANEL_BG, self.rect)
        x = self.x
        y = self.rect.y + 16

        # displays algorithm
        surface.blit(self.big_font.render("Algorithms", True, TEXT), (x, y))
        y += 24
        surface.blit(self.font.render(f"Agent 1 (Z/X):  {algo1}", True, TEXT), (x, y))
        y += 20
        surface.blit(self.font.render(f"Agent 2 (C/V):  {algo2}", True, TEXT), (x, y))
        y += 26

        # max action
        actions_display = max_actions_str if max_actions_str else "_"
        surface.blit(self.big_font.render(f"Max Actions: {actions_display}", True, TEXT), (x, y))
        y += 28

        # total actions
        text = f"Total Actions: {total_steps}" if game_started else "Total Actions: --"
        surface.blit(self.big_font.render(text, True, TEXT), (x, y))
        y += 28

        # playback
        surface.blit(self.big_font.render("Playback", True, TEXT), (x, y))
        y += 22
        text = f"Step {step} / {total_steps}" if game_started else "Step -- / --"
        surface.blit(self.font.render(text, True, TEXT), (x, y))
        y += 20

        if game_started and step_time is not None:
            if step_time < 0.001:
                time_str = "Step Time: <1 ms"
            elif step_time < 1.0:
                time_str = f"Step Time: {step_time * 1000:.1f} ms"
            else:
                time_str = f"Step Time: {step_time:.3f} s"
        else:
            time_str = "Step Time: --"
        surface.blit(self.font.render(time_str, True, TEXT), (x, y))
        y += 26

        # goals scored
        surface.blit(self.big_font.render("Goals Scored", True, TEXT), (x, y))
        y += 22
        text_occ1 = f"Agent 1: {score1}" if game_started else "Agent 1: --"
        surface.blit(self.font.render(text_occ1, True, TEXT), (x, y))
        y += 19
        text_occ2 = f"Agent 2: {score2}" if game_started else "Agent 2: --"
        surface.blit(self.font.render(text_occ2, True, TEXT), (x, y))
        y += 26

        # controls
        surface.blit(self.big_font.render("Controls", True, TEXT), (x, y))
        y += 22

        controls = [
            "Z / X:     Agent 1 prev / next algo",
            "C / V:     Agent 2 prev / next algo",
            "Algorithms: BFS DFS DLS IDS GBFS UCS A*",
            "0 - 9:     Type Max Actions",
            "Backspace: Delete Digit",
            "Space:     Start / Pause",
            "Right:     Step Forward",
            "Left:      Step Backward",
            "WASD:      Pan Board",
            "Q / E:     Zoom in / out",
        ]
        for ctrl in controls:
            surface.blit(self.small_font.render(ctrl, True, TEXT), (x, y))
            y += 18

        y += 14

        # announces the end of the game
        if is_game_over:
            surface.blit(self.title_font.render("Game Over", True, TEXT), (x, y))
            y += 26

            if score1 > score2:
                winner_text = "Winner: Agent 1"
            elif score2 > score1:
                winner_text = "Winner: Agent 2"
            else:
                winner_text = "Result: Tie Game"

            surface.blit(self.title_font.render(winner_text, True, TEXT), (x, y))
            y += 26
            surface.blit(self.big_font.render(f"Agent 1: {score1} goals", True, TEXT), (x, y))
            y += 22
            surface.blit(self.big_font.render(f"Agent 2: {score2} goals", True, TEXT), (x, y))
            y += 22
            surface.blit(self.font.render(f"Total Steps: {total_steps}", True, TEXT), (x, y))

        elif not game_started:
            surface.blit(self.font.render("Press Space to start", True, TEXT), (x, y))
