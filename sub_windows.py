import matplotlib.pyplot as plt
import tkinter as TK
import numpy as np
import os, cv2, fitting, glob
from scipy.optimize import curve_fit
from tkinter import filedialog, ttk, messagebox, Menu
from PIL import Image, ImageTk, ImageDraw, ImageFont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

CMAP = ["jet","gnuplot","gnuplot2","CMRmap","ocean","gist_earth","gist_stern","terrain",
        "cubehelix","brg","gist_rainbow","rainbow","nipy_spectral","gist_ncar"]
CMAP_INDEX = 0

class IM_ALIVE:
    def __init__(self, master, text='Working in progress...'):
        LOCATION = master.GET_MASTER_LOCATION()
        self.POPUP = TK.Toplevel(master.WINDOW)
        self.POPUP.geometry('200x100+{0}+{1}'.format( LOCATION[0] - 100 , LOCATION[1]-50))
        self.POPUP.resizable(0,0); self.POPUP.config(bg='#1E1E1E')
        self.FRAME = TK.LabelFrame(self.POPUP, bg='#1E1E1E',foreground='#FFFFFF')
        self.FRAME.place(x=10,y=10,width=180,height=80)
        self.TEXT_VAR = TK.StringVar(); self.TEXT_VAR.set(text)
        self.TEXT = TK.Label(self.FRAME, textvariable=self.TEXT_VAR,background='#1E1E1E',foreground='#FFFFFF')
        self.TEXT.place(x=10,y=15,width=160,height=20)
        self.PROGRESSBAR = ttk.Progressbar(self.FRAME, length=160)
        self.PROGRESSBAR.place(x=10,y=40,width=160,height=20)
        self.POPUP.overrideredirect(1)
        self.POPUP.grab_set()
    
    def STEP(self,progress):
        self.PROGRESSBAR.update_idletasks()
        self.PROGRESSBAR.step(100/progress)
        self.POPUP.update()

    def STEP_FINISH(self):
        self.PROGRESSBAR.stop()
        self.PROGRESSBAR.step(100)
        self.PROGRESSBAR.update_idletasks()
        self.POPUP.update()

    def CHANGE_TEXT(self, TEXT):
        self.TEXT_VAR.set(TEXT); self.POPUP.update()

    def DESTROY(self): self.POPUP.destroy()

class ASK_PRESETTINGS_WINDOW:
    def __init__(self, master, TOTAL, mode='DICOM'):
        LOCATION = master.GET_MASTER_LOCATION()
        self.Master, self.TOTAL, self.MODE = master, TOTAL, mode
        self.Loading = TK.StringVar(); self.Loading.set('RF Frequency: __ / Images: __ ')
        self.ASK_PRESETTINGS = TK.Toplevel(self.Master.WINDOW)
        self.ASK_PRESETTINGS.geometry('290x430+{0}+{1}'.format( LOCATION[0] - 145 , LOCATION[1] - 215))
        self.ASK_PRESETTINGS.config(bg='#1E1E1E')
        self.ASK_PRESETTINGS.title("CEST Loader")
        self.ASK_PRESETTINGS.resizable(0,0)
        self.ASK_PRESETTINGS.bind('<Return>', self.GO)
        self.FRAME0 = TK.LabelFrame(self.ASK_PRESETTINGS, text="Total Images",background='#1E1E1E',foreground='#FFFFFF')
        self.FRAME0.place(x=10, y=10, width=270, height=40)
        self.LABEL_TOTAL_IMAGE = TK.Label(self.FRAME0, text='{0}'.format(self.TOTAL),anchor="center",background='#1E1E1E',foreground='#FFFFFF')
        self.LABEL_TOTAL_IMAGE.place(x=10,y=5,width=250, height=10)

        self.FRAME1 = TK.LabelFrame(self.ASK_PRESETTINGS, text="CEST Parameters",background='#1E1E1E',foreground='#FFFFFF')
        self.FRAME1.place(x=10, y=0+60, width=270, height=260)
        self.LABEL_VOL_SIZE = TK.Label(self.FRAME1, text='Volume Size',background='#1E1E1E',foreground='#FFFFFF')
        self.LABEL_VOL_SIZE.place(x=10,y=10,width=90, height=20)
        self.INPUT_VOL_SIZE = TK.Entry(self.FRAME1,validate="focusout",validatecommand=self.Refresh,state='normal' if self.MODE=='DICOM' else 'disabled')
        self.INPUT_VOL_SIZE.place(x=110,y=10,width=150, height=20)
        self.INPUT_VOL_SIZE.insert(0,40)
        self.LABEL_DUMMY_VOL_IDX = TK.Label(self.FRAME1, text='Dummy Volume',background='#1E1E1E',foreground='#FFFFFF')
        self.LABEL_DUMMY_VOL_IDX.place(x=10,y=50,width=90, height=20)
        self.INPUT_DUMMY_VOL_IDX = TK.Entry(self.FRAME1,validatecommand=self.Refresh,state='normal' if self.MODE=='DICOM' else 'disabled')
        self.INPUT_DUMMY_VOL_IDX.place(x=110,y=50,width=150, height=20)
        self.INPUT_DUMMY_VOL_IDX.insert(0,1)
        self.LABEL_S0_VOL_IDX = TK.Label(self.FRAME1, text='S0 Volume',background='#1E1E1E',foreground='#FFFFFF')
        self.LABEL_S0_VOL_IDX.place(x=10,y=90,width=90, height=20)
        self.INPUT_S0_VOL_IDX = TK.Entry(self.FRAME1,validatecommand=self.Refresh)
        self.INPUT_S0_VOL_IDX.place(x=110,y=90,width=150, height=20)
        self.INPUT_S0_VOL_IDX.insert(0,2)
        self.LABEL_SLICE_NUMBER = TK.Label(self.FRAME1, text='Slice Number',background='#1E1E1E',foreground='#FFFFFF')
        self.LABEL_SLICE_NUMBER.place(x=10,y=130,width=90, height=20)
        self.INPUT_SLICE_NUMBER = TK.Entry(self.FRAME1,validatecommand=self.Refresh,state='normal' if self.MODE=='DICOM' else 'disabled')
        self.INPUT_SLICE_NUMBER.place(x=110,y=130,width=150, height=20)
        self.INPUT_SLICE_NUMBER.insert(0,20)
        self.Presets, self.PPM = self.LOAD_PRESETS()
        self.LABEL_PRESETS = TK.Label(self.FRAME1,  text='RF Frequency',background='#1E1E1E',foreground='#FFFFFF')
        self.LABEL_PRESETS.place(x=10,y=170,width=90, height=20)
        self.PRESET_COMBOBOX = TK.ttk.Combobox(self.FRAME1, height=30, values=self.Presets, state='readonly')
        self.PRESET_COMBOBOX.place(x=110,y=170,width=150); self.Refresh()
        self.PRESET_COMBOBOX.current(0); self.PRESET_COMBOBOX.bind("<<ComboboxSelected>>", self.Refresh)
        self.LABEL_FREQUENCY = TK.Label(self.FRAME1, text='Frequency',background='#1E1E1E',foreground='#FFFFFF')
        self.LABEL_FREQUENCY.place(x=10,y=210,width=90, height=20)
        self.INPUT_FREQUENCY = TK.Entry(self.FRAME1)
        self.INPUT_FREQUENCY.place(x=110,y=210,width=150, height=20)
        self.INPUT_FREQUENCY.insert(0,128)
        
        self.FRAME2 = TK.LabelFrame(self.ASK_PRESETTINGS, text="Expected Result",background='#1E1E1E',foreground='#FFFFFF')
        self.FRAME2.place(x=10, y=230+60+40, width=270, height=90)
        self.LABEL_RESULT1 = TK.Label(self.FRAME2, textvariable=self.Loading,background='#1E1E1E',foreground='#FFFFFF')
        self.LABEL_RESULT1.place(x=10,y=5,width=230, height=20)
        
        self.Generate_Bttn = TK.Button(self.FRAME2,text='Ok',command=self.GO,bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.Generate_Bttn.bind('<Any-Enter>',lambda x: self.Generate_Bttn.config(bg='#094771')); self.Generate_Bttn.bind('<Any-Leave>',lambda x: self.Generate_Bttn.config(bg='#3C3C3C'))
        self.Generate_Bttn.place(x=10,y=35,width=250,height=30)
        self.ASK_PRESETTINGS.grab_set()

    def LOAD_PRESETS(self):
        PATH = os.path.dirname(os.path.abspath(__file__))
        name, freq = [], []
        for FILE in glob.glob(PATH+'/CEST_Frequency/*.txt'):
            with open(FILE,"r") as f:
                name.append( (FILE.split('\\')[-1]).split('.')[0] )
                data, fq = f.readlines(),[]
                for d in data:
                    try: fq.append(int(d.split('\n')[0]))
                    except: pass
                freq.append(np.array(fq))
        return name, freq

    def Refresh(self,event=None):
        try: 
            MINUS = (-1 if int(self.INPUT_DUMMY_VOL_IDX.get())!=0 else 0 ) + (-1 if int(self.INPUT_S0_VOL_IDX.get())!=0 else 0 )
            self.Loading.set('RF Frequency: {0} / Images: {1}'.format(len(self.PPM[self.PRESET_COMBOBOX.current()]),self.TOTAL//int(self.INPUT_VOL_SIZE.get())+MINUS)); return True
        except: return False

    def GO(self,event=None):
        try:
            self.Master.Vol_Size  = int(self.INPUT_VOL_SIZE.get()) if self.MODE=='DICOM' else 1   
            self.Master.Dummy_Vol = int(self.INPUT_DUMMY_VOL_IDX.get()) if self.MODE=='DICOM' else 0 
            self.Master.S0_Vol    = int(self.INPUT_S0_VOL_IDX.get())    
            self.Master.Slice     = int(self.INPUT_SLICE_NUMBER.get()) if self.MODE=='DICOM' else 1
            self.Master.RF        = np.array(self.PPM[self.PRESET_COMBOBOX.current()]) / int(self.INPUT_FREQUENCY.get())
            self.Master.RF_Name   = self.Presets[self.PRESET_COMBOBOX.current()]
            if self.Master.Vol_Size == 0 or self.Master.Vol_Size>self.TOTAL: 
                messagebox.showerror('ERROR!',"Invalid volume size!"); raise IndexError
            if self.Master.Dummy_Vol < 0 or self.Master.Dummy_Vol>self.TOTAL//self.Master.Vol_Size: 
                messagebox.showerror('ERROR!',"Invalid dummy volume index!\nIf there are no dummy images, type 0!"); raise IndexError
            if self.Master.S0_Vol < 0 or self.Master.S0_Vol>self.TOTAL//self.Master.Vol_Size: 
                messagebox.showerror('ERROR!',"Invalid S0 volume index!\nIf there are no S0 images, type 0!"); raise IndexError
            if self.Master.Slice < 0 or self.Master.Slice>self.Master.Vol_Size: 
                messagebox.showerror('ERROR!',"Slice number is must be lower than volume size!"); raise IndexError
            if (self.TOTAL//self.Master.Vol_Size) - (1 if self.Master.Dummy_Vol!=0 else 0) - (1 if self.Master.S0_Vol!=0 else 0) != len(self.Master.RF):
                messagebox.showerror('ERROR!','Number of RF frequencies is not correct!'); raise IndexError
            self.Master.GO        = True
            self.ASK_PRESETTINGS.destroy()
        except ValueError: messagebox.showerror('ERROR!',"Invalid parameter! Please check again.")
        except IndexError: pass
        
    def RadioButton_EVENT(self):
        STATE = "normal" if self.RAW_IMAGE.get() else "disabled"
        self.INPUT_DUMMY_VOL_IDX.config(state=STATE)
        self.INPUT_S0_VOL_IDX.config(state=STATE)
        self.INPUT_SLICE_NUMBER.config(state=STATE)
        self.INPUT_VOL_SIZE.config(state=STATE)
        
class Thresholder:
    def __init__(self, master, src):
        LOCATION = master.GET_MASTER_LOCATION()
        self.Master = master
        self.MAIN = TK.Toplevel(self.Master.WINDOW)
        self.MAIN.geometry('580x300+{0}+{1}'.format(LOCATION[0]-290, LOCATION[1]-150))
        self.MAIN.title('ROI Maker')
        self.MAIN.resizable(0,0); self.MAIN.config(bg='#1E1E1E')
        self.src = (src/src.max()*255).astype(np.uint8)
        self.Presets_Names = ["THRESH_OTSU","THRESH_BINARY"]
        self.Gaussian_Presets = ["(None)","(3,3)","(5,5)","(7,7)","(9,9)"]                            
        self.threshold, self.threshold_show = TK.IntVar(), TK.StringVar(); self.threshold_show.set("%3d"%(000))                            

        self.SI_FRAME = TK.Frame(self.MAIN, bg='#1E1E1E')
        self.SI_FRAME.place(x=10,y=10,width=280,height=280)
        self.SI_FIG = plt.figure(1,[5,5])
        plt.rc('font', size=4) 
        self.SI_CANVAS = FigureCanvasTkAgg(self.SI_FIG, master=self.SI_FRAME)
        self.SI_CANVAS.get_tk_widget().pack(fill='both')
        self.SI_CANVAS.draw()

        self.SI_FRAME2 = TK.Frame(self.MAIN, bg='#1E1E1E')
        self.SI_FRAME2.place(x=300,y=10,width=270,height=150)
        self.SI_FIG2 = plt.figure(2,[9,5])
        self.SI_CANVAS2 = FigureCanvasTkAgg(self.SI_FIG2, master=self.SI_FRAME2)
        self.SI_CANVAS2.get_tk_widget().pack(fill='both')

        self.LABEL1 = TK.Label(self.MAIN,text='Mode',background='#1E1E1E',foreground='#FFFFFF')
        self.LABEL1.place(x=300, y=170)
        self.MODE_COMBOBOX = ttk.Combobox(self.MAIN, height=30, values=self.Presets_Names, state='readonly')
        self.MODE_COMBOBOX.place(x=360,y=170,width=205)
        self.MODE_COMBOBOX.current(0)
        self.MODE_COMBOBOX.bind("<<ComboboxSelected>>", self.Process)

        self.LABEL2 = TK.Label(self.MAIN,text='Gaussian',background='#1E1E1E',foreground='#FFFFFF')
        self.LABEL2.place(x=300, y=200)
        self.Gaussian_COMBOBOX = ttk.Combobox(self.MAIN, height=30, values=self.Gaussian_Presets, state='readonly')
        self.Gaussian_COMBOBOX.place(x=360,y=200,width=205)
        self.Gaussian_COMBOBOX.current(0)
        self.Gaussian_COMBOBOX.bind("<<ComboboxSelected>>", self.Process)

        self.LABEL3 = TK.Label(self.MAIN,text='Threshold',background='#1E1E1E',foreground='#FFFFFF')
        self.LABEL3.place(x=300, y=230)
        self.Value1_Set = TK.Scale(self.MAIN,variable=self.threshold,command=self.Change_Value, orient='horizontal',showvalue=0, to=255, from_=0,bg='#3C3C3C', fg='#FFFFFF' )
        self.Value1_Set.place(x=360,y=230,width=185)
        self.Value1_Set.bind('<ButtonRelease-1>',self.Process) 
        self.Value1_Show = TK.Label(self.MAIN, textvariable=self.threshold_show,background='#1E1E1E',foreground='#FFFFFF')
        self.Value1_Show.place(x=545,y=230)

        self.Generate_Bttn = TK.Button(self.MAIN,text='Ok',command=self.GENERATE_ROI, bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.Generate_Bttn.place(x=300,y=260,width=120)
        self.Cancel_Bttn = TK.Button(self.MAIN,text='Cancel',command=self.Close, bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.Cancel_Bttn.place(x=450,y=260,width=120)
        self.Process(); self.Change_Value()
        self.MAIN.protocol('WM_DELETE_WINDOW',self.Close)
        self.MAIN.grab_set()

    def Change_Value(self, event=None): 
        self.threshold_show.set("%d"%(self.threshold.get()))
        values = self.img.ravel()
        plt.figure(2); plt.cla(); #plt.axis('off')
        a, b, _ = plt.hist(values,bins=30)
        plt.plot([self.threshold.get(),255],[10000,a.max()])
        #plt.plot(self.threshold.get(),0,values.max(),values.argmax())
        self.SI_CANVAS2.draw() #; plt.cla(); plt.axis('off')

    def Process(self,event=None):
        OPTION = self.MODE_COMBOBOX.current()
        Blur   = self.Gaussian_COMBOBOX.current()
        self.threshold_show.set("%d"%(self.threshold.get()))

        if Blur==0: self.img = self.src.copy()
        if Blur==1: self.img = cv2.GaussianBlur(self.src, (3,3), 0)
        if Blur==2: self.img = cv2.GaussianBlur(self.src, (5,5), 0)
        if Blur==3: self.img = cv2.GaussianBlur(self.src, (7,7), 0)
        if Blur==4: self.img = cv2.GaussianBlur(self.src, (9,9), 0)

        if OPTION<2:
            if   OPTION==0: 
                mode = cv2.THRESH_BINARY + cv2.THRESH_OTSU
                self.Value1_Set.config(state='disabled')
            elif OPTION==1: 
                mode = cv2.THRESH_BINARY 
                self.Value1_Set.config(state='normal')
            _, result = cv2.threshold(self.img, self.threshold.get(), 255, mode)

        _, self.contour, _ = cv2.findContours(result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        MASK = np.zeros_like(result); MASK = cv2.drawContours(MASK, self.contour, -1, (255,255,255),2)
        plt.figure(1); plt.cla(); plt.imshow(MASK,cmap='gray'); plt.axis('off'); self.SI_CANVAS.draw()

    def GENERATE_ROI(self):
        if self.Master.AUTO_ROI(self.contour): self.Close()

    def Close(self): 
        plt.close(self.SI_FIG); plt.close(self.SI_FIG2); plt.rc('font', size=11) 
        self.MAIN.destroy()

class MAP_VIEWER: #3
    def __init__(self, master, src, fig_index=3, title='', lock=False):
        self.POPUP = TK.Toplevel(master)
        self.screen_width = self.POPUP.winfo_screenwidth()
        self.screen_height = self.POPUP.winfo_screenheight()
        self.fig_index = fig_index
        self.POPUP.geometry('650x575+100+100')
        self.POPUP.title('Image Viewer')
        self.POPUP.resizable(0,0)
        self.src = src
        self.title = title
        self.idx = 0
        self.SI_FRAME = TK.Frame(self.POPUP)
        self.SI_FRAME.place(x=0,y=0,width=650,height=540)
        self.SI_FIG = plt.figure(self.fig_index,[7,6])
        self.SI_CANVAS = FigureCanvasTkAgg(self.SI_FIG, master=self.SI_FRAME)
        self.SI_CANVAS.get_tk_widget().pack(fill='both')
        self.VMIN, self.VMAX = self.src.min(), self.src.max()
        self.PLOT()
        self.toolbarFrame = TK.Frame(master=self.POPUP)
        self.toolbarFrame.place(x=0,y=540,width=600)
        self.toolbar = NavigationToolbar2Tk(self.SI_CANVAS, self.toolbarFrame)
        self.RANGE_SET = TK.Button(self.POPUP, text='Range', command=self.Range_Setup)
        self.RANGE_SET.place(x=240,y=542,width=45,height=30)

        self.SAVE_AS_FILE = TK.Button(self.POPUP, text='Export', command=self.EXPORT_MENU_POPUP)
        self.SAVE_AS_FILE.place(x=295,y=542,width=45,height=30)
        self.MENU_FILE = Menu(self.POPUP, tearoff=0)
        self.MENU_FILE.add_command(label="Save as NiFTI",    command=self.SAVE_AS_NIFTI_FILE)
        self.MENU_FILE.add_command(label="Save as Numpy",    command=self.SAVE_AS_NUMPY_FILE)
        self.MENU_FILE.add_command(label="Save as MAT",      command=self.SAVE_AS_MATLAB_FILE)

        if lock: self.POPUP.grab_set()
        self.POPUP.protocol('WM_DELETE_WINDOW',self.Close)
    
    def PLOT(self):
        plt.figure(self.fig_index); plt.cla(); plt.grid(b=None)
        if self.title!='': plt.title(self.title)
        plt.imshow(self.src, cmap=CMAP[self.idx],vmin=self.VMIN, vmax=self.VMAX)
        plt.colorbar()
        self.SI_CANVAS.draw()
    
    def Close(self):
        plt.close(self.SI_FIG)
        self.POPUP.destroy()

    def EXPORT_MENU_POPUP(self):
        self.MENU_FILE.tk_popup(self.POPUP.winfo_x()+295, self.POPUP.winfo_y()+542, 0)
        self.MENU_FILE.grab_release()

    def SAVE_AS_NIFTI_FILE(self):
        FILE = filedialog.asksaveasfilename(initialdir=os.getcwd(),defaultextension=".nii.gz", title='Save as NiFTI file', initialfile='data.nii.gz',filetypes=[("NiFTI files","*.nii.gz")])
        if FILE!='':
            os.chdir(os.path.dirname(FILE)); import nibabel as nib
            temp = nib.Nifti1Image(self.src.swapaxes(-2,-1), affine=np.eye(4))
            nib.save(temp, FILE)
            messagebox.showinfo('Done!',"Data just saved as \n{0}".format(FILE))
    
    def SAVE_AS_NUMPY_FILE(self):
        FILE = filedialog.asksaveasfilename(initialdir=os.getcwd(),defaultextension=".npy", title='Save numpy array file', initialfile='data.npy',filetypes=[("Numpy files","*.npy")])
        if FILE!='': os.chdir(os.path.dirname(FILE)); np.save(FILE,self.src); messagebox.showinfo('Done!',"Data just saved as \n{0}".format(FILE))

    def SAVE_AS_MATLAB_FILE(self):
        FILE = filedialog.asksaveasfilename(initialdir=os.getcwd(),defaultextension=".mat", title='Save as MATLAB file', initialfile='data.mat',filetypes=[("MATLAB file","*.mat")])
        if FILE!='':
            import scipy.io as sio 
            os.chdir(os.path.dirname(FILE))
            mdic = {self.title: self.src}; sio.savemat(FILE, mdic, True)
            messagebox.showinfo('Done!',"Data just saved as \n{0}".format(FILE))

    def Range_Setup(self):
        self.window = TK.Toplevel(self.POPUP)
        self.window.config(bg='#1E1E1E')
        self.window.geometry('210x170+{0}+{1}'.format(self.screen_width//2-105, self.screen_height//2-85))
        self.window.resizable(0,0)
        self.LABEL_INTERVAL1 = TK.Label(self.window, text='VMIN',background='#1E1E1E',foreground='#FFFFFF')
        self.LABEL_INTERVAL1.place(x=10,y=10,width=70, height=20)
        self.INPUT_INTERVAL1 = TK.Entry(self.window)
        self.INPUT_INTERVAL1.place(x=85,y=10,width=95, height=20)
        self.INPUT_INTERVAL1.insert(0,self.VMIN)
        self.LABEL_INTERVAL2 = TK.Label(self.window, text='VMAX',background='#1E1E1E',foreground='#FFFFFF')
        self.LABEL_INTERVAL2.place(x=10,y=50,width=70, height=20)
        self.INPUT_INTERVAL2 = TK.Entry(self.window)
        self.INPUT_INTERVAL2.place(x=85,y=50,width=95, height=20)
        self.INPUT_INTERVAL2.insert(0,self.VMAX)
        self.LABEL_CMAP = TK.Label(self.window, text='CMAP',background='#1E1E1E',foreground='#FFFFFF')
        self.LABEL_CMAP.place(x=10,y=90,width=70, height=20)
        self.MODE_COMBOBOX = ttk.Combobox(self.window, height=30, values=CMAP, state='readonly')
        self.MODE_COMBOBOX.place(x=85,y=90,width=95)
        self.MODE_COMBOBOX.current(self.idx)
        self.PROCESS = TK.Button(self.window, command=self.Range_Setup_Close, text='Change',bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771' )
        self.PROCESS.place(x=60,y=130,width=90,height=30)
        self.window.grab_set()

    def Range_Setup_Close(self):
        try: self.VMIN = float(self.INPUT_INTERVAL1.get()); self.VMAX = float(self.INPUT_INTERVAL2.get())
        except: messagebox.showerror('ERROR!',"Invalid parameter!"); return None
        self.idx=self.MODE_COMBOBOX.current()
        self.SI_FIG.clear(); self.PLOT()
        self.window.destroy()

class EXPORT_WIZARD_WINDOW:
    def __init__(self, master, B0_MAP=False):
        LOCATION = master.GET_MASTER_LOCATION() if type(master)!=type(None) else [500, 500]
        self.Master = master
        self.EXPORT_WIZARD = TK.Tk(self.Master.WINDOW if type(master)!=type(None) else None)
        self.EXPORT_WIZARD.geometry('290x394+{0}+{1}'.format( LOCATION[0] - 145 , LOCATION[1] - 197))
        self.EXPORT_WIZARD.config(bg='#1E1E1E')
        self.EXPORT_WIZARD.title("Data Export Wizard")
        self.EXPORT_WIZARD.resizable(0,0)
        #self.EXPORT_WIZARD.bind('<Return>', self.GO)
        self.FRAME0 = TK.LabelFrame(self.EXPORT_WIZARD, text="Select File type",background='#1E1E1E',foreground='#FFFFFF')
        self.FRAME0.place(x=10, y=10, width=270, height=40)
        self.Presets = ["NiFTI (*.nii.gz)","Numpy (*.npy)","MATLAB (*.mat)"]
        self.PRESET_COMBOBOX = TK.ttk.Combobox(self.FRAME0, height=30, values=self.Presets, state='readonly')
        self.PRESET_COMBOBOX.pack(fill='both')#; self.Refresh()
        self.PRESET_COMBOBOX.current(0); self.PRESET_COMBOBOX.bind("<<ComboboxSelected>>", self.Preset_Handler)

        self.FRAME1 = TK.LabelFrame(self.EXPORT_WIZARD, text="Select data",background='#1E1E1E',foreground='#FFFFFF')
        self.FRAME1.place(x=10, y=0+60, width=270, height=229)
        
        self.OPTION = [TK.IntVar() for _ in range(8)]
        self.Z_SPECTRUM_PLZ = TK.Checkbutton(self.FRAME1, text="Z-Spectrum", variable=self.OPTION[0], state='normal',
                            bg='#1E1E1E', fg='#808080', highlightcolor='#1E1E1E', activebackground='#1E1E1E'); self.Z_SPECTRUM_PLZ.place(x=10,y=10-10)
        self.B0_MAP_PLZ     = TK.Checkbutton(self.FRAME1, text="B0 MAP" if B0_MAP==True else 'B0 MAP(Need B0 Correction!)', variable=self.OPTION[1], state='normal' if B0_MAP==True else 'disabled',
                            bg='#1E1E1E', fg='#808080', highlightcolor='#1E1E1E', activebackground='#1E1E1E'); self.B0_MAP_PLZ.place(x=10,y=40-10)
        self.MTR_aysm_PLZ   = TK.Checkbutton(self.FRAME1, text="MTR_asymmetry",  variable=self.OPTION[2], state='normal',
                            bg='#1E1E1E', fg='#808080', highlightcolor='#1E1E1E', activebackground='#1E1E1E'); self.MTR_aysm_PLZ.place(x=10,y=70-10)
        self.MTR_Rex_PLZ    = TK.Checkbutton(self.FRAME1, text="MTR_REX", variable=self.OPTION[3],
                            bg='#1E1E1E', fg='#808080', highlightcolor='#1E1E1E', activebackground='#1E1E1E'); self.MTR_Rex_PLZ.place(x=10,y=100-10)
        
        self.OPTION5_PLZ = TK.Checkbutton(self.FRAME1, text="Not supported", variable=self.OPTION[4], state='disabled',
                            bg='#1E1E1E', fg='#808080', highlightcolor='#1E1E1E', activebackground='#1E1E1E'); self.OPTION5_PLZ.place(x=10,y=130-10)
        self.OPTION6_PLZ     = TK.Checkbutton(self.FRAME1, text="Not supported",  variable=self.OPTION[5], state='disabled',
                            bg='#1E1E1E', fg='#808080', highlightcolor='#1E1E1E', activebackground='#1E1E1E'); self.OPTION6_PLZ.place(x=10,y=160-10)
        self.OPTION7_PLZ   = TK.Checkbutton(self.FRAME1, text="Not supported",  variable=self.OPTION[6], state='disabled',
                            bg='#1E1E1E', fg='#808080', highlightcolor='#1E1E1E', activebackground='#1E1E1E'); self.OPTION7_PLZ.place(x=10,y=190-10)
        
        self.FRAME2 = TK.LabelFrame(self.EXPORT_WIZARD, text="",background='#1E1E1E',foreground='#FFFFFF')
        self.FRAME2.place(x=10, y=230+60+9, width=270, height=80)
        self.OPTION8_PLZ    = TK.Checkbutton(self.FRAME2, text="Integrate data (MATLAB only)", variable=self.OPTION[7], state='disabled',
                            bg='#1E1E1E', fg='#808080',highlightcolor='#1E1E1E', activebackground='#1E1E1E'); self.OPTION8_PLZ.place(x=10,y=5)
        self.Generate_Bttn = TK.Button(self.FRAME2,text='Export data',command=None, bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.Generate_Bttn.bind('<Any-Enter>',lambda x: self.Generate_Bttn.config(bg='#094771')); self.Generate_Bttn.bind('<Any-Leave>',lambda x: self.Generate_Bttn.config(bg='#3C3C3C'))
        self.Generate_Bttn.place(x=10,y=35,width=250,height=30)
        self.EXPORT_WIZARD.grab_set()
        self.EXPORT_WIZARD.mainloop()

    def Preset_Handler(self, event=None): 
        self.OPTION8_PLZ.config(state='normal' if self.PRESET_COMBOBOX.current()==2 else 'disabled')
        if self.PRESET_COMBOBOX.current()!=2: self.OPT8.set(0)


    def EXPORT_DATA(self):
        import nibabel as nib
        PATH = filedialog.asksaveasfilename(title='Save as matlab file', initialfile='data.mat', defaultextension='*mat', initialdir=os.getcwd(), filetypes=[('MATLAB File(*.mat)','.mat')]) if self.OPT8.get()==1 else filedialog.askdirectory(title='Choose directory',initialdir=os.getcwd())
        if PATH!='':
            src = {'Z-spectrum':None, 'B0 Map':None, 'MTR_asym':None, 'MTR_Rex':None}; END = self.master.IMAGEs.IMGs.shape[-1]
            if   self.OPTION[0].get()!=0: src['Z-spectrum'] = self.master.IMAGEs.Z_IMGs.copy()
            elif self.OPTION[1].get()!=0: src['B0 Map'] = self.master.B0_MAP.copy()
            elif self.OPTION[2].get()!=0:
                src['MTR_asym'] = []
                for IDX in range(END//2): src['MTR_asym'].append(self.master.IMAGEs.Z_IMGs[:,:,END-IDX-1] - self.master.IMAGEs.Z_IMGs[:,:,IDX]) 
            elif self.OPTION[3].get()!=0: 
                src['MTR_Rex'] = []
                for IDX in range(END//2):
                    Z_lab = self.master.IMAGEs.Z_IMGs[:,:,IDX].copy(); Z_lab[np.where(Z_lab==0)] = 1; Z_lab = 1/Z_lab
                    Z_ref = self.master.IMAGEs.Z_IMGs[:,:,END-IDX-1].copy(); Z_lab[np.where(Z_lab==0)] = 1; Z_ref = 1/Z_ref
                    src['MTR_Rex'].append(Z_lab - Z_ref)
            
            #FILE_TYPE
            if self.PRESET_COMBOBOX.current()!=2:
                for key in src:
                    if type(src[key])!=type(None):
                        temp = (nib.Nifti1Image(src[key], affine=np.eye(4))).swapaxes(-2,-1) if self.PRESET_COMBOBOX.current()==0 else src[key].copy()
                        np.save(PATH+'/'+key,temp)
            else: pass

class SNR_SELECT_WINDOW:
    def __init__(self, master=None, PREVIEW=None):
        LOCATION = master.GET_MASTER_LOCATION() if type(master)!=type(None) else [500, 500]
        self.MAIN = TK.Toplevel(master.WINDOW)
        self.MAIN.geometry('500x550+{0}+{1}'.format( LOCATION[0] - 250 , LOCATION[1] - 275))
        self.MAIN.resizable(0,0)
        self.DICOM_CANVAS = TK.Canvas(self.WINDOW, width=650, height=650, bg='black',cursor='crosshair')
        self.DICOM_CANVAS.place(x=10,y=10, width=460,height=460)
        self.DICOM_IMAGE = self.DICOM_CANVAS.create_image(0,0,anchor=TK.NW, image=ImageTk.PhotoImage(Image.fromarray(PREVIEW)))
        

if __name__=='__main__':
    A = EXPORT_WIZARD_WINDOW(None)