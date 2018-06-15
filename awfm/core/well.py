from .transientparameter import ConstantParameter, LinearParameter
import numpy as np

class Well:
    def __init__(self, name, x, y, rw=1.0, h0=0):
        self.name = name
        self.x = x
        self.y = y
        self.rw = 1.0
        self.set_rw(rw)
        self.h0 = ConstantParameter(h0)
        self.b = ConstantParameter(0)
        self.c = ConstantParameter(0)

    def distance_to_point(self, x, y):
        dx = self.x - x
        dy = self.y - y
        return max(np.sqrt(dx*dx + dy*dy), self.rw)

    def distance_to_well(self, w):
        return self.distance_to_point(w.x, w.y)

    def set_rw(self, rw):
        if rw > 0:
            self.rw = rw
