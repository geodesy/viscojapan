import unittest
import os

from numpy import loadtxt

from viscojapan.epochal_data.epochal_sites_data import \
     EpochalSitesData, EpochalSitesFilteredData
from .test_utils import create_a_sites_data_file

_dir_data = os.path.dirname(os.path.abspath(__file__))

class TestEpochalSitesData(unittest.TestCase):
    def setUp(self):
        self.sites_data_file = 'sites_data.h5'
        create_a_sites_data_file(self.sites_data_file)

    def test(self):
        sites_data_obj = EpochalSitesData(self.sites_data_file)

class TestEpochalSitesFilteredData(unittest.TestCase):
    def setUp(self):
        self.sites_data_file = 'sites_data.h5'
        create_a_sites_data_file(self.sites_data_file)
        self.filter_sites_file = os.path.join(_dir_data,'filter_sites')
        self.filter_sites = loadtxt(self.filter_sites_file,'4a')

    def test(self):
        sites_data_obj = EpochalSitesFilteredData(self.sites_data_file,
                                                  self.filter_sites_file)

        epochs = sites_data_obj.get_epochs()
        for epoch in epochs:
            val = sites_data_obj.get_epoch_value(epoch)

        for epoch in epochs[:-1]:
            val = sites_data_obj.get_epoch_value(epoch+0.1)
        
if __name__== '__main__':
    unittest.main()
