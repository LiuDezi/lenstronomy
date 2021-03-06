__author__ = 'sibirrer'
#this file contains a class to make a gaussian

import numpy as np
import lenstronomy.Util.util as util
from lenstronomy.LensModel.Profiles.sersic_utils import SersicUtil


class Sersic(SersicUtil):
    """
    this class contains functions to evaluate a Sersic mass profile: https://arxiv.org/pdf/astro-ph/0311559.pdf
    """


    def function(self, x, y, n_sersic, r_eff, k_eff, center_x=0, center_y=0):
        """
        returns Gaussian
        """
        n = n_sersic
        x_red = self._x_reduced(x, y, n, r_eff, center_x, center_y)
        b = self.b_n(n)
        #hyper2f2_b = util.hyper2F2_array(2*n, 2*n, 1+2*n, 1+2*n, -b)
        hyper2f2_bx = util.hyper2F2_array(2*n, 2*n, 1+2*n, 1+2*n, -b*x_red)
        f_eff = np.exp(b)*r_eff**2/2.*k_eff# * hyper2f2_b
        f_ = f_eff * x_red**(2*n) * hyper2f2_bx# / hyper2f2_b
        return f_

    def derivatives(self, x, y, n_sersic, r_eff, k_eff, center_x=0, center_y=0):
        """
        returns df/dx and df/dy of the function
        """
        x_ = x - center_x
        y_ = y - center_y
        r = np.sqrt(x_**2 + y_**2)
        if isinstance(r, int) or isinstance(r, float):
            r = max(self._s, r)
        else:
            r[r < self._s] = self._s
        alpha = -self.alpha_abs(x, y, n_sersic, r_eff, k_eff, center_x, center_y)
        f_x = alpha * x_ / r
        f_y = alpha * y_ / r
        return f_x, f_y

    def hessian(self, x, y, n_sersic, r_eff, k_eff, center_x=0, center_y=0):
        """
        returns Hessian matrix of function d^2f/dx^2, d^f/dy^2, d^2/dxdy
        """
        x_ = x - center_x
        y_ = y - center_y
        r = np.sqrt(x_**2 + y_**2)
        if isinstance(r, int) or isinstance(r, float):
            r = max(self._s, r)
        else:
            r[r < self._s] = self._s
        d_alpha_dr = self.d_alpha_dr(x, y, n_sersic, r_eff, k_eff, center_x, center_y)
        alpha = -self.alpha_abs(x, y, n_sersic, r_eff, k_eff, center_x, center_y)

        #f_xx_ = d_alpha_dr * calc_util.d_r_dx(x_, y_) * x_/r + alpha * calc_util.d_x_diffr_dx(x_, y_)
        #f_yy_ = d_alpha_dr * calc_util.d_r_dy(x_, y_) * y_/r + alpha * calc_util.d_y_diffr_dy(x_, y_)
        #f_xy_ = d_alpha_dr * calc_util.d_r_dy(x_, y_) * x_/r + alpha * calc_util.d_x_diffr_dy(x_, y_)

        f_xx = -(d_alpha_dr/r + alpha/r**2) * x_**2/r + alpha/r
        f_yy = -(d_alpha_dr/r + alpha/r**2) * y_**2/r + alpha/r
        f_xy = -(d_alpha_dr/r + alpha/r**2) * x_*y_/r

        return f_xx, f_yy, f_xy
