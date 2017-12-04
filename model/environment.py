import numpy as np
import service_queue as q
import service_provider as sp
import service_requester as sr
from random import randrange
import termios, fcntl, sys, os

class environment:
    
    def __init__(self, request_size, queue_size):
        self.active  = 1
        self.idle    = 2
        self.sleep   = 3
        self.service_provider = sp.Service_Provider(self.idle)
        self.service_requester = sr.Service_Requester(request_size)
        self.service_queue = q.Service_Queue(queue_size)
        self.snapshot = np.zeros(6)
        self.current_action = -1
        self.transition_dir = ""
        self.power_profile = {"active": 1, "idle" : 0.80, "sleep": 0.1}     # mW
        self.state_value = np.zeros((3,queue_size))
        self.process_time = 1
        self.cost_init = 0
        self.cost_final = 0
    
        print "STATE Value Function: \n", self.state_value
    
    #self.service_requester.view()

# non-stationary
    def stimulate(self, clk):
        #check if inter arrival request has arrived
        if(self.service_requester.time(clk)):
            #check if timer has been enabled
            if(not self.service_queue.is_running()):
                self.service_queue.start_timer()
            
            #inter arrival is true
            request_count = self.service_requester.request_count()
            if(not self.service_queue.add(request_count)):
                print "queue is full ..."
    
        self.service_queue.increment_timer()
        #take snapshot of state
        self.take_snapshot()
        self.check_queue()

      
      
      
    def check_queue(self):
        if(self.current_state() == self.active):
            print "Before -", self.service_queue.view()
            self.service_queue.get()
            print "After -", self.service_queue.view()

        
# state details/history
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


    def current_state(self):
        return self.service_provider.get_state()
    
    
    def t_minus_one(self):
        return self.snapshot[1]
    
    
    def change_state(self, state):
        self.service_provider.set_state(state)

    def state_str(self, state):
        if(state == 1):
            return "active"
        elif(state == 2):
            return "idle"
        elif(state == 3):
            return "sleep"

#queue details
    def view_queue(self):
        self.service_queue.view()

    def queue_count(self):
        return self.service_queue.count()
    
    def queue_len(self):
        return self.service_queue.length()


# Agent/Evironment interaction
    def transition(self, current_state):
        #message = " .. in transition ", self.state_str(current_state)
        #self.wait_debug(message)
        self.service_provider.transition_period += 1
        delay = self.service_provider.get_transition_delay(self.transition_dir)
        #print "delay .. transition: ", delay
        print "self.service_provider.transition_period = ", self.service_provider.transition_period
        
        if(self.service_provider.transition_period == delay):
            self.service_provider.transition_period = 0
            #print "transition direction:", self.transition_dir
            self.evaluate_cost(current_state)
            self.service_provider.set_cycle(0)
            self.service_provider.set_time_out(0)
            self.service_provider.set_duration(0)
            
            new_state = self.service_provider.get_transition(self.transition_dir)
            print "previous state :", current_state , "[", self.state_str(current_state), "]"
            print "next state :", new_state , "[", self.state_str(new_state), "]"
            self.change_state(new_state)


    def change_transition_delay(self, state, value):
        print "change_transition_delay [state, value] =", "[",state, ",", value, "]"
        self.service_provider.set_transition_delay(state, value)

    def evaluate_transition(self):
        cost = self.cost(self.current_state(), self.transition_dir)
        self.update_state_value(self.current_state(), self.queue_count(), cost)
    
#evaluate cost function
    def evaluate_cost(self, current_state):
        cost = self.cost(current_state, self.transition_dir)
        self.update_state_value(current_state, self.queue_count(), cost)
    
# state value details
    def cost(self, state, direction):
        a = 0.9
        return  -1*(a*self.delay_cost(state, direction) + (1-a)*self.power_cost(state))

    def delay_cost(self, state, direction):
        if(state == self.sleep):
            delay = (self.cost_final - self.cost_init)# + self.service_provider.get_transition_delay(direction)
            A = 2
        
        elif(state == self.active and direction == "active2active"):
            self.cost_init = self.service_queue.request_time()
            delay = (self.cost_final - self.cost_init)# + self.service_provider.get_transition_delay(direction)
            A = 3
        else:
            delay = self.service_provider.get_transition_delay(direction)
            A = 1
        

        
        print "[A:",A,"]","self.cost_final, self.cost_init, delay: ",self.cost_final, self.cost_init, delay
        return delay + self.process_time

    def power_cost(self, state):
        cycle_duration = self.service_provider.get_duration()

        power = self.power_profile[self.state_str(state)]
        energy = power*cycle_duration

#print "power_cost [cycle_duration, power] =", "[",cycle_duration, ",", power, "]"
#print "energy: ", energy

        return energy

    def update_state_value(self, state, queue_count, value):
        self.state_value[state-1][queue_count] = value
        print "[UPDATE] \n", self.state_value
    #print "\n[state, queue_count] = cost\n", "[", self.state_str(state), ",", queue_count, "] = ", value
    

    
# debugging
    def wait_debug(self, message):
        print "[DEBUG] ", message
        sys.stdin.read(1)








