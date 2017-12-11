import numpy as np
import service_queue as q
import service_provider as sp
import service_requester as sr
from random import randrange
import termios, fcntl, sys, os
import math
import matplotlib.pyplot as plt


class environment:
    
    def __init__(self, request_size, queue_size, requests_per_episode, episodes, runs):
        # environment needs
        self.power_profile = {"active": 1, "idle" : 0.80, "sleep": 0.01}     # mW
        self.current_action = -1
        self.process_time = 1
        self.cost_init = 0
        self.cost_final = 0
        self.under_N_poicy = False
        self.requests_processed = 0
        self.active_process = 0
        self.current_episode = 1
        self.current_run = 0
        self.Max_Episode = episodes
        self.Max_runs = runs
        self.active  = 1
        self.idle    = 2
        self.sleep   = 3
        self.gamma   = 0.95
        self.alpha   = 0.1
        self.case_number = 0
        self.defualt_reward = 0
        self.valid_state_action = False
        self.valid_state_value = False
        self.accum_rewards = []
        self.internal_clock = 0
        self.average_runs = np.zeros((runs, episodes))
        self.average_delays_per_episode = np.zeros((episodes, requests_per_episode))
        self.average_delays = []
        
        # SQ, SP, SR
        queue_size = queue_size + 2
        self.requests_per_episode = requests_per_episode
        self.service_provider = sp.Service_Provider(self.idle)
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
        self.state_action_returns = []
        
        
        # state-value and state-action functions (tau and N-Policy)
        self.state_value = np.ones((3,queue_size))*self.defualt_reward
        self.tau_state_action_values = []
        self.n_state_action_values = []


        # formatting
        np.set_printoptions(threshold='nan')


# non-stationary
    def stimulate(self, clk):
        self.internal_clock += 1
        #check if inter arrival request has arrived
        if(self.service_requester.time(self.internal_clock)):
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
            #print "[QUEUE]   Before -", self.service_queue.view_queue()
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
        shape = (tau_state_action_len, 2)#self.service_queue.queue_size)
        self.tau_state_action_values = np.ones(shape)*self.defualt_reward

        # Case 3 & 4 (N-Policy)
        # shape = (depth, rows, columns)
        shape = (n_state_action_len, self.requests_per_episode+1)#self.service_queue.queue_size)
        self.n_state_action_values = np.ones(shape)*self.defualt_reward
    
    
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
        #print "self.service_provider.transition_period = ", self.service_provider.transition_period
        
        self.store_state_action_pair(current_state)
        self.store_state_value_pair(current_state)
        
        # transition delay complete
        if(self.service_provider.transition_period == delay):
            self.service_provider.transition_period = 0
            
            # evaluate cost for (current_state,SQ.count) pair
            self.evaluate_cost(current_state)
            

            
            if(current_state != "active2active"):
                # reset new case variables
                self.service_provider.set_cycle(0)
                self.service_provider.set_time_out(0)
                self.service_provider.set_duration(0)
            
            # change to new case
            new_state = self.service_provider.get_transition(self.transition_dir)
            #print "current state :", "[", self.state_str(current_state), ",", self.queue_count() ,"]"
            #print "next state :", new_state , "[", self.state_str(new_state), ",", self.queue_count() ,"]"
            self.change_state(new_state)
            
            
            # check for a completion of an episode
            if(self.requests_processed == self.requests_per_episode):
                #print "\n\n\nTransition History: count = ", len(self.state_value_transitions), "\n", self.state_value_transitions
                    
                    #print "\n\n\nRewards History: count = ", len(self.rewards),  "\n", self.rewards

                self.evaluate_returns()
                self.requests_processed = 0
                self.internal_clock = 0
                if(self.current_episode == self.Max_Episode):
                    self.current_run += 1
                    #message = "Episode", self.current_episode,
                    #self.wait_debug(message)
                    self.current_episode = 0
                    
                if(self.current_run == self.Max_runs):
                    self.accum_rewards = self.average_over_runs()
                    print self.accum_rewards
                    plt.plot(self.accum_rewards[1:])
                    plt.ylabel("Accum. Rewards")
                    plt.xlabel("Episode")
                    plt.show()
                    message = "Run:", self.current_run,
                    self.wait_debug(message)

                self.current_episode += 1
        else:
            self.evaluate_cost(current_state)


    def change_transition_delay(self, state, value):
        #print "change_transition_delay [state, value] =", "[",state, ",", value, "]"
        self.service_provider.set_transition_delay(state, value)

    def store_state_action_pair(self, current_state):
        # state-action transition history
        #({SP state, SQ count}, action taken)
        #state = self.service_provider.get_transition(self.transition_dir)
        #current_state = self.state_str(state)
        #current_state = current_state - 1
        
        if(current_state == self.idle):
            transition = ([current_state],          \
                          [0],                      \
                          [self.current_action])
        else:
            transition = ([current_state],          \
                          [self.queue_count()],     \
                          [self.current_action])
        
        if(self.is_state_action_allowed(transition)):
            self.state_action_transitions.append(transition)

    def store_state_value_pair(self, current_state):
        # environment transition history
        sq_count = self.queue_count()
        transition = ([current_state-1],[sq_count])
        
        if(self.is_state_value_allowed(transition)):
            self.state_value_transitions.append(transition)
            # human readable transition
            transition = ([self.state_str(current_state)],[sq_count])
            self.human_history.append(transition)
    
#evaluate cost function
    def evaluate_cost(self, current_state):

        
        cost = self.cost(current_state, self.transition_dir)
        cost = float(str(round(cost, 2)))

        if(self.valid_state_action):
            self.state_action_rewards.append(cost)
            self.valid_state_action = False
        else:
            if(len(self.state_action_rewards) > 0):
                index = len(self.state_action_rewards) - 1
                self.state_action_rewards[index] = cost

    
        if(self.valid_state_value):
            self.rewards.append(cost)
            if(current_state == self.sleep):
                self.service_provider.set_duration(0)
            self.valid_state_value = False

        else:
            if(len(self.rewards) > 0):
                index = len(self.rewards) - 1
                self.rewards[index] = cost
    
# cost function value details
    def cost(self, state, direction):
        a = 0.0
        delay_value = self.delay_cost(state, direction)
        energy_value = self.power_cost(state)
        
        #self.average_delays_per_episode[self.current_episode -1 ][self.requests_processed-1] = delay_value
        
        #print "cost_value: ", cost_value
        #print "a*cost_value", a*cost_value
        
        #print
        #print "energy_value: ", energy_value
        #print "(1-a)*energy_value: ", (1-a)*energy_value
        #self.wait_debug("cost ... ")
        return  -1*(a*delay_value + (1-a)*energy_value)

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

#print "[A:",A,"]"," delay, final: ", delay, " , ", self.cost_final

        return math.pow(delay, 1.5)+ self.process_time

    def power_cost(self, state):
        if(state == self.sleep  and self.under_N_poicy == True):     # Case 3 & 4
            cycle_duration = self.service_provider.get_duration()
            A = 34
        
        elif(state == self.active and self.queue_count() > 0):    # Case 6
            cycle_duration = 1
            A = 6
            #print "[",A, "] cycle_duration", cycle_duration

        
        elif(state == self.idle):               # Case 1 & 2
            cycle_duration = self.service_provider.get_cycle()
            A = 12
        
        else:                                                           # Case 5 & 7
            cycle_duration = self.service_provider.get_duration()
            A = 57


        old_state = state

        if(self.transition_dir == "sleep2active"):
            state = self.service_provider.get_transition(self.transition_dir)



        power = self.power_profile[self.state_str(state)]
        energy = power*cycle_duration

        '''
        print "state: (", self.state_str(old_state), self.queue_count(), ")"
        print "power: ", power
        print "cycle_duration: ", cycle_duration
        print "energy: ", energy
        self.wait_debug("calcualting energy ... ")
        '''
        return energy
    
# Evaluation of instantenous Rewards
    def update_i_rewards(self, state, queue_count, value):
        #cycle = queue_count
            #if(state == 1):
            #cycle = self.active_process
        
        self.i_rewards[state-1][queue_count] = value
#print "[UPDATE] \n", self.i_rewards

# Evaluate Returns, State-Value Function, and State-Action-Value Function
    def evaluate_returns(self):
        
        self.evaluate_state_values()
        self.evaluate_state_action_values()
        
        self.total_rewards = sum(self.rewards)
        self.total_rewards = float(str(round(self.total_rewards, 2)))

        self.average_runs[self.current_run][self.current_episode-1] = self.total_rewards

#average = np.mean(self.average_delays_per_episode[self.current_episode-1])
#self.average_delays.append(average)
        self.show_transition()

        self.returns = []
        self.rewards = []
        self.state_value_transitions = []
        self.state_action_transitions = []
        self.state_action_rewards = []
        self.state_action_returns = []
        self.human_history = []
        self.total_rewards  = 0
    
    # state value rewards and returns
    def evaluate_state_values(self):
        g = self.gamma
        size = len(self.state_value_transitions)
        n = size - 1
        state = self.state_value_transitions[n]
        Rn = self.rewards[n]
        Gn = Rn
        Gn = float(str(round(Gn, 2)))
        self.returns.insert(0, Gn)
        
        while(n >= 0):
            n -= 1
            Rn = self.rewards[n]
            return_value = Rn + g* Gn
            return_value = float(str(round(return_value, 2)))
            self.returns.insert(0, return_value)
            Gn = Rn
    
        #update matrix
        index = 0
        for state in self.state_value_transitions:
            Gt = self.returns[index]
            if(self.is_sv_updated(state) == self.defualt_reward):
                self.update_state_value(state, Gt)
            index += 1

    # state-action rewards and returns
    def evaluate_state_action_values(self):
        g = self.gamma
        size = len(self.state_action_transitions)
        n = size - 1
        Rn = self.state_action_rewards[n]
        Gn = Rn
        Gn = float(str(round(Gn, 2)))
        self.state_action_returns.insert(0, Gn)
        
        while(n >= 0):
            n -= 1
            Rn = self.state_action_rewards[n]
            return_value = Rn + g* Gn
            return_value = float(str(round(return_value, 2)))
            self.state_action_returns.insert(0, return_value)

            # hold previous return
            Gn = Rn
                
                
        #update matrix
        for index in np.arange(0, len(self.state_action_transitions)):
            state_action = self.state_action_transitions[index]
            state = state_action[2], state_action[1]
            Gt = self.state_action_returns[index]
            SP_State = state_action[0][0]
           
           #print self.state_str(SP_State)
            if(not self.is_Q_tau_updated(state, SP_State)):
                self.update_state_action_value(state, Gt, SP_State)
            
            if(not self.is_Q_n_updated(state, SP_State)):
                #self.wait_debug("hit ...")
                self.update_state_action_value(state, Gt, SP_State)





# check if transition, action, or state is allowed
    def update_state_value(self, state, value):
        old_estimate = self.state_value[state]
        target = float(str(round(value, 2)))
        
        self.state_value[state] = old_estimate + self.alpha*(target - old_estimate)
    
    def is_sv_updated(self, state):
        return self.state_value[state]
    
    
    def is_Q_tau_updated(self, state, SP_State):

        if(SP_State == self.idle):
            #print "is_Q_tau_updated ", state
            value = int(self.tau_state_action_values[state])
            if(value ==  self.defualt_reward):
                return  False
            
            else:
                return True
    
    def is_Q_n_updated(self, state, SP_State):
        if(SP_State == self.sleep):
            value = int(self.n_state_action_values[state])
            if(value ==  self.defualt_reward):
                return  False
            
            else:
                    return True

    def get_tau_q_values(self):
        return self.tau_state_action_values

    def get_n_q_values(self):
        return self.n_state_action_values
    
    def update_state_action_value(self, state, value, SP_State):

        target = float(str(round(value, 2)))
        if(SP_State == self.idle):
            old_estimate = self.tau_state_action_values[state]
            self.tau_state_action_values[state] = old_estimate + self.alpha*(target - old_estimate)
        
        elif(SP_State == self.sleep):
            old_estimate = self.n_state_action_values[state]
            self.n_state_action_values[state] = old_estimate + self.alpha*(target - old_estimate)
    
    def is_tau_sv_updated(self, state):
        return  self.tau_state_action_values[state]
    
    
    def is_n_sv_updated(self, state):
        return  self.n_state_action_values[state]

    def is_state_action_allowed(self, state_action_pair):

        current_length = len(self.state_action_transitions)
        current_index = current_length - 1

        try:
            state_action_index = self.state_action_transitions.index(state_action_pair)
            current_pair = self.state_action_transitions[current_index]
                
            if(current_pair == state_action_pair):
                self.valid_state_action = False
                return self.valid_state_action

            else:
                self.valid_state_action = True
                return self.valid_state_action
                    
        except ValueError:
                self.valid_state_action = True
                return self.valid_state_action

    def is_state_value_allowed(self, state_value_pair):

        current_length = len(self.state_value_transitions)
        current_index = current_length - 1

        
        try:
            state_value_index = self.state_value_transitions.index(state_value_pair)
            current_pair = self.state_value_transitions[current_index]
            
            
            if(current_pair == state_value_pair):
                self.valid_state_value = False
                return self.valid_state_value
            
            else:
                self.valid_state_value = True
                return self.valid_state_value

        except ValueError:
            self.valid_state_value = True
            return self.valid_state_value


# converging
    def get_average_run_column(self, index):
        column = [self.average_runs[row][index] for row in np.arange(0, self.Max_runs)]
        return sum(column)

    def average_over_runs(self):
        runs = []
        for ep in np.arange(0, self.Max_Episode):
            value = self.get_average_run_column(ep)
            runs.insert(ep, value)
    
        average = [i/float(self.Max_runs) for i in runs]
        average = [float(str(round(i, 2))) for i in average]
        return average



# debugging
    def wait_debug(self, message):
        print "[DEBUG] ", message
        sys.stdin.read(1)


    def show_transition(self):
        print "\n" * 15
        n = 0
        size = len(self.rewards)
        
        print "state_value_transitions(self) {size}: ", size
        '''
        while(n < size-2):
            print self.human_history[n], "{Rt:", self.rewards[n], "}",\
            "->", self.human_history[n+1],"{Rt:", self.rewards[n+1], "}", "\n"
            n += 2

        if(size % 2 != 0):
            print self.human_history[n],"{Rt:", self.rewards[n], "}\n\n",
        '''



#                    "\n\n\nself.average_runs\n\n", str(self.average_runs),                         \


        report =    "tau_state_action_values\n\n", str(self.tau_state_action_values),                   \
                    "\n\n\nself.n_state_action_values\n\n", str(self.n_state_action_values),            \
                    "\n\nself.average_delays, ", str(self.average_delays),                              \
                    "\n\nProgress:\nEpisode: ", str(self.current_episode), "/", str(self.Max_Episode),  \
                    "\nRun: ", str(self.current_run+1), "/", str(self.Max_runs)
        self.write2file(report, "debug_report.txt")







    def write2file(self, data, file_name):
        f = open(file_name,"w")
        n = 0
        f.writelines(data)
        f.writelines("\n\n\n\n")
        f.close()







