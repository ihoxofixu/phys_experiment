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

    def __rpow__(self, other):
        if isinstance(other, (int, float, measurement)):
            raise TypeError("Only int, float or measurement type values can be raised to power, not " + str(type(other)).split("'")[1])
        return calc_new_value(other, self, lambda x, y: x ** y)

    def __str__(self):
        return str(self.value) + " ± " + str(self.error**0.5)


def fit_linear(x_values, y_values, method="MNK"):
    if len(x_values) != len(y_values):
        raise SizeError("Incorrect data, can not pair the values, please check the amount of elements")
    elif len(x_values) < 2:
        raise SizeError("Not enought data, can not fit the line")
    n = len(x_values)

    if method not in ["MNK", "CHI"]:
        raise MethodError("Unrecognised method, can only fit using MNK or CHI method")

    x_sum, y_sum, xx_sum, xy_sum = 0, 0, 0, 0
    w_x_tot, w_y_tot, w_xx_tot, w_xy_tot = 0, 0, 0, 0
    for i in range(len(x_values)):
        if not isinstance(x_values[i], (int, float, measurement)):
            raise TypeError("Can not fit using " + str(type(x_values[i])).split("'")[1] + " type values, only int, float or measurement type")
        elif isinstance(x_values[i], (int, float)):
            if method != "CHI":
                x_values[i] = measurement(x_values[i], 0)
            else:
                raise TypeError("Can not use definite values(int or float) in CHI method")

        if not isinstance(y_values[i], (int, float, measurement)):
            raise TypeError("Can not fit using " + str(type(y_values[i])).split("'")[1] + " type values, only int, float or measurement type")
        elif isinstance(y_values[i], (int, float)):
            if method != "CHI":
                y_values[i] = measurement(y_values[i], 0)
            else:
                raise TypeError("Can not use definite values(int or float) in CHI method")

        w_x, w_y, w_xx, w_xy = 1, 1, 1, 1
        if method == "CHI":
            w_x = 1 / x_values[i].error
            w_y = 1 / y_values[i].error
            w_xx = 1 / (x_values[i] ** 2).error
            w_xy = 1 / (x_values[i] * y_values[i]).error
        x_sum += x_values[i].value * w_x
        y_sum += y_values[i].value * w_y
        xx_sum += x_values[i].value ** 2 * w_xx
        xy_sum += x_values[i].value * y_values[i].value * w_xy
        w_x_tot += w_x
        w_y_tot += w_y
        w_xx_tot += w_xx
        w_xy_tot += w_xy

    x_av, y_av, xx_av, xy_av = x_sum / w_x_tot, y_sum / w_y_tot, xx_sum / w_xx_tot, xy_sum / w_xy_tot
    k_value = (xy_av - x_av * y_av) / (xx_av - x_av ** 2)
    b_value = y_av - k_value * x_av
    return k_value, b_value
