import pygame
import random
import math

WIDTH = 1000
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Dot&Dot")
FPS = 30

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
BROWN = (165, 42, 42)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
AQUA = (100, 200, 200)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
WHITE = (255, 255, 255)
TURQUOISE = (64, 224, 208)

BACKGROUND_COLOR = WHITE
VERTEX_RADIUS = 10
EDGE_THICKNESS = 5
SNAP_DISTANCE = 40
BASE_EDGE_COLOR = BLACK


class Box:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = BACKGROUND_COLOR
        self.width = width
        self.total_rows = total_rows
        self.owner = None

    def is_complete(self, highlighted_lines):
        corners = [
            (self.x, self.y),  # Top-left corner
            (self.x + self.width, self.y),  # Top-right corner
            (self.x, self.y + self.width),  # Bottom-left corner
            (self.x + self.width, self.y + self.width)  # Bottom-right corner
        ]
        edges = [
            ((corners[0], corners[1]), BASE_EDGE_COLOR),  # Top edge
            ((corners[1], corners[3]), BASE_EDGE_COLOR),  # Right edge
            ((corners[3], corners[2]), BASE_EDGE_COLOR),  # Bottom edge
            ((corners[2], corners[0]), BASE_EDGE_COLOR)  # Left edge
        ]

        return all(edge in highlighted_lines or ((edge[0][1], edge[0][0]), BASE_EDGE_COLOR) in highlighted_lines for edge in edges)

    def claim_box(self, highlighted_lines, claiming_player):
        if self.is_complete(highlighted_lines) and self.color == BACKGROUND_COLOR:
            self.owner = claiming_player
            self.color = claiming_player.color

    def draw_box(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))


class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color


def get_clicked_corner(grid):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    tolerance = 15

    for row in grid:
        for box in row:
            corners = [
                (box.x, box.y),  # Top-left corner
                (box.x + box.width, box.y),  # Top-right corner
                (box.x, box.y + box.width),  # Bottom-left corner
                (box.x + box.width, box.y + box.width)  # Bottom-right corner
            ]
            for corner in corners:
                corner_x, corner_y = corner
                if abs(mouse_x - corner_x) <= tolerance and abs(mouse_y - corner_y) <= tolerance:
                    return corner
    return None


def make_grid(rows, width):
    grid = []
    gap = width // rows  # gap in a box = total width of window divided by individual number of rows wanted
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            box = Box(i, j, gap, rows)
            grid[i].append(box)
    return grid


def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
    for j in range(rows):
        pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw_circles(win, grid):
    for row in grid:
        for box in row:
            corners = [
                (box.x, box.y),
                (box.x + box.width, box.y),
                (box.x, box.y + box.width),
                (box.x + box.width, box.y + box.width)
            ]
            for corner in corners:
                pygame.draw.circle(win, BLACK, corner, VERTEX_RADIUS)


def draw(win, grid, rows, width, highlighted_lines, current_player):
    win.fill(BACKGROUND_COLOR)
    # print(highlighted_lines)
    for row in grid:
        for box in row:
            box.claim_box(highlighted_lines, current_player)
            box.draw_box(win)


    draw_grid(win, rows, width)
    draw_circles(win, grid)

    for line, color in highlighted_lines:
        start_pos, end_pos = line
        pygame.draw.line(win, color, start_pos, end_pos, EDGE_THICKNESS)


def draw_animated_line(win, start_pos, end_pos, highlighted_lines_arr, color, duration=2):
    steps = int(FPS * duration)
    for i in range(steps):
        alpha = i / steps
        intermediate_pos = (
            start_pos[0] + alpha * (end_pos[0] - start_pos[0]),
            start_pos[1] + alpha * (end_pos[1] - start_pos[1])
        )
        pygame.draw.line(win, color, start_pos, intermediate_pos, EDGE_THICKNESS)
        pygame.display.update()
    highlighted_lines_arr.append(((start_pos, end_pos), color))


def snap_to_nearest_corner(pos, grid, start_corner):
    x, y = pos
    nearest_corner = None
    min_distance = float('inf')

    for row in grid:
        for box in row:
            corners = [
                (box.x, box.y),
                (box.x + box.width, box.y),
                (box.x, box.y + box.width),
                (box.x + box.width, box.y + box.width)
            ]
            for corner in corners:
                if (start_corner[0] == corner[0] and abs(start_corner[1] - corner[1]) == box.width) or (
                        start_corner[1] == corner[1] and abs(start_corner[0] - corner[0]) == box.width):
                    distance = math.hypot(corner[0] - x, corner[1] - y)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_corner = corner

    return nearest_corner if min_distance <= SNAP_DISTANCE else None


def main(win, width):
    clock = pygame.time.Clock()
    ROWS = 5
    grid = make_grid(ROWS, width)
    players = [Player("Player 1", RED), Player("Player 2", TURQUOISE), Player("Player 3", GREEN)]
    current_player_index = 0

    highlighted_lines_arr = []
    start_corner = None

    running = True

    while running:
        current_player = players[current_player_index]
        box_completed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                start_corner = get_clicked_corner(grid)

            if event.type == pygame.MOUSEBUTTONUP and start_corner:
                end_corner = snap_to_nearest_corner(pygame.mouse.get_pos(), grid, start_corner)

                if end_corner and start_corner != end_corner:
                    if (start_corner, end_corner) not in highlighted_lines_arr and (
                    end_corner, start_corner) not in highlighted_lines_arr:
                        draw_animated_line(win, start_corner, end_corner, highlighted_lines_arr, BASE_EDGE_COLOR)
                        start_corner = None

                        for row in grid:
                            for box in row:
                                if box.is_complete(highlighted_lines_arr) and box.owner is None:
                                    box.claim_box(highlighted_lines_arr, current_player)
                                    box_completed = True

                        if not box_completed:
                            current_player_index = (current_player_index + 1) % len(players)
                start_corner = None

        draw(win, grid, ROWS, width, highlighted_lines_arr, current_player)

        # Handle snapping to nearest corner
        if start_corner and pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            end_corner = snap_to_nearest_corner(mouse_pos, grid, start_corner)
            if end_corner:
                pygame.draw.line(win, current_player.color, start_corner, end_corner, 3)
            else:
                pygame.draw.line(win, current_player.color, start_corner, mouse_pos, 3)

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()


main(WIN, WIDTH)
