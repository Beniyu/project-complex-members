from PointManager import PointManager
from SimEqManager import SimEqManager
from BucklingOptimiser import BucklingOptimiser
import matplotlib.pyplot as plt
import numpy as np


class BridgeManager:
    def __init__(self, points, connections, constraints, loads, buckling_optimiser = ''):
        self.dimensions = 2
        self.points = points
        self.connections = connections
        self.constraints = constraints
        self.loads = loads
        self.material_properties = [
            {'area': 27.7, 'b': 9.5, 'p': 0.076, 't': 1.6, 'e': 7e10},
            {'area': 37.6, 'b': 12.5, 'p': 0.102, 't': 1.6, 'e': 7e10},
            {'area': 46.9, 'b': 15.9, 'p': 0.127, 't': 1.6, 'e': 7e10},
            {'area': 58.7, 'b': 16.0, 'p': 0.159, 't': 2.0, 'e': 7e10},
            {'area': 73.2, 'b': 19.5, 'p': 0.199, 't': 2.0, 'e': 7e10}
        ]
        if buckling_optimiser == '':
            buckling_optimiser = BucklingOptimiser(self.material_properties)
        self.buckling_optimiser = buckling_optimiser

        self.point_manager = PointManager()
        self.add_points()
        self.add_first_load()

    def get_reactions(self):  # unused function
        special_points = self.point_manager.get_special_points()
        coefficients = []

        for point in special_points['fixed']:
            if 'x' in point.constraint:
                coefficients.append((point, 0))
            if 'y' in point.constraint:
                coefficients.append((point, 1))

        seq_manager = SimEqManager(coefficients)
        for point in special_points['fixed'] + special_points['loaded']:
            point_1 = point.direction_array()
            seq = seq_manager.create_sim_eq()
            for fixed_point in special_points['fixed']:
                if fixed_point != point:
                    point_2 = fixed_point.direction_array()
                    displacement = point_2 - point_1
                    if 'x' in fixed_point.constraint:
                        seq.set_coefficient((fixed_point, 0), displacement[1])
                    if 'y' in fixed_point.constraint:
                        seq.set_coefficient((fixed_point, 1), displacement[0])
            for loaded_point in special_points['loaded']:
                point_2 = loaded_point.direction_array()
                load = loaded_point.load
                displacement = point_2 - point_1
                moment = displacement[1] * load[0] - displacement[0] * load[1]
                seq.set_result(moment)
        left_matrix = seq_manager.produce_left_matrix()
        right_vector = seq_manager.produce_right_vector()
        inverse_left_matrix = np.linalg.inv(left_matrix)
        result_matrix = np.dot(inverse_left_matrix, right_vector)
        for coefficient_num, coefficient in enumerate(coefficients):
            dimension_names = {
                0: 'X',
                1: 'Y'
            }
            print("F_{} at point {}: {}".format(dimension_names[coefficient[1]], coefficient[0].name,
                                                result_matrix[coefficient_num]))

    def get_reactions_2(self):
        reactions = {}
        for point_name, point in self.point_manager.point_list.items():
            connections = point.connections.connection_list
            total_tension_vector = np.zeros(2)
            for connection in connections:
                direction_vector = self.get_direction_vector(point, connection)
                connection_name = sorted([point, connection])
                tension = self.tensions[tuple(connection_name)]
                tension_vector = tension * direction_vector
                total_tension_vector += tension_vector
            reaction_vector = -total_tension_vector
            reactions[point_name] = reaction_vector
        self.reactions = reactions
        return reactions

    def get_displacements(self):
        displacements = {}
        for point_name, point in self.point_manager.point_list.items():
            displacement = np.zeros(2)
            for dimension in range(self.dimensions):
                bridge_manager = BridgeManager(self.points, self.connections, self.constraints, self.loads, self.buckling_optimiser)
                bridge_manager.reset_loads()
                load = np.array([1 - dimension, dimension])
                bridge_manager.point_manager.set_point_load(point_name, load)
                tensions = bridge_manager.solve_tension()
                te_sum = 0
                for connection, tension in tensions.items():
                    point_1 = self.point_manager.get_point(connection[0].direction_array())
                    point_2 = self.point_manager.get_point(connection[1].direction_array())
                    point_identifier = sorted([point_1, point_2])
                    real_extension = self.extensions[tuple(point_identifier)]
                    te = tension * real_extension
                    te_sum += te
                displacement[dimension] = te_sum
            displacements[point_name] = displacement
        self.displacements = displacements
        return displacements

    def solve_tension(self):
        connection_list = self.point_manager.get_connections()
        seq_manager = SimEqManager(connection_list)

        for point in self.point_manager.point_list.values():
            if point.constraint == 'none':
                for dimension in range(self.dimensions):
                    seq = seq_manager.create_sim_eq()
                    for connection in point.connections.connection_list:
                        direction_vector = self.get_direction_vector(point, connection)
                        connection_name = tuple(sorted([connection, point]))
                        seq.set_coefficient(connection_name, direction_vector[dimension])
                    seq.add_to_result(-point.load[dimension])

        solution = seq_manager.solve()
        solution_dict = {}
        for connection_number, connection in enumerate(connection_list):
            solution_dict[(connection[0], connection[1])] = solution[connection_number]

        self.tensions = solution_dict
        return solution_dict

    def get_length(self, point_1, point_2):
        return np.linalg.norm(point_1.direction_array() - point_2.direction_array())

    def solve_extension(self):
        extension_dict = {}
        for connection, tension in self.tensions.items():
            member_properties = self.final_members[connection]['material']
            area = member_properties['area']
            e = member_properties['e']
            connection_length = self.get_length(connection[0], connection[1])
            extension = tension * connection_length / (area * e / 1000000)
            extension_dict[tuple(connection)] = extension
        self.extensions = extension_dict
        return extension_dict

    def get_next_dict_num(self, dictionary):
        value = 0
        while value in dictionary and value < 10000:
            value += 1
        return value

    def get_direction_vector(self, point_1, point_2):
        raw_vector = point_2.direction_array() - point_1.direction_array()
        unit_vector = raw_vector / np.linalg.norm(raw_vector)
        return unit_vector

    def get_connection_identifier(self, point_1, point_2):
        connection_identifier = [point_1.name, point_2.name]
        connection_identifier.sort()
        return str(connection_identifier)

    def display_points(self):
        for point in self.point_manager.point_list.values():
            x = point['x']
            y = point['y']
            plt.plot(x, y, 'xr')
            plt.annotate(point.name, (x + 10, y + 10))

        connections = self.point_manager.get_connections()
        for connection in connections:
            point_1 = connection[0]['xy']
            point_2 = connection[1]['xy']
            plt.plot([point_1[0], point_2[0]], [point_1[1], point_2[1]], 'b')

    def draw_displacement(self):
        connections = self.point_manager.get_connections()
        for connection in connections:
            point_1 = connection[0].name
            point_2 = connection[1].name
            deflection_1 = self.displacements[point_1]
            new_point_1 = connection[0].direction_array() + deflection_1
            deflection_2 = self.displacements[point_2]
            new_point_2 = connection[1].direction_array() + deflection_2
            plt.plot([new_point_1[0], new_point_2[0]], [new_point_1[1], new_point_2[1]], 'c--')

    def add_first_load(self):
        first_load = self.loads[0]
        for point, load in first_load.items():
            self.point_manager.set_point_load(point, np.array(load))

    def add_points(self):
        self.point_manager.point_list = {}
        for point in self.points:
            self.point_manager.make_point(*point)
        for connection in self.connections:
            self.point_manager.connect_point(*connection)
        for point, constraint in self.constraints.items():
            self.point_manager[point].set_constraint(constraint)

    def draw_tensions(self):
        new_data = {}
        for points, data in self.tensions.items():
            string = "{}N".format(round(data))
            new_data[points] = string
        self.draw_member_data(new_data, [5, 10])

    def draw_member_properties(self):
        if hasattr(self, 'final_members'):
            data_converter = {'mode': {}, 'mass': {}, 'breadth': {}}
            for member, properties in self.final_members.items():
                for property_name, property_value in properties.items():
                    if property_name == 'material':
                        data = '{}mm'.format(property_value['b'])
                        property_name = 'breadth'
                    elif property_name == 'mass':
                        data = '{}g'.format(round(property_value, 1))
                    else:
                        data = property_value

                    data_converter[property_name][member] = data

            self.draw_member_data(data_converter['mode'], [5, 40])
            self.draw_member_data(data_converter['mass'], [5, 30])
            self.draw_member_data(data_converter['breadth'], [5, 20])

    def draw_member_data(self, data, displacement):
        for points, data in data.items():
            point_1 = points[0].direction_array()
            point_2 = points[1].direction_array()
            midpoint = (point_1 + point_2) / 2 + np.array(displacement)

            data_type = type(data)

            if data_type in [float, np.float64]:
                real_data = str(round(data))
            else:
                real_data = str(data)

            plt.annotate(real_data, midpoint)

    def get_member_properties(self):
        buckling_configuration = self.optimise_buckling()
        tension_configuration = self.optimise_tension()
        configuration_list = [buckling_configuration, tension_configuration]

        member_list = self.point_manager.get_connections()
        member_material = {}

        for member in member_list:
            member_configuration = {}
            for mode in ['A', 'B', 'C']:
                mode_materials = []

                for configuration in configuration_list:
                    mode_materials.append(configuration[member][mode])

                if 'none' in mode_materials:
                    member_configuration[mode] = 'none'
                    continue

                else:
                    for material in reversed(self.material_properties):
                        if material in mode_materials:
                            member_configuration[mode] = material
                            break
            member_material[member] = member_configuration

        self.member_material = member_material
        return member_material

    def optimise_buckling(self):
        member_list = self.point_manager.get_connections()
        member_material = {}

        for member in member_list:
            tension = self.tensions[member]
            length = self.get_length(member[0], member[1])
            if tension < 0:
                optimal_configuration = self.buckling_optimiser.member_optimal_b(-tension, length)
                member_material[member] = optimal_configuration
            else:
                optimal_configuration = {
                    'A': self.material_properties[0],
                    'B': self.material_properties[0],
                    'C': self.material_properties[0]
                }
                member_material[member] = optimal_configuration

        return member_material

    def optimise_tension(self):
        member_list = self.point_manager.get_connections()
        member_material = {}

        for member in member_list:
            force = self.tensions[member]
            member_configuration = {}

            for mode in ['A', 'B', 'C']:
                if mode == 'A':
                    area_multiplier = 1
                else:
                    area_multiplier = 2

                for material in self.material_properties:
                    breadth = material['b']
                    thickness = material['t']
                    conversion_factor = 0.9
                    rivet_diameter = 3.20

                    if force >= 0:
                        effective_area = (3 * breadth * thickness / 2 - rivet_diameter * thickness) * \
                                         conversion_factor * area_multiplier

                    else:
                        effective_area = material['area']

                    axial_stress = abs(force) / effective_area
                    if axial_stress <= 255:
                        member_configuration[mode] = material
                        break

                else:
                    member_configuration[mode] = 'none'

            member_material[member] = member_configuration

        return member_material

    def optimise_mass(self):
        member_list = self.point_manager.get_connections()
        optimal_member_material = {}
        total_mass = 0
        possible = True

        for member in member_list:
            member_configuration = self.member_material[member]
            optimal_mass = 1000000000000000
            optimal_mode = 'none'
            optimal_material = 'none'
            length = self.get_length(member[0], member[1])
            for mode in ['A', 'B', 'C']:
                mode_material = member_configuration[mode]
                if mode_material != 'none':
                    density = mode_material['p']

                    if mode == 'A':
                        mass_multiplier = 1
                    else:
                        mass_multiplier = 2

                    mode_mass = length * density * mass_multiplier
                    if mode_mass < optimal_mass:
                        optimal_mode = mode
                        optimal_mass = mode_mass
                        optimal_material = mode_material

            if optimal_mode == 'none':
                possible = False

            optimal_configuration = {
                'mode': optimal_mode,
                'mass': optimal_mass,
                'material': optimal_material
            }

            optimal_member_material[member] = optimal_configuration

            if optimal_mass != 'none':
                total_mass += optimal_mass

        if possible:
            self.final_members = optimal_member_material
            # print("Total mass: {}g".format(total_mass))
            return optimal_member_material, total_mass
        else:
            # print("No members found which can fit this configuration.")
            return 'none', 10000000000000

    def get_member_properties_multi(self):
        possible_properties = {}
        connections = self.point_manager.get_connections()
        for connection in connections:
            possible_properties[connection] = []

        bridge = BridgeManager(self.points, self.connections, self.constraints, self.loads, self.buckling_optimiser)

        bridge.reset_loads()

        for load in self.loads:
            for load_point, load_value in load.items():
                bridge.point_manager.set_point_load(load_point, np.array(load_value))
                bridge.solve_tension()
                member_properties = bridge.get_member_properties()

                for member, properties in member_properties.items():
                    point_1 = self.point_manager.get_point(member[0].direction_array())
                    point_2 = self.point_manager.get_point(member[1].direction_array())
                    member_identifier = tuple(sorted([point_1, point_2]))
                    possible_properties[member_identifier].append(properties)
                bridge.point_manager.set_point_load(load_point, np.zeros(2))
        member_material = {}

        for member in connections:
            member_configuration = {}
            member_possible_properties = possible_properties[member]
            for mode in ['A', 'B', 'C']:
                mode_materials = []
                for property_set in member_possible_properties:
                    mode_materials.append(property_set[mode])

                if 'none' in mode_materials:
                    member_configuration[mode] = 'none'
                    continue

                else:
                    for material in reversed(self.material_properties):
                        if material in mode_materials:
                            member_configuration[mode] = material
                            break

            member_material[member] = member_configuration

        self.member_material = member_material
        return member_material

    def reset_loads(self):
        for point in self.point_manager.point_list.values():
            point.set_load(np.zeros(2))
