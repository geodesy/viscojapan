import h5py

from pylab import plt

nreses =[]
rakes = []

for ano in range(30):
    with h5py.File('outs/ano_%02d.h5'%ano,'r') as fid:
        nres = fid['misfit/norm_weighted'][...]
        nreses.append(nres)

        rake = fid['nlin_pars/rake'][...]
        rakes.append(rake)
    
plt.semilogx(nreses, rakes,'o')
plt.show()
