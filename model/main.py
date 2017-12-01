import numpy as np
import environment as en
import dpm as manager
from random import randrange

size = 25
queue_size = 10

agent = manager.DPM()
environment = en.environment(size, queue_size)

clk = 0
while(1):
    # seq.  simultaneous time execution
    environment.stimulate(clk)
    agent.stimulate(clk, environment)
    clk += 1

    
    if(clk == size+1):
        break

#environment.view_queue()

#i = 0
    #while(not agent.service_queue.is_empty()):
    #print "queue[",i,"] = ", agent.service_queue.get()
#i += 1

print "done"
