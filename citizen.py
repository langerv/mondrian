'''
Created on 2010-06-04

@author: rv
'''
from globals import *
from agent import Agent
import random
import math


class Citizen(Agent):
    '''
    classdocs
    '''
    __AGENT_MAX_TYPES = 2

    def __init__(self, city, location):
        '''
        Constructor
        '''
        Agent.__init__(self, city, location)
        self.type = random.randint(0, Citizen.__AGENT_MAX_TYPES)
        self.color = colorBlue if self.type else colorRed
        self.groundType = city.getLocationType(location[0], location[1])
        self.regions = None
        self.path = None
#        self.dist = lambda (x1, y1), (x2, y2): math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        self.dist = lambda (x1, y1), (x2, y2): abs(x2 - x1) + abs(y2 - y1)

    '''
    rules
    '''
    def getColor(self):
        return self.color

    def setRegions(self, regions):
        if self.regions:
            self.regions.extend(regions)
        else:
            self.regions = regions

    # MOVE:`
    def move(self):
        if not self.path:
            city = self.getEnvironment()
            random.shuffle(self.regions)
            target = self.regions[0]
            t = (random.randint(target.location[0], target.location[0] + target.size[0]),
                random.randint(target.location[1], target.location[1] + target.size[1]))
            (s, g) = city.getClosestNodes(self.location, t)
            self.path = [city.getNodePos(i) for i in city.getPath(s, g)]
            self.path.append(t)
        elif self.path:
            if self.dist(self.path[0], self.location) < 1:
                self.path.pop(0)
                if not self.path:
                    return False
            Agent.move(self, self.path[0][0] - self.location[0], self.path[0][1] - self.location[1])
        return True
