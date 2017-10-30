import numpy as np
import operator as op
import itertools

import piece
from piece import SHAPES

def coords(dims):
    assert len(dims) == 3
    return [(i,j,k)
            for i in range(dims[0])
            for j in range(dims[1])
            for k in range(dims[2])]

class Box(object):
    def __init__(self, state = None, done = None, pending = SHAPES, dims=(4,4,4),
                 _idx = None):
        self.dims = dims
        if state is None:
            state = np.zeros(dims)
        if done is None:
            done = []
        self.m = state
        self.done = done
        self.pending = pending
        self.idx = _idx
        self.build_position_index()


    def build_position_index(self):
        if self.idx:
            return
        self.idx = dict()
        c = coords(self.dims)
        for i in c:
            self.idx[i] = dict()
        for s in itertools.chain(self.done, self.pending):
            for i in c:
                self.idx[i][s] = []
            for p in s.positions():
                for i in c:
                    if p.m[i]:
                        self.idx[i][s].append(p)



    def valid(self, pos):
        m = self.m + pos.m
        if m.max() > 1:
            return False
        s = self.m + pos.n
        if s.min() < 0:
            return False
        return True


    def step(self):
        for i in range(len(self.pending)):
            candidate = self.pending[i]
            for pos in candidate.positions():
                if not self.valid(pos):
                    continue
                yield self.__class__(
                    state = self.m + pos.m,
                    done = self.done + [pos],
                    pending = self.pending[i+1:] + self.pending[:i])


class Score(object):
    longest = 0

def find(b, score = Score()):
    if not b.pending:
        print "Found!"
        print b.done
        import sys
        sys.exit(0)
    if len(b.done) > score.longest:
        print b.done
        score.longest = len(b.done)
        print "-----------------------------------"
    for bb in b.step():
        find(bb)

