#!/usr/bin/env python3

import argparse
import csv
import collections
import logging
import random
from discrete_event_sim import Simulation, Event
import random
import matplotlib.pyplot as plt

class MMN(Simulation):

    def __init__(self, lambd, mu, n, d):
        if n < d:
            raise ValueError('d must be less than n')

        super().__init__()
        self.arrivals = {}      
        self.completions = {}   
        self.lambd = lambd
        self.n = n
        self.d = d
        self.mu = mu
        self.arrival_rate = lambd * n
        self.completion_rate = mu * n
        self.idJob = 0 
        self.listOfJobs = {}        
        self.schedule(random.expovariate(lambd), Arrival(self.idJob, random.randint(0,self.n -1)))

        self.listOfStateServer = [None for _ in range(n)]                    
        self.listOfQueueServers = [collections.deque() for _ in range(n)]    
        self.listMesuration = []     
        self.listaSomme = []
        self.d_Server = {}

    
    def min_queue(self):
        self.d_Server = {}
        self.d_Server = random.sample(range(0, self.n), self.d)
        first = True
        ind = None
        for i in range(len(self.d_Server)):
            if first:
                min = self.queue_len(self.d_Server[i])
                ind = self.d_Server[i]
                first = False
                continue
            x = self.queue_len(self.d_Server[i])
            if (x < min):
                min = x
                ind = self.d_Server[i]
        return ind

    def schedule_arrival(self, job_id, priority): 
        if job_id % 2 == 0:
            for arrayN in range(self.n):
                self.listMesuration.append(self.queue_len(arrayN))
        self.priority = priority
        server_id = self.min_queue()
        self.schedule(random.expovariate(self.arrival_rate), Arrival(job_id,server_id))

    def schedule_completion(self, job_id, server_id):
        self.schedule(random.expovariate(self.mu), Completion(job_id, server_id))

    #@property
    def queue_len(self, queueId):
        return (self.listOfStateServer[queueId] is not None) + len(self.listOfQueueServers[queueId])
            
class Arrival(Event):

    def __init__(self, job_id, server_id):
        self.server_id = server_id
        self.job_id = job_id
        self.priority = random.randint(0,3)

    def process(self, sim: MMN):
        sim.listOfJobs[self.job_id] = self.priority
        # print("JOB ID ", self.job_id, "PRIORITA ", self.priority)
        sim.arrivals[self.job_id] = sim.t
        if sim.listOfStateServer[self.server_id] is None:
            sim.listOfStateServer[self.server_id] = self.job_id
            sim.schedule_completion(self.job_id, self.server_id)
        else:
           sim.listOfQueueServers[self.server_id].append(self.job_id)
        sim.schedule_arrival(self.job_id + 1, self.priority)

class Completion(Event):
    def __init__(self, job_id,server_id):
        self.server_id = server_id
        self.job_id = job_id  

    def process(self, sim: MMN):
        assert sim.listOfStateServer[self.server_id] is not None
        sim.completions[self.job_id] = sim.t
        if sim.listOfQueueServers[self.server_id]: # if the queue is not empty
            maxPriority = -1
            next_job_id = -1    
            indx = -1
            for i, job in enumerate(sim.listOfQueueServers[self.server_id]): # for each job
                indx = i 
                if sim.listOfJobs[job] == 3: # if the job have the max priority
                    next_job_id = job
                    break
                elif maxPriority < sim.listOfJobs[job]:
                    maxPriority = sim.listOfJobs[job]
                    next_job_id = job
            
            if indx >= 0:
                del sim.listOfQueueServers[self.server_id][indx]
                sim.listOfStateServer[self.server_id] = next_job_id
                sim.schedule_completion(next_job_id,self.server_id) # schedule its completion
        else:
            sim.listOfStateServer[self.server_id] = None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lambd', type=float, default=0.5)
    parser.add_argument('--mu', type=float, default=1)
    parser.add_argument('--max-t', type=float, default=1_000_000)#1_000_000
    parser.add_argument('--n', type=int, default=100)
    parser.add_argument('--d', type=int, default=1)
    parser.add_argument('--csv', help="CSV file in which to store results")
    parser.add_argument("--seed", help="random seed")
    parser.add_argument("--verbose", action='store_true')
    parser.add_argument("--createCsv", help='creazione csv')
    args = parser.parse_args()

    if args.seed:
        random.seed(args.seed)  # set a seed to make experiments repeatable
    if args.verbose:
        logging.basicConfig(format='{levelname}:{message}', level=logging.INFO, style='{')  # output info on stdout

    sim = MMN(args.lambd, args.mu, args.n, args.d)
    print("LAMBDA ", args.lambd, " MU ", args.mu, " N ", args.n, " D ", args.d)
    sim.run(args.max_t)
    completions = sim.completions
    W = (sum(completions.values()) - sum(sim.arrivals[job_id] for job_id in completions)) / len(completions)
    print(f"Average time spent in the system: {W}")
    print(f"Theoretical expectation for random server choice: {1 / (1 - args.lambd)}")

    if args.csv is not None:
        with open(args.csv, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([args.lambd, args.mu, args.max_t, W])
    if args.createCsv is not None:
        with open(args.createCsv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(sim.listMesuration)

if __name__ == '__main__':
    main()
