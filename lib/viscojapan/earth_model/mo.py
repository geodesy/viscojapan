import h5py
from numpy import log10, asarray
import numpy as np

from viscojapan.epochal_data import EpochalIncrSlip
import viscojapan as vj

from .earth_model_file_reader import EarthModelFileReader

class ComputeMoment(object):
    def __init__(self, fault_file, earth_file):
        self.fault_model_file = fault_file
        self.earth_model_file = earth_file

    def _get_shear(self):
        reader = vj.FaultFileReader(self.fault_model_file)
        ddeps = reader.ddeps[1:, 1:]
        reader = EarthModelFileReader(self.earth_model_file)
        return reader.get_shear_modulus(ddeps)
        
        
    def moment(self, slip):
        ''' Compute moment.
'''
        reader = vj.FaultFileReader(self.fault_model_file)
        
        fl = reader.subflt_sz_dip
        fw = reader.subflt_sz_strike
        
        shr = self._get_shear()
        mos = shr.flatten()*slip.flatten()*fl*1e3*fw*1e3
        mo = np.sum(mos)
        mw = 2./3.*log10(mo) - 6. 
        return mo, mw

def get_mos_mws_from_epochal_file(epochal_file):
    slip = EpochalIncrSlip(epochal_file)
    epochs = slip.get_epochs()

    mws = []
    mos = []
    for epoch in epochs:
        alpha = slip.get_info('alpha')
        s = slip.get_epoch_value(epoch)

        M = ComputeMoment()
        mo,mw = M.moment(s)
        mws.append(mw)
        mos.append(mo)
    return asarray(mos), asarray(mws), asarray(epochs)
