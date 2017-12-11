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
    mu = 10
    sigma = 3
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

'''
average_runs = [-255.87, -9490.11, -12016.73, -30462.22, -46022.22, -66119.12, -72048.53, -67114.42, -37053.99, -61734.92, -116335.95, -37824.87, -201.42, -274.67, -297.66, -272.65, -228.71, -256.67, -244.67, -258.66, -297.66, -276.68, -265.67, -249.68, -266.65, -285.64, -268.73, -291.65, -296.7, -266.71, -292.67, -279.65, -249.68, -264.68, -276.67, -311.61, -267.7, -256.69, -264.66, -235.7, -256.68, -290.64, -289.63, -72483.94, -53807.27, -28339.13, -22321.03, -16836.68, -10679.19, -17997.32, -8200.79, -12105.9, -17324.85, -18120.35, -9431.59, -16899.41, -18985.96, -10627.51, -4631.53, -6727.27]
'''

average_runs = [-20.81, -27.38, -40.34, -35.31, -66.65, -14.9, -59.07, -30.69, -84.92, -15.0, -61.28, -28.98, -28.98, -28.98, -53.98, -53.98, -28.98, -28.98, -28.98, -40.28, -41.51, -28.38, -29.98, -29.98, -29.98, -29.98, -42.27, -19.07, -19.87, -20.87, -45.31, -76.93, -15.0, -35.31, -17.7, -53.38, -67.87, -31.98, -63.61, -30.95, -69.83, -41.83, -49.31, -36.57, -55.98, -37.82, -41.94, -95.94, -15.0, -16.83, -16.83, -16.83, -16.83, -16.83, -16.83, -16.83, -16.83, -16.83, -16.83, -16.83, -16.83, -54.04, -16.71, -16.83, -51.89, -14.9, -26.14, -32.86, -26.94, -27.94, -30.17, -57.71, -28.72, -31.15, -38.9, -13.89, -35.32, -16.69, -54.38, -69.85, -55.98, -38.17, -38.17, -38.17, -65.87, -55.98, -42.27, -28.38, -30.97, -40.87, -39.17, -38.17, -39.21, -38.17, -66.87, -66.87, -55.12, -64.27, -50.11, -45.52]

print average_runs

plt.plot(average_runs[1:len(average_runs)-1])
plt.ylabel("Accum. Rewards")
plt.xlabel("Episode")
plt.show()



'''
data = np.zeros((3,5))


data[0][0] = 10
data[0][2] = 5

data[1][0] = 1
data[1][2] = 6

print data
print np.mean(data[0])

'''



