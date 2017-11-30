import numpy as np
from random import randrange
import Queue

class Service_Queue:
    
    def __init__(self):
        self.q = Queue.Queue()
    
    def add(self, requests):
        self.q.put(requests)

    def get(self):
        return self.q.get()

    def view(self):
        print(self.q.qsize())

    def is_empty(self):
        return self.q.empty()




