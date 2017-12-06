import numpy as np
from random import randrange
import time
from datetime import datetime, date, time
import Queue
import matplotlib.pyplot as plt
import math
from collections import deque

rewards = []
i_rewards = np.zeros((3,10))

i_rewards[1][0] = -2.9

i_rewards[1][1] = -3.4

i_rewards[0][1] = -1.3

#print i_rewards



transitions = []

state1 = ([1],[0])
transitions.append(state1)
rewards.append(i_rewards[state1])

state2 = ([1],[1])
transitions.append(state2)
rewards.append(i_rewards[state2])


state3 = ([0],[1])
transitions.append(state3)
rewards.append(i_rewards[state3])



t1 = transitions[0]
t2 = transitions[1]
t3 = transitions[2]

x = t1[0]
y = t1[1]

#print "\n ", transitions.count(([1],[2]))

#i_rewards.count()
#i_rewards[1][1] = -34


print 11 % 2
