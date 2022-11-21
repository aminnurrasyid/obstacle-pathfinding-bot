#       LOG
#       1. quit, restart options
#
#       PROBLEM
#       1. second thread: thread timer explicitly run after game ended
#       Future update: poision square, big score square
#
#       resetfunction
#       reward
#       play(action) -> direction
#       game_iteration


from time import *
from enum import Enum
import numpy as np
import threading
import pygame
import random
import os

class Direction(Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3 
    DOWN = 4
    STAY = 5

WIDTH = 512
HEIGHT = 512
FPS = 10
MAX_TIME = 10
MAX_FRAME_ITERATION = 100

WHITE = (255,255,255)
BLACK = (0,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)
SAND = (241,161,12)

BLOCK_SIDE = 32 
SQUARE_SIDE = 32
VELOCITY = 32

RANGE_OF_SQUARE = 15

#       IMAGE COLLECTIONS
MAN_IMAGE = pygame.image.load(os.path.join('Assets', 'man.png'))
MAN = pygame.transform.scale(MAN_IMAGE, (BLOCK_SIDE, BLOCK_SIDE))

CACTUSFRUIT_IMAGE = pygame.image.load(os.path.join('Assets', 'goblin.png'))
CACTUSFRUIT = pygame.transform.scale(CACTUSFRUIT_IMAGE, (BLOCK_SIDE, BLOCK_SIDE))

CHICKEN_IMAGE = pygame.image.load(os.path.join('Assets', 'coin.png'))
CHICKEN = pygame.transform.scale(CHICKEN_IMAGE, (BLOCK_SIDE, BLOCK_SIDE))

FIELD = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'field.png')), (WIDTH, HEIGHT))


#       LIST OF EVENTS
BLUE_COLLIDE = pygame.USEREVENT + 1
GREEN_COLLIDE = pygame.USEREVENT + 2 


class PoisonSquare:
    def __init__(self, surface):
        self.parent_surface = surface
        self.square = pygame.Rect(self.multiple_placement(BLOCK_SIDE, RANGE_OF_SQUARE), self.multiple_placement(BLOCK_SIDE, RANGE_OF_SQUARE), SQUARE_SIDE, SQUARE_SIDE)
        self.square_image = CACTUSFRUIT

    def multiple_placement(self, multiple, range):
        random_range = random.randint(0,range)
        return multiple*random_range

    def draw(self):
        # draw cactus on top of poison square
        self.parent_surface.blit(self.square_image, (self.square.x, self.square.y))
        #pygame.draw.rect(self.parent_surface, GREEN, self.square)

    def check_overlapping(self, score_square):
        if self.square.colliderect(score_square.square):
            self.square.x = self.multiple_placement(BLOCK_SIDE, RANGE_OF_SQUARE)
            self.square.y = self.multiple_placement(BLOCK_SIDE, RANGE_OF_SQUARE)
        self.draw()

    def handle_collision(self, block, score_square):
        if self.square.colliderect(block.block):
            self.square.x = self.multiple_placement(BLOCK_SIDE, RANGE_OF_SQUARE)
            self.square.y = self.multiple_placement(BLOCK_SIDE, RANGE_OF_SQUARE)
            pygame.event.post(pygame.event.Event(GREEN_COLLIDE))

        self.check_overlapping(score_square)
        self.draw()

class ScoreSquare:
    def __init__(self, surface):
        self.parent_surface = surface
        self.square = pygame.Rect(self.multiple_placement(BLOCK_SIDE, RANGE_OF_SQUARE),self.multiple_placement(BLOCK_SIDE, RANGE_OF_SQUARE),SQUARE_SIDE,SQUARE_SIDE)
        self.square_image = CHICKEN

    def multiple_placement(self, multiple, range):
        random_range = random.randint(0,range)
        return multiple*random_range

    def draw(self):
        # draw chicken on top of score square
        self.parent_surface.blit(self.square_image, (self.square.x, self.square.y))
        #pygame.draw.rect(self.parent_surface, BLUE, self.square)

    def check_overlapping(self, poison_square):
        if self.square.colliderect(poison_square.square):
            self.square.x = self.multiple_placement(BLOCK_SIDE, RANGE_OF_SQUARE)
            self.square.y = self.multiple_placement(BLOCK_SIDE, RANGE_OF_SQUARE)
        self.draw()

    def handle_collision(self, block, poison_square):
        if self.square.colliderect(block.block):
            self.square.x = self.multiple_placement(BLOCK_SIDE, RANGE_OF_SQUARE)
            self.square.y = self.multiple_placement(BLOCK_SIDE, RANGE_OF_SQUARE)
            pygame.event.post(pygame.event.Event(BLUE_COLLIDE))

        #self.check_overlapping(poison_square)
        self.draw()


class Block:
    def __init__(self, surface):
        self.parent_surface = surface
        self.block = pygame.Rect(0,0,BLOCK_SIDE,BLOCK_SIDE)
        self.block_image = MAN
        self.move_direction = Direction.STAY

    def draw(self):
        self.parent_surface.blit(FIELD, (0,0))

        # drawing a man on the block
        self.parent_surface.blit(self.block_image, (self.block.x,self.block.y))
        #pygame.draw.rect(self.parent_surface, BLACK, self.block)

    def walk(self, action):

        if np.array_equal(action, [1, 0, 0, 0]):
            self.move_direction =  Direction.LEFT    
        elif np.array_equal(action, [0, 1, 0, 0]):
            self.move_direction =  Direction.RIGHT   
        elif np.array_equal(action, [0, 0, 1, 0]):
            self.move_direction =  Direction.UP      
        elif np.array_equal(action, [0, 0, 0, 1]):
            self.move_direction =  Direction.DOWN     

        if  self.move_direction == Direction.LEFT and self.block.x > 0:   # LEFT 
            self.block.x -= VELOCITY
        elif self.move_direction == Direction.RIGHT and self.block.x + BLOCK_SIDE < WIDTH:   # RIGHT
            self.block.x += VELOCITY
        elif self.move_direction == Direction.UP and self.block.y > 0:   # UP
            self.block.y -= VELOCITY
        elif self.move_direction == Direction.DOWN and self.block.y + BLOCK_SIDE < HEIGHT:   # DOWN
            self.block.y += VELOCITY
        else:
            self.move_direction = Direction.STAY 
        
        self.draw()


class GameAI:
    def __init__(self):

        pygame.init()
        self.title = pygame.display.set_caption("Time Chaser")
        self.surface = pygame.display.set_mode((WIDTH,HEIGHT))
        self.clock = pygame.time.Clock()

        self.reset()

    def reset(self):
        self.score = 0

        self.block = Block(self.surface)
        self.block.draw()

        self.score_square = ScoreSquare(self.surface)
        self.score_square.draw()

        #self.poison_square = PoisonSquare(self.surface)
        #self.poison_square.draw()

        self.frame_iteration = 0

        #global threadtimer 
        #threadtimer = MAX_TIME
        #countdown_thread = threading.Thread(target=self.countdown)
        #countdown_thread.start()


    def play(self, action):
        self.block.walk(action) 
        self.score_square.handle_collision(self.block,None)
        #self.poison_square.handle_collision(self.block,self.score_square)
        pygame.display.flip()

    #def countdown(self):
    #    global threadtimer 
    #    global stop_signal
    #    while threadtimer>0 and stop_signal:
    #        threadtimer -= 1
    #        sleep(1)

    def run(self, action):

        self.frame_iteration += 1
        reward = 0
        self.game_over = False 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            
        self.play(action)

        if self.frame_iteration > MAX_FRAME_ITERATION:
            self.game_over = True
            reward = -10
            return reward, self.game_over, self.score

        for event in pygame.event.get():
            if event.type == BLUE_COLLIDE:
                self.score += 1
                reward = 10
                self.frame_iteration -= 80
            #if event.type == GREEN_COLLIDE:
            #    self.game_over = True
            #    reward = -10
            #    #self.frame_iteration += 100
            #    return reward, self.game_over, self.score

        self.game_over = False
        self.clock.tick(FPS)
        return reward, self.game_over, self.score 