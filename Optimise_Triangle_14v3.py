import matplotlib.pyplot as plt
from numpy.linalg import LinAlgError
import numpy as np

from BridgeManager import BridgeManager
from BucklingOptimiser import BucklingOptimiser
from datetime import datetime


class Optimise:
    def __init__(self):
        print("Let's begin!")
        self.points = [[0, 0], [268, 38.389980751], [491, 29.855366287999995], [815, 79.54639574999999], [0, 255], [403.4067387359999, 209.56418884899998]]
        self.connections = [[1,2], [2,3], [3,4], [5,6], [6,4], [5,2], [2,6], [6,3]]
        self.constraints = {1: 'x', 5:'xy'}
        self.loads = [{4:[0,-1350,0]}, {4:[0,135,0]}]
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

    def randomize(self, points = (), random_factor = 32000000000):
        if points == ():
            print("First run detected.")
            points = self.points

        print(datetime.now())
        top_mass = 10000000000000000000
        top_config = {}
        point_2_x = 3
        for point_1_x in range(-1,2):
            for point_3_y in range(-5,6):
                for point_1_y in range(-5,6):
                    for point_2_y in range(-5,6):
                        for point_5_x in range(-5,6):
                            for point_5_y in range(-5,6):
                                points_copy = points.copy()
                                points_copy[3] = [815, round(points[3][1]) + point_3_y]
                                points_copy[1] = [round(points[1][0]) + point_1_x, round(points[1][1]) + point_1_y]
                                points_copy[2] = [round(points[2][0]) + point_2_x, round(points[2][1]) + point_2_y]
                                points_copy[5] = [round(points[5][0]) + point_5_x, round(points[5][1]) + point_5_y]

                                try:
                                    bridge, member_properties, total_mass = self.synthesis(points_copy)
                                    if total_mass < top_mass:
                                        point_1 = bridge.point_manager.get_point(np.array(points_copy[1]))
                                        point_2 = bridge.point_manager.get_point(np.array(points_copy[5]))
                                        member_identifier = tuple(sorted([point_1, point_2]))
                                        tension = bridge.tensions[member_identifier]
                                        if tension <= 1260:
                                            top_mass = total_mass
                                            top_config = {
                                                'points': points_copy,
                                                'materials': total_mass,
                                                'bridge': bridge
                                            }

                                except LinAlgError:
                                    print(points_copy)

        print("Mass: {}, Config: {}".format(top_mass, top_config))
        print(datetime.now())
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

        #self.randomize(top_config['points'], int(random_factor/2))

instance = Optimise()
instance.randomize()