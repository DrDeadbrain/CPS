import pygame
from pygame import gfxdraw
import numpy as np

'''
In order to display our simulation in real-time we use pygame.
This is the window class that expects a simulation class as parameter

To display basic shapes we have to define multiple drawing functions

The simulate method creates a pygame window and calls the draw method and the 
loop parameter every frame
-> Useful to update the simulation every frame
'''


class Window:
    def __init__(self, sim, config=None):
        # Sim to draw
        if config is None:
            config = {}
        self.sim = sim

        # set default config
        self.set_default_config()

        # update config
        for attr, val in config.items():
            setattr(self, attr, val)

    def set_default_config(self):
        """sets the default config"""
        self.width = 1400
        self.height = 1000
        self.bg_color = (250, 250, 250)

        self.fps = 60
        self.zoom = 5
        self.offset = (0, 0)

        self.mouse_last = (0, 0)
        self.mouse_down = False

    def simulate(self, loop=None):
        """displays the window and runs the loop function"""
        # create a pygame window
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.flip()

        # fixed fps
        clock = pygame.time.Clock()

        # to draw text
        pygame.font.init()
        self.text_font = pygame.font.SysFont('Lucida Console', 16)

        # draw loop
        running = True
        while running:
            # update simulation
            if loop: loop(self.sim)

            # draw simulation
            self.draw()

            # update window
            pygame.display.update()
            clock.tick(self.fps)

            # handle all events
            for event in pygame.event.get():
                # handle events
                if event.type == pygame.QUIT:
                    running = False

    def draw(self):
        """draws everything"""
        # fill background
        self.background(*self.bg_color)

        # major and minor grid and axes
        self.draw_grid(10, (220, 220, 220))
        self.draw_grid(100, (200, 200, 200))
        self.draw_axes()

        # draw roads
        self.draw_roads()

        # draw status info
        self.draw_status()

    def background(self, r, g, b):
        """fills screen with one color"""
        self.screen.fill((r, g, b))

    def draw_axes(self, color=(100, 100, 100)):
        """draws x and y axis"""
        x_start, y_start = self.inverse_convert(0, 0)
        x_end, y_end = self.inverse_convert(self.width, self.height)
        self.line(
            self.convert((0, y_start)),
            self.convert((0, y_end)),
            color
        )
        self.line(
            self.convert((x_start, 0)),
            self.convert((x_end, 0)),
            color
        )

    def draw_grid(self, unit=50, color=(150, 150, 150)):
        """draws grid"""
        x_start, y_start = self.inverse_convert(0, 0)
        x_end, y_end = self.inverse_convert(self.width, self.height)

        n_x = int(x_start / unit)
        n_y = int(y_start / unit)
        m_x = int(x_end / unit) + 1
        m_y = int(y_end / unit) + 1

        for i in range(n_x, m_x):
            self.line(
                self.convert((unit * i, y_start)),
                self.convert((unit * i, y_end)),
                color
            )
        for i in range(n_y, m_y):
            self.line(
                self.convert((x_start, unit * i)),
                self.convert((x_end, unit * i)),
                color
            )

    def draw_roads(self):
        """draws every road"""
        for road in self.sim.roads:
            # draw road background
            self.rotated_box(
                road.start,
                (road.length, 3.7),
                cos=road.angle_cos,
                sin=road.angle_sin,
                color=(180, 180, 220),
                centered=False
            )

    def draw_status(self):
        """draws status text"""

    def line(self, start_pos, end_pos, color):
        """draws a line"""
        gfxdraw.line(
            self.screen,
            *start_pos,
            *end_pos,
            color
        )

    def convert(self, x, y=None):
        """converts sim coords to screen coords"""
        if isinstance(x, list):
            return [self.convert(e[0], e[1]) for e in x]
        if isinstance(x, tuple):
            return self.convert(*x)
        return (
            int(self.width / 2 + (x + self.offset[0]) * self.zoom),
            int(self.height / 2 + (y + self.offset[1]) * self.zoom)
        )

    def inverse_convert(self, x, y=None):
        """converts screen coords to sim coords"""
        if isinstance(x, list):
            return [self.convert(e[0], e[1]) for e in x]
        if isinstance(x, tuple):
            return self.convert(*x)
        return (
            int(-self.offset[0] + (x - self.width / 2) / self.zoom),
            int(-self.offset[1] + (y - self.height / 2) / self.zoom)
        )

    def rotated_box(self, pos, size, angle=None, cos=None, sin=None, centered=True, color=(0, 0, 255), filled=True):
        """draws a rectangle center at *pos* with *size* rotated anti-clockwise by *angle*"""
        x, y = pos
        l, h = size

        if angle:
            cos, sin = np.cos(angle), np.sin(angle)

        vertex = lambda e1, e2: (
            x + (e1 * l * cos + e2 * h * sin) / 2,
            y + (e1 * l * sin - e2 * h * cos) / 2
        )

        if centered:
            vertices = self.convert(
                [vertex(*e) for e in [(0, -1), (0, 1), (1, 1), (1, -1)]]
            )
        else:
            vertices = self.convert(
                [vertex(*e) for e in [(0, -1), (0, 1), (2, 1), (2, -1)]]
            )
        self.polygon(vertices, color, filled=filled)

    def polygon(self, vertices, color, filled=True):
        gfxdraw.aapolygon(self.screen, vertices, color)
        if filled:
            gfxdraw.filled_polygon(self.screen, vertices, color)
