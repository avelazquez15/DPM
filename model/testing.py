import numpy as np
from random import randrange
import time
from datetime import datetime, date, time
import Queue
import matplotlib.pyplot as plt
import math
from collections import deque
import matplotlib.pyplot as plt
import termios, fcntl, sys, os

def wait_debug( message):
    print "[DEBUG] ", message
    sys.stdin.read(1)

def generate_number(size):
    mu = 100
    sigma = 25
    x = []
    n = 0
    data_points = size
    y = 0
    A = 0
    while(n < data_points):
        B = int(np.random.normal(mu, sigma, 1))
        arrival = A + B
        x.append(arrival)
        n += 1
        A = x[n-1]
    
    return sorted(set(x))

def write2file(data, file_name):
    f = open(file_name,"w")
    n = 0
    while(n < len(data)):
        f.write("{:03d}\n".format(data[n]))
        n += 1
    
    f.close()

def read_file(file_name):
    x = []
    with open(file_name, 'rb') as f:
        for line in f:
            x.append(int(line))

    return x


def is_transition_allowed(state_action_transitions, state_action_pair):
    current_length = len(state_action_transitions)
    
    if(current_length > 1):
        current_index = current_length - 1
        try:
            state_action_index = state_action_transitions.index(state_action_pair)
            if(current_index == state_action_index):
                return False
            else:
                return True
        except ValueError:
            return True



def get_column(average_runs, index):
    #print average_runs
    
    column = [average_runs[row][index] for row in range(len(average_runs[0]))]
    return sum(column)

def average(average_runs):
    runs = []
    for ep in np.arange(0, 5):
        value = get_column(average_runs, int(ep))
        runs.insert(ep, value)

    print runs
    average = [i/float(5) for i in runs]
    average = [float(str(round(i, 2))) for i in average]
    return average



'''
file_name =  "inter_arrival_time.csv"
size = 5000
ia = generate_number(size)
write2file(ia, file_name)
'''


average_runs = np.ones((5,5),  dtype=np.int8)
average_runs[2][0] = 10
average_runs[2][1] = 20
average_runs[2][2] = 30

print average_runs

x = average(average_runs)

print x



