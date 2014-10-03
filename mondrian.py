'''
Created on 2010-06-04

@author: rv
'''
import pygame
from pygame.locals import *
from globals import *
import random
from itertools import product
from city import City
from citizen import Citizen

"""
initial simulation parameters
"""

# view
screenSize = 800, 800
fps = 30
printInfos = False
displayGrid = False
displayRegions = False
displayGraph = False

# city global parameters
citySize = 100, 100
numCitizen = 200


"""
View Class
"""


class View:
    # this gets called first
    def __init__(self, screenSize, city, citizens):
        # init view
        pygame.init()
        pygame.display.set_caption("Automated Mondrian")
        self.screenSize = screenSize
        self.screen = pygame.display.set_mode(screenSize)
        width = city.getWidth()
        self.cellSize = screenSize[0] / width
        self.radius = int(self.cellSize * 0.5)
        self.quit = False
        # init city
        self.city = city
        # init agents population
        self.citizens = citizens
        self.population = [len(self.citizens)]
        # init time
        self.iteration = 0
        self.clock = pygame.time.Clock()

    # drawing code, called once
    def draw(self):
        # display city
        width = city.getWidth()
        height = city.getHeight()
        for i, j in product(range(width), range(height)):
            pygame.draw.rect(self.screen, city.getLocationColor(i, j), (i * self.cellSize, j * self.cellSize, self.cellSize, self.cellSize))

        houses = city.getRegions('houses')
        for house in houses:
            x0, y0 = house.location
            w, h = house.size
            pygame.draw.rect(self.screen, colorYellow, (x0 * self.cellSize, y0 * self.cellSize, w * self.cellSize, h * self.cellSize), 2)

        # display agents
        for citizen in citizens:
            (x, y) = citizen.getLocation()
            pygame.draw.rect(self.screen, citizen.getColor(), (x * self.cellSize, y * self.cellSize, self.cellSize, self.cellSize))

        pygame.display.flip()

    # update code
    def update(self):
        # execute agents randomly
        random.shuffle(citizens)
        # run agents' rules
        for citizen in citizens:
            # MOVE
            (x0, y0) = citizen.getLocation()
            citizen.move()
            # update visual if alive
            if citizen.isAlive():
                (x1, y1) = citizen.getLocation()
                if (x0, y0) != (x1, y1):
                    pygame.draw.rect(self.screen, city.getLocationColor(x0, y0), (x0 * self.cellSize, y0 * self.cellSize, self.cellSize, self.cellSize))
                    pygame.draw.rect(self.screen, citizen.getColor(), (x1 * self.cellSize, y1 * self.cellSize, self.cellSize, self.cellSize))
            # remove citizen if dead
            else:
                # free environment
                city.setAgent(citizen.getLocation(), None)
                # remove or replace agent
                citizens.remove(citizen)
                # clean city
                pygame.draw.rect(self.screen, city.getLocationColor(x0, y0), (x0 * self.cellSize, y0 * self.cellSize, self.cellSize, self.cellSize))

        pygame.display.flip()

    def drawGrid(self):
        grid = city.getRegions('grid')
        for x0, y0, w, h in grid:
            pygame.draw.rect(self.screen, colorRedSat, (x0 * self.cellSize, y0 * self.cellSize, w * self.cellSize, h * self.cellSize), 2)
        pygame.display.flip()

    def drawRegions(self):
        regions = city.getRegions()
        for region in regions:
            x0, y0 = region.location
            w, h = region.size
            if isinstance(region, City.House):
                pygame.draw.rect(self.screen, colorBlue, (x0 * self.cellSize, y0 * self.cellSize, w * self.cellSize, h * self.cellSize), 2)
            elif isinstance(region, City.Market):
                pygame.draw.rect(self.screen, colorRed, (x0 * self.cellSize, y0 * self.cellSize, w * self.cellSize, h * self.cellSize), 2)
        pygame.display.flip()

    def drawGraph(self):
        myfont = pygame.font.SysFont("arial", 20)
        graph = city.getGraph()
        for i, node in graph.iteritems():
            x0, y0 = node['pos']
            pygame.draw.circle(self.screen, colorRedSat, (x0 * self.cellSize, y0 * self.cellSize), self.cellSize)

            for k in node['edges']:
                try:
                    x1, y1 = graph[k]['pos']
                    pygame.draw.line(self.screen, colorRedSat, (x0 * self.cellSize, y0 * self.cellSize), (x1 * self.cellSize, y1 * self.cellSize), self.cellSize)
                except KeyError:
                    print "drawGraph key error!"

            label = myfont.render(str(i), 1, (0, 0, 0))
            self.screen.blit(label, (x0 * self.cellSize, (y0 - 3) * self.cellSize))
        # debug pathfinding
        """citizen = citizens[0]
        if citizen.target is not None:
            x0, y0 = citizen.target.center
            pygame.draw.rect(self.screen, colorRedSat, (x0 * self.cellSize, y0 * self.cellSize, 1 * self.cellSize, 1 * self.cellSize), 2)
        if citizen.goal is not None:
            x0, y0 = graph[citizen.goal]['pos']
            pygame.draw.circle(self.screen, colorBlack, (x0 * self.cellSize, y0 * self.cellSize), self.cellSize)
        if citizen.next is not None:
            x0, y0 = graph[citizen.next]['pos']
            pygame.draw.circle(self.screen, colorBlue, (x0 * self.cellSize, y0 * self.cellSize), self.cellSize)"""
        # end debug
        pygame.display.flip()

    # the main loop

    def mainLoop(self):
        global printInfos, displayGrid, displayRegions, displayGraph
        dt = 0
        framecount = 0
        framerate = 0
        self.draw()
        update = True
        while not self.quit:
            t0 = pygame.time.get_ticks()

            # handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit = True
                elif event.type == KEYDOWN:

                    if event.key == K_F1:
                        printInfos = not printInfos

                    elif event.key == K_F2:
                        displayGrid = not displayGrid
                        if not displayGrid:
                            self.draw()

                    elif event.key == K_F3:
                        displayRegions = not displayRegions
                        if not displayRegions:
                            self.draw()

                    elif event.key == K_F4:
                        displayGraph = not displayGraph
                        if not displayGraph:
                            self.draw()

                    elif event.key == K_F12:
                        update = not update

            # update city
            if update:
                self.update()
            # debug options
            if displayGrid:
                self.drawGrid()
            if displayRegions:
                self.drawRegions()
            if displayGraph:
                self.drawGraph()
            # iteration
            self.iteration += 1
            # wait simulation step
            self.clock.tick(fps)
            # calculate and display the framerate
            t1 = pygame.time.get_ticks()
            dt += t1 - t0
            framecount += 1
            if dt >= 1000:
                dt -= 1000
                framerate, framecount = framecount, 0

            # display infos
            if printInfos:
                print "Iteration = ", self.iteration, "; fps = ", framerate, "; Population = ", len(self.citizens)
                #print citizens[0].health

"""
Main
"""

if __name__ == '__main__':
    # build a city
    print "Generate city of size", citySize, "..."
    city = City(citySize)
    print len(city.getRegions('houses')), "houses generated"
    print len(city.getRegions('markets')), "markets generated"
    print len(city.getGraph()), "nodes in graph"

    # create a lit of citizens and place them into a city
    print "Generate", numCitizen, "agents..."
    citizens = []
    houses = [house for house in city.getRegions('houses') if house.vacancy is None]
    markets = city.getRegions('markets')
    for i in range(numCitizen):
        if len(houses):
            house = houses[random.randint(0, len(houses) - 1)]
            citizen = Citizen(city, house.location)
            houses.remove(house)
            house.vacancy = citizen
            citizen.setRegions([house])
            citizen.setRegions(markets)
            citizens.append(citizen)
        else:
            location = city.getRandomFreeLocation((0, 0), citySize, City.groundTypes.STREET)
            if location:
                citizen = Citizen(city, location)
                citizen.setRegions(markets)
                citizens.append(citizen)
            else:
                print "error: no more free location available!"
                break

    # Create a view with a city and citizens
    view = View(screenSize, city, citizens)
    # iterate
    view.mainLoop()
