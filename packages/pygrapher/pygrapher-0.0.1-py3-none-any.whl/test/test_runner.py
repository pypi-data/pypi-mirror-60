# in command line: python -m unittest test.test_runner

import unittest

from pygrapher.runner import *
import matplotlib.pyplot as plt 

class TestRunner(unittest.TestCase):
    # def test_linear_fitter(self):
    #     x_array = [1, 2, 22, 3, 4]
    #     y_array = [1, 2, 3.5, 4.7777, 5]
    #     point_range = [0, 10]
    #     linear_fitter(x_array = x_array, y_origin = y_array, range = point_range, line_color = 'red', point_color = 'blue', label = 'fuck', point_label = 'point')

    def test_poly_fitter(self):
        x_array = [1, 2, 3, 4, 6]
        y_array = [3, 6, 7, 5, 2]
        point_range = [0, 20]
        poly_fitter(3, x_array = x_array, y_origin = y_array, range = point_range, line_color = 'red', point_color = 'blue', label = 'fuck', point_label = 'point')
        poly_fitter(2, x_array, y_array, point_range)
        plt.show()

    def test_exp_fitter(self):
        x_array = [1, 2, 3, 4, 5]
        y_array = [3, 4, 5, 7, 6]
        point_range = [0, 20]
        exp_fitter(x_array, y_array, point_range, e_base = False, param = True)
        exp_fitter(x_array, y_array, point_range)
        plt.show()

    # def test_log_fitter(self):
    #     x_array = [1, 2, 3, 4, 5, 7]
    #     y_array = [2, 6, 3, 7, 2, 5]
    #     point_range = [0, 100]
    #     log_fitter(x_array, y_array, point_range)