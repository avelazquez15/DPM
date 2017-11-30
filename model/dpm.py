import numpy as np
import service_queue as q
import service_provider as sp
import service_requester as sr

from random import randrange

class DPM:
    active = 1
    idle = 2
    sleep = 3
    
    def __init__(self, clk):
        self.service_provider = sp.Service_Provider(self.active)
        self.service_requester = sr.Service_Requester(1000, clk)
        self.service_queue = q.Service_Queue()
