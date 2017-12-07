import numpy as np
import environment as en
import dpm as manager
from random import randrange
import time
from datetime import datetime, date, time

print "\n" * 100
print "\033[1m", "***NEW SIMULATION *** ", datetime.today(), "\033[0m"

active  = 1
idle    = 2
sleep   = 3

duration = 100000
queue_size = 20
requester_length = duration
episodes = 4
requests_per_episode = 10


environment = en.environment(requester_length, queue_size, requests_per_episode, episodes)
agent = manager.DPM(environment)
print 
clk = 0
while(1):
    # seq.  simultaneous time execution
    print "t[", clk, "]"
    environment.stimulate(clk)
    agent.stimulate(clk, environment)
    clk += 1
    
    print
    
    #if(clk == 3):
    #environment.change_state(active)

    
    if(clk == duration+1):
        #print "\n\n\nTransition History: count = ", len(environment.human_history), "\n", environment.human_history
        
        #print "\n\n\nRewards History: count = ", len(environment.rewards),  "\n", environment.rewards
        #print environment.show_transition()
        break

#environment.view_queue()

#i = 0
    #while(not agent.service_queue.is_empty()):
    #print "queue[",i,"] = ", agent.service_queue.get()
#i += 1



print "\n\n\n**DONE**"
