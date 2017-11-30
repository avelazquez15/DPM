import numpy as np
from random import randrange

class Service_Requester:
    def __init__(self, size, clk):
        self.inter_arrival = np.zeros(size)
        while(clk < 30):
            self.inter_arrival[clk] = clk + randrange(100)
            clk += 1
        self.inter_arrival = list(set(self.inter_arrival))

    def inter_arrivals(self):
        return self.inter_arrival
