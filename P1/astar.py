# %% [markdown]
# # Dependencies and Constants

# %%

import sys


import pygame
import math
import heapq
import random

#colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)  
GREY = (200, 200, 200)

ROWS, COLS = 20, 20
WIDTH, HEIGHT = 600, 600
CELL_SIZE = WIDTH // COLS

DIAGONAL_DISTANCE = math.sqrt(WIDTH**2 + HEIGHT**2)
MAX_RISK = 0.1 * DIAGONAL_DISTANCE

# %% [markdown]
# # Class Node

# %%

class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = col * CELL_SIZE
        self.y = row * CELL_SIZE
        self.color = WHITE
        self.neighbors = []
        self.risk = 0  
        self.parent = None

    def is_start(self):
        return self.color == GREEN

    def is_end(self):
        return self.color == BLUE

    def is_barrier(self):
        return self.color == BLACK

    def is_risky(self):
        return self.color == YELLOW

    def is_waypoint(self):
        return self.color == ORANGE

    def reset(self):
        self.color = WHITE
        self.risk = 0

    def make_start(self):
        self.color = GREEN

    def make_end(self):
        self.color = BLUE

    def make_barrier(self):
        self.color = BLACK

    def make_risky(self):
        self.color = YELLOW
        self.risk = random.uniform(0.1, MAX_RISK)  #penalizacion camino

    def make_waypoint(self):
        self.color = ORANGE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, CELL_SIZE, CELL_SIZE))
        if self.is_barrier():
            pygame.draw.line(win, RED, (self.x, self.y), (self.x + CELL_SIZE, self.y + CELL_SIZE), 3)
            pygame.draw.line(win, RED, (self.x + CELL_SIZE, self.y), (self.x, self.y + CELL_SIZE), 3)
        elif self.is_risky():
            pygame.draw.polygon(win, BLACK, [(self.x + CELL_SIZE // 2, self.y + 5), 
                                             (self.x + 5, self.y + CELL_SIZE - 5), 
                                             (self.x + CELL_SIZE - 5, self.y + CELL_SIZE - 5)], 2)

    def update_neighbors(self, grid):
        self.neighbors = []
        directions = [
            (0, 1), (0, -1), (1, 0), (-1, 0),  #ortogonales
            (1, 1), (-1, -1), (1, -1), (-1, 1)  #diagonales
        ]
        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            if 0 <= r < ROWS and 0 <= c < COLS and not grid[r][c].is_barrier():
                self.neighbors.append(grid[r][c])


# %% [markdown]
# # Aux Functions

# %%
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def reconstruct_path(current, draw):
    while current.parent:
        current = current.parent
        current.color = (0, 255, 255)  #color ruta
        draw()

def a_star(draw, grid, start, end):
    count = 0
    open_set = []
    heapq.heappush(open_set, (0, count, start))
    came_from = {}

    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h((start.row, start.col), (end.row, end.col))

    open_set_hash = {start}

    while open_set:
        current = heapq.heappop(open_set)[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(current, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            move_cost = math.sqrt((neighbor.row - current.row) ** 2 + (neighbor.col - current.col) ** 2)  #1 para ortogonal, sqrt(2) para diagonal
            temp_g_score = g_score[current] + move_cost + neighbor.risk  #penal

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h((neighbor.row, neighbor.col), (end.row, end.col))
                neighbor.parent = current

                if neighbor not in open_set_hash:
                    count += 1
                    heapq.heappush(open_set, (f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)

        draw()
    return False

def make_grid():
    return [[Node(i, j) for j in range(COLS)] for i in range(ROWS)]

def draw_grid(win):
    for i in range(ROWS):
        pygame.draw.line(win, GREY, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE))
        for j in range(COLS):
            pygame.draw.line(win, GREY, (j * CELL_SIZE, 0), (j * CELL_SIZE, HEIGHT))

def draw(win, grid, state):

    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid(win)
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Mode: {state.capitalize()}, R = Risk, W = Waypoint, C = Clear", True, BLACK)
    win.blit(text, (10, 10))
    pygame.display.update()

def get_clicked_pos(pos):
    x, y = pos
    row = y // CELL_SIZE
    col = x // CELL_SIZE
    return row, col

def find_path_with_waypoints(draw, grid, start, waypoints, end):
    all_points = [start] + waypoints + [end]
    for i in range(len(all_points) - 1):
        a_star(draw, grid, all_points[i], all_points[i + 1])
        for row in grid:  
            for node in row:
                node.parent = None

# %% [markdown]
# # Main

# %%
pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Algoritmo A*")



def main():
    grid = make_grid()
    start = None
    end = None
    waypoints = []
    running = True
    state = "start"

    while running:
        draw(WIN, grid, state)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if pygame.mouse.get_pressed()[0]:  #click izquierdo
                row, col = get_clicked_pos(pygame.mouse.get_pos())
                node = grid[row][col]
                if not start:
                    start = node
                    start.make_start()
                    state = "target"
                elif not end and node != start:
                    end = node
                    end.make_end()
                    state = "barrier"
                elif node != end and node != start:
                    node.make_barrier()
                    state = "barrier"

            elif pygame.mouse.get_pressed()[2]:  #click derecho
                row, col = get_clicked_pos(pygame.mouse.get_pos())
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                    state = "start"
                elif node == end:
                    end = None
                    state = "target"
                elif node in waypoints:
                    waypoints.remove(node)
                    state = "barrier"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    find_path_with_waypoints(lambda: draw(WIN, grid, state), grid, start, waypoints, end)

                if event.key == pygame.K_w:  #waypoint
                    row, col = get_clicked_pos(pygame.mouse.get_pos())
                    if grid[row][col] != start and grid[row][col] != end:
                        grid[row][col].make_waypoint()
                        waypoints.append(grid[row][col])

                if event.key == pygame.K_r:  #celda con riesgo
                    row, col = get_clicked_pos(pygame.mouse.get_pos())
                    if grid[row][col] != start and grid[row][col] != end:
                        grid[row][col].make_risky()

                if event.key == pygame.K_c:  #borrar todo
                    grid = make_grid()
                    start, end = None, None
                    waypoints = []
                    state = "start"

    pygame.quit()

main()



