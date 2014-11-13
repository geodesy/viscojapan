from os.path import exists

import h5py

from ..file_io_base import FileIOBase

__doc__ = ''' Some design consideration:
Class EpochalFileWriter and EpochalFileReader define only the most
basic writing and reading activity on epochal file.
Remember Single Responsibility Principle.
There two classes should keep small and tight.
Other functions based on these two should be dispatched to
other functions or classes.
'''

__all__ = ['EpochalFileWriter', 'EpochalFileReader']

class EpochalFileWriter(FileIOBase):
    def __init__(self,
                 file_name):
        super().__init__(file_name)
        
    def open(self):
        assert not exists(self.file_name), "File exists!"
        fid = h5py.File(self.file_name,'w-')
        return fid
    
    def set_epoch_value(self, time, value):
        assert isinstance(time,int), 'Time %s is not integer.'%(str(time))
        self.fid['epochs/%04d'%time] = value

    def set_info(self, key, value, **kwargs):
        ''' Set info. **args are attributs
'''
        self.fid['info/%s'%key] = value        
        for key_attr, value_attr in kwargs.items():
            self.fid['info/%s'%key].attrs[key_attr] = value_attr

    def set_info_dic(self, info_dic):
        for key, val in info_dic.items():
            self.set_info(key,val)

    def set_info_attr(self,key, key_attr, value_attr):
        self.fid['info/%s'%key].attrs[key_attr] = value_attr

    def __setitem__(self, name, val):
        if isinstance(name, int):
            return self.set_epoch_value(name, val)
        elif isinstance(name, str):
            return self.set_info(name, val)
        else:
            raise ValueError('Not recognized type.')

class EpochalFileReader(FileIOBase):
    ''' Use this class to CREATE and READ epochal data file.
'''
    def __init__(self,
                 file_name):
        super().__init__(file_name)

    def open(self):
        assert exists(self.file_name), "File must exists!"
        fid = h5py.File(self.file_name,'r')
        return fid

    def _assert_within_range(self,epoch):
        epochs = self.get_epochs()
            
        max_day = max(epochs)
        min_day = min(epochs)
        assert epoch <= max_day, 'Max day: %d'%max_day
        assert epoch >= min_day, 'Min day: %d'%min_day

    def _get_epoch_value(self, epoch):
        epochs = self.get_epochs()
        assert epoch in epochs, "Interpolation is not allowed in this method."
        out = self.fid['epochs/%04d'%epoch][...]
        return out
    
    def get_epoch_value(self, epoch):
        self._assert_within_range(epoch)
        epochs = self.get_epochs()
        if epoch in epochs:
            return self._get_epoch_value(epoch)
        for nth, ti in enumerate(epochs[1:]):
            if epoch <= ti:
                break
        t1 = epochs[nth]
        t2 = epochs[nth+1]

        assert (t1<t2) and (t1<=epoch) and (epoch<=t2), \
               'Epoch %d should be in %d ~ %d'%(epoch, t1, t2)
        
        G1=self._get_epoch_value(t1)
        G2=self._get_epoch_value(t2)

        G=(epoch-t1)/(t2-t1)*(G2-G1)+G1

        return G

    def get_info(self, key, attr=None):
        if attr == None:
            out = self.fid['info/%s'%key][...]
        else:
            out = self.fid['info/%s'%key].attrs[attr][...]
        return out

    def get_epochs(self):
        out = sorted([int(ii) for ii in self.fid['epochs'].keys()])
        return out

    def has_info(self, key):
        return 'info/%s'%key in self.fid
        
    def iter_epoch_values(self):
        epochs = self.get_epochs()
        for epoch in epochs:
            yield epoch, self.get_epoch_value(epoch)

    def __getitem__(self, name):
        if isinstance(name, int):
            return self.get_epoch_value(name)
        elif isinstance(name, str):
            return self.get_info(name)
        else:
            raise ValueError('Not recognized type.')
    


