import numpy as np
import service_queue as q
import service_provider as sp
import service_requester as sr
from random import randrange

class environment:
    active  = 1
    idle    = 2
    sleep   = 3
    energy_profile = {"active": 1, "idle" : 0.85, "sleep": 0.1}
    
    def __init__(self, request_size, queue_size):
        self.service_provider = sp.Service_Provider(self.idle)
        self.service_requester = sr.Service_Requester(request_size)
        self.service_queue = q.Service_Queue(queue_size)
        self.snapshot = np.zeros(6)
        self.current_action = -1
        self.transition_dir = ""
    
    #self.service_requester.view()

    def stimulate(self, clk):
        #check if inter arrival request has arrived
        if(self.service_requester.time(clk)):
            #inter arrival is true
            request_count = self.service_requester.request_count()
            if(not self.service_queue.add(request_count)):
                print "queue is full ..."
        #take snapshot of state
        self.take_snapshot()
        
    def take_snapshot(self):
        time = 0
        history = np.zeros(6)
        while(time < 6):
            if(time < 5):
                history[time+1] = self.snapshot[time]
            else:
                history[0] = self.service_provider.get_state()
            time += 1

        self.snapshot = history

    def view_queue(self):
        self.service_queue.view()

    def queue_count(self):
        return self.service_queue.count()

    def current_state(self):
        return self.service_provider.get_state()


    def t_minus_one(self):
        return self.snapshot[1]

    def transition(self, clk):
        self.service_provider.transition_period += 1
                    
        print "transition direction:", self.transition_dir
        delay = self.service_provider.get_transition_delay(self.transition_dir)
        print "delay .. transition: ", delay
        print "self.service_provider.transition_period = ", self.service_provider.transition_period
        
        if(self.service_provider.transition_period == delay):
            self.service_provider.transition_period = 0
            new_state = self.service_provider.get_transition(self.transition_dir)
            print "new state :", new_state
            self.change_state(new_state)
        
            if(new_state == self.active):
                self.change_state(new_state)
                print "Before -", self.service_queue.view()
                self.service_queue.get()
                print "After -", self.service_queue.view()
    


    def change_state(self, state):
        self.service_provider.set_state(state)






        
