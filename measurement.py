import sympy


def calc_new_value(x_var, y_var, func):
    x_var = x_var if isinstance(x_var, measurement) else measurement(x_var, 0)
    y_var = y_var if isinstance(y_var, measurement) else measurement(y_var, 0)

    x = sympy.Symbol("x")
    y = sympy.Symbol("y")
    tmp_f = func(x, y)

    dev_x = sympy.lambdify((x, y), sympy.diff(tmp_f, x))(x_var.value, y_var.value)
    dev_y = sympy.lambdify((x, y), sympy.diff(tmp_f, y))(x_var.value, y_var.value)
    return measurement(func(x_var.value, y_var.value), x_var.error * dev_x ** 2 + y_var.error * dev_y ** 2, square_errors=True)


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
