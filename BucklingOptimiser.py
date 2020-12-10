from GraphProcessor import GraphProcessor
import numpy as np


class BucklingOptimiser:
    def __init__(self, material_properties):
        self.material_properties = material_properties
        self.graphs = {}
        self.allow_C = True
        for graph_name in ['A', 'B', 'C']:
            self.graphs[graph_name] = GraphProcessor("graph_{}.png".format(graph_name))

        if not self.allow_C:
            self.graphs['C'] = self.graphs['B']

        self.moment_dict = self.get_moment_of_inertia()

    def get_moment_of_inertia(self):
        moment_of_inertia_dict = {}

        for material in self.material_properties:
            breadth = material['b']
            base_area = material['area']
            e = material['e']
            moment_of_inertia_dict[breadth] = {}
            for mode in ['A', 'B', 'C']:
                values = 0
                slendernesses = [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]
                for l_over_b in slendernesses:
                    length = l_over_b * breadth
                    if mode == 'A':
                        area_multiplier = 1
                    else:
                        area_multiplier = 2
                    maximum_stress = self.graphs[mode].x_to_y(l_over_b)
                    maximum_force = maximum_stress * base_area * area_multiplier
                    moi = (maximum_force * (length * 1e-3) ** 2) / (np.pi ** 2 * e)
                    values += moi
                average_moment_of_inertia = values / len(slendernesses)
                moment_of_inertia_dict[breadth][mode] = average_moment_of_inertia
        print(moment_of_inertia_dict)
        return moment_of_inertia_dict

    def mode_max_stress(self, mode, slenderness, material, length):
        if slenderness < 39:
            graph = self.graphs[mode]
            maximum_stress = graph.x_to_y(slenderness)
        else:
            e = material['e']
            breadth = material['b']
            area = material['area']
            if mode == 'A':
                area_multiplier = 1
            else:
                area_multiplier = 2
            moi = self.moment_dict[breadth][mode]
            maximum_force = (np.pi ** 2 * e * moi) / ((length * 1e-3) ** 2)
            maximum_stress = maximum_force / (area * area_multiplier)
        return maximum_stress

    def member_optimal_b(self, force, length):
        mode_profile = {}

        for mode in ['A', 'B', 'C']:
            area_multiplier = 1
            if mode in ['B', 'C']:
                area_multiplier = 2

            for material in self.material_properties:
                breadth = material['b']
                base_area = material['area']
                maximum_stress = self.mode_max_stress(mode, length/breadth, material, length)
                true_stress = force / (base_area * area_multiplier)
                if true_stress < maximum_stress:
                    mode_profile[mode] = material
                    break

            else:
                mode_profile[mode] = 'none'

        return mode_profile
