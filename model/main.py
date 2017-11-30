import numpy as np
import dpm as manager
from random import randrange




clk = 0

agent = manager.DPM(clk)

inter_arrivals = agent.service_requester.inter_arrivals()

while(clk <= max(inter_arrivals) ):
    #print("CLK =", clk)
    i = 0
    while(i < len(inter_arrivals) ):
        if(clk == inter_arrivals[i]):
            #request generated
            request = randrange(1, 50)
            agent.service_queue.add(request)
        i += 1
    clk += 1


i = 0
while(not agent.service_queue.is_empty()):
    print "queue[",i,"] = ", agent.service_queue.get()
    i += 1

print "done"
