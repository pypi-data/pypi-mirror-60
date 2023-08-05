
import numpy as np
import os
import sys


#----------------------------------------------------------------------
def load_sample_8ch_raw(file_id=0):
    """"""
    return np.loadtxt(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                   f'sample_8ch_raw{file_id}.txt')).T


#----------------------------------------------------------------------
def load_sample_8ch_bin(file_id=0):
    """"""
    return open(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             f'sample_8ch_bin{file_id}.txt'), 'rb')


