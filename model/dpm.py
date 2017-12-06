import numpy as np
import environment as en
from random import randrange
import termios, fcntl, sys, os

class DPM:

    
    def __init__(self, environment):
        self.active  = 1
        self.idle    = 2
        self.sleep   = 3
        self.tau = [5, 2, 3, 7]
        #self.Ns = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.Ns =  np.arange(0, environment.queue_len())
        print "N-Policy", self.Ns
        self.wait_debug("wait...")
        self.N = self.randomN()



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
                environment.current_action = self.random_tau_action()
                environment.transition_dir = "idle2sleep"
                environment.service_provider.set_time_out(environment.current_action)
                environment.service_provider.set_cycle(0)
                print "selecting a tau policy ..."
                #print "environment.current_action = ", environment.current_action
            
            elif( cycle == timeout):
                #environment.service_provider.set_cycle(0)
                #environment.service_provider.set_time_out(0)
                print "timeout tau reached ... "
                environment.transition_dir = "idle2sleep"
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

            print "duration = ", duration, "cycle = ", cycle, "  timeout = ", timeout
            cycle = self.increment_cycle(environment)
            environment.view_queue()
            environment.current_action = self.random_idel2active()
            environment.transition_dir = "idle2active"
            print "environment.current_action = ", environment.current_action
            environment.transition(current_state)

        elif((current_state == self.sleep and previous_state == self.idle) and queue_count > 0):
            print "case 3: entering sleep ... "
            #environment.service_provider.set_cycle(0)
            duration = self.increment_duration(environment)
            
            print "previous state :", previous_state , "[", environment.state_str(previous_state), "]"
            print "current state :", current_state , "[", environment.state_str(current_state), "]"
 
            print "[N-Policy, queue_count] " , "[",self.N, ",", environment.queue_count() ,"]"
            
            environment.under_N_poicy = True
            
            if(environment.cost_init == 0):
                environment.cost_init = environment.service_queue.timer_value()
                self.wait_debug(".......... case 3 ..........")
            
            #if(environment.queue_count() >= self.N):
            #self.wait_debug(".......... case 3 ..........")
                    #self.preform_N_policy
        
        elif((current_state == self.sleep and previous_state == self.sleep )and queue_count > 0):
            print "case 4: in sleep, but request in queue arrived ... "
            duration = self.increment_duration(environment)
            print "previous state :", previous_state , "[", environment.state_str(previous_state), "]"
            print "current state :", current_state , "[", environment.state_str(current_state), "]"
            #environment.service_queue.view()
            print "[N-Policy, queue_count] " , "[",self.N, ",", environment.queue_count() ,"]"
            
            
            if(environment.cost_init == 0):
                environment.cost_init = environment.service_queue.timer_value()
            # message = environment.cost_init
            #self.wait_debug(message)
            
            environment.cost_final = environment.service_queue.timer_value() + 1

            
            environment.under_N_poicy = True

            if(environment.queue_count() >= self.N):
                
                self.preform_N_policy(environment, current_state)
            else:
                environment.evaluate_cost(current_state, False)


        elif(current_state == self.active and queue_count == 0):
            print "case 5: going to idle ... "


            environment.service_provider.set_cycle(0)
            #cycle = environment.service_provider.get_cycle()
            duration = self.increment_duration(environment)
            #timeout = environment.service_provider.get_time_out()
            
            # print "duration = ", duration, "cycle = ", cycle, "  timeout = ", timeout
            environment.cost_final = environment.service_queue.timer_value() + 1
            #environment.view_queue()
            environment.current_action = self.random_active2idle()
            environment.transition_dir = "active2idle"
            environment.transition(current_state)

        elif(current_state == self.active and queue_count > 0):
            print "case 6: staying in active ..."


            if(environment.cost_init == 0):
                environment.cost_init = environment.service_queue.timer_value()
        
            environment.cost_final = environment.service_queue.timer_value() + 1
            
            duration = self.increment_duration(environment)
            #environment.view_queue()

            environment.current_action = self.random_active2idle()
            environment.transition_dir = "active2active"
            environment.transition(current_state)
            environment.check_queue()
            environment.view_status()

        elif(current_state == self.sleep and queue_count == 0):
            print "case 7: staying in sleep ..."
            print "previous state :", previous_state , "[", environment.state_str(previous_state), "]"
            print "current state :", current_state , "[", environment.state_str(current_state), "]"
            
            
            environment.under_N_poicy = False
            
            if(previous_state == self.idle):
                environment.service_provider.set_duration(0)

            environment.cost_final = environment.service_queue.timer_value() + 1
        
            duration = self.increment_duration(environment)
            environment.view_queue()
            environment.current_action = self.random_active2idle()
            environment.transition_dir = "sleep2sleep"
            environment.transition(current_state)



        #print "queue_timer: [", environment.service_queue.timer_value() , "]"
    

    def stimulate(self, clk, environment):
        #random policy
        # print environment.current_state()
        self.take_action(environment)


    def random_tau_action(self):
        action = randrange(0, len(self.tau))
        return 4# self.tau[action]

    def random_idel2active(self):
        action =  randrange(0, 1)
        return action

    def randomN(self):
        action = randrange(1, len(self.Ns))
        return 4 #self.Ns[action]


    def random_active2idle(self):
        action =  randrange(0, 1)
        return action

    def increment_duration(self, environment):
        duration = environment.service_provider.get_duration()
        environment.service_provider.set_duration(duration+1)
        duration = environment.service_provider.get_duration()
        #print "_[+]_[+]__: ", duration
        return duration

    def increment_cycle(self, environment):
        cycle = environment.service_provider.get_cycle()
        environment.service_provider.set_cycle(cycle + 1)
        cycle = environment.service_provider.get_cycle()
        return cycle


    def preform_N_policy(self, environment, current_state):

        environment.view_queue()
        environment.current_action = self.randomN()
        self.N = environment.current_action
        environment.transition_dir = "sleep2active"
        environment.transition(current_state)


    def wait_debug(self, message):
        print "[DEBUG] ", message
        sys.stdin.read(1)
