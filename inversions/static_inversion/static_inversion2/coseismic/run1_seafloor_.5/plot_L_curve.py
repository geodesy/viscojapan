import glob

import h5py

from viscojapan.plots import plot_L, plt


def plot_files(files, color):
    nreses =[]
    nroughs = []
    for file in files:
        with h5py.File(file,'r') as fid:
            nres = fid['misfit/norm_weighted'][...]
            nreses.append(nres)
            nrough = fid['regularization/roughening/norm'][...]
            nroughs.append(nrough)
        
    plot_L(nreses, nroughs, color=color)

files = glob.glob('outs/rough_??.h5')
plot_files(files, 'blue')

plt.show()
