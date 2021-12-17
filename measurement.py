def deriviative_two_variables(x, y, func, var_x=True, var_y=True):
    dev_x = (func(x + x / 100000, y) - func(x, y)) / (x / 100000) if var_x else 0
    dev_y = (func(x, y + y / 100000) - func(x, y)) / (y / 100000) if var_y else 0
    return dev_x, dev_y


def calc_new_value(x, y, func):
    var_x = isinstance(x, measurement)
    var_y = isinstance(y, measurement)
    x = x if var_x else measurement(x, 0)
    y = y if var_y else measurement(y, 0)
    dev_x, dev_y = deriviative_two_variables(x.value, y.value, func, var_x, var_y)
    return measurement(func(x.value, y.value), x.error * dev_x ** 2 + y.error * dev_y ** 2, square_errors=True)


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
        if not isinstance(other, (int, float, measurement)):
            raise TypeError("Can only add int, float or measurement type values, not " + str(type(other)).split("'")[1])
        return calc_new_value(self, other, lambda x, y: x + y)

    def __radd__(self, other):
        if not isinstance(other, (int, float, measurement)):
            raise TypeError("Can only add int, float or measurement type values, not " + str(type(other)).split("'")[1])
        return calc_new_value(other, self, lambda x, y: x + y)

    def __sub__(self, other):
        if not isinstance(other, (int, float, measurement)):
            raise TypeError("Can only substract int, float or measurement type values, not " + str(type(other)).split("'")[1])
        return calc_new_value(self, other, lambda x, y: x - y)

    def __rsub__(self, other):
        if not isinstance(other, (int, float, measurement)):
            raise TypeError("Can only substract from int, float or measurement type values, not " + str(type(other)).split("'")[1])
        return calc_new_value(other, self, lambda x, y: x - y)

    def __mul__(self, other):
        if not isinstance(other, (int, float, measurement)):
            raise TypeError("Can only multiply by int, float or measurement type values, not " + str(type(other)).split("'")[1])
        return calc_new_value(self, other, lambda x, y: x * y)

    def __rmul__(self, other):
        if not isinstance(other, (int, float, measurement)):
            raise TypeError("Only int, float or measurement type values can be multiplied by, not " + str(type(other)).split("'")[1])
        return calc_new_value(other, self, lambda x, y: x * y)

    def __truediv__(self, other):
        if not isinstance(other, (int, float, measurement)):
            raise TypeError("Can only divide by int, float or measurement type values, not " + str(type(other)).split("'")[1])
        return calc_new_value(self, other, lambda x, y: x / y)

    def __rtruediv__(self, other):
        if not isinstance(other, (int, float, measurement)):
            raise TypeError("Only int, float or measurement type values can be divided by , not " + str(type(other)).split("'")[1])
        return calc_new_value(other, self, lambda x, y: x / y)

    def __pow__(self, other):
        if isinstance(other, (int, float, measurement)):
            raise TypeError("Can only raise to power of int, float or measurement type values, not " + str(type(other)).split("'")[1])
        return calc_new_value(self, other, lambda x, y: x ** y)

    def __pow__(self, other):
        if isinstance(other, (int, float, measurement)):
            raise TypeError("Only int, float or measurement type values can be raised to power, not " + str(type(other)).split("'")[1])
        return calc_new_value(other, self, lambda x, y: x ** y)

    def __str__(self):
        return str(self.value) + " ± " + str(self.error**0.5)
