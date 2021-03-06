__author__ = 'sibirrer'

import pytest
import numpy as np
import numpy.testing as npt
from lenstronomy.PointSource.point_source_param import PointSourceParam


class TestParam(object):

    def setup(self):
        kwargs_model = {'num_point_sources_list': [4], 'point_source_model_list': ['LENSED_POSITION', 'SOURCE_POSITION', 'UNLENSED']}
        kwargs_fixed = [{}, {}, {}]
        num_point_sources_list = [4]
        point_source_model_list = ['LENSED_POSITION', 'SOURCE_POSITION', 'UNLENSED']
        self.param = PointSourceParam(model_list=point_source_model_list, kwargs_fixed=kwargs_fixed, num_point_source_list=num_point_sources_list)
        self.kwargs =[{'ra_image': np.array([0, 0, 0, 0]), 'dec_image': np.array([0 , 0, 0, 0]),
                       'point_amp': np.array([1, 1, 1, 1])},
                      {'ra_source': 1, 'dec_source': 1, 'point_amp': 1.},
                      {'ra_image': 1, 'dec_image': 1, 'point_amp': 1.}]
        self.kwargs_sigma = [{'pos_sigma': 1, 'point_amp_sigma': 1}, {'pos_sigma': 1, 'point_amp_sigma': 1}, {'pos_sigma': 1, 'point_amp_sigma': 1}]

        self.kwargs_mean = []
        for i in range(len(self.kwargs)):
            kwargs_mean_k = self.kwargs[i].copy()
            kwargs_mean_k.update(self.kwargs_sigma[i])
            self.kwargs_mean.append(kwargs_mean_k)

    def test_get_setParams(self):
        args = self.param.setParams(self.kwargs)
        kwargs_new, _ = self.param.getParams(args, i=0)
        args_new = self.param.setParams(kwargs_new)
        for k in range(len(args)):
            npt.assert_almost_equal(args[k], args_new[k], decimal=8)

    def test_param_init(self):
        mean, sigma = self.param.param_init(self.kwargs_mean)
        assert mean[0] == 0

    def test_num_params(self):
        num, list = self.param.num_param()
        assert num == 12


if __name__ == '__main__':
    pytest.main()
