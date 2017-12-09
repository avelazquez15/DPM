import numpy as np
import environment as en
from random import randrange
import termios, fcntl, sys, os

class DPM:

    
    def __init__(self, environment):
        self.active  = 1
        self.idle    = 2
        self.sleep   = 3
        self.tau = [1,3,5,7,10,12,14,16,20]
        #self.Ns = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.Ns =  list(np.arange(0, environment.queue_len()))
        print "N-Policy", self.Ns
        self.wait_debug("wait...")
        self.N = self.select_nPolicy()
        environment.setup(len(self.tau ), len(self.Ns))
        self.action = 0



    def take_action(self, environment):
        queue_count     = environment.queue_count()
        current_state   = environment.current_state()
        previous_state  = environment.t_minus_one()
        cycle = environment.service_provider.get_cycle()
        
        if(current_state == self.idle and queue_count == 0):
            print "case 1: idle"
            
            timeout = environment.service_provider.get_time_out()
            duration = self.increment_duration(environment)

            
            if(timeout == 0):
                environment.service_provider.set_transition_period(0)
                environment.view_queue()
                
                # select tau action from Policy
                action = self.select_tauPolicy()
                environment.current_action = self.tau.index(action)
                environment.case_number = 1
                
                # set transition properties
                environment.transition_dir = "idle2sleep"
                environment.service_provider.set_time_out(action)
                environment.service_provider.set_cycle(0)
                print "selecting a tau policy ..."
            
            elif( cycle == timeout):
                print "timeout tau reached ... "

                environment.transition_dir = "idle2sleep"
                environment.case_number = 1
                environment.transition(current_state)
            
            else:
                cycle = self.increment_cycle(environment)

            print "In cycle ", cycle, "  waiting for timeout = ", timeout


        elif(current_state == self.idle and queue_count > 0):
            print "case 2: going to active ... "
            timeout = environment.service_provider.get_time_out()
            environment.service_provider.set_cycle(0)
            cycle = environment.service_provider.get_cycle()
            duration = self.increment_duration(environment)

            cycle = self.increment_cycle(environment)
            environment.view_queue()
            environment.transition_dir = "idle2active"
            environment.case_number = 1
            environment.transition(current_state)

        elif((current_state == self.sleep and previous_state == self.idle) and queue_count > 0):
            print "case 3: entering sleep ... "
            print "[N-Policy, queue_count] " , "[",self.N, ",", environment.queue_count() ,"]"
            
            duration = self.increment_duration(environment)
            environment.under_N_poicy = True
            
            # just about to enter sleep state -> select an N Policy
            self.N = self.select_nPolicy()
            environment.current_action = self.Ns.index(self.N)
            environment.case_number = 2
            
            if(environment.cost_init == 0):
                environment.cost_init = environment.service_queue.timer_value()
        
        elif((current_state == self.sleep and previous_state == self.sleep )and queue_count > 0):
            print "case 4: in sleep, but request in queue arrived ... "
            print "[N-Policy, queue_count] " , "[",self.N, ",", environment.queue_count() ,"]"
                
            duration = self.increment_duration(environment)
            
            if(environment.cost_init == 0):
                environment.cost_init = environment.service_queue.timer_value()-1

            environment.cost_final = environment.service_queue.timer_value() + 1
            environment.under_N_poicy = True
            environment.case_number = 2
            environment.current_action = self.Ns.index(self.N)

            if(environment.queue_count() >= self.N):
                environment.transition_dir = "sleep2active"
                environment.transition(current_state)
            
            else:
                environment.store_state_action_pair(current_state)
                environment.store_state_value_pair(current_state)
                environment.evaluate_cost(current_state, False)


        elif(current_state == self.active and queue_count == 0):
            print "case 5: going to idle ... "

            environment.service_provider.set_cycle(0)
            duration = self.increment_duration(environment)
            environment.cost_final = environment.service_queue.timer_value() + 1
            environment.current_action = self.random_active2idle()
            environment.transition_dir = "active2idle"
            environment.case_number = 0
            environment.transition(current_state)

        elif(current_state == self.active and queue_count > 0):
            print "case 6: staying in active ..."

            if(environment.cost_init == 0):
                environment.cost_init = environment.service_queue.timer_value()
        
            environment.cost_final = environment.service_queue.timer_value() + 1
            duration = self.increment_duration(environment)

            environment.current_action = self.random_active2idle()
            environment.transition_dir = "active2active"
            environment.case_number = 0
            environment.transition(current_state)
            environment.check_queue()
            environment.view_status()

        elif(current_state == self.sleep and queue_count == 0):
            print "case 7: staying in sleep ..."
            
            environment.under_N_poicy = False
            
            if(previous_state == self.idle):
                environment.service_provider.set_duration(0)

            environment.cost_final = environment.service_queue.timer_value() + 1
        
            duration = self.increment_duration(environment)
            environment.view_queue()
            environment.current_action = self.random_active2idle()
            environment.transition_dir = "sleep2sleep"
            environment.case_number = 2
            environment.transition(current_state)
    

    def stimulate(self, clk, environment):
        # choose an action to take based on each case
        self.take_action(environment)


    def select_tauPolicy(self):
        
        #Epsilon Policy
        
        #Random Policy
        action = randrange(0, len(self.tau))
        
        # return Policy
        return self.tau[action]
 

    def random_idel2active(self):
        action =  randrange(0, 1)
        return action

    def select_nPolicy(self):
        # epsilon
        
        #random
        action = randrange(0, len(self.Ns))
        
        # return Policy
        return action


    def random_active2idle(self):
        action =  randrange(0, 1)
        return action

    def increment_duration(self, environment):
        duration = environment.service_provider.get_duration()
        environment.service_provider.set_duration(duration+1)
        duration = environment.service_provider.get_duration()
        return duration

    def increment_cycle(self, environment):
        cycle = environment.service_provider.get_cycle()
        environment.service_provider.set_cycle(cycle + 1)
        cycle = environment.service_provider.get_cycle()
        return cycle


    def wait_debug(self, message):
        print "[DEBUG] ", message
        sys.stdin.read(1)
