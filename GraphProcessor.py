import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np


class GraphProcessor:
    def __init__(self, file, x_bottom=0, y_bottom=0):
        print('Loading Graph Processor for {}.'.format(file))
        self.file = file
        self.graph = mpimg.imread(file)
        self.x = 475
        self.y = 753
        self.x_bottom = x_bottom
        self.y_bottom = y_bottom
        self.x_bottom_index = 0
        self.y_bottom_index = 0
        self.x_top_range = 0
        self.x_top_value = 0
        self.x_bottom_range = self.x-1
        self.x_bottom_value = 0
        self.y_top_range = 0
        self.y_top_value = 0
        self.y_bottom_range = self.y-1
        self.y_bottom_value = 0
        self.find_x_range()
        self.find_y_range()
        self.x_conversion_factor = self.find_x_scale(30, self.y - 1)
        self.y_conversion_factor = self.find_y_scale(250, 1)
        print('Graph Processor loaded.')

    def reload_graph(self):
        self.graph = mpimg.imread(self.file)

    def find_x_scale(self, distance, y_line):
        top_row = self.graph[y_line]
        index = []
        for pixel_x, pixel in enumerate(top_row):
            if np.array_equal(pixel, np.array([1, 0, 0, 1])):
                index.append(pixel_x)
                if len(index) == 1:
                    self.x_bottom_index = pixel_x
        x_difference = index[-1] - index[0]
        conversion_factor = x_difference / distance
        return conversion_factor

    def find_y_scale(self, distance, x_line):
        index = []
        y_bottom_index = self.y - 1
        for row_num, row in enumerate(self.graph):
            if np.array_equal(row[x_line], np.array([0, 0, 1, 1])):
                index.append(row_num)
                y_bottom_index = row_num
        self.y_bottom_index = self.y - y_bottom_index - 1
        y_difference = index[-1] - index[0]
        conversion_factor = y_difference / distance
        return conversion_factor

    def find_x_range(self):
        for row_num, row in enumerate(self.graph):
            for pixel_num, pixel in enumerate(row):
                if self.check_black(pixel):
                    if pixel_num < self.x_bottom_range:
                        self.x_bottom_range = pixel_num
                        self.x_bottom_value = row_num
                    if pixel_num >= self.x_top_range:
                        self.x_top_range = pixel_num
                        self.x_top_value = row_num

    def find_y_range(self):
        for row_num, row in enumerate(self.graph):
            for pixel_num, pixel in enumerate(row):
                if self.check_black(pixel):
                    self.y_top_range = row_num
                    self.y_top_value = pixel_num
                    if row_num < self.y_bottom_range:
                        self.y_bottom_range = row_num
                        self.y_bottom_value = pixel_num

    def y_to_x(self, y):
        converted_y = round((y - self.y_bottom) * self.y_conversion_factor)
        x_list = []
        actual_y = self.y - converted_y
        if self.y_bottom_range <= actual_y < self.y_top_range:
            # self.plot_y_line(actual_y)
            row = self.graph[actual_y]
            for pixel_num, pixel in enumerate(row):
                if self.check_black(pixel):
                    x_list.append(pixel_num)
            x_coordinate = self.average(x_list)
        elif actual_y < self.y_bottom_range:
            x_coordinate = self.y_bottom_value
        else:
            x_coordinate = self.y_top_value
        # self.plot_x_line(x_coordinate)
        # self.plot_point(x_coordinate, actual_y)
        x_coordinate_adjusted = x_coordinate - self.x_bottom_index
        x_value = self.x_bottom + x_coordinate_adjusted / self.x_conversion_factor
        return x_value

    def x_to_y(self, x):
        converted_x = round((x - self.x_bottom) * self.x_conversion_factor)
        if converted_x >= self.x:
            converted_x = self.x - 1
        if converted_x < 0:
            converted_x = 0
        y_list = []
        if self.x_bottom_range <= converted_x <= self.x_top_range:
            # self.plot_x_line(converted_x)
            for row_num, row in enumerate(self.graph):
                pixel = row[converted_x]
                if self.check_black(pixel):
                    y_list.append(row_num)
            y_coordinate = self.average(y_list)
        elif converted_x < self.x_bottom_range:
            y_coordinate = self.x_bottom_value
        else:
            y_coordinate = self.x_top_value
        # self.plot_y_line(y_coordinate)
        # self.plot_point(converted_x, y_coordinate)
        reverse_y_coordinate = self.y - y_coordinate - 1
        y_coordinate_adjusted = reverse_y_coordinate - self.y_bottom_index
        y_value = self.y_bottom + y_coordinate_adjusted / self.y_conversion_factor
        return y_value

    def average(self, num_list):
        if len(num_list) > 0:
            return sum(num_list)/len(num_list)
        else:
            return 'none'

    def check_black(self, pixel):
        for color in pixel[:3]:
            if color > 0.1:
                return False
        else:
            return pixel[3] > 0.1

    def draw(self):
        plt.imshow(self.graph)
        plt.show()

    def plot_x_line(self, x):
        plt.plot([x, x], [0, self.y-1], 'r--')

    def plot_y_line(self, y):
        plt.plot([0, self.x-1], [y, y], 'b--')

    def plot_point(self, x, y):
        plt.plot(x, y, 'xc')
