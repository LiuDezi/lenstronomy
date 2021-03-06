__author__ = 'sibirrer'


import lenstronomy.Util.class_creator as class_creator
from lenstronomy.LensModel.lens_model import LensModel

import numpy.testing as npt
import pytest


class TestClassCreator(object):

    def setup(self):
        self.kwargs_model = {'lens_model_list': ['SIS'], 'source_light_model_list': ['SERSIC'],
                             'lens_light_model_list': ['SERSIC'], 'point_source_model_list': ['LENSED_POSITION']}
        self.kwargs_psf = {'psf_type': 'NONE'}
        self.kwargs_data = {'numPix': 10}

    def test_creat_lens_model_extension(self):
        lensModel = LensModel(lens_model_list=['SIS'])
        lensExtensions = class_creator.creat_lens_model_extension(lensModel)
        theta_E = lensExtensions.effective_einstein_radius(kwargs_lens_list=[{'theta_E': 1, 'center_x': 0, 'center_y': 0}])
        npt.assert_almost_equal(theta_E, 1, decimal=1)

    def test_creat_image_model(self):
        imageModel = class_creator.creat_image_model(self.kwargs_data, self.kwargs_psf, kwargs_numerics={}, kwargs_model=self.kwargs_model)
        assert imageModel.LensModel.lens_model_list[0] == 'SIS'

        imageModel = class_creator.creat_image_model(self.kwargs_data, self.kwargs_psf, kwargs_numerics={},
                                                     kwargs_model={})
        assert imageModel.LensModel is None

    def test_creat_multiband(self):
        multi_band_list = [[self.kwargs_data, self.kwargs_psf, {}]]
        multi_band = class_creator.creat_multiband(multi_band_list, self.kwargs_model)
        assert multi_band.lensModel.lens_model_list[0] == 'SIS'

        multi_band = class_creator.creat_multiband(multi_band_list, {})
        assert multi_band.lensModel is None


if __name__ == '__main__':
    pytest.main()
