import os
import numpy as np

PATH = os.path.dirname( os.path.abspath(__file__) )
OPTION = 0 #0: Interval, 1: Manual
FILE_NAME = 'CEST3_freq_user6.txt'
frequency = 128

if OPTION==0:   
    Plus_ppm  = 4
    Interval  = 0.1
    Minus_ppm = -4
    Preset = np.arange(4,-4-Interval,-1*Interval)

else: Preset = [4, 
                3, 
                2, 
                1.75,
                1.5, 
                1.25, 
                1,
                0.75, 
                0.5, 
                0.25, 
                0, 
                -0.25, 
                -0.5,
                -0.75, 
                -1, 
                -1.25,
                -1.5, 
                -1.75
                -2, 
                -3, 
                -4]

PPM = [i*frequency for i in Preset]

with open(PATH+'/'+FILE_NAME, 'w') as F:
    for idx in range(len(PPM)): 
        F.write(str(int(PPM[idx])))
        if idx!=len(PPM)-1: F.write('\n')