import tempfile
from os.path import exists, join, dirname
from os import makedirs

import pGMT

from ..share import file_kur_top, file_etopo1

__all__ = ['GMTSlipPlotter']

def make_basename_dir(fn):
    bn = dirname(fn)
    if not exists(bn):
        makedirs(bn)

class GMTSlipPlotter(object):
    def __init__(self,
                 gplt,
                 slip_file_txt,
                 topo_file = file_etopo1,
                 workdir = '~tmp',
                 I = '5k',
                 low_cut_value = 1,
                 A = '-70/20'
                 ):
        self.gplt = gplt
        self.slip_file_txt = slip_file_txt
        
        self.topo_file = topo_file

        self._workdir = workdir
        
        
        # I option, grid spacing
        self.I = I
        self.low_cut_value = low_cut_value
        # light of intensity
        self.A = A

    def plot_slip(self):
        self.gplt.grdimage(
            self.slip_file_grd_cutted, J='', R='',
            C = self.cpt_file,
            O='',K='', G='', Q='',
            I = self.intensity_file,
            )

    def init(self,
             original_cpt_file = 'no_green',
             if_cpt_reverse = False
             ):
        self._init_working_dir()
        self._prepare_slip_file()
        self._prepare_cpt_file(original_cpt_file, if_cpt_reverse)
        self._prepare_intensity_file()

    def _init_working_dir(self):
        if not exists:
            makedirs(self._workdir)

    def _prepare_slip_file(self):
        self.slip_file_grd = join(self._workdir, 'slip.grd')
        self.slip_file_grd_cutted = join(self._workdir, 'slip_cutted.grd')
        
        self._interpolate_slip_file(self.slip_file_grd)
        self._low_cut_slip_grd(self.slip_file_grd,
                               join(self._workdir, 'slip1.grd'))
        self._trench_cut_slip_grd(join(self._workdir, 'slip1.grd'),
                               join(self._workdir, 'slip2.grd'))
        self._land_cut_slip_grd(join(self._workdir, 'slip2.grd'),
                               self.slip_file_grd_cutted)

        

    def _interpolate_slip_file(self, out_grd):
        make_basename_dir(out_grd)
        gmt = pGMT.GMT()
        gmt.nearneighbor(
            self.slip_file_txt,
            G = '"%s"'%out_grd, I=self.I, N='8', R='', S='40k'
            )

        gmt.grdfilter(
            out_grd,
            G = out_grd,
            D='4',
            F='c25')
        
    def _low_cut_slip_grd(self, grd_in, grd_out):
        gmt = pGMT.GMT()
        gmt.grdclip(
            grd_in,
            G = grd_out,
            Sb='%f/NaN'%self.low_cut_value)
        

    def _trench_cut_slip_grd(self, grd_in, grd_out):
        gmt = pGMT.GMT()
        file_mask = join(self._workdir, 'trench_cut_mask.grd')
        gmt.grdmask(
            file_kur_top,
            G = file_mask,
            A='',
            N='1/1/NaN',
            I = self.I,
            R=''
            )

        gmt.grdmath(grd_in, file_mask, 'OR', '= ', grd_out)
        
    def _land_cut_slip_grd(self, grd_in, grd_out):
        gmt = pGMT.GMT()
        file_mask = join(self._workdir, 'land_mask.grd')
        gmt.grdlandmask(R='', Dh='', I = self.I,
                        N='1/NaN',G=file_mask)
        gmt.grdmath(grd_in, file_mask, 'OR', '= ', grd_out)

    def _prepare_cpt_file(self,
                          original_cpt_file = 'no_green',
                          if_cpt_reverse = False
                          ):
        self.cpt_file = join(self._workdir, 'slip.cpt')
        gmt = pGMT.GMT()

        if if_cpt_reverse:
            I = ''
        else:
            I = None
        gmt.grd2cpt(
            self.slip_file_grd,
            #C='temperature.cpt',
            C=original_cpt_file,
            Z='',
            I = I,
            )
        gmt.save_stdout(self.cpt_file)

    def _prepare_intensity_file(self):
        self.intensity_file = join(self._workdir, 'intensity.grd')
        self._cutted_topo = join(self._workdir, 'cutted_topo.grd')
        _intensity_file_before_resample = join(self._workdir,
                                               '~intensity_before_resample.grd')
        gmt = pGMT.GMT()
        gmt.grdcut(
            self.topo_file,
            G = self._cutted_topo,
            R = '')
        gmt.grdgradient(
            self._cutted_topo,
            G = _intensity_file_before_resample,
            A = self.A, R = '')

        gmt.grdsample(
            _intensity_file_before_resample,
            G=self.intensity_file, I=self.I)

    def plot_slip_contour(self,
                          contours = [5, 10 , 20, 40, 60],
                          W = 'thickest',):
        _txt = ''
        for ii in contours:
            _txt += '%f A\n'%ii
            
        with tempfile.NamedTemporaryFile('w+t') as fid:
            fid.write(_txt)
            fid.seek(0,0)

            gmt = pGMT.GMT()            
            
            self.gplt.grdcontour(
                self.slip_file_grd_cutted,
                C=fid.name,
                A='1+f9+um',
                G='n1/.5c', J='', R='', O='',K='',
                W = W,
                )

    def plot_scale(self,
                   xpos = '0',
                   ypos = '0',
                   tick_interval = '10',
                   ):
        self.gplt.psscale(
            R='', J='', O = '', K='',
            C = self.cpt_file,
            D='{xpos}/{ypos}/3/.2'.format(xpos=xpos, ypos=ypos),
            B='{tick_interval}::/:m:'.format(tick_interval=tick_interval),
            )
            

        

    

        
        
        
    
    
        

