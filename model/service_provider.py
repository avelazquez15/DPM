import numpy as np

class Service_Provider:
    def __init__(self, state):
        self.current_state = state

    def get_state(self):
        return self.current_state

    def set_state(self, state):
        self.current_state = state
