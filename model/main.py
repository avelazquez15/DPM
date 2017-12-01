import numpy as np
import environment as en
import dpm as manager
from random import randrange

active  = 1
idle    = 2
sleep   = 3

duration = 20
queue_size = 3
request_size = 10

agent = manager.DPM()
environment = en.environment(request_size, queue_size)
print 
clk = 0
while(1):
    # seq.  simultaneous time execution
    print "t[", clk, "]"
    environment.stimulate(clk)
    agent.stimulate(clk, environment)
    environment.transition(clk)
    clk += 1
    
    print
    
    #if(clk == 3):
    #environment.change_state(active)

    
    if(clk == duration+1):
        break

#environment.view_queue()

#i = 0
    #while(not agent.service_queue.is_empty()):
    #print "queue[",i,"] = ", agent.service_queue.get()
#i += 1

print "done"
