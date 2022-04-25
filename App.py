import os
import sys
import glob
import json
import time
import random

import pygame
from pygame.locals import *

GRID_SIZE = 64
TILE_SIZE = 16
WINDOW_SIZE = GRID_SIZE * TILE_SIZE


class App(object):
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("WFC")
        self.display = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        self.deltaTime = 0.0001
        self.endTime = time.time()

        self.max_recursion_depth = 0

        # Handle modules data loading
        with open("./modules.json", "r") as f:
            self.modules_data = json.load(f)
        for x in range(len(self.modules_data)):
            tmp_neighbors = self.modules_data[x]["neighbors"]
            self.modules_data[x]["neighbors"] = []
            for z in tmp_neighbors:
                self.modules_data[x]["neighbors"].append(
                    self.get_module_index(z))
        # Load sprites
        self.sprites = []
        self.load_sprites()
        # Initialize map
        self.map = []
        for x in range(GRID_SIZE):
            self.map.append([set([x for x in range(len(self.modules_data))])] *
                            GRID_SIZE)
        # Perform WFC on the map
        self.remaining_cells_cound = GRID_SIZE * GRID_SIZE
        self.waveshift_function_collapse()
        print(self.max_recursion_depth)

    def launch(self):
        """ For now, is only used to keep the window opened """
        while not self.handle_loop():
            self.display_map()

#########################################
# WFC functions
    def waveshift_function_collapse(self):
        while self.is_not_finished():
            print("==========")
            # Update the display so we can see the algorithm working in real time
            self.handle_loop()
            # Get the next cell to update
            cell = self.get_minimal_entropy_cell()
            # Randomly choose a module from the possible modules at this position
            module = random.choice(list(self.map[cell.y][cell.x]))
            self.map[cell.y][cell.x] = [module]
            # Display the change
            self.display.blit(
                self.sprites[list(self.map[cell.y][cell.x])[0]],
                (cell.x * TILE_SIZE, cell.y * TILE_SIZE),
            )
            # Now propagate to neighbors
            self.update_possibilities(cell, 0)

    def update_possibilities(self, cell, depth):
        print("depth", depth)
        if depth > self.max_recursion_depth:
            self.max_recursion_depth = depth
        # End of recursion conditions
        to_be_updated_neighbors = []
        # if depth == 0:
        #     return
        # Create a list of all possible modules based on the ones in the selected cell
        possible_modules = set()
        cell_modules = self.map[cell.y][cell.x]
        for cell_module in cell_modules:
            for elem in self.modules_data[cell_module]["neighbors"]:
                possible_modules.add(elem)
            possible_modules.add(cell_module)
        # Get neighboring cells
        neighbors = self.get_neighbors(cell)
        # Remove all non compatible modules in the neighbors
        for neighbor in neighbors:
            tmp = set()
            for neighbor_possible_module in self.map[neighbor.y][neighbor.x]:
                if neighbor_possible_module in possible_modules:
                    tmp.add(neighbor_possible_module)
            # If something has changed (a collapse has been made) add the neighbor
            # to the to-be-updated neighbors list
            if set(self.map[neighbor.y][neighbor.x]) != tmp:
                to_be_updated_neighbors.append(neighbor)
                self.map[neighbor.y][neighbor.x] = tmp
        if len(to_be_updated_neighbors) == 0:
            print("not to neighbors")
        # Propagate the collapse to neighbor which had changes
        for neighbor in to_be_updated_neighbors:
            self.update_possibilities(neighbor, depth + 1)

    def get_minimal_entropy_cell(self):
        """ Returns the cell with the lowest entropy of all, if multiple cells
        have the same entropy, choose one at random """
        minimal_entropy = len(self.modules_data)
        minimal_entropy_cells = []
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                # Ignore already finished cells
                if len(self.map[y][x]) < 2:
                    continue
                # Lower entropy found
                elif len(self.map[y][x]) < minimal_entropy:
                    minimal_entropy = len(self.map[y][x])
                    minimal_entropy_cells = [Position(y, x)]
                # Add to the list of lowest entropy cells
                elif len(self.map[y][x]) == minimal_entropy:
                    minimal_entropy_cells.append(Position(y, x))
        # Choose a random minimum entropy cell
        return random.choice(minimal_entropy_cells)

#########################################
# Utility functions
    def get_neighbors(self, cell):
        """ Returns all valid neighbors with an entropy > 1 """
        neighbors = []
        if cell.y > 0:  # Up
            neighbors.append(Position(cell.y - 1, cell.x))
        if cell.y < GRID_SIZE - 1:  # Down
            neighbors.append(Position(cell.y + 1, cell.x))
        if cell.x > 0:  # Left
            neighbors.append(Position(cell.y, cell.x - 1))
        if cell.x < GRID_SIZE - 1:  # Right
            neighbors.append(Position(cell.y, cell.x + 1))
        # Remove already collapsed neighbors, so we don't iterate twice on them
        out = []
        for neighbor in neighbors:
            if len(self.map[neighbor.y][neighbor.x]) > 1:
                out.append(neighbor)
        return out

    def get_module_index(self, module_name):
        """ Returns the index associated to the module name, exit if not found"""
        for idx, module in enumerate(self.modules_data):
            if module_name == module["module_name"]:
                return idx
        exit(84)

    def is_not_finished(self):
        """ Returns true if at least one cell has an entropy > 1
        (meaning we should keep the WFC running) """
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if len(self.map[y][x]) != 1:
                    return True
        return False

#########################################
# Display functions
    def display_map(self):
        pass
        # for y in range(GRID_SIZE):
        # for x in range(GRID_SIZE):
        # if len(self.map[y][x]) == 1:
        #     self.display.blit(self.sprites[list(self.map[y][x])[0]], (x*TILE_SIZE, y*TILE_SIZE))

    def load_sprites(self):
        for module in self.modules_data:
            tmp_sprite = pygame.image.load(
                f"""./assets/{module["sprite_name"]}""")
            # Transform it to a pygame friendly format (quicker drawing)
            tmp_sprite.convert()
            tmp_sprite = pygame.transform.scale(tmp_sprite,
                                                (TILE_SIZE, TILE_SIZE))
            self.sprites.append(tmp_sprite)

    def handle_loop(self):
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        delta = time.time() - self.endTime
        if delta < self.deltaTime:
            time.sleep(self.deltaTime - delta)
        self.endTime = time.time()


class Position(object):
    def __init__(self, y, x):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"x:{self.x} y:{self.y}"


if __name__ == "__main__":
    app = App()
    app.launch()
