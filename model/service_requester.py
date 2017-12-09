import numpy as np
from random import randrange
import random
import matplotlib.pyplot as plt
import math


class Service_Requester:
  
    def __init__(self, size):
        self.file_name =  "inter_arrival_time.csv"

        self.inter_arrival = self.read_file(self.file_name)


    def inter_arrivals(self):
        return self.inter_arrival

    def time(self, value):
        return value in self.inter_arrival

    def request_count(self):
        return randrange(1, 10)

    def view(self):
        plt.stem( self.inter_arrival)
        plt.ylabel('Inter Arrival Time')
        plt.xlabel('global clock')
        plt.show()

    def read_file(self, file_name):
        x = []
        with open(file_name, 'rb') as f:
            for line in f:
                x.append(int(line))

        return x

    def generate_number(self, size):
        x = []
        n = 0
        
        while(n < size/25):
            n += 1
            num = np.random.randint(0, size)
            x.append(num)

        return sorted(set(x))
