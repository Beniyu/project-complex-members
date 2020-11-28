class Connections:
    def __init__(self, point):
        self.connection_list = []
        self.point = point

    def connect(self, point, first=False):
        self.connection_list.append(point)
        if first:
            point.connect(self.point, False)

    def disconnect(self, point, first=False):
        if point in self.connection_list:
            self.connection_list.remove(point)
            if first:
                point.disconnect(self.point, False)
        else:
            raise RuntimeError("The points {} and {} are not connected.".format(self.point.name, point.name))

    def __repr__(self):
        connection_list = "["
        for connection in self.connection_list:
            connection_list += str(connection.name) + ', '
        connection_list += "]"
        return connection_list
