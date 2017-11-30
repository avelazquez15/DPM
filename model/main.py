import numpy as np
import dpm as manager
from random import randrange

size = 1000
agent = manager.DPM(size)

clk = 0
while(1):
    print "clk[",clk,"]"
    agent.stimulate(clk)
    clk += 1

    if(clk == size+1):
        break

agent.view_queue()

#i = 0
    #while(not agent.service_queue.is_empty()):
    #print "queue[",i,"] = ", agent.service_queue.get()
#i += 1

print "done"
