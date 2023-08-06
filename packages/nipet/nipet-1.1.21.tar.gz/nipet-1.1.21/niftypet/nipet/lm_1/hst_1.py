import os
import sys

import numpy as np
import h5py

from math import pi
import scipy.ndimage as ndi

# import the C-extension with CUDA
from . import lmproc_1

#-------------------------------------------------------------------------------
# LOGGING
#-------------------------------------------------------------------------------
import logging

#> console handler
ch = logging.StreamHandler()
formatter = logging.Formatter(
    '\n%(levelname)s> %(asctime)s - %(name)s - %(funcName)s\n> %(message)s'
    )
ch.setFormatter(formatter)
logging.getLogger(__name__).addHandler(ch)

def get_logger(name):
    return logging.getLogger(name)
#-------------------------------------------------------------------------------



def lminfo_sig(datain, Cnt):

    #> set verbose and its level
    log = get_logger(__name__)
    log.setLevel(Cnt['LOG'])

    if not os.path.isfile(datain['lm_h5']):
        raise IOError('LM HDF5 file not found!')

    f = h5py.File(datain['lm_h5'],'r')

    if (f['HeaderData']['ListHeader']['isListCompressed'][0])>0:
        raise IOError(
            'The list mode data is compressed \
            and has to be first decompressed using GE proprietary software!'
        )

    else:
        log.debug('the list mode data is not compressed: OK')

    lm = f['ListData']['listData']  

    # find first time marker by reading first k=1 time markers
    # event offset
    eoff = 0
    # direction of time search: 1-forward
    dsearch = 1
    # how many t-markers forward?
    k_markers = 1
    eoff0, t0, _ = lmproc_1.nxtmrkr(datain['lm_h5'], Cnt['BPE'], eoff, k_markers, dsearch)

    # toff = t0
    # OR
    toff = Cnt['toff']

    # for the next markers...
    k_markers = 50
    eoff, tmrk, counts = lmproc_1.nxtmrkr(datain['lm_h5'], Cnt['BPE'], eoff0, k_markers, dsearch)

    # average recorded events per ms
    epm = (eoff-eoff0)/float(k_markers)

    skip_off = np.int32( (toff-t0)*epm ) 
    eoff, tmrk, _ = lmproc_1.nxtmrkr(datain['lm_h5'], Cnt['BPE'], eoff0+skip_off, 1, dsearch)
    

    # get the event offset to the start of scan as given by toff
    while (toff-tmrk)>0:
        skip_off = np.int32( (toff-tmrk)*epm )
        eoff, tmrk, _ = lmproc_1.nxtmrkr(datain['lm_h5'], Cnt['BPE'], eoff+skip_off, 1, 1)

    eoff_strt = eoff
    tstrt = tmrk

    # now get the last time marker
    eoff_end, tend, _ = lmproc_1.nxtmrkr(datain['lm_h5'], Cnt['BPE'], (lm.shape[0]//Cnt['BPE'])-Cnt['BPE'], 1, -1)

    # number of elements to be considered in the list mode data
    ele = lm.shape[0]/Cnt['BPE'] - (eoff_strt-1)

    #> integration time tags (+1 for the end)
    nitag = ((tend-toff)+Cnt['ITIME']-1)/Cnt['ITIME']

    log.info('''\
        \r> the first time tag is: {} at event address: {} (used as offset)
        \r> the last  time tag is: {} at event address: {}
        \r> the number of report itags is: {}
        '''.format(toff, eoff_strt, tend, eoff_end, nitag))

    f.close()

    return nitag, ele, (toff, tend), (eoff_strt, eoff_end)


#================================================================================
# HISTOGRAM THE LIST-MODE DATA
#--------------------------------------------------------------------------------
def hst_sig(datain, txLUT, axLUT, Cnt, frms=np.array([0], dtype=np.uint16), use_stored=False, hst_store=False, tstart=0, tstop=0, cmass_sig=5 ):

    # histogramming with bootstrapping:
    # Cnt['BTP'] = 0: no bootstrapping [default];
    # Cnt['BTP'] = 2: parametric bootstrapping (using Poisson distribution with mean = 1)

    #> set verbose and its level
    log = get_logger(__name__)
    log.setLevel(Cnt['LOG'])

    # gather info about the LM time tags
    nitag, ele, t_strt_end, pos = lminfo_sig(datain, Cnt)
    log.info('duration by integrating time tags [s]: {}'.format(nitag))


    # ====================================================================
    # SETTING UP CHUNKS
    # divide the data into data chunks
    # the default is to read around 1GB to be dealt with all streams (default: 32)
    nchnk = (ele+Cnt['ELECHNK']-1)/Cnt['ELECHNK']
    log.info('''\
        \r> # chunks of data (initial): {}
        \r> # elechnk: {}', 
        '''.format(nchnk, Cnt['ELECHNK']))

    # divide the list mode data into chunks in terms of addresses of selected time tags
    # break time tag
    btag = np.zeros((nchnk+1), dtype=np.int32)

    # address (position) in file (in bpe-bytes unit)
    atag = np.zeros((nchnk+1), dtype=np.int64)

    # elements per thread to be dealt with
    ele4thrd = np.zeros((nchnk), dtype=np.int32)

    # elements per data chunk
    ele4chnk = np.zeros((nchnk), dtype=np.int32)

    # byte values for the whole event
    bval = np.zeros(Cnt['BPE'], dtype=int)

    atag[0] = pos[0]
    btag[0] = 0

    # LM data properties in a dictionary
    lmprop = {
        'lmfn':datain['lm_h5'],
        'bpe' :Cnt['BPE'],
        'elem':ele,
        'nchk':nchnk,
        'nitg':nitag,
        'toff':t_strt_end[0],
        'tend':t_strt_end[1],
        'atag':atag,
        'btag':btag,
        'ethr':ele4thrd,
        'echk':ele4chnk}

    # get the setup into <lmprop>
    lmproc_1.lminfo(lmprop)

    # ---------------------------------------
    # preallocate all the output arrays
    if (nitag>Cnt['MXNITAG']): tn = Cnt['MXNITAG']/(1<<Cnt['VTIME'])
    else: tn = nitag/(1<<Cnt['VTIME'])

    # sinogram projection views (sort timre frames govern by VTIME)
    pvs = np.zeros((tn, 2*Cnt['NRNG']-1, Cnt['NSBINS']), dtype=np.uint32)
    # prompt head curve (counts per second)
    phc = np.zeros((nitag), dtype=np.uint32)
    # centre of mass of radiodistribution (axially only)
    mss = np.zeros((nitag), dtype=np.float32)
    # prompt sinogram
    psino = np.zeros((Cnt['NRNG']*Cnt['NRNG'], Cnt['NSBINS'], Cnt['NSANGLES']), dtype=np.uint32)
    hstout = {  'phc':phc,
                'mss':mss,
                'pvs':pvs,
                'psn':psino}

    # do the histogramming and processing
    lmproc_1.hist(hstout, lmprop, frms, tstart, tstop, txLUT, axLUT, Cnt)

    #unpack short (interval) sinogram projection views
    pvs_sgtl = np.array( hstout['pvs']>>8, dtype=float)
    pvs_sgtl = pvs_sgtl[:,::-1,:]
    pvs_crnl = np.array( np.bitwise_and(hstout['pvs'], 255), dtype=float )
    pvs_crnl = pvs_crnl[:,::-1,:]
    cmass = 1*ndi.filters.gaussian_filter(hstout['mss'], cmass_sig, mode='mirror')

    hst = {
        'pvs_sgtl':pvs_sgtl,
        'pvs_crnl':pvs_crnl,
        'cmass':cmass,
        'phc':hstout['phc'],
        'psino':np.transpose(hstout['psn'], (0,2,1)),
        'dur':nitag
    }
    return hst

