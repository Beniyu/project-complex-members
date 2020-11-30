import matplotlib.pyplot as plt
from numpy.linalg import LinAlgError

from BridgeManager import BridgeManager
from BucklingOptimiser import BucklingOptimiser
import random


class Optimise:
    def __init__(self):
        print("Let's begin!")
        self.points = [[0,0], [815/3,0], [815*2/3,0], [815,0], [0,255], [815/3,255/3*2]]
        self.connections = [[1,2], [2,3], [3,4], [5,6], [6,4], [2,6], [3,6], [5,2]]
        self.constraints = {1: 'x', 5:'xy'}
        self.loads = [{4:[0,-1350*0.95,0]}, {4:[0,135*0.95,0]}]
        self.material_properties = [
            {'area': 27.7, 'b': 9.5, 'p': 0.076, 't': 1.6, 'e': 7e10},
            {'area': 37.6, 'b': 12.5, 'p': 0.102, 't': 1.6, 'e': 7e10},
            {'area': 46.9, 'b': 15.9, 'p': 0.127, 't': 1.6, 'e': 7e10},
            {'area': 58.7, 'b': 16.0, 'p': 0.159, 't': 2.0, 'e': 7e10},
            {'area': 73.2, 'b': 19.5, 'p': 0.199, 't': 2.0, 'e': 7e10}
        ]
        self.optimal_mass = 100000000000000
        self.buckling_optimiser = BucklingOptimiser(self.material_properties)
        self.optimal_configuration = {}

    def synthesis(self, points):
        bridge_manager = BridgeManager(points, self.connections, self.constraints, self.loads, self.buckling_optimiser)
        bridge_manager.solve_tension()
        bridge_manager.get_member_properties_multi()
        config, mass = bridge_manager.optimise_mass()
        return bridge_manager, config, mass

    def randomize(self, points = (), random_factor = 250000000000):
        if points == ():
            print("First run detected.")
            points = self.points

        top_mass = 10000000000000000000
        top_config = {}
        for i in range(10000):
            points_copy = points.copy()
            for point_num in [1,2,5]:
                point = points_copy[point_num]
                new_point_x = point[0] + random.randint(-random_factor,random_factor) / 1000000000
                new_point_y = point[1] + random.randint(-random_factor,random_factor) / 1000000000
                if new_point_x <= 0:
                    new_point_x = 0.001
                if new_point_y <= 0:
                    new_point_y = 0.001
                new_point = [new_point_x, new_point_y]
                points_copy[point_num] = new_point

            for point_num in [3]:
                point = points_copy[point_num]
                new_point_y = point[1] + random.randint(-random_factor,random_factor) / 1000000000
                new_point = [point[0], new_point_y]
                points_copy[point_num] = new_point

            try:
                bridge, member_properties, total_mass = self.synthesis(points_copy)
                if total_mass < top_mass:
                    top_mass = total_mass
                    top_config = {
                        'points': points_copy,
                        'materials': total_mass,
                        'bridge': bridge
                    }
            except LinAlgError:
                print(points_copy)

            if i % 100 == 0:
                print("Current minimum: {}".format(top_mass))

        print("Mass: {}, Config: {}".format(top_mass, top_config))
        bridge = top_config['bridge']
        bridge.add_first_load()
        bridge.display_points()
        bridge.draw_tensions()
        bridge.draw_member_properties()
        bridge.solve_extension()
        bridge.get_reactions_2()
        bridge.get_displacements()
        bridge.draw_displacement()
        plt.show()

        if top_mass < self.optimal_mass:
            self.optimal_mass = top_mass
            self.optimal_configuration = top_config

        self.randomize(top_config['points'], int(random_factor/2))

instance = Optimise()
instance.randomize()