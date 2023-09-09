import sympy as smp
import numpy as np
import pandas as pd
import types


class measurement:
    """Class measurement

    Implements a value with an error and arithmetic features to work with errors.
    Operators to be added: "+=", "-=", "*=", "/="
    """
    def __init__(self, value, *errors, square_errors=False):
        """
        value         - the exact value you get from your measurers durig lab
        errors        - all the possible errors such as instrument error, random error, etc.
        square errors - wheather you pass errors already to the power of 2 or not
        """
        if not isinstance(value, (int, float, measurement, np.int64)):
            raise TypeError("measurement() arguments must be \'measurement\' or numbers, not \'" + str(type(value)).split("'")[1] + "\'")
        res_error = 0
        for error in errors:
            if not isinstance(error, (int, float, np.int64)):
                raise TypeError("error arguments must be numbers, not \'" + str(type(error)).split("'")[1] + "\'")
            res_error += error ** (2 - square_errors)
        if isinstance(value, measurement):
            self.value = value.value
            self.error = value.error + res_error
        else:
            self.value = float(value)
            self.error = float(res_error)

    def __calc_new_value(self, x_var, y_var, func):
        x_var = x_var if isinstance(x_var, measurement) else measurement(x_var, 0)
        y_var = y_var if isinstance(y_var, measurement) else measurement(y_var, 0)

        x = smp.Symbol("x")
        y = smp.Symbol("y")
        tmp_f = func(x, y)

        dev_x = smp.lambdify((x, y), smp.diff(tmp_f, x))(x_var.value, y_var.value)
        dev_y = smp.lambdify((x, y), smp.diff(tmp_f, y))(x_var.value, y_var.value)
        return measurement(func(x_var.value, y_var.value), x_var.error * dev_x ** 2 + y_var.error * dev_y ** 2, square_errors=True)

    def __add__(self, other):
        return self.__calc_new_value(self, other, (lambda x, y: x + y))

    def __radd__(self, other):
        return self.__calc_new_value(other, self, (lambda x, y: x + y))

    def __sub__(self, other):
        return self.__calc_new_value(self, other, (lambda x, y: x - y))

    def __rsub__(self, other):
        return self.__calc_new_value(other, self, (lambda x, y: x - y))

    def __mul__(self, other):
        return self.__calc_new_value(self, other, (lambda x, y: x * y))

    def __rmul__(self, other):
        return self.__calc_new_value(other, self, (lambda x, y: x * y))

    def __truediv__(self, other):
        return self.__calc_new_value(self, other, (lambda x, y: x / y))

    def __rtruediv__(self, other):
        return self.__calc_new_value(other, self, (lambda x, y: x / y))

    def __pow__(self, other):
        return self.__calc_new_value(self, other, (lambda x, y: x ** y))

    def __rpow__(self, other):
        return self.__calc_new_value(other, self, (lambda x, y: x ** y))

    def __str__(self):
        return str(self.value) + " ± " + str(self.error**0.5)

    def deepcopy(self):
        """
        Returns the copy of element
        """
        return measurement(self)
    
    def round_to(self, digits=3, for_print=True):
        """
        Either returns a string if for_print is True or a measurement if for_print is False
        default for_print = True
        """
        tmp = self.deepcopy()
        dec_deg = 0
        if abs(tmp.value) < 10**digits:
            while abs(tmp.value) <= 10**digits:
                tmp = tmp * 10
                dec_deg -= 1
        while abs(tmp.value) >= 10**digits:
                tmp = tmp / 10
                dec_deg += 1
        if for_print:
            if abs(dec_deg) > 3:
                return f"({str(measurement(round(tmp.value), round(tmp.error**0.5)))})e{dec_deg}"
            else:
                tmp = measurement(round(tmp.value), round(tmp.error**0.5)) * 10**dec_deg
                return str(tmp)
        else:
            return tmp * 10**dec_deg

    def view(self, digits=3):
        """
        Receives the amount of significant digits and prints the value with this accuracy
        """
        print(self.round_to(digits))