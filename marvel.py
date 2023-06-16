from abc import ABC, abstractmethod
from collections import defaultdict
import math
import random
import copy
import time
from os import listdir
from os.path import isfile, join
from multiprocessing import Lock, Process, Queue, current_process
import multiprocessing as mp

import board

FILE = None

'''
Class that Controls the number of Simulations performed
'''
class SweetbreakAI:

    def __init__(self, file=None, string=None):
        self.plays = 0 # Number of moves
        self.wins = 0 # Number of wins
        self.max = -1
        self.min = 99999999
        self.media = 0
        self.rewards = 0
        self.file = file
        self.map_string = string
    
    def get_board(self):
        return board.Board(file=self.file, string=self.map_string)

    # Returns the canes' rewards
    def get_reward_canes(self, board):
        canes = board.get_canes_reward()
        value = self.canes - len(canes)

        # Add the values
        for c in canes:
            value += c

        return float(value/self.canes)

    def get_reward(self, board):
        p_blocks = 1
        p_canes = 1
        p_points = 1

        count = 0
        total = 0
        if self.blocks > 0:
            if self.blocks != board.blocks:
                blocks = 1/(self.blocks/(self.blocks - board.blocks))
            else:
                blocks = 0
            total += blocks
            count += p_blocks
        
        if self.canes > 0:
            total += self.get_reward_canes(board)
            count += p_canes

        if self.w_points > 0:
            points = 0
            if board.points >= self.w_points:
                points = 1
            else:
                points = board.points/self.w_points
            
            total += points
            count += p_points
        
        if count > 0:
            return total/count
        else:
            return 1.0

    def best_move(self, board, n):
        moves = board.possible_moves()
        children = []
        i = 0
        while i < n:
            aux = copy.deepcopy(board)
            move = random.choice(moves)
            try:
                aux.test_move(move[0], move[1])
                children.append((move, self.get_reward(aux)))
                i += 1
            except KeyboardInterrupt:
                exit(1)
            except:
                print("There was a problem, try again!")
        
        move = max(children, key=lambda x: x[1])
        return move[0]

    def _playout(self, n, n_moves, queue, id, info):
        data = {}
        data['max'] = -1
        data['min'] = 9999999
        data['media'] = 0
        data['wins'] = 0
        data['plays'] = 0
        data['rewards'] = 0

        i = 1
        breaked = 0
        while i <= n:

            if breaked > 5:
                break

            match = time.time()

            try:
                board = self.get_board()
                while True:
                    if board.moves == 0 or board.is_finished():
                        break
                    
                    move = None
                    if n_moves > 1:
                        move = self.best_move(board, n_moves)
                    else:
                        moves = board.possible_moves()
                        move = random.choice(moves)
                    board.test_move(move[0], move[1])
                
                if board.points > data['max']:
                    data['max'] = board.points
                if board.points < data['min']:
                    data['min'] = board.points
                data['media'] += board.points 

                if board.is_finished():
                    data['wins'] += 1
                
                data['rewards'] += self.get_reward(board)
                data['plays'] += 1
                i += 1

                if info:
                    if i % 10 == 0:
                        print("Process %d played %d times" % (id, i))
                
                breaked = 0
            except KeyboardInterrupt:
                exit(1)
            except:
                breaked += 1
                if info:
                    print("Bot_play #%d in Process %d failed" % (id, i))
        
        if info:
            print("Process %d FINISHED" % id)
        queue.put(data)

    def _print_data(self, i, data):
        print("Results from Process", i)
        for key, value in data.items():
            print("%s: %s" % (key, value))
        print("")

    def _evaluate(self):
        w = float(self.wins/self.plays)
        r = float(self.rewards/self.plays)

        return r

    def do_playouts(self, n=100, n_moves=1, info=True, final=False):
        board = self.get_board()
        self.w_points = board.w_points
        self.blocks = board.blocks
        self.canes = board.canes

        if info:
            print("\nDoing %d simulations" % n)
            print("With %d possible moves" % n_moves)
            print("In the Level: %s\n" % FILE)
            print("")

        begin = time.time()

        # Take the amount of CPUs and divide the values
        cpu_count = mp.cpu_count()
        values = [int(n/cpu_count) for i in range(cpu_count)]

        # Add the extra values
        extra = n % cpu_count 
        i = 0
        while extra > 0:
            values[i] += 1
            i += 1
            extra -= 1

        # Result of processes
        results = Queue()

        # Send to processes
        procs = []

        if info:
            print("Using %d process" % cpu_count)
        for i in range(cpu_count):

            if info:
                print("\tProcess %d simulates %d times" % (i, values[i]))

            proc = Process(
                target=self._playout, 
                args=(values[i], n_moves, results, i, info))
            procs.append(proc)
            proc.start()
        
        if info:
            print("")
            print("Simulation Started\n")
        
        # Receive the processes
        for proc in procs:
            proc.join()
        
        if info:
            print("Simulation Finished\n")

        # Adds the results of each Process
        while not results.empty():
            data = results.get()
            self.plays += data['plays']
            self.wins += data['wins']
            self.rewards += data['rewards']
            self.media += data['media']

            if self.max < data['max']:
                self.max = data['max']
            if self.min > data['min']:
                self.min = data['min']

            if info:
                self._print_data(i, data)

        if self.plays == 0:
            return 0

        if info or final:
            print("Total Plays:", self.plays)
            print("Total Wins:", self.wins)
            print("Total reward:", self.rewards)
            print("Win/Ratio:", float(self.wins/self.plays))
            print("Reward/Ratio: %s" % float(self.rewards/self.plays))
            print("Max points:", self.max)
            print("Min points:", self.min)
            print("Mean:", float(float(self.media)/float(self.plays)))
            print("Tempo Total:", time.time() - begin)

        if FILE is not None:
            string = FILE.replace("levels/", "")
        else:
            string = "None"
        
        with open("tests/%s_%d_%d.txt" % (string, n, n_moves), mode="w+") as f:
            f.write("Doing %d simulations\n" % n)
            f.write("With %d possible moves\n" % n_moves)
            f.write("In the Level: %s\n\n" % string)
            f.write("Total Plays: %d\n" % self.plays)
            f.write("Total Wins: %d\n" % self.wins)
            f.write("Total reward: %s\n" % self.rewards)
            f.write("Win/Ratio: %s\n" % float(self.wins/self.plays))
            f.write("Reward/Ratio: %s\n" % float(self.rewards/self.plays))
            f.write("Evaluate: %s\n" % self._evaluate())
            f.write("Max points: %s\n" % self.max)
            f.write("Min points: %s\n" % self.min)
            f.write("Mean: %s\n" % float(float(self.media)/float(self.plays)))
            f.write("Tempo Total: %s\n" % (str(time.time() - begin)))
        
        # Returns Bot rating
        return self._evaluate()

# Get a random level from the levels folder
def _pick_a_level():
    mypath = "levels/"
    onlyfiles = [join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f))]
    onlyfiles.append(None)
    return onlyfiles
