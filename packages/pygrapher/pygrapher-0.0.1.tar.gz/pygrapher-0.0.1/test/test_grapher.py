# in command line: python -m unittest test.test_grapher
import unittest

from pygrapher.grapher import *
from pygrapher.equations import *

class TestGrapher(unittest.TestCase):
    longMessage = True

    def test_fit(self):
        test_eq = linear
        x_array = [0, 1, 2]
        y_array = [0, 1, 2]
        print(fit(test_eq, x_array, y_array))

    def test_draw_fitted_normal(self):
        x_array = [0, 1, 2]
        y_array = [0, 1, 2]
        fit1 = linear
        fit2 = e_exponential
        draw_fitted_normal(fit1, fit(fit1, x_array, y_array), [0,10], color = 'red', show_params = True)
        draw_fitted_normal(fit2, fit(fit2, x_array, y_array), [0,5], legend = 'upper right', show_params= True)
        show_scatter(x_array, y_array, color = 'green', point_size = 20)

    def test_fit_draw_ploy(self):
        x_array = [0 ,1, 2, 3]
        y_array = [1, 2, 5, 10]
        fit_draw_poly(2, x_array, y_array, [0,20], show_params = True, label = 'FUCK', legend = 'upper right')
    
