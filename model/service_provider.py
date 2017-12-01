import numpy as np

class Service_Provider:

    
    def __init__(self, state):
        self.current_state = state
        self.active  = 1
        self.idle    = 2
        self.sleep   = 3
        self.transition_delay = {   "active2idle": 1,   \
                                    "idle2active": 2,   \
                                    "idle2sleep": 1,    \
                                    "sleep2active": 4,  \
                                    "active2active": 1, \
                                    "sleep2sleep": 1}
        
        
        
        self.transition = { "active2idle": self.idle,       \
                            "idle2active": self.active,     \
                            "idle2sleep": self.sleep,       \
                            "sleep2active": self.active,    \
                            "active2active": self.active,   \
                            "sleep2sleep": self.sleep}

        self.transition_period = 0

    def get_state(self):
        return self.current_state

    def set_state(self, state):
        self.current_state = state

    def get_transition_delay(self, value):
        return self.transition_delay[value]

    def get_transition(self, value):
        return self.transition[value]
