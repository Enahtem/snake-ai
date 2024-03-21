# Need to rework genetic algorithm method
# Referece and follow https://www.youtube.com/watch?v=zIkBYwdkuTk
# Imports

import pygame
import random



import numpy as np
import random
import copy

# Variables
speed=100
window_size=(800,600)
block_size=20

hidden_nodes=16
hidden_layers=2

mutation_rate=0.05

is_human_playing=False
class NeuralNetwork:
    def __init__(self, input, hidden, output, hidden_layers):
        # Constructor method
        self.input_nodes=input
        self.hidden_nodes=hidden
        self.output_nodes=output
        self.hidden_layers=hidden_layers

        self.weights = []
        self.weights.append(np.random.uniform(-1, 1, size=(self.hidden_nodes, self.input_nodes + 1)))
        for i in range(1, self.hidden_layers + 1):
            self.weights.append(np.random.uniform(-1, 1, size=(self.hidden_nodes, self.hidden_nodes + 1)))
        self.weights.append(np.random.uniform(-1, 1, size=(self.output_nodes, self.hidden_nodes + 1)))


    def mutate(self, mutation_rate=mutation_rate):
        clone=self.clone()
        for n in range (len(clone.weights)):
            for i in range(clone.weights[n].shape[0]):
                for j in range(clone.weights[n].shape[1]):
                    if(random.random()<mutation_rate):
                        clone.weights[n][i][j]+=np.random.normal(0,0.2)
                        if (clone.weights[n][i][j]>1):
                            clone.weights[n][i][j]=1
                        elif (clone.weights[n][i][j]<-1):
                            clone.weights[n][i][j]=-1
        return clone

    def calculate(self, inputs):
        output = np.append(inputs, 1)
        for i in range(self.hidden_layers + 2):
            output = np.maximum(np.dot(self.weights[i], output), 0)
            if i != self.hidden_layers + 1:
                output = np.append(output, 1)
        return output

    def clone(self):
        clone = NeuralNetwork(self.input_nodes, self.hidden_nodes, self.output_nodes, self.hidden_layers)
        clone.weights = copy.deepcopy(self.weights)
        return clone

class Food:
    def __init__(self):
        x = random.randint(0, (window_size[0]-block_size )//block_size )*block_size 
        y = random.randint(0, (window_size[1]-block_size )//block_size )*block_size
        self.position = (x, y)
    def new_food(self, snake):
        x = random.randint(0, (window_size[0]-block_size )//block_size )*block_size 
        y = random.randint(0, (window_size[1]-block_size )//block_size )*block_size
        self.position = (x, y)
        if self.position in snake.get_position():
            self.new_food(snake)
    def get_position(self):
        return self.position


class Snake:
    def __init__(self, isHumanPlaying, neuralnet):
        self.head = (window_size[0]/2, window_size[1]/2)
        self.position = [self.head, (self.head[0]-block_size, self.head[1]), (self.head[0]-(2*block_size), self.head[1])]
        self.alive=True
        self.score=0
        self.neuralnet = neuralnet
        self.isHumanPlaying=isHumanPlaying
        self.direction='r'
    def move(self, food):
        x = self.head[0]
        y = self.head[1]
        if self.direction == 'r':
            x += block_size
        elif self.direction == 'l':
            x -= block_size
        elif self.direction == 'd':
            y += block_size
        elif self.direction == 'u':
            y -= block_size
            
        self.head = (x, y)
        self.position.insert(0,self.head)

        if self.head[0] > window_size[0] - block_size or self.head[0] < 0 or self.head[1] > window_size[1] - block_size or self.head[1] < 0:
            self.alive=False
        if self.head in self.position[1:]:
            self.alive=False
        
        if self.head == food.get_position():
            self.score += 1
            food.new_food(self)
        else:
            self.position.pop()
    def get_position(self):
        return self.position
    def sense(self, food):
            senses=[0]*24
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
            for i in range (len(directions)):
                    dx, dy = directions[i]
                    x, y = self.head[0] + dx*block_size, self.head[1] + dy*block_size
                    distance=1
                    wall_found=False
                    food_found=False
                    tail_found=False
                    while 0<=x<window_size[0] and 0<=y<window_size[1]:
                        if wall_found==False and (x==0 or x==window_size[0]-block_size or y==0 or y==window_size[1]-block_size):
                            wall_found=True
                            senses[i*3]=distance
                        if food_found==False and (x==food.get_position()[0] and y==food.get_position()[1]):
                            food_found=True
                            senses[i*3+1]=distance
                        if tail_found==False and (x==self.position[-1][0] and y==self.position[-1][1]):
                            tail_found=True
                            senses[i*3+2]=distance
                        x += dx*block_size
                        y += dy*block_size
                        distance+=1
                    if food_found==False:
                        senses[i*3+1]=0
                    if tail_found==False:
                        senses[i*3+2]=0
            return senses
    def think(self, food):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and is_human_playing:
                if event.key == pygame.K_LEFT:
                    self.direction= 'l'
                elif event.key == pygame.K_RIGHT:
                    self.direction= 'r'
                elif event.key == pygame.K_UP:
                    self.direction= 'u'
                elif event.key == pygame.K_DOWN:
                    self.direction= 'd'
        if not is_human_playing:
            thought=self.neuralnet.calculate(self.sense(food)).tolist()
            thought_direction=thought.index(max(thought))
            if thought_direction == 0:
                self.direction= 'l'
            elif thought_direction == 1:
                self.direction= 'r'
            elif thought_direction == 2:
                self.direction= 'd'
            elif thought_direction == 3:
                self.direction= 'u'    
    def get_score(self):
        return self.score
    def get_status(self):
        return self.alive
    def get_neuralnet(self):
        return self.neuralnet.clone()





# Setup

pygame.init()
font = pygame.font.SysFont('arial', 25)


class SnakeAI:
    
    def __init__(self, neuralnet, w=window_size[0], h=window_size[1]):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('SnakeAI')
        self.clock = pygame.time.Clock()
        
        # init game state
        self.snake = Snake(is_human_playing, neuralnet)
        self.food=Food()
        self.food.new_food(self.snake) 
    
        
    def update_ui(self):
        self.display.fill((0,0,0))
        
        for pt in self.snake.get_position():
            pygame.draw.rect(self.display, (0, 255, 0), pygame.Rect(pt[0], pt[1], block_size, block_size))
            
        pygame.draw.rect(self.display, (255,0,0), pygame.Rect(self.food.get_position()[0], self.food.get_position()[1], block_size, block_size))
        
        text = font.render("Score: " + str(self.snake.get_score()), True, (255,255,255))
        self.display.blit(text, [0, 0])
        pygame.display.flip()
        
    def iterate(self):
        self.snake.think(self.food)
        self.snake.move(self.food)
        self.update_ui()
        self.clock.tick(speed)
        return self.snake.get_status(), self.snake.get_score()
    def get_snake(self):
        return self.snake

if __name__ == '__main__':
    best=[(-1, NeuralNetwork(24, hidden_nodes, 4, hidden_layers))]
    for m in range(20):
        population=2000
        if best[0][0]==-1:
            neuralnets=[NeuralNetwork(24, hidden_nodes, 4, hidden_layers) for _ in range (population)]
        else:
            neuralnets=[random.choice(best)[1].mutate() for _ in range (population)]
        for neuralnet in neuralnets:
            game = SnakeAI(neuralnet)
            
            # game loop
            for i in range (300): # Steps allowed
                is_alive, score = game.iterate()
                
                if is_alive == False:
                    break
                
            if (score>best[0][0]):
                best.clear()
                best.append((score, game.get_snake().get_neuralnet()))
                print('Final Score', score)
            elif (score==best[0][0]):
                best.append((score, game.get_snake().get_neuralnet()))
        print("New Gen "+str(m))
    pygame.quit()