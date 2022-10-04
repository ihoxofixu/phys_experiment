import sympy as smp
import matplotlib.pyplot as plt
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
            self.value = value
            self.error = res_error

    def __calc_new_value(x_var, y_var, func):
        x_var = x_var if isinstance(x_var, measurement) else measurement(x_var, 0)
        y_var = y_var if isinstance(y_var, measurement) else measurement(y_var, 0)

        x = smp.Symbol("x")
        y = smp.Symbol("y")
        tmp_f = func(x, y)

        dev_x = smp.lambdify((x, y), smp.diff(tmp_f, x))(x_var.value, y_var.value)
        dev_y = smp.lambdify((x, y), smp.diff(tmp_f, y))(x_var.value, y_var.value)
        return measurement(func(x_var.value, y_var.value), x_var.error * dev_x ** 2 + y_var.error * dev_y ** 2, square_errors=True)

    def round_to(self, digits=3):
        dec_cnt = 0
        x = self.deepcopy()
        while abs(x.value) < 10 ** (digits - 1):
            x *= 10
            dec_cnt -= 1
        while abs(x.value) > 10 ** digits:
            x /= 10
            dec_cnt += 1
        val = str(round(x.value))
        err = str(round(x.error ** 0.5))
        if len(err) < len(val):
            err = "0" * (len(val) - len(err)) + err
        return "(" + val[0] + "." + val[1::] + " ± " + err[0] + "." + err[1::] + ")e" + str(dec_cnt + len(val) - 1)

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

    def view(self, digits=3):
        """
        Receives the amount of significant digits and prints the value with this accuracy
        """
        print(self.round_to(digits))


class PlotPlot:
    """Class PlotPlot

    Class to visualise experimental dependences.
    Initialisation is done by passing X values and Y values with their errors
    Right now it is only able to approximate with a line using Least Squares method
    """

    def __check_exp_type(data_experimental):
        if not isinstance(data_experimental, (list, np.ndarray, pd.core.series.Series)):
            raise TypeError("data_experimental argument must be list, np.array or pd.core.series.Series, not \'" + str(type(data_experimental)).split("'")[1] + "\'")

    def __check_err_type(err):
        if not isinstance(err, (types.FunctionType, list, np.ndarray, pd.core.series.Series)):
            raise TypeError("error arguments must be function, list, np.array or pd.core.series.Series, not \'" + str(type(xerr)).split("'")[1] + "\'")

    def __init__(self, x_experimental, y_experimental, xerr=0, yerr=0):
        """
        x_experimental - list of int/float/measurement/np.int64, np.array, pd.core.series.Series
        y_experimental - list of int/float/measurement/np.int64., np.array, pd.core.series.Series

        xerr(optional) - int, float, np.int64, list of int/float/np.int64, np.array, pd.core.series.Series, function
        yerr(optional) - int, float, np.int64, list of int/float/np.int64, np.array, pd.core.series.Series, function

        NOTE:
        passing errors with X_experimental being list of measurements adds errors to values
        passing errors as function with X_experimental being list of measurements throws Exception(I'm thinking how to avoid it smartly)
        """
        #checking the types of values
        #TODO: iterate through to find non math types such as str
        measurement.__check_exp_type(x_experimental)
        measurement.__check_exp_type(y_experimental)

        #checking the types of errors
        #TODO: iterate through to find non math types such as str
        if isinstance(xerr, (int, float, np.int64)):
            xerr = [xerr for i in range(len(x_experimental))]

        if isinstance(yerr, (int, float, np.int64)):
            yerr = [yerr for i in range(len(y_experimental))]

        measurement.__check_err_type(xerr)
        measurement.__check_err_type(yerr)

        #checking values list and value errors list to be the same size
        if not isinstance(xerr, (types.FunctionType)) and len(x_experimental) != len(xerr):
            raise Exception("xerr length does not match x_experimental length")
        if not isinstance(yerr, (types.FunctionType)) and len(y_experimental) != len(yerr):
            raise Exception("yerr length does not match y_experimental length")
        if len(x_experimental) != len(y_experimental):
            raise Exception("y_experimental length does not match x_experimental length")

        if isinstance(xerr, types.FunctionType):
            xerr = xerr(np.array(x_experimental))
        if isinstance(yerr, types.FunctionType):
            yerr = yerr(np.array(y_experimental))

        xx = []
        yy = []
        for i in range(len(x_experimental)):
            xx.append(measurement(x_experimental[i], xerr[i]))
        for i in range(len(y_experimental)):
            yy.append(measurement(y_experimental[i], yerr[i]))

        self.xx = xx
        self.yy = yy

    def __err_linear_MNK(self, k, b, x, y):
        Dxx = np.var(x)
        Dyy = np.var(y)
        err_k = ((Dyy / Dxx - k ** 2) / (len(x) - 2)) ** 0.5
        err_b = err_k * (np.mean(x ** 2)) ** 0.5
        return err_k, err_b


    def plot(self, xlbl="x", ylbl="y", xmu="", ymu="", fitline=False):
        """
        xlbl    - x axis label
        ylbl    - y axis label
        xmu     - measurenemt unit of value on the x axis
        ymu     - measurenemt unit of value on the y axis
        fitline - whether you want to approximate your scatter plot with a line

        with fitline being true returns k and b from line y = k * x + b
        """
        plt.figure(figsize=(15, 6))

        #this is disgusting, to be changed
        x, y, xerr, yerr = [], [], [], []
        for i in range(len(self.xx)):
            x.append(self.xx[i].value)
            xerr.append(self.xx[i].error**0.5)
            y.append(self.yy[i].value)
            yerr.append(self.yy[i].error**0.5)
        x = np.array(x)
        xerr = np.array(xerr)
        y = np.array(y)
        yerr = np.array(yerr)

        plt.errorbar(x, y, xerr=xerr, yerr=yerr,
                     marker="o", ms=6.5,
                     linewidth=0, elinewidth=1.8,
                     mec="black", mfc="black", ecolor="grey",
                     label="Experimantal " + ylbl + "(" + xlbl + ")")
        if fitline:
            k_val, b_val = np.polyfit(np.array(x), np.array(y), 1)
            plt.plot(x, k_val * x + b_val, 'b-', label="y = k * x + b", color="red")
            err_k, err_b = measurement.__err_linear_MNK(k_val, b_val, x, y)
            k = measurement(k_val, err_k)
            b = measurement(b_val, err_b)
        plt.xlabel(xlbl+", " * (len(xmu) != 0)+xmu)
        plt.ylabel(ylbl+", " * (len(ymu) != 0)+ymu)
        plt.legend()
        plt.minorticks_on()
        plt.grid(which='major')
        plt.grid(which='minor', linestyle=':')
        plt.show()
        if fitline:
            k.view()
            b.view()
            return k, b
