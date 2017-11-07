import numpy as np
import operator as op
import itertools
from collections import OrderedDict

import piece
from piece import SHAPES

def coords(dims):
    assert len(dims) == 3
    return [(i,j,k)
            for i in range(dims[0])
            for j in range(dims[1])
            for k in range(dims[2])]

class Box(object):
    _idx = None
    _neighbors = None
    _valid_volumes = None
    valid_pending = 5
    def __init__(self, state = None, done = None, pending = SHAPES, dims=(4,4,4),
                 _parent = None):
        self.dims = dims
        if state is None:
            state = np.zeros(dims)
        if done is None:
            done = []
        self.m = state
        self.done = done
        self.pending = pending
        self._parent = _parent
        if _parent:
            self._idx = _parent._idx
            self._neighbors = _parent._neighbors
            self._valid_volumes = _parent._valid_volumes
        if not self._idx:
            self.build_position_index()

    def __repr__(self):
        p = self.show_tightness().astype("S")
        for d in self.done:
            for c in coords(self.dims):
                if d.m[c]:
                    p[c] = d.piece.shape.name
        return str(p)

    def build_position_index(self):
        if self._idx:
            return
        self._idx = dict()
        self._neighbors = dict()

        c = coords(self.dims)

        def neighbors(coord):
            for i in range(3):
                cc = list(coord)
                cc[i] -= 1
                if cc[i] >= 0:
                    yield cc
                cc = list(coord)
                cc[i] += 1
                if cc[i] < self.dims[i]:
                    yield cc
        for i in c:
            self._idx[i] = OrderedDict()
            self._neighbors[i] = map(tuple,neighbors(i))

        shapes = list(sorted(itertools.chain((p.piece.shape for p in self.done), self.pending), key=lambda s: s.name))
        for s in shapes:
            for i in c:
                self._idx[i][s] = []
            for p in s.positions():
                for i in c:
                    if p.m[i]:
                        self._idx[i][s].append(p)
        self._valid_volumes = set()
        sv = [np.array(s.m).sum() for s in shapes]
        for n in range(1,self.valid_pending):
            self._valid_volumes.update(
                itertools.imap(
                    sum,
                    itertools.combinations(sv, n)))

    def valid(self, pos):
        m = self.m + pos.m
        if m.max() > 1:
            return False
        return True

    def neighbors(self, coord):
        return self._neighbors[coord]

    def tightness(self, coord):
        if self.m[coord]:
            return 99
        return sum(1 - self.m[c] for c in self.neighbors(coord))

    def fill(self, m, c, v):
        pending = [c]
        colored = []
        while pending:
            c = pending.pop()
            if m[c] == 0:
                m[c] = v
                colored.append(c)
                pending.extend(self.neighbors(c))
        return colored

    def volumes(self):
        m = self.m.copy()
        a = []
        for c in coords(self.dims):
            if m[c] == 0:
                a.append(self.fill(m,c,len(a)+10))
        self._v = m
        return sorted((len(v), sorted(v)) for v in a)

    def show_tightness(self):
        t = np.zeros(self.dims, dtype=int)
        for c in coords(self.dims):
            t[c] = self.tightness(c)
        return t

    def tightest(self):
        return min((self.tightness(c),c) for c in coords(self.dims))

    def step(self):
        t, coord = self.tightest()
        if not t:
            return
        if len(self.pending) < self.valid_pending:
            for v, elts in self.volumes():
                if v not in self._valid_volumes:
                    #print
                    #print "invalid volume", v, elts, self._valid_volumes
                    #print
                    #print self
                    #print self._v
                    return
        for shape, pieces in self._idx[coord].iteritems():
            if shape not in self.pending:
                continue
            for pos in pieces:
                if not self.valid(pos):
                    continue
                yield self.__class__(
                    state = self.m + pos.m,
                    done = self.done + [pos],
                    pending = [s for s in self.pending if s != shape],
                    _parent = self)



class Score(object):
    longest = 0
    cnt = 0
    CURRENT = None
    done = []
    MAX_ROUNDS = 0
    def __init__(self):
        self.__class__.CURRENT = self

    def progress(self, b):
        self.cnt += 1
        self.b = b
        b.score = self
        if not b.pending:
            self.done.append(b)
            self.trace(b)
            print
            print "Found!"
            print
            print b
            print
            print "-----------------------------------"
#        elif len(b.done) >= self.longest:
#            self.trace(b)
#            print
#            print b
#            self.longest = max(self.longest, len(b.done))
#            print "-----------------------------------"
        elif self.cnt % 100 == 0:
            self.trace(b)

        return not self.MAX_ROUNDS or self.cnt < self.MAX_ROUNDS

    def trace(self, b):
        sys.stdout.write("%s          %d        \r" % (
            " ".join(p.piece.shape.name for p in b.done),
            self.cnt))
        sys.stdout.flush()

import sys

def find(b, score = Score()):
    if score.progress(b):
        for bb in find_one(b, score):
            find(bb, score)

def find_one(b, score):
    for bb in b.step():
        yield bb

