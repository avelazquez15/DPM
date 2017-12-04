import numpy as np

class Service_Provider:

    
    def __init__(self, state):
        self.current_state = state
        self.active  = 1
        self.idle    = 2
        self.sleep   = 3
        self.transition_delay = {   "active2idle": 1,   \
                                    "idle2active": 2,   \
                                    "idle2sleep": 2,    \
                                    "sleep2active": 6,  \
                                    "active2active": 1, \
                                    "sleep2sleep": 1}
        
        
        
        self.transition = { "active2idle": self.idle,       \
                            "idle2active": self.active,     \
                            "idle2sleep": self.sleep,       \
                            "sleep2active": self.active,    \
                            "active2active": self.active,   \
                            "sleep2sleep": self.sleep}

        self.transition_period = 0
        self.time_out = 0
        self.cycle = 0
        self.duration = 0
    
# state
    def get_state(self):
        return self.current_state

    def set_state(self, state):
        self.current_state = state
    
# transition delay
    def get_transition_delay(self, value):
        return self.transition_delay[value]

    def set_transition_delay(self, state, value):
        self.transition_delay[state] = value

# transition
    def get_transition(self, value):
        return self.transition[value]
    
# transition period
    def get_transition_period(self):
        return self.transition_period

    def set_transition_period(self, value):
        self.transition_period = value
    
# time out
    def get_time_out(self):
        return self.time_out

    def set_time_out(self, value):
            self.time_out = value

# cycle
    def get_cycle(self):
        return self.cycle

    def set_cycle(self, value):
        self.cycle = value

#duration
    def get_duration(self):
        return self.duration

    def set_duration(self, value):
        self.duration = value
