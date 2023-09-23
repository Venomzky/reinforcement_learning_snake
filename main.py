import random
import time 
from collections import deque
import copy
import pickle
class Environment:
    def __init__(self,x,y) -> None:
        self.states = []
        self.x = x
        self.y = y
        self.apple = 0
        pass
    
    def reset(self, state):
        column = []
        for i in range(self.y):
            row = []
            for j in range(self.x):
                row.append(0)
            column.append(row)
        self.states = column
        
        self.apple = [random.randint(0,self.x-1),random.randint(0,self.y-1)]
        while(self.apple in state):
            self.apple = [random.randint(0,self.y-1),random.randint(0,self.x-1)]

        self.states[self.apple[1]][self.apple[0]]=1
        

    def step(self, action, state):   #next_state, reward, done

        new_state = [state[0][0]+action[0], state[0][1]+action[1]]
        segments = state[1:]
        if len(state) == self.x * self.y:
            # print("DONE!!!")
            return [state[0][0], state[0][1]],1,1
        if new_state in segments:
            return new_state,-1, 1
        if state[0][0]+action[0] < 0 or state[0][0]+action[0] > self.x-1 or state[0][1]+action[1] < 0 or state[0][1]+action[1] > self.y-1:
             return new_state,-1,1 
        if self.states[state[0][1]+action[1]][state[0][0]+action[0]]==1:
             return new_state,1,0
        else:
             return new_state,0,0
        




class Agent:
    def __init__(self) -> None:
        self.state = 0
        self.q_table = {}
        self.done = 0
        self.apple = []
        pass
    
    def set_apple(self, x,y):
        self.apple = [x,y]
        
    def q_table_display(self):
        for key, values in self.q_table.items():
            print(key, values)
    def set_agent(self,board_x, board_y):
        self.state = [[random.randint(0,board_x-1), random.randint(0,board_y-1)]]
        self.done = 0
    def get_best_action(self, values):
        for x in values:
            same = 0
            for i in range(len(values)):
                if x == values[i]:
                    same +=1
            if same > 1:
                ret =  random.randint(0,3)
                
                return ret
            same = 0
        biggest = max(values)
        return values.index(biggest)
    def get_action(self):
        action = [[1,0],[-1,0],[0,1],[0,-1]]
        values = []
        key1 = copy.deepcopy(self.state)
        for i in range(len(key1)):
            key1[i]=[self.apple[0]-self.state[i][0], self.apple[1]-self.state[i][1]]
        key1 = tuple(map(tuple,key1))
        if key1 not in self.q_table:
            self.q_table[key1]=[0.0,0.0,0.0,0.0]
        for row in action:   
            key = copy.deepcopy(self.state)
            for i in range(len(key1)):
                key[i]=[self.apple[0]-(self.state[i][0]+row[0]), self.apple[1]-(self.state[i][1]+row[1])]
            key = tuple(map(tuple,key))
            if key not in self.q_table:
                self.q_table[key]=[0.0,0.0,0.0,0.0]
        return action[self.get_best_action(self.q_table[key1])]
    
    def update(self, action, next_state, reward, done):   #q_table actualization
        gamma = 0.9
        alpha = 0.1
        index = 0
        actions = [[1,0],[-1,0],[0,1],[0,-1]]
        for i, x in enumerate(actions):
            if x == action:
                index = i

        key1 = copy.deepcopy(self.state)
        for i in range(len(key1)):
            key1[i]=[self.apple[0]-self.state[i][0], self.apple[1]-self.state[i][1]]
        key2 = copy.deepcopy(self.state)
        for i in range(len(key2)):
            key2[i] = [key1[i][0]-action[0], key1[i][1]-action[1]]
        key1 = tuple(map(tuple, key1))
        key2 = tuple(map(tuple, key2))
        r = alpha*(reward+gamma*max(self.q_table[key2])-self.q_table[key1][index])
        self.q_table[key1][index] += r
        self.state.insert(0, next_state)
        self.done=done
        if reward != 1:
            self.state = self.state[:-1]
            

board_size_x = 10
board_size_y = 10

apple_x = 0
apple_y = 0
environment = Environment(board_size_x,board_size_y)
agent = Agent()

def generate_board(board_size_y, board_size_x):
    board = []
    for i in range(board_size_y+2):
        row=[]
        for j in range(board_size_x+2):
            if i == 0 or i == board_size_y+1:
                row.append("+")
                continue
            if j == 0 or j == board_size_x+1:
                row.append("+")
                continue
            row.append(" ")
        board.append(row)
    return board



def display_board(board, state, apple):

    for i in range(board_size_y+2):
        for j in range(board_size_x+2):
            if board[i][j]=='*' or board[i][j]=='o' or board[i][j]=='@':
                board[i][j]=' '
    board[apple[1]+1][apple[0]+1]="@"
    
    for row in state:
        board[row[1]+1][row[0]+1]="*"
    board[state[0][1]+1][state[0][0]+1]="o"

    print("_________")
    for row in board:
        for x in row:
            print(x, end='')
        print()
epizodes = 10000
n = 0
#learning in block makes it possible to stop it whenever I want to, but decrease learning speed
while epizodes > 1:


    file_path = "data"+str(board_size_x)+"x"+str(board_size_y)+".txt"
    # loading already learned data
    with open(file_path, 'rb') as file:
        agent.q_table = pickle.load(file)

    for i in range(epizodes):
        agent.set_agent(board_size_x, board_size_y)
        environment.reset(agent.state)
        agent.set_apple(environment.apple[0],environment.apple[1])
        board = generate_board(board_size_y,board_size_x)
        # display_board(board, agent.state, agent.apple)
        while agent.done == 0:
            action = agent.get_action()
            next_state, reward, done = environment.step(action, agent.state)
            agent.update(action, next_state, reward, done)
            if(reward == 1 and len(agent.state)<board_size_x*board_size_y):
                environment.reset(agent.state)
                agent.set_apple(environment.apple[0],environment.apple[1])
            # uncoment these two lines if want to see what snake can do
            display_board(board, agent.state, agent.apple)
            time.sleep(0.2)


    #saving q_table to text file in order to use learned data in next time running program
    with open(file_path, 'wb') as file:
        pickle.dump(agent.q_table, file)
    n=n+epizodes
    print(n)


