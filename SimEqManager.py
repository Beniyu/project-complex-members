from SimEquation import SimEquation
from Coefficient import Coefficient
import numpy as np


class SimEqManager:
    def __init__(self, coefficients):
        self.equation_list = []
        self.coefficients_template = coefficients

    def create_sim_eq(self):
        coefficient_list = self.create_coefficient_list()
        new_sim_eq = SimEquation(coefficient_list)
        self.equation_list.append(new_sim_eq)
        return new_sim_eq

    def create_coefficient_list(self):
        coefficient_list = []
        for coefficient in self.coefficients_template:
            new_coefficient = Coefficient(coefficient, 0)
            coefficient_list.append(new_coefficient)
        return coefficient_list

    def __repr__(self):
        output_string = "["
        for eq in self.equation_list:
            output = str(eq)
            output_string += output
        output_string += "]"
        return output_string

    def produce_left_matrix(self):
        matrix_size = len(self.coefficients_template)
        matrix = np.zeros((matrix_size, matrix_size))
        for eq_num, eq in enumerate(self.equation_list):
            for coefficient_num, coefficient in enumerate(eq.coefficients):
                matrix[eq_num][coefficient_num] = coefficient.value
        return matrix

    def produce_right_vector(self):
        vector_size = len(self.coefficients_template)
        vector = np.zeros(vector_size)
        for eq_num, eq in enumerate(self.equation_list):
            vector[eq_num] = eq.result
        return vector

    def solve(self):
        left_matrix = self.produce_left_matrix()
        right_vector = self.produce_right_vector()
        inverse_left_matrix = np.linalg.inv(left_matrix)
        return np.dot(inverse_left_matrix, right_vector)
