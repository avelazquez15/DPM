import numpy as np
from random import randrange
import Queue
import matplotlib.pyplot as plt

class Service_Queue:
 
    
    def __init__(self, size):
        self.q = Queue.Queue()
        self.queue_size = size
    
    def add(self, requests):
        if(self.q.qsize() < self.queue_size):
            self.q.put(requests)
            return True
        else:
            return False

    def get(self):
        if(self.q.qsize() > 0):
           return self.q.get()
        else:
           return 0
           

    def view(self):
        print "QUEUE: ", list(self.q.queue)
        #print(self.q.qsize())
        #plt.stem(list(self.q.queue))
        #plt.ylabel('Requests')
        #plt.xlabel('queue index')
        #plt.show()


    def is_empty(self):
        return self.q.empty()

    def queue(self):
        return self.q

    def count(self):
        return self.q.qsize()




