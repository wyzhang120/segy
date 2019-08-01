import os
import numpy as np
import matplotlib.pyplot as plt

datadir = 'C:\DFiles\Geophysics\Project\Pioneer\Rotated_052019'
iphase = 1
fname = 'Phase{:d}P_CRG_DELIV.sgy'.format(iphase)
nt = 601
dt = 1

def bytes2Arr(f, offset, nt, dtype):
    nbyte = 4 * nt
    f.seek(offset)
    tmp = f.read(nbyte)
    arr = np.frombuffer(tmp, dtype=dtype, count=nt)
    return arr



t = np.arange(nt) * dt
dtype = np.dtype(np.float32)
dtype = dtype.newbyteorder('>')
ntrace = 55832
with open(os.path.join(datadir, fname), 'rb') as f:
    data = np.zeros([ntrace, nt])
    tsize = 240 + nt * 4
    for itrace in range(ntrace):
        data[itrace, :] = bytes2Arr(f, 3840+tsize*itrace, nt, dtype)

fig, ax = plt.subplots()
ax.imshow(data[:200, :300].T, cmap='gray')
plt.show()
