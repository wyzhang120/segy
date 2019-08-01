import os
from SegyParser import readsegy
import pandas as pd
import numpy as np
dataDir = '/project/stewart/wzhang/Pioneer/Seismic/vp_extr'
fsegy = 'Texas_Ten_zz31_28_arb_Vp.sgy'

segy = readsegy(dataDir, fsegy)
trcDict = {'tracl': (1, 4, 1), 'tracr': (5, 4, 1), 'tracf': (13, 4, 1),
           'shotnum': (17, 4, 1), 'cdp': (21, 4, 1), 'cdpt': (25, 4, 1),
           'xsrc': (73, 4, 1), 'ysrc': (77, 4, 1), 'xrec': (81, 4, 1), 'yrec': (85, 4, 1),
           'z0': (105, 2, 1)}
# if __name__ == '__main__':
#     segy.trchdr(trcDict, nproc=3)



def findDulicates(df, key):
    arr = df.loc[:, key].values
    idxSort = np.argsort(arr)
    arrSorted = arr[idxSort]
    val, idxStart, count = np.unique(arrSorted, return_counts=True, return_index=True)
    res = np.split(idxSort, idxStart[1:])
    val = val[count > 1]
    res = filter(lambda x : x.size > 1, res)
    return val, list(res)

df = pd.read_csv(os.path.join(dataDir, 'trchdr.csv'),  index_col=0)
xsrcDup, xsrcDuId = findDulicates(df, 'xsrc')
print('test')