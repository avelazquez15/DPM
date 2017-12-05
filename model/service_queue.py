import numpy as np
from random import randrange
import Queue
import matplotlib.pyplot as plt
import math
from collections import deque
import termios, fcntl, sys, os


class Service_Queue:
 
    
    def __init__(self, size):
        self.q = Queue.Queue()
        self.queue_size = size
        self.timer = 0
        self.running = False
        self.effective_packets = 10
        self.request_arrival = deque()
    
    def add(self, requests):
        available_space = self.queue_size - self.q.qsize()
        available_packets = available_space * self.effective_packets
        
        if(requests < available_packets):
            space2use = math.ceil(requests/self.effective_packets)
            packets = 0
            mirror_time = self.timer
            for slot in range(0, int(space2use)+1):
                
                packets += self.effective_packets
                if(packets < requests):
                     self.q.put(self.effective_packets)
                else:
                    self.q.put(packets - requests)
                
                #print "Arrival time @ index: " , self.timer, " @ ", self.q.qsize()-1
                self.request_arrival.append(self.timer)
        
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
        print "ARRIVAL: ", list(self.request_arrival)
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

    def queue_list(self):
        return list(self.q.queue)

    def length(self):
        return self.queue_size

# packet details
    def request_time(self):
        times = list(self.request_arrival)
        if(len(times) > 0):
            return self.request_arrival.popleft()

# Timer details
    def increment_timer(self):
        if(self.running == True):
            self.timer += 1

    def start_timer(self):
        self.running = True

    def is_running(self):
        return self.running

    def timer_value(self):
        return self.timer

    def reset_timer(self):
        self.timer = 0


# debugging
    def wait_debug(self, message):
        print "[DEBUG] ", message
        sys.stdin.read(1)





