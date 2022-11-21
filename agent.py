import torch
import random 
import numpy as np
from collections import deque
from mainAI import *
from model import Linear_Qnet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LEARNING_RATE = 0.001

class Agent:
    
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0      # randomness
        self.gamma = 0.1     # discount rate (usually must be smaller than 1)
        self.memory = deque(maxlen=MAX_MEMORY)      #popleft()
        self.model =  Linear_Qnet(4, 256, 4)
        self.trainer = QTrainer(self.model, lr=LEARNING_RATE, gamma=self.gamma)

    def get_state(self, game):
        #movement 
        dir_l = game.block.move_direction == Direction.LEFT
        dir_r = game.block.move_direction == Direction.RIGHT
        dir_u = game.block.move_direction == Direction.UP
        dir_d = game.block.move_direction == Direction.DOWN
        dir_s = game.block.move_direction == Direction.STAY

        state = [
            #movement
            #dir_l,
            #dir_r,
            #dir_u,
            #dir_d,
            #dir_s,

            # score location
            game.score_square.square.x < game.block.block.x,     # left of block
            game.score_square.square.x > game.block.block.x,     # right of block
            game.score_square.square.y < game.block.block.y,     # up of block
            game.score_square.square.y > game.block.block.y,     # down of block
            # score proximity ( any 2 signals of this will state North-East, North-West, etc)
            #game.score_square.square.x == game.block.block.x + 32,    # right of block
            #game.score_square.square.x == game.block.block.x - 32,    # left of block
            #game.score_square.square.y == game.block.block.y + 32,    # up of block
            #game.score_square.square.y == game.block.block.y - 32,    # down of block

            # poison location
            #game.poison_square.square.x < game.block.block.x,     # left of block
            #game.poison_square.square.x > game.block.block.x,     # right of block
            #game.poison_square.square.y < game.block.block.y,     # up of block
            #game.poison_square.square.y > game.block.block.y,     # down of block
            # poison proximity ( any 2 signals of this will state North-East, North-West, etc)
            #game.poison_square.square.x == game.block.block.x + 32,    # right of block
            #game.poison_square.square.x == game.block.block.x - 32,    # left of block
            #game.poison_square.square.y == game.block.block.y + 32,    # up of block
            #game.poison_square.square.y == game.block.block.y - 32,    # down of block

            # proximity range of squares
            #game.poison_square.square.x < game.score_square.square.x,     # poison is more left than score
            #game.poison_square.square.x > game.score_square.square.x,     # poison is more right than score
            #game.poison_square.square.y < game.score_square.square.y,     # poison is more up than score
            #game.poison_square.square.y > game.score_square.square.y     # poison is more down than score

            ]
        return np.array(state, dtype=int)


    def remember(self, state, action, reward, next_state, done):
        # reward can be either 0,10,-10
        # done is boolean True / False
        self.memory.append((state, action, reward, next_state, done)) # pop left is max memory is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # return list of tupple
        else:
            mini_sample = self.memory
        
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)


    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):

        # Implemented Decayed Epsilon Greedy method
        # handling trade-off exploration / exploitation
        # make random moves in early stages to make agent learn about environement

        # after game 80th, no more random moves made
        self.epsilon = 40 - self.n_games
        final_move = [0,0,0,0]
        if random.randint(0,200) < self.epsilon:
            move = random.randint(0,3)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        
        return final_move  

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0

    agent = Agent()
    game = GameAI()

    while True:

        # get old state
        state_old = agent.get_state(game)

        # get move (making prediction/random move)
        final_move = agent.get_action(state_old)

        # perform move and get new state
        # score is not model parameter, it is for self-evaluation
        reward, done , score = game.run(final_move)
        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train the long memory, plot result
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print("Game", agent.n_games, "Score", score, 'Record: ', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

            
if __name__ == '__main__':
    train()
     