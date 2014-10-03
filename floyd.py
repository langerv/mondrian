import sys


class Floyd():
    '''
    classdocs floyd
    '''

    __FLOYD_MAXVALUE__ = sys.maxint

    def __init__(self, g):
        '''
        Constructor
        '''
        n = len(g)
        self.C = [[Floyd.__FLOYD_MAXVALUE__ for i in xrange(n)] for j in xrange(n)]
        L = [[Floyd.__FLOYD_MAXVALUE__ for i in xrange(n)] for j in xrange(n)]
        for i, node in g.iteritems():
            for j in node['edges']:
                L[i][j] = 1
        for i in xrange(n):
            L[i][i] = 0
        for k in xrange(n):
            for i in xrange(n):
                for j in xrange(n):
                    if L[i][k] + L[k][j] < L[i][j]:
                        L[i][j] = L[i][k] + L[k][j]
                        self.C[i][j] = k

    """ retreive full path """
    def path(self, i, j):
        path = [i]

        # recursive closure
        def subpath(i, j):
            k = self.C[i][j]
            if k == Floyd.__FLOYD_MAXVALUE__:
                return
            subpath(i, k)
            path.append(k)
            subpath(k, j)
            
        subpath(i, j)
        path.append(j)
        return path

    """ get next k from i, j """
    def next(self, i, j):
        try:
            return self.C[i][j]
        except IndexError:
            return None
