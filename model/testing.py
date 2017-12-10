import numpy as np
from random import randrange
import time
from datetime import datetime, date, time
import Queue
import matplotlib.pyplot as plt
import math
from collections import deque
import matplotlib.pyplot as plt



def generate_number(size):
    mu = 10
    sigma = 5
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

file_name =  "inter_arrival_time.csv"
size = 2000000
ia = generate_number(size)

write2file(ia, file_name)




