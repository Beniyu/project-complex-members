from Location import Location
from Connections import Connections
import numpy as np


class Point:
    def __init__(self, name, x=0, y=0, constraint='none', load=np.zeros(2)):
        self.location = Location(x, y)
        self.connections = Connections(self)
        self.name = name
        self.constraint = constraint
        self.load = load

    def __getitem__(self, item):
        if item == 'x':
            return self.location.x
        if item == 'y':
            return self.location.y
        if item == 'xy':
            return [self.location.x, self.location.y]

    def direction_array(self):
        return np.array(self['xy'])

    def connect(self, point, first):
        self.connections.connect(point, first)

    def disconnect(self, point, first):
        self.connections.disconnect(point, first)

    def set_location(self, x=0, y=0):
        self.location.set_location('x', x)
        self.location.set_location('y', y)

    def __repr__(self):
        return "[Location: {}, Connections: {}, Constraint: {}, Load: {}]".format(self.location, self.connections,
                                                                                  self.constraint, self.load)

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def set_constraint(self, constraint):
        self.constraint = constraint

    def set_load(self, load):
        self.load = load
