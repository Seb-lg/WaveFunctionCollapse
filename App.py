import time
import random
import json
import glob
import os

import pygame
from pygame.locals import *

from config import *

GRID_SIZE = 128
TILE_SIZE = 16
WINDOW_WIDTH = GRID_SIZE * TILE_SIZE
WINDOW_HEIGHT = GRID_SIZE * TILE_SIZE

class Position(object):
    def __init__(self,y,x):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'x:{self.x} y:{self.y}'

class App(object):
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Rota')
        self.display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.deltaTime = 0.0001
        self.endTime = time.time()


        with open("./modules.json", "r") as f:
            self.modules_data = json.load(f)

        for x in range(len(self.modules_data)):
            tmp_neighbors = self.modules_data[x]["neighbors"]
            self.modules_data[x]["neighbors"] = []
            for z in tmp_neighbors:
                self.modules_data[x]["neighbors"].append(self.get_module_index(z))

        self.sprites = []
        self.load_sprites()

        self.map = []
        for x in range(GRID_SIZE):
            self.map.append([set([x for x in range(len(self.modules_data))])]*GRID_SIZE)
        self.waveshift_function_collapse()

        
    def get_module_index(self, module_name):
        for idx, module in enumerate(self.modules_data):
            if module_name == module["module_name"]:
                return idx
        exit(84)

    def waveshift_function_collapse(self):

        while self.is_not_finished():
            self.handle_loop()
            self.display_map()
            cell = self.get_minimal_entropy_cell()
            module = random.choice(list(self.map[cell.y][cell.x]))
            self.map[cell.y][cell.x] = [module]
            self.display.blit(self.sprites[list(self.map[cell.y][cell.x])[0]], (cell.x*TILE_SIZE, cell.y*TILE_SIZE))

            # now propagate TNE COLLAPSE to neighbors
            self.update_possibilities(cell, 3)

            # input("1")

    def update_possibilities(self, cell, depth):
        if depth == 0:
            return
        possible_modules = set()
        cell_modules = self.map[cell.y][cell.x]
        flag = False

        for cell_module in cell_modules:
            for elem in self.modules_data[cell_module]["neighbors"] :
                possible_modules.add(elem)
            possible_modules.add(cell_module)
        # input("2")
        neighbors = self.get_neighbors(cell)
        for neighbor in neighbors:
            tmp = set()
            for neighbor_possible_module in self.map[neighbor.y][neighbor.x]:
                if neighbor_possible_module in possible_modules:
                    tmp.add(neighbor_possible_module)

            if set(self.map[neighbor.y][neighbor.x]) != tmp:
                flag = True
            self.map[neighbor.y][neighbor.x] = tmp
        
        if flag:
            for neighbor in neighbors:
                self.update_possibilities(neighbor, depth - 1)
            
    def get_minimal_entropy_cell(self):
        minimal_entropy = len(self.modules_data)
        minimal_entropy_cells = []
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if len(self.map[y][x]) < 2:
                    continue
                elif len(self.map[y][x]) < minimal_entropy:
                    minimal_entropy = len(self.map[y][x])
                    minimal_entropy_cells = [Position(y,x)]
                elif len(self.map[y][x]) == minimal_entropy:
                    minimal_entropy_cells.append(Position(y,x))
        return random.choice(minimal_entropy_cells)

    def is_not_finished(self):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if len(self.map[y][x]) != 1:
                    return True
        return False

    def get_neighbors(self, cell):
        neighbors = []
        ##case up
        if cell.y > 0:
            neighbors.append(Position(cell.y-1, cell.x))
        ##case down
        if cell.y < GRID_SIZE - 1:
            neighbors.append(Position(cell.y+1, cell.x))
        ##case left
        if cell.x > 0:
            neighbors.append(Position(cell.y, cell.x-1))
        ##case right
        if cell.x < GRID_SIZE - 1:
            neighbors.append(Position(cell.y, cell.x+1))

        out = []
        for neighbor in neighbors:
            if len(self.map[neighbor.y][neighbor.x]) > 1:
                out.append(neighbor)

        return out


    def launch(self):
        while not self.handle_loop():
            self.display_map()

    
    def display_map(self):
        pass
        # for y in range(GRID_SIZE):
            # for x in range(GRID_SIZE):
                # if len(self.map[y][x]) == 1: 
                #     self.display.blit(self.sprites[list(self.map[y][x])[0]], (x*TILE_SIZE, y*TILE_SIZE))


    def load_sprites(self):
        for module in self.modules_data:
            tmp_sprite = pygame.image.load(f"""./assets/{module["sprite_name"]}""")
            # Transform it to a pygame friendly format (quicker drawing)
            tmp_sprite.convert()
            tmp_sprite = pygame.transform.scale(tmp_sprite, (TILE_SIZE, TILE_SIZE))
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