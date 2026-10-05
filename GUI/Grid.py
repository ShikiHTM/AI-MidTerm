import os
import pygame

# colors of game elements
BG = (244, 245, 247)
FLOOR = (235, 237, 240)
GRIDLINE = (220, 223, 228)
WALL = (40, 44, 52)
BOXGOAL = (105, 72, 48)
BOXGOAL_BD = (65, 42, 26)
GOAL = (185, 45, 45)
BOX = (42, 98, 60)
BOX_BD = (24, 60, 36)
AGENT = (35, 40, 50)
AGENT_1 = (230, 126, 34)
AGENT_2 = (52, 152, 219)

# this class was really hard to implement


class Camera:
    def __init__(self, viewport: pygame.Rect, cell_size=60):
        self.viewport = viewport
        self.cell_size = cell_size

        # position of the grid's top left corner
        self.x = 0
        self.y = 0

        self.pan_keys = (
            pygame.K_w,
            pygame.K_a,
            pygame.K_s,
            pygame.K_d
        )

    def center(self, rows, cols):
        w = cols * self.cell_size
        h = rows * self.cell_size
        self.x = int(self.viewport.x + (self.viewport.width - w) / 2)
        self.y = int(self.viewport.y + (self.viewport.height - h) / 2)

    def zoom(self, zoom_in):
        old = self.cell_size
        step = 10 if old < 50 else 15
        new = 0
        if zoom_in:
            # largest cell size when zoomed in is 140 pixels
            new = min(140, old + step)
        else:
            # smallest size for a cell after zooming in is 20 pixels
            new = max(20, old - step)

        # scales and positions the grid relative to the viewport center
        ratio = new / old
        cx, cy = self.viewport.centerx, self.viewport.centery
        self.x = int(cx + (self.x - cx) * ratio)
        self.y = int(cy + (self.y - cy) * ratio)
        self.cell_size = new

    def handle_event(self, event):
        # returns True if we used the event (so the caller knows to skip it)
        pan_const = 50

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.zoom(True)
                return True
            if event.key == pygame.K_e:
                self.zoom(False)
                return True

        if event.type == pygame.KEYDOWN and event.key in self.pan_keys:
            if event.key == self.pan_keys[0]:
                self.y += pan_const
            elif event.key == self.pan_keys[1]:
                self.x += pan_const
            elif event.key == self.pan_keys[2]:
                self.y -= pan_const
            elif event.key == self.pan_keys[3]:
                self.x -= pan_const

            return True

        return False


class Grid:
    def __init__(self):
        self.matrix = []
        self.rows = 0
        self.cols = 0

        self.sprite = None
        path = os.path.join(os.path.dirname(__file__), "agent.bmp")
        self.sprite = pygame.image.load(path).convert_alpha()
        self.agent_sprites: dict[
            tuple[tuple[int, int, int], int], pygame.Surface
        ] = {}

    def _get_agent_sprite(self, color: tuple[int, int, int], size: int) -> pygame.Surface:
        key = (color, size)
        if key not in self.agent_sprites:
            tinted = pygame.Surface(self.sprite.get_size(), pygame.SRCALPHA)
            rgb_pixels = pygame.surfarray.pixels3d(tinted)
            rgb_pixels[:] = color
            del rgb_pixels

            alpha_pixels = pygame.surfarray.pixels_alpha(tinted)
            alpha_pixels[:] = pygame.surfarray.array_alpha(self.sprite)
            del alpha_pixels

            self.agent_sprites[key] = pygame.transform.smoothscale(
                tinted, (size, size)
            )

        return self.agent_sprites[key]

    def set_matrix(self, matrix):
        self.matrix = matrix
        self.rows = len(matrix)
        self.cols = 0
        if self.rows > 0:
            self.cols = len(matrix[0])

    def draw(self, surface, cam):
        old_clip = surface.get_clip()  # saves old clip
        # clips to the viewport so the rendering dont break the ui panel
        surface.set_clip(cam.viewport)
        pygame.draw.rect(surface, BG, cam.viewport)

        sz = cam.cell_size
        pad = max(2, int(sz * 0.08))

        for i in range(self.rows):
            for j in range(self.cols):
                px = cam.x + j * sz
                py = cam.y + i * sz

                tile = self.matrix[i][j]
                pcx = px + (sz / 2)
                pcy = py + (sz / 2)

                sp = (px, py, sz, sz)  # size + position of each cell

                if tile == '%':
                    pygame.draw.rect(surface, WALL, sp)
                elif tile == 'D':
                    pygame.draw.circle(
                        surface, GOAL, (pcx, pcy), max(3, sz / 5))
                elif tile in ('B', 'B_1', 'B_2', 'C', 'C_1', 'C_2'):
                    on_goal = tile.startswith('C')
                    box_color = BOXGOAL if on_goal else BOX
                    pygame.draw.rect(surface, box_color, sp)

                    if tile.endswith('_1') or tile.endswith('_2'):
                        owner_color = AGENT_1 if tile.endswith(
                            '_1') else AGENT_2
                        triangle = (
                            (px, py),
                            (px + sz, py),
                            (px + sz / 2, py + sz / 2),
                        )
                        pygame.draw.polygon(surface, owner_color, triangle)

                    border_color = BOXGOAL_BD if on_goal else BOX_BD
                    pygame.draw.rect(surface, border_color,
                                     sp, max(1, sz // 16))
                elif tile in ('A_1', 'A_2', 'A'):
                    agent_color = (
                        AGENT_1 if tile == 'A_1'
                        else AGENT_2 if tile == 'A_2'
                        else AGENT
                    )
                    surface.blit(self._get_agent_sprite(agent_color, sz), (px, py))

                pygame.draw.rect(surface, GRIDLINE, (px, py, sz, sz), 1)

        surface.set_clip(old_clip)
