import numpy as np
import environment as en
from random import randrange


class DPM:

    
    def __init__(self):
        self.active  = 1
        self.idle    = 2
        self.sleep   = 3
        self.tau = [11, 12, 15, 19]


    def take_action(self, environment):
        queue_count     = environment.queue_count()
        current_state   = environment.current_state()
        previous_state  = environment.t_minus_one()
        
        
        if(current_state == self.idle and queue_count == 0):
            print "case 1"
            environment.current = self.random_tau_action()
            print "environment.current = ", environment.current
        elif(current_state == self.idle and queue_count > 0):
            print "case 2"
        elif((current_state == self.sleep and previous_state == self.idle) and queue_count > 0):
            print "case 3"
        elif(current_state == self.sleep and queue_count > 0):
            print "case 4"

        
        
        
    

    def stimulate(self, clk, environment):
        #random policy
        # print environment.current_state()
        self.take_action(environment)


    def random_tau_action(self):
        action = randrange(0, len(self.tau))
        return self.tau[action]
