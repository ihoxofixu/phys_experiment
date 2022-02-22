import sympy as smp
import matplotlib.pyplot as plt
import numpy as np
import types


def calc_new_value(x_var, y_var, func):
    x_var = x_var if isinstance(x_var, measurement) else measurement(x_var, 0)
    y_var = y_var if isinstance(y_var, measurement) else measurement(y_var, 0)

    x = smp.Symbol("x")
    y = smp.Symbol("y")
    tmp_f = func(x, y)

    dev_x = smp.lambdify((x, y), smp.diff(tmp_f, x))(x_var.value, y_var.value)
    dev_y = smp.lambdify((x, y), smp.diff(tmp_f, y))(x_var.value, y_var.value)
    return measurement(func(x_var.value, y_var.value), x_var.error * dev_x ** 2 + y_var.error * dev_y ** 2, square_errors=True)


def round_to(x, digits=3):
    dec_cnt = 0
    while abs(x.value) < 10 ** (digits - 1):
        x *= 10
        dec_cnt += 1
    while abs(x.value) > 10 ** digits:
        x /= 10
        dec_cnt -= 1
    val = str(round(x.value) / 10 ** dec_cnt)
    err = str(round(x.error ** 0.5) / 10 ** dec_cnt)
    val_afterdot = len(val.split(".")[1])
    err_afterdot = len(err.split(".")[1])
    if val_afterdot < err_afterdot:
        val += "0" * (err_afterdot - val_afterdot)
    elif val_afterdot > err_afterdot:
        err += "0" * (val_afterdot - err_afterdot)
    return val + " ± " + err


class measurement:
    def __init__(self, value, *errors, square_errors=False):
        if not isinstance(value, (int, float, measurement)):
            raise ValueError("measurement() arguments must be \'measurement\' or numbers, not \'" + str(type(value)).split("'")[1] + "\'")
        elif isinstance(value, measurement):
            self.value = value.value
            self.error = value.error
        else:
            self.value = value
            res_error = 0
            for error in errors:
                if not isinstance(error, (int, float, measurement)):
                    raise ValueError("measurement() arguments must be \'measurement\' or numbers, not \'" + str(type(error)).split("'")[1] + "\'")
                res_error += error ** (2 - square_errors)
            self.error = res_error

    def __add__(self, other):
        return calc_new_value(self, other, lambda x, y: x + y)

    def __radd__(self, other):
        return calc_new_value(other, self, lambda x, y: x + y)

    def __sub__(self, other):
        return calc_new_value(self, other, lambda x, y: x - y)

    def __rsub__(self, other):
        return calc_new_value(other, self, lambda x, y: x - y)

    def __mul__(self, other):
        return calc_new_value(self, other, lambda x, y: x * y)

    def __rmul__(self, other):
        return calc_new_value(other, self, lambda x, y: x * y)

    def __truediv__(self, other):
        return calc_new_value(self, other, lambda x, y: x / y)

    def __rtruediv__(self, other):
        return calc_new_value(other, self, lambda x, y: x / y)

    def __pow__(self, other):
        return calc_new_value(self, other, lambda x, y: x ** y)

    def __rpow__(self, other):
        return calc_new_value(other, self, lambda x, y: x ** y)

    def __str__(self):
        return str(self.value) + " ± " + str(self.error**0.5)

    def view(self, digits=3):
        print(round_to(self, digits))


def err_linear_MNK(k, b, x, y):
    Dxx = np.var(x)
    Dyy = np.var(y)
    err_k = ((Dyy / Dxx - k ** 2) / (len(x) - 2)) ** 0.5
    err_b = err_k * (np.mean(x ** 2)) ** 0.5
    return err_k, err_b


def plot_exprimental(x, y, xerr=0, yerr=0,
                     xlbl="x", ylbl="y", xmu="", ymu="",
                     fitline=False):
    plt.figure(figsize=(15, 6))
    if isinstance(xerr, types.FunctionType):
        xerr = xerr(np.array(x))
    if isinstance(yerr, types.FunctionType):
        yerr = yerr(np.array(y))
    plt.errorbar(x, y, xerr=xerr, yerr=yerr,
                 marker="o", ms=6.5,
                 linewidth=0, elinewidth=1.8,
                 mec="black", mfc="black", ecolor="grey",
                 label="Experimantal " + ylbl + "(" + xlbl + ")")
    if fitline:
        k_val, b_val = np.polyfit(np.array(x), np.array(y), 1)
        plt.plot(x, k_val * x + bb_val, 'b-', label="y = k * x + b", color="red")
        err_k, err_b = err_linear_MNK(k_val, b_val, x, y)
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
