import numpy as np
import service_queue as q
import service_provider as sp
import service_requester as sr
from random import randrange

class DPM:
    active  = 1
    idle    = 2
    sleep   = 3
    energy_profile = {"active": 1, "idle" : 0.85, "sleep": 0.1}
    
    def __init__(self, size):
        self.service_provider = sp.Service_Provider(self.active)
        self.service_requester = sr.Service_Requester(size)
        self.service_queue = q.Service_Queue(10)
    
        self.service_requester.view()

    def stimulate(self, clk):
        #check if inter arrival request has arrived
        if(self.service_requester.time(clk)):
            request_count = self.service_requester.request_count()
            if(not self.service_queue.add(request_count)):
                print "queue is full ..."



    def view_queue(self):
        self.service_queue.view()


        

        
