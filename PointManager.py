from Point import Point
import numpy as np


class PointManager:
    def __init__(self):
        self.point_list = {}

    def add_point(self, point: Point):
        if not (point.name in self.point_list.keys()):
            self.point_list[point.name] = point
        else:
            raise RuntimeError("Point with name {} already exists.".format(point.name))

    def get_next_name(self):
        point_name = 1
        while point_name < 10000 and point_name in self.point_list.keys():
            point_name += 1
        return point_name

    def __getitem__(self, point):
        return self.point_list[point]

    def del_point(self, point):
        if point in self.point_list.keys():
            del self.point_list[point]
        else:
            raise RuntimeError("Point {} does not exist.".format(point))

    def make_point(self, x=0, y=0, name="unnamed"):
        if name == "unnamed":
            name = self.get_next_name()
        if not (name in self.point_list.keys()):
            point = Point(name, x, y)
            self.point_list[name] = point
        else:
            raise RuntimeError("Point with name {} already exists.".format(name))

    def connect_point(self, point_1_name, point_2_name):
        point_1 = self[point_1_name]
        point_2 = self[point_2_name]
        point_1.connect(point_2, True)

    def disconnect_point(self, point_1_name, point_2_name):
        point_1 = self[point_1_name]
        point_2 = self[point_2_name]
        point_1.disconnect(point_2, True)

    def __repr__(self):
        return str([i for i in self.point_list.values()])

    def get_connections(self):
        connections = []
        for point in self.point_list.values():
            for point_connection in point.connections.connection_list:
                point_connection_list = [point, point_connection]
                point_connection_list.sort()
                connection_name = tuple(point_connection_list)
                if connection_name not in connections:
                    connections.append(connection_name)
        connections.sort()
        return connections

    def get_special_points(self):
        fixed_points = []
        loaded_points = []
        for point in self.point_list.values():
            load = point.load
            if point.constraint != 'none':
                fixed_points.append(point)
            if np.any(load):
                loaded_points.append(point)
        return {'fixed': fixed_points, 'loaded': loaded_points}

    def set_point_load(self, point_name, load):
        self[point_name].set_load(load)

    def get_point(self, position):
        for point in self.point_list.values():
            if np.array_equal(point.direction_array(), position):
                return point
        else:
            raise RuntimeError("Point not found.")
