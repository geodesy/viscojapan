#!/usr/bin/env python3
''' Define a basic class wrapping command strainA.
The class is a subclass of Popen so it acquires all the features
that can be used to control the excution of the command.
'''
from os.path import exists,join,basename, dirname
from os import makedirs
from tsana.date_utils import *
from subprocess import Popen, check_output
import sys
from tempfile import TemporaryFile, mkdtemp
from time import time
from shutil import copyfile, rmtree

__all__=['StrainA']

class StrainA(Popen):
    ''' Class wraper of VISCO1D command strainA
'''
    def __init__(self):
        # The following files should be in cwd directory:
        self.earth_dir=None
        # required working files and derectories by this command:
        self.earth_files=['earth.model',
                         'decay.out','decay4.out',
                         'vsph.out','vtor.out']
        self.file_out=None # output file

        # user inputs:
        # these files are in current work directory.
        self.file_flt=None # faults file
        self.file_sites=None # sites file
        
        # set day of computation:
        self.t_eq=asmjd('11MAR11')
        self.days_after=None

        self.stdout=sys.stdout
        self.stderr=sys.stderr        

        self.start_time=None # used to time the program.
        self.end_time=None

        # Change cwd for the command. See Popen page.
        # _cwd is a temporary directory.
        self._cwd=None
        self._tmp_dir='/home/zy/tmp/'

    def check_user_input_files(self):
        ''' Check if user input files exist:
- file_flt - fault file
- file_sites - station file
'''
        for f in [self.file_flt,self.file_sites]:
            if not exists(f):
                raise ValueError("User input file %s doesn't not exist!"%f)

    def check_earth_files(self):
        ''' Check if earth model files generated by former VISCO1D commands exist.
These files include:
- earth.model - earth model file
- decay.out
- decay4.out
- vsph.out
- vtor.out
'''
        for f in self.earth_files:
            if not exists(join(self.earth_dir,f)):
                raise ValueError("Earth file %s doesn't not exist!"%f)

    def deploy(self):
        ''' Copy earth files to temporary working directory.
'''
        if not exists(self._tmp_dir):
            makedirs(self._tmp_dir)
        self.check_earth_files()
        self._cwd=mkdtemp(dir=self._tmp_dir)
        for f in self.earth_files:
            tp=join(self.earth_dir,f)
            copyfile(tp,join(self._cwd,f))

    def form_stdin(self):
        ''' Form the stdin for command strainA.
'''
        self.check_user_input_files()
        t1=asdyr(self.t_eq)
        t2=asdyr(self.t_eq+self.days_after)
        # temporary file:
        stdin=TemporaryFile('r+')
        stdin.write('Comment Line.\n')
        stdin.write(check_output("grep -v '#' %s | head -n 1"\
                                 %(self.file_flt),shell=True).decode())
        stdin.write("%f %f %f 1.\n"%(t1,t1,t2))
        stdin.write(check_output("grep -v '#' %s | tail -n +2"\
                                 %(self.file_flt),shell=True).decode())
        stdin.write(check_output("grep -v '#' %s | wc -l"\
                                 %(self.file_sites),shell=True).decode())
        stdin.write(check_output("grep -v '#' %s"\
                                 %(self.file_sites),shell=True).decode())
        stdin.write("0\n")
        stdin.write("0\n")
        stdin.write("out")
        stdin.seek(0)
        return stdin

    def start(self,nice=True):
        ''' Start to run the program.
'''
        self.deploy()
        fin=self.form_stdin()
        self.start_time=time()
        if nice:
            super().__init__(['nice','strainA'],
                             stdout=self.stdout,stderr=self.stderr,stdin=fin,
                             cwd=self._cwd)
        else:
            super().__init__(['strainA'],
                             stdout=self.stdout,stderr=self.stderr,stdin=fin,
                             cwd=self._cwd)
            
        fin.close()

        # wait until strainA finishes.
        self.wait()

        dname=dirname(self.file_out)
        if dname!='':
            if not exists(dname):
                makedirs(dname)

        # fetch output from the temp dir.
        copyfile(join(self._cwd,'out'),self.file_out)        

        # delete tmp fir
        rmtree(self._cwd)

    def total_exe_time(self):
        ''' Total execution of the process.(min)
'''
        return (self.start_time-self.end_time)/60.

    def wait(self):
        super().wait()
        self.end_time=time()

    def if_output_exist(self):
        '''If output file exists.
'''
        if exists(self.file_out):
            return True
        return False

    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        if exists(self._cwd):
            rmtree(self._cwd)
        return True


if __name__=='__main__':
    pass
