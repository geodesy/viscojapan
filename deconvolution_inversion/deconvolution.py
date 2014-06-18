from numpy.random import normal

from viscojapan.deconvolution_inversion import Deconvolution
from viscojapan.utils import gen_error_for_sites    

class DeconvolutionTestFromFakeObs(Deconvolution):
    def __init__(self):
        super().__init__()
        self.file_G = '/home/zy/workspace/viscojapan/greensfunction/050km-vis02/G.h5'
        self.file_fake_d = 'simulated_disp.h5'
        self.sites_filter_file = 'sites'
        self.epochs = [0, 10, 1100]        

    def get_d(self):
        d = super().get_d()
        num_obs = len(d)
        assert num_obs%3 == 0, 'Wrong number of observations.'
        num_sites = num_obs//3
        error = gen_error_for_sites(num_sites)
        d += error
        return d

if __name__ == '__main__':
    dtest = DeconvolutionTest()
    dtest.init()
    dtest.load_data()
    alpha = 1.
    dtest.invert(alpha)
