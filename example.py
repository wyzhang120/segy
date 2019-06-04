import os
from SegyParser import readsegy

if 'HOSTNAME' in os.environ.keys():
    if os.environ['HOSTNAME'] == 'sabine.cacds.uh.edu' or 'compute-' in os.environ['HOSTNAME']:
        dataDir = '/project/stewart/wzhang/Pioneer/Rotated_052019'
    else:
        raise ValueError('Host not recognized')
elif os.environ['COMPUTERNAME'] == 'LENOVO-PC':
    dataDir = 'C:\\DFiles\\Geophysics\\Project\\Pioneer\\Rotated_052019'
elif os.environ['COMPUTERNAME'] == 'WENYUAN-PC':
    dataDir = 'E:\\Geophysics\\Project\\Pioneer\\Logs'
else:
    dataDir = os.getcwd()

fsegy = 'Phase1P_CRG_DELIV.sgy'
trcDict = {'recid': (9, 4, 1), 'srcid': (13, 4, 1), 'zsrc': (41, 4, 1),
           'zrec': (45, 4, 1), 'zfbscaler': (61, 2, 1), 'xyscaler': (71, 2, 1),
           'xrec': (73, 4, 1), 'yrec': (77, 4, 1), 'xsrc': (81, 4, 1), 'ysrc': (85, 4, 1),
           'fb' : (221, 4, 1)}
segy = readsegy(dataDir, fsegy)
if __name__ == '__main__':
    segy.trchdr(trcDict, nproc=4)