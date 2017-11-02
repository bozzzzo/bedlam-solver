import numpy as np
from functools import total_ordering

class Shape(object):
    def __init__(self, name, arr):
        self.name = name
        self.m = arr
        self.rot = set()
        self.pos = list()

    def rotations(self):
        if not self.rot:
            self._gen_rot()
        return self.rot

    def _gen_rot(self):
        for rot in (dict(i=i,j=j,k=k) 
                   for i in range(4)
                   for j in range(4)
                   for k in range(4)):
            p = Piece(self).rot90(**rot)
            if p not in self.rot:
                self.rot.add(p)

    def positions(self, w=4, h=4, d=4):
        if not self.pos:
            self._gen_pos(w,h,d)
        return self.pos

    def _gen_pos(self, w, h, d):
        for r in self.rotations():
            a,b,c = np.array([w,h,d]) - r.m.shape
            for i in range(a+1):
                ip = (i, a - i)
                for j in range(b+1):
                    jp = (j, b - j)
                    for k in range(c+1):
                        kp = (k, c - k)
                        self.pos.append(r.pad(ip,jp,kp))

    def __repr__(self):
        return "%s(%s,rot=%s,pos=%s)" % (
            self.__class__.__name__, self.name,
            len(self.rotations()),
            len(self.positions()))

@total_ordering
class Piece(object):
    def __init__(self, shape, arr=None, i=0, j=0, k=0):
        self.shape = shape
        if arr is None:
            arr = shape.m
        self.m = np.array(arr)
        self.rot = (i,j,k)

    def __eq__(self, other):
        if not isinstance(other, Piece):
            raise TypeError("argument must be a %s not a '%s'" % (
                self.__class__.__name__, type(other).__name__))
        if self.m.shape == other.m.shape:
            return tuple(self.m.flatten()) == tuple(other.m.flatten())
        else:
            return False

    def __lt__(self, other):
        if not isinstance(other, Piece):
            raise TypeError("argument must be a %s not a '%s'" % (
                self.__class__.__name__, type(other).__name__))
        if self.m.shape == other.m.shape:
            st = tuple(self.m.flatten())
            ot = tuple(other.m.flatten())
            if st == ot:
                return self.rot < other.rot
        else:
            return self.m.shape < other.m.shape

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "\n%sPiece(%s,%s,%s,%s)" % (self.shape.__class__.__name__,
                                         self.shape.name,
                                         self.m, self.m.shape, self.rot)

    def __hash__(self):
        return reduce(lambda i, e: i*2 + e, self.m.flatten(), 0)

    def rot90(self, i, j, k):
        return self.__class__(
            self.shape,
            np.rot90(
                np.rot90(
                    np.rot90(
                        self.m,
                        i % 4, (0,1)),
                    j % 4, (0,2)),
                k % 4, (1,2)),
            i = i % 4,
            j = j % 4,
            k = k % 4)

    def pad(self, *pad):
        return PaddedPiece(
            self,
            np.pad(self.m, pad, mode='constant', constant_values=0),
            pad)

class PaddedPiece(object):
    def __init__(self, piece, m, pad):
        self.piece = piece
        self.m = m
        self.pad = pad

    def __repr__(self):
        return "\nPadded%s(%s\n%s,%s,%s)" % (self.piece.shape.__class__.__name__,
                                             self.piece.shape.name,
                                       self.m, self.m.shape, self.piece.rot)

class Blue(Shape):
    pass
class Green(Shape):
    pass
class White(Shape):
    pass


SHAPES = (
    Blue('A',[[[1,1,1],
               [1,0,0]],
              [[1,0,0],
               [0,0,0]]]),
    Blue('B', [[[0,1,1],
                [1,1,0]],
               [[0,1,0],
                [0,0,0]]]),
    Blue('C', [[[0,1,0],
                [1,1,1],
                [0,1,0]]]),
    Blue('D', [[[0,1,1],
                [1,1,0]],
               [[0,0,0],
                [1,0,0]]]),
    Green('E', [[[1,1,1],
                 [0,1,0]],
                [[0,0,0],
                 [0,1,0]]]),
    Green('F', [[[0,1,1],
                 [0,1,0]],
                [[0,0,0],
                 [1,1,0]]]),
    Green('G', [[[1,0,0],
                 [1,1,1],
                 [0,1,0]]]),
    Green('H', [[[1,1,1],
                 [0,1,0]],
                [[0,0,1],
                 [0,0,0]]]),
    White('I', [[[1,1,1],
                 [1,0,0]],
                [[0,0,1],
                 [0,0,0]]]),
    White('J', [[[1,1,1],
                 [0,0,1]],
                [[0,0,0],
                 [0,0,1]]]),
    White('K', [[[1,1,0],
                 [0,1,1],
                 [0,0,1]]]),
    White('L', [[[1,1],
                 [0,1]],
                [[1,0],
                 [0,0]]]),
    White('M', [[[1,1,1],
                 [0,1,0]],
                [[0,1,0],
                 [0,0,0]]])
)
