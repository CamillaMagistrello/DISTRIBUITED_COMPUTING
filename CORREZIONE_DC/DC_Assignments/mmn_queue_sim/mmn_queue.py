#!/usr/bin/env python

import argparse
import csv
import collections
from random import expovariate
import random
from matplotlib import pyplot as plt

import math
from discrete_event_sim import Simulation, Event

# To use weibull variates, for a given set of parameter do something like
# from weibull import weibull_generator
# gen = weibull_generator(shape, mean)
#
# and then call gen() every time you need a random variable
from enum import Enum
 
class LoadBalancer(Enum):
    RANDOM = 1
    BASIC_SUPERMARKET = 2
    EXTENSION_SUPERMARKET = 3

class MMN(Simulation):

    def __init__(self, lambd, mu, n, balancer):
        super().__init__()

        self.arrivals = {}  # dictionary mapping job id to arrival time
        self.completions = {}  # dictionary mapping job id to completion time
        self.lambd = lambd
        self.n = n
        self.last_job=0
        self.mu = mu
        self.arrival_rate = lambd * n
        self.completion_rate = mu 
        self.balancer= balancer
        
        if n != 1:
            self.queues = collections.deque()  # FIFO queue of the system
            self.running = []
            for s in range(n):
                self.queues.append(collections.deque())
                self.running.append( None)
            self.schedule(expovariate(self.arrival_rate ), Arrival_n(0,0))
            
        else:
            self.running = None  # if not None, the id of the running job
            self.queue = collections.deque()  # FIFO queue of the system
          
            self.schedule(expovariate(self.arrival_rate ), Arrival(0))


    def load_balancer_extension(self):
        result=1000000
        result_index = 0

        d = self.n
        start = 0
        if self.n > 3:
            d = math.floor(abs(self.n/2))
            start = random.randint(0, self.n-1)

            for i in range(start, (d + start)):

                # Make it ring
                index = i
                total_queues = self.n
                if  total_queues <= i:
                    index = i % total_queues
                
                if result > len(self.queues[index]):
                    result = len(self.queues[index])
                    result_index = index
        else:
            for q in range(len(self.queues)):
                if result > len(self.queues[q]):
                    result = len(self.queues[q])
                    result_index = q

        return result_index
    
    def load_balancer_basic(self):
        result=1000000
        index = 0
        d = self.n
        generated_no= []

        if self.n > 3:
            d = math.floor(abs(self.n/2))
            
            #Loop for d times
            for i in range(0, d):
                
                while True:
                    #Generate random index between 0-n
                    random_index = random.randint(0,self.n-1)

                    #Check if already generated or not
                    if random_index in generated_no:
                        continue
                    else:
                        generated_no.append(random_index)
                        break 

                if result > len(self.queues[random_index]):
                    result = len(self.queues[random_index])
                    index = random_index
        else:
            for q in range(len(self.queues)):
                if result > len(self.queues[q]):
                    result = len(self.queues[q])
                    index = q

        return index
    
    def load_balancer_random(self):
        index = random.randint(0, self.n-1)
        return index
    
    def schedule_arrival_n(self, job_id, index):
        # schedule the arrival following an exponential distribution, to compensate the number of queues the arrival
        # time should depend also on "n"
        delay = expovariate(self.arrival_rate) #random delay

        if self.balancer ==  LoadBalancer.RANDOM:
            index = self.load_balancer_random()
        elif self.balancer == LoadBalancer.BASIC_SUPERMARKET:
            index = self.load_balancer_basic()
        elif self.balancer == LoadBalancer.EXTENSION_SUPERMARKET:
            index = self.load_balancer_extension()

        self.schedule(delay, Arrival_n(job_id,index))

    def schedule_completion_n(self, job_id,index):
        # schedule the time of the completion event
        delay = expovariate(self.completion_rate) #random delay
        self.schedule(delay, Completion_n(job_id,index))

   


    def schedule_arrival(self, job_id):
        # schedule the arrival following an exponential distribution, to compensate the number of queues the arrival
        # time should depend also on "n"
        delay = expovariate(self.arrival_rate) #random delay
        self.schedule(delay, Arrival(job_id))

    def schedule_completion(self, job_id):
        # schedule the time of the completion event
        delay = expovariate(self.completion_rate) #random delay
        self.schedule(delay, Completion(job_id))

    @property
    def queue_len(self):
        return (self.running is None) + len(self.queue)
    

class Arrival_n(Event):

    def __init__(self, job_id,index):
        self.id = job_id
        self.index = index


    def process(self, sim: MMN):
        # set the arrival time of the job
        # print('Job ',self.id,' is arrived for server: ', self.index)
        
        sim.arrivals[self.id] = {'t':sim.t, 'queue': self.index}

        # if there is no running job, assign the incoming one and schedule its completion
        if sim.running[self.index] is None:
            sim.running[self.index] = self.id
            sim.schedule_completion_n(self.id, self.index)
        # otherwise put the job into the queue
        else:
            sim.queues[self.index].append(self.id)
        
        # schedule the arrival of the next job
        sim.schedule_arrival_n(sim.last_job + 1, self.index) # let's assume next id will be plus one
        sim.last_job = sim.last_job + 1

class Completion_n(Event):
    def __init__(self, job_id, index):
        self.id = job_id  # currently unused, might be useful when extending
        self.index = index

    def process(self, sim: MMN):
        # print('Job ',self.id,' is completion for server: ', self.index)

        assert sim.running[self.index] is not None
        # set the completion time of the running job
        sim.completions[sim.running[self.index]] = sim.t

        # if the queue is not empty
        if len(sim.queues[self.index]) > 0:
            # get a job from the queue
           
            sim.running[self.index] =  sim.queues[self.index].popleft()
            
            # schedule its completion
            sim.schedule_completion_n(sim.running [self.index],self.index)
        else:
            sim.running[self.index] = None


class Arrival(Event):

    def __init__(self, job_id):
        self.id = job_id

    def process(self, sim: MMN):
        # set the arrival time of the job
        
        sim.arrivals[self.id] = sim.t

        # if there is no running job, assign the incoming one and schedule its completion
        if sim.running is None:
            sim.running = self.id
            sim.schedule_completion(self.id)
        # otherwise put the job into the queue
        else:
            sim.queue.append(self.id)
        
        # schedule the arrival of the next job
        sim.schedule_arrival(self.id + 1) # let's assume next id will be plus one

class Completion(Event):
    def __init__(self, job_id):
        self.id = job_id  # currently unused, might be useful when extending

    def process(self, sim: MMN):
        assert sim.running is not None
        # set the completion time of the running job
        sim.completions[sim.running] = sim.t

        # if the queue is not empty
        if len(sim.queue) > 0:
            # get a job from the queue
           
            sim.running =  sim.queue.popleft()
            
            # schedule its completion
            sim.schedule_completion(sim.running )
        else:
            sim.running = None


def main():

    balancers = [LoadBalancer.RANDOM]
    lambdas = [0.50 ,0.90 ,0.95 ,0.99]
    ns = [2, 5, 10 ,20, 50, 100]
    mu = 1
    max_t = 100000
    csv_mmn = "mmn.csv"
    csv_mm1 = "mm1.csv"
    csv_jobs = "jobs.csv"
    
    with open(csv_jobs, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Queues','Lambd', 'Arrived_Jobs', 'Completed_Jobs', 'Difference', 'Load_Balancer'])
    
    with open(csv_mm1, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Queues','Lambd', 'Mu', 'Max_T', 'Average_Time', 'Actual_Time'])
    
    with open(csv_mmn, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Queues','Lambd', 'Mu', 'Max_T', 'Average_Time', 'Actual_Time','Load_Balancer'])

    for n in ns:
        for lambd in lambdas:
            for b in balancers:

                print(f'Running For n: {n}, lambd: {lambd}, balancer: {b}')
                sim = MMN(lambd, mu, n, b)
                sim.run(max_t)
                arrived_jobs = len(sim.arrivals)
                completed_jobs = len(sim.completions)
                
                completions = sim.completions

                if n !=1:
                    W = (sum(completions.values()) - sum(sim.arrivals[job_id]['t'] for job_id in completions)) / len(completions)
                else:
                    W = (sum(completions.values()) - sum(sim.arrivals[job_id]  for job_id in completions)) / len(completions)

                T = 1 / float(1 - lambd)

                print(f"Average time spent in the system: {W}")
                print(f"Theoretical expectation for random server choice: {T}")
                print(f"T: {T}, W: {W}") 
                file = csv_mm1 if n == 1 else csv_mmn 
                with open(file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([n, lambd, mu, max_t, T, W] if n==1 else [n, lambd, mu, max_t, T, W, b.name])
                with open(csv_mmn, 'r') as f:
                    print("Content of mmn.csv:")
                    print(f.read())
                with open(csv_jobs, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([n, lambd,arrived_jobs, completed_jobs, arrived_jobs-completed_jobs, b.name])
                
                if n ==1: break


if __name__ == '__main__':
    main()
