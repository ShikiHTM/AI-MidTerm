import pygame

PANEL_BG = (244, 245, 247)   # BG
TEXT     = (40, 44, 52)      # WALL color

class UIPanel:
    def __init__(self, rect):
        self.rect = rect
        self.x = rect.x # left edge for the text

        self.big_font = pygame.font.SysFont("Arial", 26, bold=True)
        self.font = pygame.font.SysFont("Arial", 22)

    def draw(self, surface, algo, step, total_steps):
        # each y increment is telling the game where to draw the next line of text
        pygame.draw.rect(surface, PANEL_BG, self.rect)
        x = self.x
        y = self.rect.y + 50 # + 50 because it looks nicer

        # algorithm display
        text = f"Algorithm: {algo}" if algo else "Algorithm: (press 1 or 2)"
        surface.blit(self.big_font.render(text, True, TEXT), (x, y))
        y += 34

        # total actions count
        text = f"Total Actions: {total_steps}" if algo else "Total Actions: --"
        surface.blit(self.big_font.render(text, True, TEXT), (x, y))
        y += 40

        # playback counter
        surface.blit(self.big_font.render("Playback", True, TEXT), (x, y))
        y += 28
        text = f"Step {step} / {total_steps}" if algo else "Step -- / --"
        surface.blit(self.font.render(text, True, TEXT), (x, y))
        y += 48

        # controls display
        surface.blit(self.font.render("Controls", True, TEXT), (x, y))
        y += 28

        controls = [
            ("1 / 2:    Select Algorithm"),
            ("Space:    Pause / Resume"),
            ("Right Arrow:      Step Forward"),
            ("Left Arrow:       Step Backward"),
            ("WASD:       Pan Board"),
            ("Q/E:           Zoom in / Zoom out"),
        ]
        for i in controls:
            surface.blit(
                self.font.render(i, True, TEXT), 
                (x, y)
                )
            y += 22
