import numpy as np
from random import randrange
import Queue
import matplotlib.pyplot as plt

class Service_Queue:
 
    
    def __init__(self):
        self.q = Queue.Queue()
    
    def add(self, requests):
        self.q.put(requests)

    def get(self):
        return self.q.get()

    def view(self):
        #print(self.q.qsize())
        plt.stem(list(self.q.queue))
        plt.ylabel('Requests')
        plt.xlabel('queue index')
        plt.show()


    def is_empty(self):
        return self.q.empty()

    def queue(self):
        return self.q




