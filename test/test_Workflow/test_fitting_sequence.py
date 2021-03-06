__author__ = 'sibirrer'

import pytest
import numpy.testing as npt
from lenstronomy.SimulationAPI.simulations import Simulation
from lenstronomy.ImSim.image_model import ImageModel
from lenstronomy.Data.imaging_data import Data
from lenstronomy.Data.psf import PSF
from lenstronomy.PointSource.point_source import PointSource
from lenstronomy.LensModel.lens_model import LensModel
from lenstronomy.LightModel.light_model import LightModel
from lenstronomy.Workflow.fitting_sequence import FittingSequence


class TestFittingSequence(object):
    """
    test the fitting sequences
    """
    def setup(self):
        self.SimAPI = Simulation()

        # data specifics
        sigma_bkg = 0.05  # background noise per pixel
        exp_time = 100  # exposure time (arbitrary units, flux per pixel is in units #photons/exp_time unit)
        numPix = 100  # cutout pixel size
        deltaPix = 0.05  # pixel size in arcsec (area per pixel = deltaPix**2)
        fwhm = 0.5  # full width half max of PSF

        # PSF specification

        data_class = self.SimAPI.data_configure(numPix, deltaPix, exp_time, sigma_bkg)
        psf_class = self.SimAPI.psf_configure(psf_type='GAUSSIAN', fwhm=fwhm, kernelsize=31, deltaPix=deltaPix,
                                               truncate=3,
                                               kernel=None)
        psf_class = self.SimAPI.psf_configure(psf_type='PIXEL', fwhm=fwhm, kernelsize=31, deltaPix=deltaPix,
                                                    truncate=6,
                                                    kernel=psf_class.kernel_point_source)

        # 'EXERNAL_SHEAR': external shear
        kwargs_shear = {'e1': 0.01, 'e2': 0.01}  # gamma_ext: shear strength, psi_ext: shear angel (in radian)
        kwargs_spemd = {'theta_E': 1., 'gamma': 1.8, 'center_x': 0, 'center_y': 0, 'q': 0.8, 'phi_G': 0.2}

        lens_model_list = ['SPEP', 'SHEAR']
        self.kwargs_lens = [kwargs_spemd, kwargs_shear]
        lens_model_class = LensModel(lens_model_list=lens_model_list)
        # list of light profiles (for lens and source)
        # 'SERSIC': spherical Sersic profile
        kwargs_sersic = {'I0_sersic': 1., 'R_sersic': 0.1, 'n_sersic': 2, 'center_x': 0, 'center_y': 0}
        # 'SERSIC_ELLIPSE': elliptical Sersic profile
        kwargs_sersic_ellipse = {'I0_sersic': 1., 'R_sersic': .6, 'n_sersic': 7, 'center_x': 0, 'center_y': 0,
                                 'phi_G': 0.2, 'q': 0.9}

        lens_light_model_list = ['SERSIC']
        self.kwargs_lens_light = [kwargs_sersic]
        lens_light_model_class = LightModel(light_model_list=lens_light_model_list)
        source_model_list = ['SERSIC_ELLIPSE']
        self.kwargs_source = [kwargs_sersic_ellipse]
        source_model_class = LightModel(light_model_list=source_model_list)
        self.kwargs_ps = [{'ra_source': 0.0, 'dec_source': 0.0,
                           'source_amp': 1.}]  # quasar point source position in the source plane and intrinsic brightness
        point_source_list = ['SOURCE_POSITION']
        point_source_class = PointSource(point_source_type_list=point_source_list, fixed_magnification_list=[True])
        kwargs_numerics = {'subgrid_res': 1, 'psf_subgrid': False}
        imageModel = ImageModel(data_class, psf_class, lens_model_class, source_model_class,
                                lens_light_model_class,
                                point_source_class, kwargs_numerics=kwargs_numerics)
        image_sim = self.SimAPI.simulate(imageModel, self.kwargs_lens, self.kwargs_source,
                                         self.kwargs_lens_light, self.kwargs_ps)

        data_class.update_data(image_sim)
        self.data_class = data_class
        self.psf_class = psf_class
        self.kwargs_data = data_class.constructor_kwargs()
        self.kwargs_psf = psf_class.constructor_kwargs()
        self.kwargs_model = {'lens_model_list': lens_model_list,
                               'source_light_model_list': source_model_list,
                               'lens_light_model_list': lens_light_model_list,
                               'point_source_model_list': point_source_list,
                               'fixed_magnification_list': [False],
                             }
        self.kwargs_numerics = {
                               'subgrid_res': 2,
                               'psf_subgrid': True}

        num_source_model = len(source_model_list)

        self.kwargs_constraints = {'joint_center_lens_light': False,
                              'joint_center_source_light': False,
                              'num_point_source_list': [4],
                              'additional_images_list': [False],
                              'fix_to_point_source_list': [False] * num_source_model,
                              'image_plane_source_list': [False] * num_source_model,
                              'solver': False,
                              'solver_type': 'PROFILE_SHEAR',  # 'PROFILE', 'PROFILE_SHEAR', 'ELLIPSE', 'CENTER'
                              }

        self.kwargs_likelihood = {'force_no_add_image': True,
                             'source_marg': True,
                             'point_source_likelihood': False,
                             'position_uncertainty': 0.004,
                             'check_solver': True,
                             'solver_tolerance': 0.001
                             }

    def test_simulationAPI_image(self):
        npt.assert_almost_equal(self.data_class.data[4, 4], 0.1, decimal=0)

    def test_simulationAPI_psf(self):
        npt.assert_almost_equal(self.psf_class.kernel_pixel[1, 1], 1.681921511056146e-07, decimal=8)

    def test_fitting_sequence(self):
        kwargs_init = [self.kwargs_lens, self.kwargs_source, self.kwargs_lens_light, self.kwargs_ps]
        lens_sigma = [{'theta_E_sigma': 0.1, 'gamma_sigma': 0.1, 'ellipse_sigma': 0.1, 'center_x_sigma': 0.1, 'center_y_sigma': 0.1}, {'shear_sigma': 0.1}]
        source_sigma = [{'R_sersic_sigma': 0.05, 'n_sersic_sigma': 0.5, 'center_x_sigma': 0.1, 'center_y_sigma': 0.1, 'ellipse_sigma': 0.1}]
        lens_light_sigma = [{'R_sersic_sigma': 0.05, 'n_sersic_sigma': 0.5, 'center_x_sigma': 0.1, 'center_y_sigma': 0.1}]
        ps_sigma = [{'pos_sigma': 1, 'point_amp_sigma': 1}]
        kwargs_sigma = [lens_sigma, source_sigma, lens_light_sigma, ps_sigma]
        kwargs_fixed = [[{}, {}], [{}], [{}], [{}]]
        kwargs_params = [kwargs_init, kwargs_sigma, kwargs_fixed, kwargs_init, kwargs_init]
        image_band = [self.kwargs_data, self.kwargs_psf, self.kwargs_numerics]
        multi_band_list = [image_band]
        fittingSequence = FittingSequence(multi_band_list, self.kwargs_model, self.kwargs_constraints, self.kwargs_likelihood, kwargs_params)

        lens_temp, source_temp, lens_light_temp, else_temp, chain_list, param_list, samples_mcmc, param_mcmc, dist_mcmc = fittingSequence.fit_sequence(fitting_kwargs_list=[])
        npt.assert_almost_equal(lens_temp[0]['theta_E'], self.kwargs_lens[0]['theta_E'], decimal=2)

        n_p = 2
        n_i = 2
        """
        
        fitting_kwargs_list = [
            {'fitting_routine': 'lens_only', 'sigma_scale': 1, 'n_particles': n_p, 'n_iterations': n_i},
            {'fitting_routine': 'lens_fixed', 'sigma_scale': 1., 'n_particles': n_p, 'n_iterations': n_i},
            {'fitting_routine': 'lens_light_only', 'sigma_scale': .1, 'n_particles': n_p, 'n_iterations': n_i},
            {'fitting_routine': 'source_only', 'sigma_scale': .1, 'n_particles': n_p, 'n_iterations': n_i},
            {'fitting_routine': 'lens_combined_gamma_fixed', 'sigma_scale': 1., 'n_particles': n_p, 'n_iterations': n_i},
            {'fitting_routine': 'lens_combined', 'sigma_scale': 0.1, 'n_particles': n_p,'n_iterations': n_i},
            {'fitting_routine': 'MCMC', 'sigma_scale': 0.1, 'n_burn': 2, 'n_run': 2, 'walkerRatio': 2},
            {'fitting_routine': 'MCMC_source', 'sigma_scale': 0.1, 'n_burn': 2, 'n_run': 2, 'walkerRatio': 2},
            {'fitting_routine': 'align_images', 'lower_limit_shift': -0.1, 'upper_limit_shift': 0.1, 'n_particles': 2, 'n_iterations': 2},
        ]
        lens_temp, source_temp, lens_light_temp, else_temp, chain_list, param_list, samples_mcmc, param_mcmc, dist_mcmc = fittingSequence.fit_sequence(fitting_kwargs_list=fitting_kwargs_list)
        npt.assert_almost_equal(lens_temp[0]['theta_E'], self.kwargs_lens[0]['theta_E'], decimal=2)
        """


if __name__ == '__main__':
    pytest.main()
