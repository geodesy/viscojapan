import pickle

from numpy import log10

from ..epochal_data.epochal_sites_data import EpochalG, EpochalDisplacement
from ..epochal_data.diff_ed import DiffED
from ..least_square.tikhonov_regularization import TikhonovSecondOrder
from ..least_square.least_square import LeastSquare
from .formulate_occam import JacobianVec, Jacobian, D_

class OccamInversion:
    ''' Connet relative objects to work together to do inversion.
'''
    def __init__(self):
        self.sites_file = ''

        self.file_G1 = ''
        self.file_G2 = ''

        self.f_d = ''

        self.f_slip0 = ''

        self.epochs = []

        self.non_lin_par_vals = []

    def _init_jacobian_vecs(self):
        self.G1 = EpochalG(self.file_G1, self.sites_file)
        G2 = EpochalG(self.file_G2, self.sites_file)
        dG = DiffED(self.G1, G2, 'log10_visM')

        jac_1 = JacobianVec(dG, self.f_slip0)

        self.jacobian_vecs = [jac_1]
        

    def _init_jacobian(self):
        jacobian = Jacobian()
        jacobian.G = self.G1
        jacobian.jacobian_vecs = self.jacobian_vecs
        jacobian.epochs = self.epochs
        self.jacobian = jacobian
        
    def _init_d_(self):
        d_ = D_()
        d_.jacobian_vecs = self.jacobian_vecs
        d_.non_lin_par_vals = self.non_lin_par_vals
        d_.epochs = self.epochs

        obs = EpochalDisplacement(self.f_d, self.sites_file)
        d_.d = obs

        self.d_ = d_

    def _init_tikhonov_regularization(self):
        # regularization
        reg = TikhonovSecondOrder(nrows_slip=10, ncols_slip=25)
        reg.row_norm_length = 1
        reg.col_norm_length = 28./23.03
        reg.num_epochs = len(self.epochs)
        reg.num_nlin_pars = 1
        self.tikhonov_regularization = reg

    def init(self):
        self._init_jacobian_vecs()
        self._init_jacobian()
        self._init_d_()
        self._init_tikhonov_regularization()
        

    def init_least_square(self):
        ''' The computation of the following three variable is quite time
cosuming. Because I need to do inversion for a series of alphas, I need to
pre-compute these three variable so that I don't need to compute them
everytime the alpha values changes.

Before. pickle this class, I need to delete these three variables, because
they take a lot memory and space.

jacobian
d_
tikhonov_regularization
'''       
        self.jacobian_mat = self.jacobian()
        self.d__vec = self.d_()
        
        self.regularization_mat = self.tikhonov_regularization()
        

    def invert(self, alpha):
        least_square = LeastSquare()
        
        least_square.G = self.jacobian_mat
        least_square.d = self.d__vec
        least_square.regularization_matrix = self.regularization_mat
        
        least_square.alpha = alpha
        self.alpha =  alpha
        
        self.solution = least_square()

    def pickle(self,fn):
        self.jacobian = None
        self.d_ = None
        #self.tikhonov_regularization = None
        
        with open(fn, 'wb') as fid:
            pickle.dump(self, fid)

        
