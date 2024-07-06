import pygame
import random
import math

WIDTH = 1000
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Dot&Dot")
FPS = 30

pygame.font.init()

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
LEFT_MARGIN = 10
RIGHT_MARGIN = 10
BOTTOM_MARGIN = 10
TOP_STATS_HEIGHT = 100


class Box:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = LEFT_MARGIN + row * width
        self.y = TOP_STATS_HEIGHT + col * width
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

        return all(
            edge in highlighted_lines or ((edge[0][1], edge[0][0]), BASE_EDGE_COLOR) in highlighted_lines for edge in
            edges)

    def claim_box(self, highlighted_lines, claiming_player):
        if self.is_complete(highlighted_lines) and self.color == BACKGROUND_COLOR:
            self.owner = claiming_player
            self.color = claiming_player.color

    def get_owner(self):
        return self.owner

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
    gap = (width - LEFT_MARGIN - RIGHT_MARGIN) // rows  # Adjust the gap based on the margins
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            box = Box(i, j, gap, rows)
            grid[i].append(box)
    return grid


def draw_grid(win, rows, width):
    gap = (width - LEFT_MARGIN - RIGHT_MARGIN) // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (LEFT_MARGIN, TOP_STATS_HEIGHT + i * gap),
                         (width - RIGHT_MARGIN, TOP_STATS_HEIGHT + i * gap))
    for j in range(rows):
        pygame.draw.line(win, GREY, (LEFT_MARGIN + j * gap, TOP_STATS_HEIGHT),
                         (LEFT_MARGIN + j * gap, width - BOTTOM_MARGIN))


def draw_rotating_dotted_circle(win, center, radius):
    num_dots = 20
    dot_radius = 2
    time = pygame.time.get_ticks() / 1000
    angle = math.radians(360 / num_dots)

    for i in range(num_dots):
        offset_angle = angle * i + time * math.pi  # Rotate based on time
        dot_x = center[0] + radius * math.cos(offset_angle)
        dot_y = center[1] + radius * math.sin(offset_angle)
        pygame.draw.circle(win, BLACK, (int(dot_x), int(dot_y)), dot_radius)


def draw_circles(win, grid, highlighted_corners=None):
    if highlighted_corners is None:
        highlighted_corners = []

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
                if corner in highlighted_corners:
                    draw_rotating_dotted_circle(win, corner, VERTEX_RADIUS + 3)



def get_neighbouring_corners(corner, grid):
    x, y = corner
    neighbours = []

    for row in grid:
        for box in row:
            corners = [
                (box.x, box.y),
                (box.x + box.width, box.y),
                (box.x, box.y + box.width),
                (box.x + box.width, box.y + box.width)
            ]
            for c in corners:
                if (corner[0] == c[0] and abs(corner[1] - c[1]) == box.width) or (
                        corner[1] == c[1] and abs(corner[0] - c[0]) == box.width):
                    neighbours.append(c)
    return neighbours


def draw(win, grid, rows, width, highlighted_lines, current_player, highlighted_corners=None, players=None):
    win.fill(BACKGROUND_COLOR)
    for row in grid:
        for box in row:
            box.claim_box(highlighted_lines, current_player)
            box.draw_box(win)

    draw_grid(win, rows, width)
    draw_circles(win, grid, highlighted_corners)
    for line, color in highlighted_lines:
        start_pos, end_pos = line
        pygame.draw.line(win, color, start_pos, end_pos, EDGE_THICKNESS)

    # Calculate player scores
    scores = {player: 0 for player in players}
    for row in grid:
        for box in row:
            if box.get_owner() is not None:
                scores[box.get_owner()] += 1

    # Draw player scores
    font = pygame.font.SysFont('Arial', 24)
    scores_text = "Scores: " + " - ".join([f'{player.name}: {scores[player]}' for player in players])
    text = font.render(scores_text, True, BLACK)
    win.blit(text, (10, 10))


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
    ROWS = 10
    grid = make_grid(ROWS, width)
    players = [Player("Player 1", RED), Player("Player 2", TURQUOISE), Player("Player 3", GREEN)]
    current_player_index = 0

    highlighted_lines_arr = []
    start_corner = None
    highlighted_corners = []

    running = True

    while running:
        current_player = players[current_player_index]
        box_completed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                start_corner = get_clicked_corner(grid)
                if start_corner:
                    highlighted_corners = get_neighbouring_corners(start_corner, grid)

            if event.type == pygame.MOUSEBUTTONUP and start_corner:
                end_corner = snap_to_nearest_corner(pygame.mouse.get_pos(), grid, start_corner)

                if end_corner and start_corner != end_corner:
                    if (start_corner, end_corner) not in highlighted_lines_arr and (
                            end_corner, start_corner) not in highlighted_lines_arr:
                        draw_animated_line(win, start_corner, end_corner, highlighted_lines_arr, BASE_EDGE_COLOR)
                        start_corner = None
                        highlighted_corners = []

                        for row in grid:
                            for box in row:
                                if box.is_complete(highlighted_lines_arr) and box.owner is None:
                                    box.claim_box(highlighted_lines_arr, current_player)
                                    box_completed = True

                        if not box_completed:
                            current_player_index = (current_player_index + 1) % len(players)
                start_corner = None
                highlighted_corners = []

        draw(win, grid, ROWS, width, highlighted_lines_arr, current_player, highlighted_corners, players)

        # Handle snapping to nearest corner and drawing guide line
        if start_corner and pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            end_corner = snap_to_nearest_corner(mouse_pos, grid, start_corner)
            if end_corner:
                pygame.draw.line(win, current_player.color, start_corner, end_corner, 3)
            else:
                pygame.draw.line(win, current_player.color, start_corner, mouse_pos, 3)

        draw_circles(win, grid, highlighted_corners)

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()


main(WIN, WIDTH)
