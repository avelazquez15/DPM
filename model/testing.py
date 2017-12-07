import numpy as np
from random import randrange
import time
from datetime import datetime, date, time
import Queue
import matplotlib.pyplot as plt
import math
from collections import deque

rewards = []
returns = np.ones((5,3,10))*-1000

active = 1
idle = 2
sleep = 3

#i_rewards[0][idle-1][0] = -2.9

#i_rewards[0][idle-1][1] = -3.4

#i_rewards[0][active-1][1] = -1.3

#print i_rewards



transitions = []

action1 = 2 #tau
state1 = ([action1], [idle-1],[0])
transitions.append(state1)
#rewards.append(i_rewards[state1])

state2 = ([action1],[idle-1],[1])
transitions.append(state2)
#rewards.append(i_rewards[state2])

action3 = 3
state3 = ([action3],[active-1],[1])
transitions.append(state3)
#rewards.append(i_rewards[state3])


returns[state3] = 500

print "\n ", transitions



print "\n ", returns

