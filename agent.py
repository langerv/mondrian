'''
@author: rv
'''
from globals import *
import random


class Agent():
    '''
    classdocs
    '''
    __AGENT_MAX_AGENT_METABOLISM = 4
    __AGENT_MAX_VISION = 6
    __AGENT_INIT_HEALTH = 500, 1000

    def __init__(self, environment, location):
        '''
        Constructor
        '''
        self.env = environment
        self.location = location
        self.env.setAgent(self.location, self)
        self.metabolism = random.randint(1, Agent.__AGENT_MAX_AGENT_METABOLISM)
        self.vision = Agent.__AGENT_MAX_VISION  # random.randint(1, Agent.__AGENT_MAX_VISION)
        self.health = random.randint(Agent.__AGENT_INIT_HEALTH[0], Agent.__AGENT_INIT_HEALTH[1])

    def getEnvironment(self):
        return self.env

    def getLocation(self):
        return self.location

    def getColor(self):
        return colorCyanS

    def setLocation(self, newLocation):
        self.env.setAgent(self.location, None)
        self.location = newLocation
        self.env.setAgent(self.location, self)

    def getMetabolism(self):
        return self.metabolism

    def getVision(self):
        return self.vision

    def isAlive(self):
        return (self.health > 0)

    '''
    rules
    '''
    # MOVE:
    def isLocationValid(self, i, j):
        env = self.getEnvironment()
        return env.isLocationValid(i, j) and env.isLocationFree(i, j)

    # build a list of free locations around
    def getNeighbourhood(self, (i, j)):
        neighbours = [(k, j) for k in range(i - self.vision, i + self.vision + 2) if self.isLocationValid(k, j)]
        neighbours.extend([(i, k) for k in range(j - self.vision, j + self.vision + 2) if self.isLocationValid(i, k)])
        return neighbours

    def move(self, di, dj):
        # normalize
        di = di / abs(di) if abs(di) > 1 else di
        dj = dj / abs(dj) if abs(dj) > 1 else dj
        if not di and not dj:
            return False
        # try move
        i, j = self.location
        if not self.isLocationValid(i + di, j + dj):
            # if not try around avoiding the obstacle
            for (di, dj) in {
                (1, 0): [(1, -1), (1, 1)],
                (-1, 0): [(-1, -1), (-1, 1)],
                (0, -1): [(-1, -1), (1, -1)],
                (0, 1): [(-1, 1), (1, 1)],
                (-1, -1): [(-1, 0), (0, -1)],
                (1, -1): [(0, -1), (1, 0)],
                (-1, 1): [(-1, 0), (0, 1)],
                (1, 1): [(0, 1), (1, 0)]
            }[(di, dj)]:
                if self.isLocationValid(i + di, i + dj):
                    break
            else:
                # else stay here and wait next turn
                return False

        # actual move in environment
        self.setLocation((i + di, j + dj))
        self.health = max(self.health + self.getEnvironment().consCapacity(self.location) - self.metabolism, 0)
        return True
