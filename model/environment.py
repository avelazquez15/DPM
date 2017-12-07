import numpy as np
import service_queue as q
import service_provider as sp
import service_requester as sr
from random import randrange
import termios, fcntl, sys, os

class environment:
    
    def __init__(self, request_size, queue_size, requests_per_episode, episodes):
        # environment needs
        self.power_profile = {"active": 1, "idle" : 0.80, "sleep": 0.1}     # mW
        self.current_action = -1
        self.process_time = 1
        self.cost_init = 0
        self.cost_final = 0
        self.under_N_poicy = False
        self.requests_processed = 0
        self.active_process = 0
        self.current_episode = 1
        self.Max_Episode = episodes
        self.active  = 1
        self.idle    = 2
        self.sleep   = 3
        self.gamma = 0.8
        
        
        # SQ, SP, SR
        queue_size = queue_size + 1
        self.requests_per_episode = requests_per_episode
        self.service_provider = sp.Service_Provider(self.sleep)
        self.service_requester = sr.Service_Requester(request_size)
        self.service_queue = q.Service_Queue(queue_size)
        
        
        # transition history details
        self.snapshot = np.zeros(6)
        self.transition_dir = ""
        self.state_value_transitions = []
        self.state_action_transitions = []
        self.human_history = []
        
        
        # instantaneous rewards
        self.i_rewards = np.zeros((3,queue_size))

        
        # rewards
        self.rewards = []
        self.state_action_rewards = []
        self.total_rewards = 0
        
        
        # returns
        self.returns = []
        
        
        # state-value and state-action functions (tau and N-Policy)
        self.state_value = np.ones((3,queue_size))*-1000
        self.tau_state_action_values = []
        self.n_state_action_values = []


        # formatting
        np.set_printoptions(threshold='nan')

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
                self.wait_debug("queue is full ...")
    
        self.service_queue.increment_timer()
        #take snapshot of state
        self.take_snapshot()
      
    def check_queue(self):
        if(self.current_state() == self.active):
            print "[QUEUE]   Before -", self.service_queue.view_queue()
            #print "[ARRIVAL] Before -", self.service_queue.view_request_arrival()
            self.service_queue.get()
            self.active_process += 1
        else:
            self.active_process = 0

    def view_status(self):
            print "[QUEUE]   After -", self.service_queue.view_queue()
            #print "[ARRIVAL] After -", self.service_queue.view_request_arrival()

    def setup(self, tau_state_action_len, n_state_action_len):
        # Case 1 & 2 (Tau Policy)
        # shape = (depth, rows, columns)
        shape = (tau_state_action_len, self.service_queue.queue_size)
        self.tau_state_action_values = np.ones(shape)*-1000

        # Case 3 & 4 (N-Policy)
        # shape = (depth, rows, columns)
        shape = (n_state_action_len, self.service_queue.queue_size)
        self.n_state_action_values = np.ones(shape)*-1000
    
    
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

        self.service_provider.transition_period += 1
        delay = self.service_provider.get_transition_delay(self.transition_dir)
        print "self.service_provider.transition_period = ", self.service_provider.transition_period
        
        # transition delay complete
        if(self.service_provider.transition_period == delay):
            self.service_provider.transition_period = 0
            
            # human readable transition
            transition = ([self.state_str(current_state)],[self.queue_count()])
            self.human_history.append(transition)
            
            # environment transition history
            transition = ([current_state-1],[self.queue_count()])
            self.state_value_transitions.append(transition)
            
            state_action = ([current_state-1],[self.queue_count()])
            self.self.state_action_transitions.append(state_action)

            
            # evaluate cost for (current_state,SQ.count) pair
            self.evaluate_cost(current_state, True)
            
            # reset new case variables
            self.service_provider.set_cycle(0)
            self.service_provider.set_time_out(0)
            self.service_provider.set_duration(0)
            
            # change to new case
            new_state = self.service_provider.get_transition(self.transition_dir)
            print "current state :", "[", self.state_str(current_state), ",", self.queue_count() ,"]"
            print "next state :", new_state , "[", self.state_str(new_state), ",", self.queue_count() ,"]"
            self.change_state(new_state)
            
            
            
            # check for a completion of an episode
            if(self.requests_processed == self.requests_per_episode):
                print "\n\n\nTransition History: count = ", len(self.human_history), "\n", self.human_history
                    
                print "\n\n\nRewards History: count = ", len(self.rewards),  "\n", self.rewards

                self.evaluate_returns()
                self.requests_processed = 0
                if(self.current_episode == self.Max_Episode):
                    

                    message = "Episode", self.current_episode,
                    self.wait_debug(message)

                self.current_episode += 1
        else:
            self.evaluate_cost(current_state, False)


    def change_transition_delay(self, state, value):
        #print "change_transition_delay [state, value] =", "[",state, ",", value, "]"
        self.service_provider.set_transition_delay(state, value)

    def evaluate_transition(self):
        cost = self.cost(self.current_state(), self.transition_dir)
        self.update_i_rewards(self.current_state(), self.queue_count(), cost)
    
#evaluate cost function
    def evaluate_cost(self, current_state, valid_transition):
        cost = self.cost(current_state, self.transition_dir)
        self.update_i_rewards(current_state, self.queue_count(), cost)
    
        if(valid_transition):
            self.rewards.append(cost)
            self.state_action_rewards.append(cost)
    
# cost function value details
    def cost(self, state, direction):
        a = 0.45
        cost_value = self.delay_cost(state, direction)
        energy_value = self.power_cost(state)
        
        print "cost_value: ", cost_value
        print "a*cost_value", a*cost_value
        
        print
        print "energy_value: ", energy_value
        print "(1-a)*energy_value: ", (1-a)*energy_value
        return  -1*(a*cost_value + (1-a)*energy_value)

    def delay_cost(self, state, direction):
        if(state == self.sleep  and self.under_N_poicy == True):     # Case 3 & 4
            delay = (self.cost_final - self.cost_init)
            A = 34
        
        elif(state == self.active and self.service_queue.request_arrival_count() > 0):    # Case 6
            self.cost_init = self.service_queue.request_time()
            delay = (self.cost_final - self.cost_init)
            self.requests_processed += 1
            A = 6
                
        elif(state == self.idle):               # Case 1 & 2
            timeout = self.service_provider.get_cycle()
            delay = timeout + self.service_provider.get_transition_delay(direction)
            A = 12
        
        else:                                                           # Case 5 & 7
            delay = self.service_provider.get_transition_delay(direction)
            A = 57

        print "[A:",A,"]"," delay, final: ", delay, " , ", self.cost_final

        return delay + self.process_time

    def power_cost(self, state):
        cycle_duration = self.service_provider.get_duration()
        power = self.power_profile[self.state_str(state)]
        energy = power*cycle_duration
        
        print "cycle_duration: ", cycle_duration
        
        return energy
    
# Evaluation of Rewards, Returns, State-Value Function, and State-Action-Value Details
    def update_i_rewards(self, state, queue_count, value):
        #cycle = queue_count
            #if(state == 1):
            #cycle = self.active_process
        
        self.i_rewards[state-1][queue_count] = value
        print "[UPDATE] \n", self.i_rewards

    def evaluate_returns(self):
        
        self.evaluate_state_values()

        
        self.total_rewards = sum(self.rewards)
        
        if(self.current_episode == self.Max_Episode):
            sv = list([i/self.Max_Episode for i in self.state_value])
            print "\n\n\n State Values:\n", sv
            print "total_rewards = ", self.total_rewards
        

        self.returns = []
        self.rewards = []
        self.state_value_transitions = []
        self.human_history = []
    
    def evaluate_state_values(self):
        g = self.gamma
        size = len(self.state_value_transitions)
        n = size - 1
        state = self.state_value_transitions[n]
        Rn = self.rewards[n]
        Gn = Rn
        
        while(n >= 0):
            n -= 1
            Rn = self.rewards[n]
            self.returns.insert(0, Rn + g* Gn)
            Gn = Rn
        
        print "\n\nReturns:\n", self.returns
        #self.update_return(state,  Rn + g* Gn)
        print
        #self.show_transition()
        
        index = 0
        for state in self.state_value_transitions:
            Gt = self.returns[index]
            if(self.is_sv_updated(state) == -1000):
                self.update_state_value(state, Gt)
            index += 1


    def update_state_value(self, state, value):
        self.state_value[state] = float(str(round(value, 2)))
    
    def is_sv_updated(self, state):
        return  self.state_value[state]
    
    
    #def evaluate_state_actions(self):
    
    
# debugging
    def wait_debug(self, message):
        print "[DEBUG] ", message
        sys.stdin.read(1)


    def show_transition(self):
        n = 0
        size = len(self.human_history)
        
        print "show_transition(self) {size}: ", size
        while(n < size-1):
            print self.human_history[n], "{Gt:", self.returns[n], "}",\
                "->", self.human_history[n+1],"{Gt:", self.returns[n+1], "}", "\n"
            n += 2

        if(size % 2 != 0):
            print self.human_history[n],"{Gt:", self.returns[n], "}\n\n",







