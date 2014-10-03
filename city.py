'''
Created on 2010-06-04

@author: rv
'''
from globals import *
from utils import Enumerate as Enum
#from math import sqrt, copysign
import random
import math
from itertools import product
from floyd import Floyd


class City():

    '''
    classdocs ground
    '''

    ''' ground constants '''
    groundTypes = Enum('NONE STREET FOOD')

    colorGround = {
        groundTypes.NONE: colorWhite,
        groundTypes.STREET: colorYellow,
        groundTypes.FOOD: colorRed
    }

    ''' streets constants '''
    ''' Connectors : North, east, south, west '''
    streetPattern = {
#        'none':     [0b00000, 0b00000, 0b00000, 0b00000],
        'hori':     [0b00000, 0b00100, 0b00000, 0b00100],
        'hori-n':   [0b00100, 0b00100, 0b00000, 0b00100],
        'hori-s':   [0b00000, 0b00100, 0b00100, 0b00100],
        'vert':     [0b00100, 0b00000, 0b00100, 0b00000],
        'vert-e':   [0b00100, 0b00100, 0b00100, 0b00000],
        'vert-w':   [0b00100, 0b00000, 0b00100, 0b00100],
        'turn-ne':  [0b00100, 0b00100, 0b00000, 0b00000],
        'turn-nw':  [0b00100, 0b00000, 0b00000, 0b00100],
        'turn-se':  [0b00000, 0b00100, 0b00100, 0b00000],
        'turn-sw':  [0b00000, 0b00000, 0b00100, 0b00100],
        'cross':    [0b00100, 0b00100, 0b00100, 0b00100]
    }

    class Node():
        def __init__(self, type, color):
            self.type = type
            self.color = color
            self.agent = None

    class Food(Node):

        __FOOD_CAPACITY_MAX = 100

        def __init__(self, type, color):
            City.Node.__init__(self, type, color)
            self.capacityMax = City.Food.__FOOD_CAPACITY_MAX
            self.capacity = City.Food.__FOOD_CAPACITY_MAX

        def getCapacity(self):
            return self.capacity

        def consCapacity(self):
            return self.capacity
            """self.capacity, c = 0, self.capacity
            return c"""

        def grow(self, alpha):
            self.capacity = min(self.capacity + alpha, self.capacityMax)

    '''
    classdocs map
    '''
    class Region():
        def __init__(self, i, j, width, height):
            self.location = (i, j)
            self.size = (width, height)
            self.center = (i + width / 2, j + height / 2)

    class House(Region):
        def __init__(self, i, j, width, height):
            City.Region.__init__(self, i, j, width, height)
            self.vacancy = None

    class Market(Region):
        def __init__(self, i, j, width, height):
            City.Region.__init__(self, i, j, width, height)
            # open / close

    '''
    classdocs city
    '''
    def __init__(self, (width, height)):
        '''
        Constructor
        '''
        self.groundWidth = width
        self.groundHeight = height
        self.ground = [[City.Node(City.groundTypes.NONE, City.colorGround[City.groundTypes.NONE]) for i in xrange(width)] for j in xrange(height)]
        self.map = {'houses': [], 'markets': [], 'grid': []}
        """ graph = { N: {'pos':(X,Y), 'edges':[P,Q]}} """
        self.graph = self.generate(10, 10)
        self.pathfinder = Floyd(self.graph)
#        self.dist = lambda (x1, y1), (x2, y2): math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        self.dist = lambda (x1, y1), (x2, y2): abs(x2 - x1) + abs(y2 - y1)
        """G = {
        0: {'pos': (0, 0), 'edges': [1, 3]},
        1: {'pos': (0, 0), 'edges': [0, 2]},
        2: {'pos': (0, 0), 'edges': [1, 3, 4]},
        3: {'pos': (0, 0), 'edges': [0, 2]},
        4: {'pos': (0, 0), 'edges': [0]}
        }
        floyd = Floyd(G)
        print floyd.C"""

    __BORDER_CONNSTREET_PROBA__ = 2
    __AVENUE_CONNSTREET_PROBA__ = 2
    __HOUSE_MINSIZE__ = 5

    def generate(self, sw, sh):
        width = self.groundWidth / sw
        height = self.groundHeight / sh

        for i, j in product(xrange(width), xrange(height)):
            self.map['grid'].append((i * sw, j * sh, sw, sh))

        streetmap = [['none' for i in xrange(height)] for j in xrange(width)]

        # first, start with border streets
        for i in xrange(1, width - 1):
            streetmap[i][0] = 'hori-s' if random.randint(0, City.__BORDER_CONNSTREET_PROBA__) else 'hori'
            self.draw(streetmap[i][0], i * sw, 0, sw, sh)
            streetmap[i][height - 1] = 'hori-n' if random.randint(0, City.__BORDER_CONNSTREET_PROBA__) else 'hori'
            self.draw(streetmap[i][height - 1], i * sw, (height - 1) * sh, sw, sh)

        for j in xrange(1, height - 1):
            streetmap[0][j] = 'vert-e' if random.randint(0, City.__BORDER_CONNSTREET_PROBA__) else 'vert'
            self.draw(streetmap[0][j], 0, j * sh, sw, sh)
            streetmap[width - 1][j] = 'vert-w' if random.randint(0, City.__BORDER_CONNSTREET_PROBA__) else 'vert'
            self.draw(streetmap[width - 1][j], (width - 1) * sw, j * sh, sw, sh)

        # and corners
        streetmap[0][0] = 'turn-se'
        self.draw('turn-se', 0, 0, sw, sh)
        streetmap[width - 1][0] = 'turn-sw'
        self.draw('turn-sw', (width - 1) * sw, 0, sw, sh)
        streetmap[width - 1][height - 1] = 'turn-nw'
        self.draw('turn-nw', (width - 1) * sw, (height - 1) * sh, sw, sh)
        streetmap[0][height - 1] = 'turn-ne'
        self.draw('turn-ne', 0, (height - 1) * sh, sw, sh)

        # second, randomly populate cells excluding but compatible with borders and corners
        checkNeighbour = {
            # compatibility rules between connectors a,b
            'W': lambda a, b: a[1] ^ b[3],
            'E': lambda a, b: a[3] ^ b[1],
            'N': lambda a, b: a[2] ^ b[0],
            'S': lambda a, b: a[0] ^ b[2]
        }
        cells = [(i, j) for i, j in product(xrange(width), xrange(height)) if i > 0 and i < width - 1 and j > 0 and j < height - 1]
        random.shuffle(cells)
        patterns = City.streetPattern.keys()
        for i, j in cells:
            random.shuffle(patterns)
            for pattern in patterns:
                # build neighbourhood list
                neighbours = [(neighbour, streetmap[i + dx][j + dy])
                    for neighbour, dx, dy in [('W', -1, 0), ('E', +1, 0), ('N', 0, -1), ('S', 0, +1)] if streetmap[i + dx][j + dy] != 'none']
                # check pattern is valid with neighbours
                connectors = City.streetPattern[pattern]
                for neighbour, pattern1 in neighbours:
                    if checkNeighbour[neighbour](City.streetPattern[pattern1], connectors):
                        break
                else:
                    # pattern is valid
                    streetmap[i][j] = pattern
                    self.draw(pattern, i * sw, j * sh, sw, sh)
                    break

        # third, add avenues using border connectors
        table = {
        'vert': {
            'none': 'vert',
            'hori': 'cross',
            'hori-n': 'cross',
            'hori-s': 'cross',
            'turn-ne': 'vert-e',
            'turn-nw': 'vert-w',
            'turn-se': 'vert-e',
            'turn-sw': 'vert-w'},
        'hori': {
            'none': 'hori',
            'vert': 'cross',
            'vert-e': 'cross',
            'vert-w': 'cross',
            'turn-ne': 'hori-n',
            'turn-nw': 'hori-n',
            'turn-se': 'hori-s',
            'turn-sw': 'hori-s'}
        }

        def translate(pattern, mask):
            try:
                return table[mask][pattern]
            except KeyError:
                return pattern

        avenues = [i for i in xrange(1, width - 2) if streetmap[i][0] == 'hori-s' and random.randint(0, City.__AVENUE_CONNSTREET_PROBA__)]
        sh2 = sh / 2
        for i in avenues:
            # modify ground
            x = i * sw + sw / 2
            for y in xrange(self.groundHeight - sh):
                self.setLocationType(x - 1, y + sh2, City.groundTypes.STREET)
                self.setLocationType(x, y + sh2, City.groundTypes.STREET)
                self.setLocationType(x + 1, y + sh2, City.groundTypes.STREET)
            # modify streetmap patterns
            # first pattern is already set
            for j in xrange(1, height):
                # in-between patterns
                streetmap[i][j] = translate(streetmap[i][j], 'vert')
            else:
                # last closure pattern
                streetmap[i][j] = 'hori-n'

        sw2 = sw / 2
        avenues = [j for j in xrange(1, height - 2) if streetmap[0][j] == 'vert-e' and random.randint(0, City.__AVENUE_CONNSTREET_PROBA__)]
        for j in avenues:
            # modify ground
            y = j * sh + sh / 2
            for x in xrange(self.groundHeight - sh):
                self.setLocationType(x + sw2, y - 1, City.groundTypes.STREET)
                self.setLocationType(x + sw2, y, City.groundTypes.STREET)
                self.setLocationType(x + sw2, y + 1, City.groundTypes.STREET)
            # modify streetmap patterns
            # first pattern is already set
            for i in xrange(1, width):
                # in-between patterns
                streetmap[i][j] = translate(streetmap[i][j], 'hori')
            else:
                # last closure pattern
                streetmap[i][j] = 'vert-w'

        # fourth, build graph
        graph = {}
        grid = {}

        """ nodes """
        sw2 = sw / 2 + 1
        sh2 = sh / 2 + 1
        k = 0
        for i, j in product(xrange(width), xrange(height)):
            if streetmap[i][j] != 'none' and streetmap[i][j] != 'hori' and streetmap[i][j] != 'vert':
                graph[k] = {'pos': (i * sw + sw2, j * sh + sh2), 'edges': []}
                grid[(i, j)] = k
                k += 1

        """ edges """
        def cast(i0, j0, diri, dirj):
            try:
                i = i0 + diri
                j = j0 + dirj
                while (True):
                    if streetmap[i][j] == 'none':
                        break
                    if diri and streetmap[i][j] == 'hori':  # and i > 0 and i < width:
                        i += diri
                    elif dirj and streetmap[i][j] == 'vert':  # and j > 0 and j < height:
                        j += dirj
                    else:
                        break
                return grid[(i, j)]
            except KeyError:
                return None

        for (i0, j0), k in grid.iteritems():
            pattern = streetmap[i0][j0]
            if pattern == 'hori-n':
                graph[k]['edges'].append(cast(i0, j0, 0, -1))
                graph[k]['edges'].append(cast(i0, j0, -1, 0))
                graph[k]['edges'].append(cast(i0, j0, +1, 0))
            elif pattern == 'hori-s':
                graph[k]['edges'].append(cast(i0, j0, 0, +1))
                graph[k]['edges'].append(cast(i0, j0, -1, 0))
                graph[k]['edges'].append(cast(i0, j0, +1, 0))
            elif pattern == 'vert-e':
                graph[k]['edges'].append(cast(i0, j0, +1, 0))
                graph[k]['edges'].append(cast(i0, j0, 0, -1))
                graph[k]['edges'].append(cast(i0, j0, 0, +1))
            elif pattern == 'vert-w':
                graph[k]['edges'].append(cast(i0, j0, -1, 0))
                graph[k]['edges'].append(cast(i0, j0, 0, -1))
                graph[k]['edges'].append(cast(i0, j0, 0, +1))
            elif pattern == 'turn-ne':
                graph[k]['edges'].append(cast(i0, j0, 0, -1))
                graph[k]['edges'].append(cast(i0, j0, +1, 0))
            elif pattern == 'turn-nw':
                graph[k]['edges'].append(cast(i0, j0, 0, -1))
                graph[k]['edges'].append(cast(i0, j0, -1, 0))
            elif pattern == 'turn-se':
                graph[k]['edges'].append(cast(i0, j0, 0, +1))
                graph[k]['edges'].append(cast(i0, j0, +1, 0))
            elif pattern == 'turn-sw':
                graph[k]['edges'].append(cast(i0, j0, 0, +1))
                graph[k]['edges'].append(cast(i0, j0, -1, 0))
            elif pattern == 'cross':
                graph[k]['edges'].append(cast(i0, j0, 0, -1))
                graph[k]['edges'].append(cast(i0, j0, 0, +1))
                graph[k]['edges'].append(cast(i0, j0, -1, 0))
                graph[k]['edges'].append(cast(i0, j0, +1, 0))

            # filter edge cases
            graph[k]['edges'] = [edge for edge in graph[k]['edges'] if edge is not None]

        # fith, add buildings
        """ scan empty spans """
        def scan(width, height):
            spans = []
            span = None
            for j in xrange(height):
                for i in xrange(width):
                    if self.getLocationType(i, j) is self.groundTypes.NONE:
                        if span is None:
                            span = (i, j, 0, 1)
                        else:
                            i0, j0, w, h = span
                            span = (i0, j0, i - i0 + 1, h)
                    elif self.getLocationType(i, j) is not self.groundTypes.NONE:
                        if span is not None:
                            spans.append(span)
                        span = None
                else:
                    if span is not None:
                        spans.append(span)
                    span = None
            return spans

        """ compact spans to regions """
        def compact(spans):
            spans.sort(key=lambda span: span[0])
            for n in xrange(len(spans) - 1):
                i0, j0, w0, h0 = spans[n]
                i, j, w, h = spans[n + 1]
                # condition : same origin, same width and adjacent
                if i == i0 and w == w0 and not (j - j0 - h0):
                    spans[n] = None
                    spans[n + 1] = (i0, j0, w, h0 + h)
            return [span for span in spans if span is not None]

        builds = compact(scan(self.groundWidth, self.groundHeight))

        """ generate markets """
        markets = [build for build in builds if build[2] == build[3]]
        for market in markets:
            i0, j0, w, h = market
            M = City.Market(i0, j0, w, h)
            self.map['markets'].append(M)
            builds.remove(market)
            # add food
            for i, j in product(xrange(w), xrange(h)):
                self.setLocationType(i0 + i, j0 + j, City.groundTypes.FOOD)

        """ generate houses """
        def split(i, j, w, h):
            w2 = w / 2
            h2 = h / 2
            if w2 < City.__HOUSE_MINSIZE__ and h2 < City.__HOUSE_MINSIZE__:
                self.map['houses'].append(City.House(i, j, w, h))
                return
            # case 1 : vertical split
            if w2 < City.__HOUSE_MINSIZE__:
                split(i, j, w, h2)
                split(i, j + h2, w, h - h2)
            # case 2 : horizontal split
            elif h2 < City.__HOUSE_MINSIZE__:
                split(i, j, w2, h)
                split(i + w2, j, w - w2, h)
            # case 1 : split all
            else:
                split(i, j, w2, h2)
                split(i + w2, j, w - w2, h2)
                split(i, j + h2, w2, h - h2)
                split(i + w2, j + h2, w - w2, h - h2)

        """ split builds into houses """
        for i, j, w, h in builds:
            split(i, j, w, h)

        return graph

    """ This table is describing how to draw each corner
    [{horizontal offsets x, y and range} or None, {vertical offsets x, y and range} or None]
    """
    streetShape = {
        'hori':     [{'offx': 0, 'offy': 0.5, 'range': 1}, None],
        'hori-n':   [{'offx': 0, 'offy': 0.5, 'range': 1}, {'offx': 0.5, 'offy': 0, 'range': 0.5}],
        'hori-s':   [{'offx': 0, 'offy': 0.5, 'range': 1}, {'offx': 0.5, 'offy': 0.5, 'range': 0.5}],
        'vert':     [None, {'offx': 0.5, 'offy': 0, 'range': 1}],
        'vert-e':   [{'offx': 0.5, 'offy': 0.5, 'range': 0.5}, {'offx': 0.5, 'offy': 0, 'range': 1}],
        'vert-w':   [{'offx': 0, 'offy': 0.5, 'range': 0.5}, {'offx': 0.5, 'offy': 0, 'range': 1}],
        'turn-ne':  [{'offx': 0.5, 'offy': 0.5, 'range': 0.5}, {'offx': 0.5, 'offy': 0, 'range': 0.5}],
        'turn-nw':  [{'offx': 0, 'offy': 0.5, 'range': 0.7}, {'offx': 0.5, 'offy': 0, 'range': 0.5}],
        'turn-se':  [{'offx': 0.5, 'offy': 0.5, 'range': 0.5}, {'offx': 0.5, 'offy': 0.5, 'range': 0.5}],
        'turn-sw':  [{'offx': 0, 'offy': 0.5, 'range': 0.5}, {'offx': 0.5, 'offy': 0.5, 'range': 0.5}],
        'cross':    [{'offx': 0, 'offy': 0.5, 'range': 1}, {'offx': 0.5, 'offy': 0, 'range': 1}]
    }

    def draw(self, pattern, i, j, width, height):
        try:
            shape = City.streetShape[pattern][0]
            if shape:
                ox = int(float(width) * shape['offx'])
                oy = int(float(height) * shape['offy'])
                r = int(float(width) * shape['range'])
                for k in xrange(r):
                    self.setLocationType(ox + i + k, oy + j, City.groundTypes.STREET)
                    self.setLocationType(ox + i + k, oy + j + 1, City.groundTypes.STREET)
            shape = City.streetShape[pattern][1]
            if shape:
                ox = int(float(width) * shape['offx'])
                oy = int(float(height) * shape['offy'])
                r = int(float(width) * shape['range'])
                for k in xrange(r):
                    self.setLocationType(ox + i, oy + j + k, City.groundTypes.STREET)
                    self.setLocationType(ox + i + 1, oy + j + k, City.groundTypes.STREET)
        except KeyError:
            print "City:draw Key error"

    ''' ground '''
    def getHeight(self):
        return self.groundHeight

    def getWidth(self):
        return self.groundWidth

    ''' locations '''
    def isLocationValid(self, i, j):
        try:
            return (i >= 0 and i < self.groundWidth and j >= 0 and j < self.groundHeight)
        except IndexError:
            return False

    '''TODO: include node max capacity?'''
    def isLocationFree(self, i, j):
        try:
            return (not self.ground[i][j].agent)
        except IndexError:
            return False

    def setLocationType(self, i, j, type):
        try:
            if type == City.groundTypes.FOOD:
                self.ground[i][j] = City.Food(type, City.colorGround[type])
            else:
                self.ground[i][j].type = type
                self.ground[i][j].color = City.colorGround[type]
        except IndexError:
            pass

    def getLocationType(self, i, j):
        try:
            return self.ground[i][j].type
        except IndexError:
            return City.groundTypes.NONE

    def setLocationColor(self, i, j, color):
        try:
            self.ground[i][j].color = color
        except IndexError:
            pass

    def getLocationColor(self, i, j):
        try:
            return self.ground[i][j].color
        except IndexError:
            return colorWhite

    def getRandomFreeLocation(self, (xmin, ymin), (xmax, ymax), type=None):
        # build a list of free locations i.e. where env.getAgent(x,y) == None
        # we don't use a global list and we re-build the list each time
        # because init a new agent is much less frequent than updating agent's position (that would require append / remove to the global list)
        freeLocations = [(i, j) for i, j in product(range(xmin, xmax), range(ymin, ymax)) if self.isLocationFree(i, j) and (type == None or self.ground[i][j].type == type)]
        # return random free location if exist
        if len(freeLocations) > 0:
            return freeLocations[random.randint(0, len(freeLocations) - 1)]
        return None

    def consCapacity(self, (i, j)):
        try:
            if isinstance(self.ground[i][j], City.Food):
                return self.ground[i][j].consCapacity()
        except IndexError:
            pass
        return 0

    ''' map '''
    def getRegions(self, key=None):
        if key is None:
            # append all regions
            regions = self.map['houses']
            regions.extend(self.map['markets'])
        else:
            try:
                regions = self.map[key]
            except KeyError:
                return None
        return regions

        ''' graph '''
    def getGraph(self):
        return self.graph

    def getClosestNodes(self, start, goal):
        ks = None
        kg = None
        dsmin = 1000000
        dgmin = 1000000
        for i, node in self.graph.iteritems():
            ds = self.dist(node['pos'], start)
            if ds < dsmin:
                dsmin = ds
                ks = i
            dg = self.dist(node['pos'], goal)
            if dg < dgmin:
                dgmin = dg
                kg = i
        return (ks, kg)

    def getNodePos(self, i):
        try:
            x, y = self.graph[i]['pos']
            return (x, y)
        except KeyError:
            return None

    def getPath(self, i, j):
        return self.pathfinder.path(i, j)

    def getNext(self, i, j):
        k = self.pathfinder.next(i, j)
        return j if k == Floyd.__FLOYD_MAXVALUE__ else k

    ''' agents '''
    def setAgent(self, (i, j), agent):
        try:
            self.ground[i][j].agent = agent
        except IndexError:
            pass

    def getAgent(self, (i, j)):
        try:
            return self.ground[i][j].agent
        except IndexError:
            return None
