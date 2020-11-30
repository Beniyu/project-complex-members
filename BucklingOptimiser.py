from GraphProcessor import GraphProcessor


class BucklingOptimiser:
    def __init__(self, material_properties):
        self.material_properties = material_properties
        self.graphs = {}
        for graph_name in ['A', 'B', 'C']:
            self.graphs[graph_name] = GraphProcessor("graph_{}.png".format(graph_name))

            #if graph_name == 'C':
            #    self.graphs[graph_name] = GraphProcessor("graph_B.png")
            #else:
            #    self.graphs[graph_name] = GraphProcessor("graph_{}.png".format(graph_name))

    def mode_max_stress(self, mode, slenderness):
        graph = self.graphs[mode]
        maximum_stress = graph.x_to_y(slenderness)
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
                maximum_stress = self.mode_max_stress(mode, length/breadth)
                true_stress = force / (base_area * area_multiplier)
                if true_stress < maximum_stress:
                    mode_profile[mode] = material
                    break

            else:
                mode_profile[mode] = 'none'

        return mode_profile
