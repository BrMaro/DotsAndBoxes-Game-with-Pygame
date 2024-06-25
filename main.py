import pygame

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


class Box:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE  # Initialize with WHITE color
        self.width = width
        self.total_rows = total_rows
        self.owner = None

    def is_complete(self, clicked_corners):
        corners = [
            (self.x, self.y),  # Top-left corner
            (self.x + self.width, self.y),  # Top-right corner
            (self.x, self.y + self.width),  # Bottom-left corner
            (self.x + self.width, self.y + self.width)  # Bottom-right corner
        ]
        return all(corner in [c for c, color in clicked_corners] for corner in corners)

    def claim_box(self, clicked_corners, claiming_player): # player claimer is object rerpesenting the player class
        if self.is_complete(clicked_corners) and self.color == WHITE: # claim only when unclaimed
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


def draw_circles_on_clicked_corners(win, clicked_corners_arr):
    if clicked_corners_arr:
        for corner, color in clicked_corners_arr:
            if corner:
                pygame.draw.circle(win, BLACK, corner, 10)


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


def draw(win, grid, rows, width, clicked_corners, highlighted_lines_arr, current_player):
    print(current_player.name)
    win.fill(WHITE)

    for row in grid:
        for box in row:
            if box.is_complete(clicked_corners):
                box.claim_box(clicked_corners, current_player)
            box.draw_box(win)

    draw_grid(win, rows, width)

    draw_circles_on_clicked_corners(win, clicked_corners)

    for line, color in highlighted_lines_arr:
        start_pos, end_pos = line
        pygame.draw.line(win, color, start_pos, end_pos, 5)


def draw_animated_line(win, start_pos, end_pos, highlighted_lines_arr, color, duration=2):
    steps = int(FPS * duration)
    for i in range(steps):
        alpha = i / steps
        intermediate_pos = (
            start_pos[0] + alpha * (end_pos[0] - start_pos[0]),
            start_pos[1] + alpha * (end_pos[1] - start_pos[1])
        )
        pygame.draw.line(win, BLACK, start_pos, intermediate_pos, 5)
        pygame.display.update()
    highlighted_lines_arr.append(((start_pos, end_pos), BLACK))


def main(win, width):
    clock = pygame.time.Clock()
    players = [Player("Player 1", RED), Player("Player 2", TURQUOISE),Player("Player 3", GREEN)]
    current_player_index = 0

    clicked_corners = []
    highlighted_lines_arr = []

    ROWS = 15
    grid = make_grid(ROWS, width)

    running = True

    while running:
        current_player = players[current_player_index]

        draw(win, grid, ROWS, width, clicked_corners, highlighted_lines_arr, current_player)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # click and only click open corners
            # Rembmer the clicked corners array contains a 2d tuple(corner,BLACK)
            if pygame.mouse.get_pressed()[0] and not ((get_clicked_corner(grid), BLACK) in clicked_corners):
                current_player_index = (current_player_index + 1) % len(players)

                corner = get_clicked_corner(grid)
                if corner and (corner, BLACK) not in clicked_corners:
                    for prev_corner, prev_color in clicked_corners:
                        if prev_corner and (
                                (abs(prev_corner[0] - corner[0]) == grid[0][0].width and prev_corner[1] == corner[1]) or
                                (abs(prev_corner[1] - corner[1]) == grid[0][0].width and prev_corner[0] == corner[0])):
                            draw_animated_line(win, prev_corner, corner, highlighted_lines_arr, BLACK)
                    clicked_corners.append((corner, BLACK))

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()


main(WIN, WIDTH)
