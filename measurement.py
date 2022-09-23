import sympy as smp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import types


class measurement:
    def __init__(self, value, *errors, square_errors=False):
        if not isinstance(value, (int, float, measurement)):
            raise TypeError("measurement() arguments must be \'measurement\' or numbers, not \'" + str(type(value)).split("'")[1] + "\'")
        res_error = 0
        for error in errors:
            if not isinstance(error, (int, float)):
                raise TypeError("eroor arguments must be numbers, not \'" + str(type(error)).split("'")[1] + "\'")
            res_error += error ** (2 - square_errors)
        if isinstance(value, measurement):
            self.value = value.value
            self.error = value.error + res_error
        else:
            self.value = value
            self.error = res_error

    def __calc_new_value(self, x_var, y_var, func):
        x_var = x_var if isinstance(x_var, measurement) else measurement(x_var, 0)
        y_var = y_var if isinstance(y_var, measurement) else measurement(y_var, 0)

        x = smp.Symbol("x")
        y = smp.Symbol("y")
        tmp_f = func(x, y)

        dev_x = smp.lambdify((x, y), smp.diff(tmp_f, x))(x_var.value, y_var.value)
        dev_y = smp.lambdify((x, y), smp.diff(tmp_f, y))(x_var.value, y_var.value)
        return measurement(func(x_var.value, y_var.value), x_var.error * dev_x ** 2 + y_var.error * dev_y ** 2, square_errors=True)

    def __round_to(self, digits=3):
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
        return measurement(self)

    def view(self, digits=3):
        print(self.__round_to(digits))


class PlotPlot:
    def __check_exp_type(self, data_experimental):
        if not isinstance(data_experimental, (list, np.ndarray, pd.core.series.Series)):
            raise TypeError("data_experimental argument must be list, np.array or pd.core.series.Series, not \'" + str(type(data_experimental)).split("'")[1] + "\'")

    def __check_err_type(self, err):
        if not isinstance(err, (types.FunctionType, list, np.ndarray, pd.core.series.Series)):
            raise TypeError("error arguments must be function, list, np.array or pd.core.series.Series, not \'" + str(type(xerr)).split("'")[1] + "\'")

    def __init__(self, x_experimental, y_experimental, xerr=None, yerr=None):
        self.__check_exp_type(x_experimental)
        self.__check_exp_type(y_experimental)

        if xerr is None:
            xerr = [0 for i in range(len(x_experimental))]
        if isinstance(xerr, (int, float)):
            xerr = [xerr for i in range(len(x_experimental))]

        if yerr is None:
            yerr = [0 for i in range(len(y_experimental))]
        if isinstance(yerr, (int, float)):
            yerr = [yerr for i in range(len(y_experimental))]

        self.__check_err_type(xerr)
        self.__check_err_type(yerr)

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
        plt.figure(figsize=(15, 6))

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
            err_k, err_b = self.__err_linear_MNK(k_val, b_val, x, y)
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
        else:
            return None, None
