class SimEquation:
    def __init__(self, coefficients, result=0):
        self.coefficients = coefficients
        self.result = result

    def __getitem__(self, item):
        return self.coefficients[item]

    def get_coefficient(self, coefficient_identifier):
        for coefficient in self.coefficients:
            if coefficient.identifier == coefficient_identifier:
                return coefficient
        else:
            raise RuntimeError("The coefficient {} does not exist.".format(coefficient_identifier))

    def set_coefficient(self, coefficient, value):
        coefficient = self.get_coefficient(coefficient)
        coefficient.value = value

    def set_result(self, result):
        self.result = result

    def add_to_result(self, value):
        self.result += value

    def __repr__(self):
        output_string = "["
        for coefficient in self.coefficients:
            output = "{}: {}, ".format(coefficient.identifier, coefficient.value)
            output_string += output
        output_string += "]"
        return output_string
