class Location:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def set_location(self, value_name, value):
        if value_name == "x":
            self.x = value
        elif value_name == "y":
            self.y = value

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def aslist(self):
        point_list = [self.x, self.y]
        return point_list

    def asdict(self):
        point_dict = {'x': self.x, 'y': self.y}
        return point_dict

    def __repr__(self):
        return "[X={}, Y={}]".format(self.x, self.y)
