import numpy as np
import environment as en
from random import randrange
import termios, fcntl, sys, os

class DPM:

    
    def __init__(self, environment, epsilon):
        self.active  = 1
        self.idle    = 2
        self.sleep   = 3
        self.taus = [1,2,3,5,7,10,12,14,16,20]
        #self.Ns = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.Ns =  [0, 1,2,3,4,5]#list(np.arange(0, environment.queue_len()-1))
        print "N-Policy", self.Ns
        self.wait_debug("wait...")
        self.tau = 0
        environment.setup(len(self.taus), len(self.Ns))
        self.action = 0
        self.epsilon = epsilon
        self.N = 1#self.select_nPolicy(environment)



    def take_action(self, environment):
        queue_count     = environment.queue_count()
        current_state   = environment.current_state()
        previous_state  = environment.t_minus_one()
        cycle = environment.service_provider.get_cycle()
        
        if(current_state == self.idle and queue_count == 0):
            #print "case 1: idle"
            
            timeout = environment.service_provider.get_time_out()
            duration = self.increment_duration(environment)

            
            if(timeout == 0):
                environment.service_provider.set_transition_period(0)
                #environment.view_queue()
                
                # select tau action from Policy
                action = self.select_tauPolicy(environment)
                self.tau = self.taus.index(action)
                environment.current_action = self.tau
                environment.case_number = 1
                
                # set transition properties
                environment.transition_dir = "idle2sleep"
                environment.service_provider.set_time_out(action)
                environment.service_provider.set_cycle(0)
            #print "selecting a tau policy ..."
            
            elif( cycle == timeout):
                #print "timeout tau reached ... "

                environment.current_action = self.tau
                environment.transition_dir = "idle2sleep"
                environment.case_number = 1
                environment.transition(current_state)
            
            else:
                environment.current_action = self.tau
                cycle = self.increment_cycle(environment)
                environment.evaluate_cost(current_state, False)

            #print "In cycle ", cycle, "  waiting for timeout = ", timeout


        elif(current_state == self.idle and queue_count > 0):
            #print "case 2: going to active ... "
            timeout = environment.service_provider.get_time_out()
            environment.service_provider.set_cycle(0)
            cycle = environment.service_provider.get_cycle()
            duration = self.increment_duration(environment)

            cycle = self.increment_cycle(environment)
            #environment.view_queue()
            environment.current_action = self.tau
            environment.transition_dir = "idle2active"
            environment.case_number = 1
            environment.transition(current_state)

        elif((current_state == self.sleep and previous_state == self.idle) and queue_count == 0):
            #print "case 3: entering sleep ... "
            #print "[N-Policy, queue_count] " , "[",self.N, ",", environment.queue_count() ,"]"
            
            duration = self.increment_duration(environment)
            environment.under_N_poicy = True
            
            # just about to enter sleep state -> select an N Policy
            self.N = self.select_nPolicy(environment)
            environment.current_action = self.Ns.index(self.N)
            environment.case_number = 2
            
            if(environment.cost_init == 0):
                environment.cost_init = environment.service_queue.timer_value()
        
        elif((current_state == self.sleep and previous_state == self.sleep )and queue_count > 0):
            #print "case 4: in sleep, but request in queue arrived ... "
            #print "[N-Policy, queue_count] " , "[",self.N, ",", environment.queue_count() ,"]"
                
            duration = self.increment_duration(environment)
            
            if(environment.cost_init == 0):
                environment.cost_init = environment.service_queue.timer_value()-1

            environment.cost_final = environment.service_queue.timer_value() + 1
            environment.under_N_poicy = True
            environment.case_number = 2
            # just about to enter sleep state -> select an N Policy
            self.N = self.select_nPolicy(environment)
            environment.current_action = self.Ns.index(self.N)
            environment.case_number = 2

            if(environment.queue_count() >= self.N):
                environment.transition_dir = "sleep2active"
                environment.transition(current_state)
            
            else:
                environment.store_state_action_pair(current_state)
                environment.store_state_value_pair(current_state)
                environment.evaluate_cost(current_state, False)


        elif(current_state == self.active and queue_count == 0):
            #print "case 5: going to idle ... "

            environment.service_provider.set_cycle(0)
            duration = self.increment_duration(environment)
            environment.cost_final = environment.service_queue.timer_value() + 1
            environment.current_action = self.random_active2idle()
            environment.transition_dir = "active2idle"
            environment.case_number = 0
            environment.transition(current_state)

        elif(current_state == self.active and queue_count > 0):
            #print "case 6: staying in active ..."

            if(environment.cost_init == 0):
                environment.cost_init = environment.service_queue.timer_value()
        
            environment.cost_final = environment.service_queue.timer_value() + 1
            duration = self.increment_duration(environment)

            environment.current_action = 100#self.random_active2idle()
            environment.transition_dir = "active2active"
            environment.case_number = 0
            environment.transition(current_state)
            environment.check_queue()
            #environment.view_status()

        elif(current_state == self.sleep and queue_count == 0):
            #print "case 7: staying in sleep ..."
            
            environment.under_N_poicy = False
            
            if(previous_state == self.idle):
                environment.service_provider.set_duration(0)

            environment.cost_final = environment.service_queue.timer_value() + 1
        
            duration = self.increment_duration(environment)
            #environment.view_queue()
            environment.current_action = self.Ns.index(self.N)#self.random_active2idle()
            environment.transition_dir = "sleep2sleep"
            environment.case_number = 2
            environment.transition(current_state)
    

    def stimulate(self, clk, environment):
        # choose an action to take based on each case
        self.take_action(environment)


    def select_tauPolicy(self, environment):
        policy_type = np.random.binomial(1, self.epsilon)
                    
        #greedy-Epsilon Policy
        if(policy_type == 1):
            q_values = environment.get_tau_q_values()
            column_0 = [row[0] for row in q_values]
            max_action = max(column_0)
                #if(max_action != 0):
                #print "column_0", column_0
                #print "max_action ", max_action
                #self.wait_debug("just wait .. ")
            index = column_0.index(max_action)
            action = self.taus[index]
        
        #Random Policy
        else:
            index = randrange(0, len(self.taus))
            action = self.taus[index]
        
        # return Policy
        return action
 

    def random_idel2active(self):
        action =  randrange(0, 1)
        return action

    def select_nPolicy(self, environment):
        policy_type = np.random.binomial(1, self.epsilon)
        sq_count = environment.queue_count()
        #greedy-Epsilon Policy
        if(policy_type == 1):
            q_values = environment.get_n_q_values()
            column_0 = [row[sq_count] for row in q_values]
            max_action = max(column_0)
            index = column_0.index(max_action)
            action = self.Ns[index]

        #Random Policy
        else:
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
