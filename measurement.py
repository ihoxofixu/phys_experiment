class measurement:
    def __init__(self, value, *errors, square_errors=False):
        self.value = value
        res_error = 0
        for error in errors:
            if square_errors:
                res_error += error
            else:
                res_error += error ** 2
        self.error = res_error

    def __add__(self, other):
        if type(other) == int or type(other) == float:
            return measurement(self.value + other, self.error, square_errors=True)
        elif type(other) == measurement:
            return measurement(self.value + other.value, self.error + other.error, square_errors=True)
        else:
            raise TypeError("Can only add int, float or measurement type values, not " + str(type(other)).split("'")[1])

    def __radd__(self, other):
        if type(other) == int or type(other) == float:
            return measurement(self.value + other, self.error, square_errors=True)
        elif type(other) == measurement:
            return measurement(self.value + other.value, self.error + other.error, square_errors=True)
        else:
            raise TypeError("Can only add to int, float or measurement type values, not " + str(type(other)).split("'")[1])

    def __rsub__(self, other):
        if type(other) == int or type(other) == float:
            return measurement(other - self.value, self.error, square_errors=True)
        elif type(other) == measurement:
            return measurement(other.value - self.value, self.error + other.error, square_errors=True)
        else:
            raise TypeError("Can only substract from int, float or measurement type values, not " + str(type(other)).split("'")[1])

    def __mul__(self, other):
        if type(other) == int or type(other) == float:
            return measurement(self.value * other, self.error * other ** 2, square_errors=True)
        elif type(other) == measurement:
            return measurement(self.value * other.value, self.error * other.value ** 2 + other.error * self.error ** 2, square_errors=True)
        else:
            raise TypeError("Can only multiply by int, float or measurement type values, not " + str(type(other)).split("'")[1])

    def __rmul__(self, other):
        if type(other) == int or type(other) == float:
            return measurement(self.value * other, self.error * other ** 2, square_errors=True)
        elif type(other) == measurement:
            return measurement(self.value * other.value, self.error * other.value ** 2 + other.error * self.value ** 2, square_errors=True)
        else:
            raise TypeError("Only int, float or measurement type values can be multiplied by, not " + str(type(other)).split("'")[1])

    def __truediv__(self, other):
        if type(other) == int or type(other) == float:
            return measurement(self.value / other, self.error / other ** 2, square_errors=True)
        elif type(other) == measurement:
            return measurement(self.value / other.value, self.error / other.value ** 2 + other.error * (self.value / other.value ** 2) ** 2, square_errors=True)
        else:
            raise TypeError("Can only divide by int, float or measurement type values, not " + str(type(other)).split("'")[1])

    def __rtruediv__(self, other):
        if type(other) == int or type(other) == float:
            return measurement(other / self.value, self.error / other ** 2, square_errors=True)
        elif type(other) == measurement:
            return measurement(other.value / self.value, other.error / self.value ** 2 + self.error * (other.value / self.value ** 2) ** 2, square_errors=True)
        else:
            raise TypeError("Only int, float or measurement type values can be divided by , not " + str(type(other)).split("'")[1])

    def __pow__(self, other):
        if type(other) == int or type(other) == float:
            return measurement(self.value ** other, other ** 2 * self.error * (self.value ** 2) ** (other - 1), square_errors=True)
        elif type(other) == measurement:
            raise NotReadyYetError("In progress, not ready yet, sorry")
        else:
            raise TypeError("Can only raise to power of int, float or measurement type values, not " + str(type(other)).split("'")[1])

    def __str__(self):
        return str(self.value) + " ± " + str(self.error**0.5)
