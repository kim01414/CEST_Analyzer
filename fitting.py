import numpy as np
import scipy.interpolate as spi
from sklearn.cluster import KMeans
from scipy.ndimage import gaussian_filter
from scipy.stats import chisquare, kstest
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import sub_windows
from tkinter import messagebox

def SHOW_MTR(MAIN):
    IDX = MAIN.Current_File.get()
    IDX_END = (MAIN.Total_File.get()-1)
    if IDX > IDX_END//2: IDX = IDX_END - IDX
    Src = (MAIN.IMAGEs.Z_IMGs[:,:,IDX_END-IDX] - MAIN.IMAGEs.Z_IMGs[:,:,IDX]) * MAIN.MASK
    if type(MAIN.MTR_Windows[IDX])!=type(None): 
        MAIN.MTR_Windows[IDX].POPUP.destroy(); MAIN.MTR_Windows[IDX] = None
        plt.close(IDX+9999)
    MAIN.MTR_Windows[IDX] = sub_windows.MAP_VIEWER(MAIN.WINDOW, Src, fig_index=IDX+9999,title="MTR_aysm %.3fppm"%(MAIN.RF[IDX]))

def SHOW_MTR2(MAIN):
    IDX = MAIN.Current_File.get()
    IDX_END = (MAIN.Total_File.get()-1)
    if IDX > IDX_END//2: IDX = IDX_END - IDX
    Z_lab = MAIN.IMAGEs.Z_IMGs[:,:,IDX].copy(); Z_lab[np.where(Z_lab==0)]=1
    Z_ref = MAIN.IMAGEs.Z_IMGs[:,:,IDX_END-IDX].copy(); Z_ref[np.where(Z_ref==0)]=1
    Src = (1/Z_lab - 1/Z_ref) * MAIN.MASK
    if type(MAIN.MTR_Windows2[IDX])!=type(None): 
        MAIN.MTR_Windows2[IDX].POPUP.destroy(); MAIN.MTR_Windows2[IDX] = None
        plt.close(IDX+6666)
    MAIN.MTR_Windows2[IDX] = sub_windows.MAP_VIEWER(MAIN.WINDOW, Src, fig_index=IDX+6666,title="MTR_Rex %.3fppm"%(MAIN.RF[IDX]))

def SHOW_PTR(MAIN):
    IDX = MAIN.Current_File.get()
    IDX_END = (MAIN.Total_File.get()-1)
    if IDX > IDX_END//2: IDX = IDX_END - IDX
    Z_lab = MAIN.IMAGEs.Z_IMGs[:,:,IDX].copy(); Z_lab[np.where(Z_lab==0)]=1
    Z_ref = MAIN.IMAGEs.Z_IMGs[:,:,IDX_END-IDX].copy(); Z_ref[np.where(Z_ref==0)]=1
    Src = (Z_ref-Z_lab) / Z_ref * MAIN.MASK
    if type(MAIN.PTR_Windows[IDX])!=type(None): 
        MAIN.PTR_Windows[IDX].POPUP.destroy(); MAIN.PTR_Windows[IDX] = None
        plt.close(IDX+3333)
    MAIN.PTR_Windows[IDX] = sub_windows.MAP_VIEWER(MAIN.WINDOW, Src, fig_index=IDX+3333,title="PTR %.3fppm"%(MAIN.RF[IDX]))


def SHOW_B0_MAP(MAIN):
    if type(MAIN.Correction_Result_Windows)!=type(None): 
        MAIN.Correction_Result_Windows.POPUP.destroy(); MAIN.Correction_Result_Windows = None
        plt.close(2002)
    MAIN.Correction_Result_Windows = sub_windows.MAP_VIEWER(MAIN.WINDOW, MAIN.B0_MAP, fig_index=2000,title="B0 Map")

def Lorentzian(x, a, b, c):
    return c - c / ( (x-a)**2 + b)

def CSC_Method(Z,offset):
    shift = Z.argmin()
    return offset[shift]

def Restraint(offset, low, high):
    restraint1 = offset[np.where(offset<high)][0]
    restraint2 = offset[np.where(offset>low)][-1]
    return np.where(offset==restraint1)[0][0], np.where(offset==restraint2)[0][0]

################################################################################################################################################
def SPLINE_CORRECTION( flipped_PPM, flipped_data, PPM, interpolated_PPM ):
    ipo = spi.splrep(flipped_PPM, flipped_data,k=3)
    interpolated_Y = spi.splev(interpolated_PPM, ipo)
    Offset = interpolated_PPM[interpolated_Y.argmin()]
    return spi.splev(PPM+Offset, ipo), Offset

def TEST_SPLINE(MAIN):
    PPM, MASK, src = MAIN.RF, MAIN.MASK, MAIN.IMAGEs.Z_IMGs
    Interpolated_PPM = np.arange(PPM.min(),PPM.max()+0.002,0.002)
    Flipped_PPM = np.flip(PPM)
    B0_MAP = np.zeros_like(MASK)
    Y, X = np.where(MASK==1)
    TEST = sub_windows.IM_ALIVE(MAIN)
    for idx in range(len(Y)):
        MAIN.IMAGEs.Z_IMGs[Y[idx],X[idx]], B0_MAP[Y[idx],X[idx]] = SPLINE_CORRECTION(Flipped_PPM, np.flip(src[Y[idx],X[idx],:]) ,PPM, Interpolated_PPM )
        TEST.STEP(len(Y))
    TEST.DESTROY(); del(TEST)
    MAIN.DISPLAY_GRAPH(); MAIN.Select_Image()
    MAIN.B0_MAP = B0_MAP.copy()
    messagebox.showinfo("Done!","Spline Correction is completed!")
    if type(MAIN.Correction_Result_Windows)!=type(None):
        MAIN.Correction_Result_Windows.POPUP.destroy(); MAIN.Correction_Result_Windows = None
    MAIN.Correction_Result_Windows = sub_windows.MAP_VIEWER(MAIN.WINDOW, B0_MAP,title='Spline Correction B0 MAP')
    MAIN.MENU_CEST_B0.entryconfig('B0 Map',state='normal')
    MAIN.DISPLAY_GRAPH()

################################################################################################################################################
def TEST_LORENTZ(MAIN):
    PPM, MASK, src = MAIN.RF, MAIN.MASK, MAIN.IMAGEs.Z_IMGs
    Interpolated_PPM = np.arange(PPM.min(),PPM.max()+0.002,0.002)
    B0_MAP = np.zeros_like(MASK)
    Y, X = np.where(MASK==1)
    TEST = sub_windows.IM_ALIVE(MAIN)
    for idx in range(len(Y)):
        popt, pcov = curve_fit(Lorentzian, PPM, src[Y[idx],X[idx],:])
        B0_MAP[Y[idx],X[idx]] = popt[0]
        _Z = spi.splrep(np.flip(PPM),np.flip(src[Y[idx],X[idx],:]),k=3)
        src[Y[idx],X[idx],:] = spi.splev(PPM+popt[0], _Z)
        TEST.STEP(len(Y))
    TEST.DESTROY(); del(TEST)
    MAIN.DISPLAY_GRAPH(); MAIN.Select_Image()
    MAIN.B0_MAP = B0_MAP.copy()
    messagebox.showinfo("Done!","Lorentzian Correction is complted!")
    if type(MAIN.Correction_Result_Windows)!=type(None):
        MAIN.Correction_Result_Windows.POPUP.destroy(); MAIN.Correction_Result_Windows = None
    MAIN.Correction_Result_Windows = sub_windows.MAP_VIEWER(MAIN.WINDOW, B0_MAP,title='Lorentzian Correction B0 MAP')
    MAIN.MENU_CEST_B0.entryconfig('B0 Map',state='normal')
    MAIN.DISPLAY_GRAPH()
################################################################################################################################################
def TEST_WASSR(MAIN):
    pass

################################################################################################################################################
def TEST_IDE_LF(MAIN):
    TEST = sub_windows.IM_ALIVE(MAIN, text="Initializing...")
    PPM, MASK, src, raw = MAIN.RF, MAIN.MASK, MAIN.IMAGEs.Z_IMGs, MAIN.IMAGEs.IMGs
    IMG_SIZE, IMG_TOTAL = MASK.shape, src.shape[-1]
    Z_Data = np.zeros((IMG_SIZE[0]*IMG_SIZE[1],IMG_TOTAL))
    Offset_inter = np.arange(PPM.max(),PPM.min()-0.002,-0.002)
    #Step 1
    INDEX = 0 ; Z_data0 = np.zeros((IMG_SIZE[0],IMG_SIZE[1],IMG_TOTAL))
    for idx in range(IMG_TOTAL): Z_data0[:,:,idx] = src[:,:,idx] * MASK
    #########
    for y in range(IMG_SIZE[0]):
        for x in range(IMG_SIZE[1]):
            Z_Data[INDEX,:] = Z_data0[y,x,:]; INDEX+=1
    B0_MAP = np.zeros(IMG_SIZE); B0_history, B0_history2, cluster_history = [], [], []
    for Iteration in range(1,8):
        TEST.CHANGE_TEXT("Clustering... K={0}".format(3**Iteration))
        TEST.STEP(7)
        #Step 2
        N_clusters = 3**(Iteration)
        kmeans = KMeans(n_clusters=N_clusters, random_state=0).fit(Z_Data)
        labels = kmeans.labels_.copy()
        cluster_history.append(labels.reshape(IMG_SIZE))
        #Step 3 & Step 4
        r_high, r_low = Restraint(Offset_inter, -1/Iteration, 1/Iteration)
        B0_current = np.zeros(IMG_SIZE)
        for clstr in np.unique(labels):
            if clstr!=0:
                Z = Z_Data[np.where(labels==clstr)].mean(axis=0)
                popt, pcov = curve_fit(Lorentzian, PPM, Z, bounds=([Offset_inter[r_low],-np.inf,0],[Offset_inter[r_high],np.inf,1]) )
                r_square, _ = chisquare(Z, Lorentzian(PPM, *popt))
                if r_square<0.7:  popt = [ CSC_Method( Lorentzian(PPM, *popt), PPM ), _ , _ ]
                B0_current[np.where(cluster_history[-1]==clstr)] = popt[0]
                B0_MAP[np.where(cluster_history[-1]==clstr)] += popt[0]
        B0_history.append(B0_MAP); B0_map = B0_current.flatten()

        #Step 5
        for idx in range(Z_Data.shape[0]):
            if labels[idx]!=0:
                _Z = spi.splrep(np.flip(PPM),np.flip(Z_Data[idx]),k=3)
                shift = B0_map[idx]
                Z_Data[idx] = spi.splev(PPM+shift, _Z)
        
        #Step 6
        current_ms, total_ms = (B0_current**2).mean(), 0
        for B0 in B0_history: total_ms += (B0**2).mean()
        B0_history.append(B0_current); B0_history2.append(B0_MAP)
        Stopper = (current_ms / total_ms)*100
        if Stopper < 10: break
    
    #Step 7
    MAIN.B0_MAP = gaussian_filter(B0_MAP, sigma=1)
    MAIN.IMAGEs.Z_IMGs = Z_Data.reshape((IMG_SIZE[0],IMG_SIZE[1],IMG_TOTAL))
    TEST.DESTROY(); del(TEST)
    messagebox.showinfo("Done!","IDE-LF Correction is completed!")
    if type(MAIN.Correction_Result_Windows)!=type(None):
        MAIN.Correction_Result_Windows.POPUP.destroy(); MAIN.Correction_Result_Windows = None
    MAIN.Correction_Result_Windows = sub_windows.MAP_VIEWER(MAIN.WINDOW, MAIN.B0_MAP, title='IDE-LF B0 MAP')
    MAIN.MENU_CEST_B0.entryconfig('B0 Map',state='normal')
    MAIN.DISPLAY_GRAPH()