from pygrapher.grapher import *
from pygrapher.equations import *
import matplotlib.pyplot as plt
import numpy as np


def linear_fitter(x_array, y_origin, range, label = None, show_params = True, line_color = 'random', legend = None, scatter = True, point_color = 'random', point_size = 20, show_digit = 3, point_legend = None, point_label = None):
    '''
    x_array(required): x array (type: list) for fitting
    y_origin(required): y array(type: list) for fitting
    range(required): x range for you to draw the graph (e.g[0, 100])
    '''
    var_ls = fit(linear, x_array, y_origin)
    draw_fitted_normal(linear, var_ls, range, label= label, color = line_color, show_params = show_params, show_digit = show_digit)
    if scatter:
        show_scatter(x_array, y_origin, color = point_color, point_size = point_size, label = point_label)
    if label != None:
        if legend != None:
            plt.legend(loc = legend)
        else:
            plt.legend(loc = 'best')


    
def poly_fitter(n, x_array, y_origin, range, label = None, show_params = True, line_color = 'random', legend = None, scatter = True, point_color = 'random', point_size = 20, show_digit = 3, point_legend = None, point_label = None):
    fit_draw_poly(n, x_array, y_origin, range, label = label, color = line_color, show_params = True, show_digit = show_digit)
    
    if scatter:
        show_scatter(x_array, y_origin, color = point_color, point_size = point_size, label = point_label)

    if label != None:
        if legend != None:
            plt.legend(loc = legend)
        else:
            plt.legend(loc = 'best')


def exp_fitter(x_array, y_origin, range, e_base = True, param = False, label = None, show_params = True, line_color = 'random', legend = None, scatter = True, point_color = 'random', point_size = 20, show_digit = 3, point_legend = None, point_label = None):
    if e_base:
        if param == None:
            var_ls = fit(e_exponential, x_array, y_origin)
            draw_fitted_normal(e_exponential, var_ls, range, label= label, color = line_color, show_params = show_params, show_digit = show_digit)
        else:
            var_ls = fit(e_exponential_with_param, x_array, y_origin)
            draw_fitted_normal(e_exponential_with_param, var_ls, range, label= label, color = line_color, show_params = show_params, show_digit = show_digit)
    else:
        if param == False:
            var_ls = fit(exponential, x_array, y_origin)
            draw_fitted_normal(exponential, var_ls, range, label= label, color = line_color, show_params = show_params, show_digit = show_digit)
        else:
            var_ls = fit(exponential_with_param, x_array, y_origin)
            draw_fitted_normal(exponential_with_param, var_ls, range, label= label, color = line_color, show_params = show_params, show_digit = show_digit)

    if scatter:
        show_scatter(x_array, y_origin, color = point_color, point_size = point_size, label = point_label)
    
    if label != None:
        if legend != None:
            plt.legend(loc = legend)
        else:
            plt.legend(loc = 'best')




def log_fitter(x_array, y_origin, range, label = None, show_params = True, line_color = 'random', legend = None, scatter = True, point_color = 'random', point_size = 20, show_digit = 3, point_legend = None, point_label = None):
    
    var_ls = fit(logarithm, x_array, y_origin)
    draw_fitted_normal(logarithm, var_ls, range, label= label, color = line_color, show_params = show_params, show_digit = show_digit)

    if scatter:
        show_scatter(x_array, y_origin, color = point_color, point_size = point_size, label = point_label)

    if label != None:
        if legend != None:
            plt.legend(loc = legend)
        else:
            plt.legend(loc = 'best')


__all__ = ["linear_fitter", "poly_fitter", "exp_fitter", "log_fitter"]