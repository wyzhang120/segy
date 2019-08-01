import os
import struct
import numpy as np
import pandas as pd
from multiprocessing import Pool
from functools import partial


def byte2num(f, hdrtype, bloc, byteOrder='big'):
    """
    Convert bytes to numbers
    :param f: file object,
    :param hdrtype: string, type of header to read: bin, trc
    :param bloc: tuple of 3 ints  (the third one is optional),
                (byte location, nbytes, 1 for signed/ 0 for unsigned);
                the origin of byte location is 1 (rather than 0) which is consistent with segy definition
    :param byteOrder: string, byte order: big, litte, native
    :return:
    """
    nbyte = bloc[1]
    if nbyte == 2:
        fmt = 'H'
    elif nbyte == 4:
        fmt = 'I'
    else:
        raise ValueError('nbytes (bloc[1]) must be 2 or 4')

    if len(bloc) == 3 and bloc[2] == 1:
            fmt = fmt.lower()

    if byteOrder == 'big':
        ord = '>'
    elif byteOrder == 'little':
        ord = '<'
    elif byteOrder == 'native':
        ord = '@'
    else:
        raise ValueError('byteOrder not recognized')

    if hdrtype == 'bin':
        offset = 3200
    elif hdrtype == 'trc':
        offset = 3600
    else:
        raise ValueError('hdrtype not recognized')
    f.seek(offset + bloc[0] - 1)
    tmp = f.read(nbyte)

    return struct.unpack(ord + fmt, tmp)[0]

class readsegy:
    def __init__(self, dataDir, fsegy,
                 txthdr = 'txthdr.txt', binhdr = 'binhdr.txt', byteOrder = 'big', outDir=None):
        """

        :param dataDir: string
        :param fsegy: string,
        :param txthdr: string, file name of textural header to save
        :param binhdr: string, file name of binary header to save
        :param byteOrder: string, byte order: big, litte, native
        :param outDir: string, directory to save headers
        """
        if outDir is None:
            self.outDir = dataDir
        else:
            self.outDir = outDir
        self.dataDir = dataDir
        self.fsegy = fsegy
        self.txthdr = txthdr
        self.binhdr = binhdr
        self.byteOrder = byteOrder
        self.__txthdr__()
        self.__binhdr__()

    def __txthdr__(self):
        with open(os.path.join(self.dataDir, self.fsegy), 'rb') as f:
            tmp = f.read(3200)
            txt = tmp.decode('cp1140')
        with open(os.path.join(self.outDir, self.txthdr), 'w') as f:
            for i in range(40):
                f.write(txt[i * 80 : (i + 1) * 80] + '\n')

    def __binhdr__(self):
        bloc = {'ntrace' : (13, 2), 'dt' : (17, 2), 'nt': (21, 2)}
        binhdr = dict()
        with open(os.path.join(self.dataDir, self.fsegy), 'rb') as f:
            for key, val in bloc.items():
                binhdr[key] = byte2num(f, 'bin', val, self.byteOrder)
        self.__trcNt__()
        trcNt = self.__getattribute__('trcNt')
        ntTest = np.unique(trcNt)
        ntrace = len(trcNt)
        with open(os.path.join(self.outDir, self.binhdr), 'w') as f:
            f.write('Values from bindary header\n')
            for key, val in binhdr.items():
                f.write('{:30s} {:d}\n'.format(key, val))
                self.__setattr__(key, val)
            f.write('\nChecking trace header for nt, ns\n')
            f.write('{:30s} {:d}\n'.format('ntrace', ntrace))
            if len(ntTest) == 1:
                f.write('{:30s} {:s}\n'.format('Same nt every trace', 'True'))
                f.write('{:30s} {:d}\n'.format('nt', ntTest[0]))
            else:
                f.write('{:30s} {:s}\n'.format('Same nt every trace', 'False'))
                df = pd.DataFrame(data=trcNt, columns=['nt'])
                fcsv = os.path.join(self.outDir, 'nt.csv')
                df.to_csv(fcsv)
                f.write('  nt of every trace written in file: \n'
                        '       {:s}\n'.format(fcsv))
        self.__setattr__('ntrace', ntrace)

    def __trcNt__(self):
        fname = os.path.join(self.dataDir, self.fsegy)
        fsize = os.path.getsize(fname)
        ns = list()
        ibyte = 0
        with open(fname, 'rb') as f:
            while 3600 + ibyte < fsize:
                ins = byte2num(f, 'trc', (115 + ibyte, 2))
                ibyte += ins * 4 + 240
                ns.append(ins)
        self.__setattr__('trcNt', np.array(ns))

    def __trcAttr__(self, i, f, tmp, bloc, offset):
        bloc[0] += offset[i]
        tmp[i] = byte2num(f, 'trc', bloc , self.byteOrder)

    def __trcAttr2__(self, key, trcDict, offset, trchdr):
        with open(os.path.join(self.dataDir, self.fsegy), 'rb') as f:
            tmp = np.zeros(len(offset))
            bloc = np.array(trcDict[key])
            for i in range(len(offset)):
                bloc[0] += offset[i]
                tmp[i] = byte2num(f, 'trc', bloc.astype(np.int32) , self.byteOrder)
            trchdr[key] = tmp
        return {key: tmp}


    def trchdr(self, trcDict, nproc=4):
        trcNt = self.__getattribute__('trcNt')
        offset = np.roll(trcNt * 4 + 240, 1)
        offset[0] = 0
        trchdr = dict()
        # with open(os.path.join(self.dataDir, self.fsegy), 'rb') as f:
            # for key, bloc in trcDict.items():
            #     trchdr[key] = np.zeros(len(offset))
            #     for i in range(len(offset)):
            #         self.__trcAttr__(i, f, trchdr[key], np.array(bloc), offset)
        with Pool(nproc) as pool:
            tmplist = pool.map(partial(self.__trcAttr2__, trcDict=trcDict, offset=offset, trchdr=trchdr),
                               trcDict.keys())
        for idict in tmplist:
            for ikey, ival in idict.items():
                trchdr[ikey] = ival
        df = pd.DataFrame(data=trchdr)
        df.to_csv(os.path.join(self.outDir, 'trchdr.csv'))
