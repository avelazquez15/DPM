import numpy as np
import environment as en
import dpm as manager
from random import randrange
import time
from datetime import datetime, date, time

print "\n" * 100
print "\033[1m", "***NEW SIMULATION *** ", datetime.today(), "\033[0m"


duration = 2000000
queue_size = 300
requester_length = duration
episodes = 200
requests_per_episode = 20
epsilon = 0.9
runs = 10


environment = en.environment(requester_length, queue_size, requests_per_episode, episodes, runs)
agent = manager.DPM(environment, epsilon)
print 
clk = 0
while(1):
    # seq.  simultaneous time execution
    #print "t[", clk, "]"
    environment.stimulate(clk)
    agent.stimulate(clk, environment)
    clk += 1
    
    
    #if(clk == duration+1):
#break

print "\n\n\n**DONE**"
