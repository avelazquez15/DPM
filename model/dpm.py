import numpy as np
import environment as en
from random import randrange


class DPM:

    
    def __init__(self):
        self.active  = 1
        self.idle    = 2
        self.sleep   = 3
        self.tau = [11, 12, 15, 19]
        self.N = 12


    def take_action(self, environment):
        queue_count     = environment.queue_count()
        current_state   = environment.current_state()
        previous_state  = environment.t_minus_one()
        
        
        if(current_state == self.idle and queue_count == 0):
            print "case 1"
            environment.view_queue()
            environment.current_action = self.random_tau_action()
            environment.transition_dir = "idle2sleep"
            print "environment.current_action = ", environment.current_action
        
        elif(current_state == self.idle and queue_count > 0):
            print "case 2"
            environment.view_queue()
            environment.current_action = self.random_idel2active()
            environment.transition_dir = "idle2active"
            print "environment.current_action = ", environment.current_action

        elif((current_state == self.sleep and previous_state == self.idle) and queue_count > 0):
            print "case 3"
            environment.view_queue()
            environment.current_action = self.randomN()
            environment.transition_dir = "sleep2active"
        
        elif(current_state == self.sleep and queue_count > 0):
            print "case 4"
            environment.view_queue()
            environment.current_action = self.randomN()
            environment.transition_dir = "sleep2active"
                
        elif(current_state == self.active and queue_count == 0):
            print "case 5"
            environment.view_queue()
            environment.current_action = self.random_active2idle()
            environment.transition_dir = "active2idle"

        elif(current_state == self.active and queue_count > 0):
            print "case 6"
            environment.view_queue()
            environment.current_action = self.random_active2idle()
            environment.transition_dir = "active2active"
        
        elif(current_state == self.sleep and queue_count == 0):
            print "case 7"
            environment.view_queue()
            environment.current_action = self.random_active2idle()
            environment.transition_dir = "sleep2sleep"
        print "*************-----------**********"
    

    def stimulate(self, clk, environment):
        #random policy
        # print environment.current_state()
        self.take_action(environment)


    def random_tau_action(self):
        action = randrange(0, len(self.tau))
        return self.tau[action]

    def random_idel2active(self):
        action =  randrange(0, 1)
        return action

    def randomN(self):
        action = randrange(1, self.N)
        return action


    def random_active2idle(self):
        action =  randrange(0, 1)
        return action
