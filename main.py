import os,cv2, pickle
import pydicom
import data_structure, sub_windows, fitting
import matplotlib, math
import tkinter as TK
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
from tkinter import filedialog, ttk, messagebox, Menu, Widget
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

__version__ = '2020-07-23'
__TITLE__ = "CEST Analyzer"

def nothing(x=None): pass

class MAIN_PROGRAM:
    def __init__(self):
        self.WINDOW = TK.Tk()        
        self.TITLE_BAR = 25
        self.BTN_HEIGHT,self.BTN_WIDTH = 35, 35
        self.WINDOW.config(bg='#1E1E1E',highlightbackground='white')
        self.My_Screen = [self.WINDOW.winfo_screenwidth(), self.WINDOW.winfo_screenheight()]
        self.WINDOW.geometry('1300x792+{0}+{1}'.format(self.My_Screen[0]//2-1300//2,self.My_Screen[1]//2-792//2))
        self.WINDOW.resizable(0,0)
        self.WINDOW.title(__TITLE__)    
        self.Variable_Initializer()
        
        #######UI#######
        self.ICON_Initializer()
        self.Canvas_Initializer()
        self.MENU_Initializer()
        self.Graph_Initializer()
        
        self.FILE_HANDLE = TK.Scale(self.WINDOW,variable=self.Current_File, command=lambda x: self.Select_Image(Index=self.Current_File.get()),orient='horizontal',showvalue=0, to=1000, from_=0,state='disabled',bg='#3C3C3C', fg='#FFFFFF' )
        self.FILE_HANDLE.place(x=10,y=670+self.TITLE_BAR,width=650)
        
        self.BTTN_MARKER  = TK.Button(self.WINDOW, text="Marker" ,command=lambda: self.BTTN_Command(_mode=1), image=self.BTTN1_ICON, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN_ROI_FREE  = TK.Button(self.WINDOW, text="ROI Free",command=lambda: self.BTTN_Command(_mode=2), image=self.BTTN2_ICON, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN_ROI_POLY  = TK.Button(self.WINDOW, text="ROI Poly",command=lambda: self.BTTN_Command(_mode=3), image=self.BTTN3_ICON, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN_ROI_CIRCLE  = TK.Button(self.WINDOW, text="ROI Circle",command=lambda: self.BTTN_Command(_mode=4), image=self.BTTN4_ICON, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN_ROI_RECT  = TK.Button(self.WINDOW, text="ROI Rect",command=lambda: self.BTTN_Command(_mode=5), image=self.BTTN5_ICON, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN_ROI_EDIT  = TK.Button(self.WINDOW, text="ROI Edit",command=lambda: self.BTTN_Command(_mode=6), image=self.BTTN6_ICON, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        
        self.BTTN_ROI_CLEAR = TK.Button(self.WINDOW, text="ROI Reset",command=self.BTTN10_Command, image=self.BTTN10_ICON,state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN_ROI_AUTO  = TK.Button(self.WINDOW, text="ROI AUTO",command=self.BTTN7_Command, image=self.BTTN7_ICON, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN_ROI_OPEN  = TK.Button(self.WINDOW, text="ROI Open",command=self.BTTN8_Command, image=self.BTTN8_ICON, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN_ROI_SAVE  = TK.Button(self.WINDOW, text="ROI Save",command=self.BTTN9_Command, image=self.BTTN9_ICON, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        
        self.IMAGE_BTTN_X, self.IMAGE_BTTN_Y = 10, 705
        self.BTTN_MARKER.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*0),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN_ROI_FREE.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*1),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN_ROI_POLY.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*2),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN_ROI_CIRCLE.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*3),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN_ROI_RECT.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*4),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN_ROI_AUTO.place( x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*5),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT) 
        self.BTTN_ROI_EDIT.place( x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*6),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)       
        self.BTTN_ROI_CLEAR.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*7),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT) 
        self.BTTN_ROI_OPEN.place( x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*8),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN_ROI_SAVE.place( x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*9),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
                
        noteStyler = ttk.Style(); noteStyler.element_create('Plain.Notebook.tab', "from", 'default')
        noteStyler.layout("TNotebook.Tab",
            [('Plain.Notebook.tab', {'children': [('Notebook.padding', {'side': 'top', 'children': [('Notebook.focus', {'side': 'top', 'children': 
             [('Notebook.label', {'side': 'top', 'sticky': ''})], 'sticky': 'nswe'})], 'sticky': 'nswe'})], 'sticky': 'nswe'})])
        noteStyler.configure("TNotebook", background='#1E1E1E', borderwidth=0); noteStyler.configure("TNotebook.Tab", background='#3C3C3C', foreground='#FFFFFF',borderwidth=2)

        self.Notebook = ttk.Notebook(self.WINDOW)
        self.Notebook.place(x=670,y=535+self.TITLE_BAR, width=620,height=203)

        self.OPTION_FRAME1 = TK.Frame(self.WINDOW, bg='#1E1E1E')
        self.OPTION_FRAME1.place(x=670, y=540+self.TITLE_BAR, width=200, height=198)
        temp = ttk.Separator(self.OPTION_FRAME1, orient="vertical"); temp.place(x=160, y=10, height=158)

        self.Notebook.add(self.OPTION_FRAME1,text=" ROI ")

        self.OPTION_FRAME2 = TK.Frame(self.WINDOW,  bg='#1E1E1E')
        self.OPTION_FRAME2.place(x=880, y=540+self.TITLE_BAR, width=200, height=198)
        self.IMAGE_RAW_SELECT_BTTN = TK.Radiobutton(self.OPTION_FRAME2, text='RAW Image', value=0, variable=self.IMG_Mode, command=lambda: self.Select_Image(self.Current_File.get(),True), state='disabled', bg='#1E1E1E', fg='#FFFFFF',selectcolor='#1E1E1E')
        self.IMAGE_RAW_SELECT_BTTN.place(x=10, y=15)
        self.IMAGE_Z_SELECT_BTTN = TK.Radiobutton(self.OPTION_FRAME2, text='Z-Spectrum Image', value=1, variable=self.IMG_Mode, command=lambda: self.Select_Image(self.Current_File.get(),True), state='disabled', bg='#1E1E1E', fg='#FFFFFF',selectcolor='#1E1E1E')
        self.IMAGE_Z_SELECT_BTTN.place(x=10, y=55)
        temp = ttk.Separator(self.OPTION_FRAME2, orient="vertical"); temp.place(x=160, y=10, height=158)
        self.Notebook.add(self.OPTION_FRAME2,text=" IMAGE ")

        self.OPTION_FRAME3 = TK.Frame(self.WINDOW,bg='#1E1E1E')
        self.OPTION_FRAME3.place(x=1090, y=540+self.TITLE_BAR, width=200, height=198)
        self.GRAPH_RAW_SELECT_BTTN = TK.Radiobutton(self.OPTION_FRAME3, text='RAW Intensity', value=0, variable=self.Graph_Mode, command=lambda: self.DISPLAY_GRAPH(), state='disabled', bg='#1E1E1E', fg='#FFFFFF',selectcolor='#1E1E1E')
        self.GRAPH_RAW_SELECT_BTTN.place(x=10, y=15)
        self.GRAPH_Z_SELECT_BTTN = TK.Radiobutton(self.OPTION_FRAME3, text='Z-Spectrum', value=1, variable=self.Graph_Mode, command=lambda: self.DISPLAY_GRAPH(), state='disabled', bg='#1E1E1E', fg='#FFFFFF',selectcolor='#1E1E1E')
        self.GRAPH_Z_SELECT_BTTN.place(x=10, y=55)
        self.GRAPH_MTR_SELECT_BTTN = TK.Radiobutton(self.OPTION_FRAME3, text='MTR asym', value=2, variable=self.Graph_Mode, command=lambda: self.DISPLAY_GRAPH(), state='disabled', bg='#1E1E1E', fg='#FFFFFF',selectcolor='#1E1E1E')
        self.GRAPH_MTR_SELECT_BTTN.place(x=10, y=95)
        self.GRAPH_Z_MTR_SELECT_BTTN = TK.Radiobutton(self.OPTION_FRAME3, text='Z-Spectrum + MTR', value=3, variable=self.Graph_Mode, command=lambda: self.DISPLAY_GRAPH(), state='disabled', bg='#1E1E1E', fg='#FFFFFF',selectcolor='#1E1E1E')
        self.GRAPH_Z_MTR_SELECT_BTTN.place(x=10, y=135)
        temp = ttk.Separator(self.OPTION_FRAME3, orient="vertical"); temp.place(x=160, y=10, height=158)
        self.Notebook.add(self.OPTION_FRAME3,text=" PLOT ")
        
        self.CWD = TK.Label(self.WINDOW, bd=1, relief='sunken', anchor='w', textvariable=self.Current_Working_File, bg='#007ACC', fg='#FFFFFF')
        self.CWD.place(x=0,y=748+self.TITLE_BAR,width=1090+60)
        self.CUR_MOUSE_POS = TK.Label(self.WINDOW, bd=1, relief='sunken', anchor='e', textvariable=self.Location, bg='#16825D', fg='#FFFFFF')
        self.CUR_MOUSE_POS.place(x=1090+0+60,y=748+self.TITLE_BAR,width=150)
        self.WINDOW.protocol('WM_DELETE_WINDOW',self.GOODBYE)
        self.WINDOW.mainloop()

    def GOODBYE(self):  
        if ( messagebox.askyesno('EXIT','Do you really want to exit?') ):
            exit(0)

    def ICON_Initializer(self):
        PATH = os.path.dirname(os.path.abspath(__file__)) + '/icon/'
        self.WINDOW.iconbitmap(PATH+'icon.ico')
        self.BTTN1_ICON = ImageTk.PhotoImage(Image.open(PATH+'marker.png'))
        self.BTTN2_ICON = ImageTk.PhotoImage(Image.open(PATH+'free.png'))
        self.BTTN3_ICON = ImageTk.PhotoImage(Image.open(PATH+'poly.png'))
        self.BTTN4_ICON = ImageTk.PhotoImage(Image.open(PATH+'rectangle.png'))
        self.BTTN5_ICON = ImageTk.PhotoImage(Image.open(PATH+'circle.png'))
        self.BTTN6_ICON = ImageTk.PhotoImage(Image.open(PATH+'edit.png'))
        self.BTTN7_ICON = ImageTk.PhotoImage(Image.open(PATH+'magic-wand.png'))
        self.BTTN8_ICON = ImageTk.PhotoImage(Image.open(PATH+'load_roi.png'))
        self.BTTN9_ICON = ImageTk.PhotoImage(Image.open(PATH+'save_roi.png'))
        self.BTTN10_ICON = ImageTk.PhotoImage(Image.open(PATH+'clear_roi.png'))

    def Variable_Initializer(self):
        self.MOUSE_MODE = 0 #0: Nothing, 1: Point, 2: ROI_Free_shape, 3: ROI_Poly, 4: ROI_Rect, 5: Circle
        self.Drawing, self.MOUSE_IN = False, False
        self.IMG_X, self.IMG_Y, self.Marker_X, self.Marker_Y = 0, 0, 0, 0
        self.B0_MAP = None
        self.Canvas_X, self.Canvas_Y = 0, 0
        self.Marker_Intensities = None
        self.ROI_LIST = []
        self.ROI_Selected = -1
        self.ROI_MOVING = False
        self.LINES, self.ROI_POINTS, self.ROI_POINTS_X, self.ROI_POINTS_Y = [], [], [], []
        self.CONTROL_POINTS = []
        self.Edit_CP, self.CP = False ,None
        self.GO, self.TYPE, self.Vol_Size, self.Dummy_Vol, self.S0_Vol, self.Slice, self.RF, self.RF_Name = False, None, None, None, None, None, None, None
        self.Location = TK.StringVar(); self.Location.set("(0, 0), 0")
        self.Current_Working_File = TK.StringVar(); self.Current_Working_File.set("(None)")
        self.Status = TK.StringVar(); self.Status.set("IDLE")
        self.SI_MARKERED = False
        self.Current_File = TK.IntVar(); self.Current_File.set(0)
        self.Total_File = TK.IntVar(); self.Total_File.set(0)
        self.IMAGEs = None
        self.IMG_Mode = TK.IntVar(); self.Graph_Mode = TK.IntVar() #0: RAW / #1: Z-Spectrum
        self.Correction_Result_Windows = None
        self.MTR_Windows = []; self.MTR_Windows2 = []

    def Canvas_Initializer(self):
        self.DICOM_CANVAS = TK.Canvas(self.WINDOW, width=650, height=650, bg='black',cursor='crosshair')
        self.DICOM_CANVAS.place(x=10,y=10+self.TITLE_BAR, width=650,height=650)
        self.DICOM_CANVAS.CWD = self.DICOM_CANVAS.create_text(600,20,font='Arial 10 bold', text='(0000/0000)',fill='yellow')
        self.DICOM_CANVAS.PPM = self.DICOM_CANVAS.create_text(600,40,font='Arial 10 bold', text='')
        self.DICOM_IMAGE = self.DICOM_CANVAS.create_image(0,0,anchor=TK.NW, image=ImageTk.PhotoImage(Image.fromarray(np.zeros([650,650]))))

    def Graph_Initializer(self):
        t = np.arange(0,2*np.pi, 0.1)
        x = 16*np.sin(t)**3
        y = 13*np.cos(t)-5*np.cos(2*t)-2*np.cos(3*t)-np.cos(4*t)

        self.SI_FRAME = TK.LabelFrame(self.WINDOW,bg='#1E1E1E', fg='#FFFFFF')
        self.SI_FRAME.place(x=670,y=37+self.TITLE_BAR,width=520+100,height=400+90)
        self.SI_FIG = plt.figure(0,[5+1,4+1])
        #self.SI_FIG.patch.set_facecolor('#E0E0E0')
        self.SI_AX = self.SI_FIG.add_subplot(111)
        self.SI_AX.set_title("Welcome to {0}".format(__TITLE__))
        self.SI_AX.set_xlabel(" ")
        self.SI_AX.set_ylabel(" ")
        self.SI_AX.plot(x,y)
        self.SI_CANVAS = FigureCanvasTkAgg(self.SI_FIG, master=self.SI_FRAME)
        self.SI_CANVAS.get_tk_widget().pack(fill='both')
        self.SI_CANVAS.draw()
        toolbarFrame = TK.LabelFrame(self.WINDOW,bg='#1E1E1E', fg='#FFFFFF')
        toolbarFrame.place(x=670,y=10+self.TITLE_BAR,width=620) #y=523
        toolbar = NavigationToolbar2Tk(self.SI_CANVAS, toolbarFrame)
        toolbar.config(background='#3C3C3C'); toolbar._message_label.config(background='#3C3C3C',fg='#FFFFFF')

    def MENU_Initializer(self):
        self.MENU1 = TK.Button(self.WINDOW, text="File",command=self.MENU_FILE_POPUP , bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.MENU1.place(x=10,y=10,width=50,height=20)
        self.MENU_FILE = Menu(self.WINDOW, tearoff=0)
        self.MENU_FILE.add_command(label="Open DICOM files",    command=self.FILE_OPEN_DICOMS)
        self.MENU_FILE.add_command(label="Open NiFTI file",    command=self.FILE_OPEN_NIFTI)
        self.MENU_FILE.add_separator()
        self.MENU_FILE.add_command(label="Export Z-spectrum as NiFTI",    command=nothing, state='disabled')
        self.MENU_FILE.add_command(label="Export MTR_aysm as NiFTI",           command=nothing, state='disabled')
        self.MENU_FILE.add_separator()
        self.MENU_FILE.add_command(label="Exit",command=self.GOODBYE)
        
        self.MENU2 = TK.Button(self.WINDOW, text="CEST",command=self.MENU_CEST_POPUP , bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.MENU2.place(x=60,y=10,width=50,height=20)
        self.MENU_CEST = Menu(self.WINDOW, tearoff=0)
        self.MENU_CEST_B0 = Menu(self.WINDOW, tearoff=0)
        self.MENU_CEST_B0.add_command(label="Spline Correction" ,command=lambda: fitting.TEST_SPLINE(self),state='disabled')
        self.MENU_CEST_B0.add_command(label="Lorentzian Correction" ,command=lambda: fitting.TEST_LORENTZ(self), state='disabled')
        self.MENU_CEST_B0.add_command(label="WASSR Correction" ,command=lambda: fitting.TEST_WASSR(self), state='disabled')
        self.MENU_CEST_B0.add_command(label="IDE-LF Correction" ,command=lambda: fitting.TEST_IDE_LF(self), state='disabled')
        self.MENU_CEST_B0.add_separator()
        self.MENU_CEST_B0.add_command(label='B0 Map',command=lambda: fitting.SHOW_B0_MAP(self), state='disabled')
        self.MENU_CEST.add_cascade(label='B0 Correction', menu=self.MENU_CEST_B0)
        self.MENU_CEST_CMAPPING = Menu(self.WINDOW, tearoff=0)
        self.MENU_CEST_CMAPPING.add_command(label="MTR_asym" ,command=lambda: fitting.SHOW_MTR(self),state='disabled')
        self.MENU_CEST_CMAPPING.add_command(label="MTR_Rex"  ,command=lambda: fitting.SHOW_MTR2(self),state='disabled')
        self.MENU_CEST_CMAPPING.add_command(label="PTR"  ,command=lambda: fitting.SHOW_PTR(self),state='disabled')
        self.MENU_CEST.add_cascade(label='Mapping', menu=self.MENU_CEST_CMAPPING)
        
        self.MENU3 = TK.Button(self.WINDOW, text="Tools",command=self.MENU_TOOL_POPUP , bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.MENU3.place(x=110,y=10,width=50,height=20)
        self.MENU_TOOL = Menu(self.WINDOW, tearoff=0)
        self.MENU_TOOL.add_command(label="SNR Mapping" ,command=self.SNR_MAKER,state='disabled')

        self.MENU_INFO = TK.Button(self.WINDOW, text="?",command=self.About_Program , bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.MENU_INFO.place(x=1260,y=10,width=30,height=20)
        self.MENU_INFO.bind('<Any-Enter>',lambda x: self.MENU3.config(bg='#094771')); self.MENU3.bind('<Any-Leave>',lambda x: self.MENU3.config(bg='#3C3C3C'))
        self.RIGHT_CLK_MENU =  Menu(self.DICOM_CANVAS, tearoff = 0)
        self.RIGHT_CLK_MENU.add_command(label='====={0}====='.format(__TITLE__), command=nothing, state='disabled')
        self.RIGHT_CLK_MENU.add_separator()
        self.RIGHT_CLK_MENU.add_command(label="ROI 삭제", command=self.Remove_ROI, state='disabled')

    def BIND_Initializer(self):
        self.WINDOW.bind('<MouseWheel>',self.MOUSE_WHEEL_HANDLER)
        self.DICOM_CANVAS.bind('<Motion>',self.MOUSE_MOTION_HANDLER)
        self.DICOM_CANVAS.bind('<Button-1>',self.MOUSE_B1_CLICK_HANDLER)
        self.DICOM_CANVAS.bind('<Button-3>',self.MOUSE_B3_CLICK_HANDLER)
        self.DICOM_CANVAS.bind('<B1-Motion>',self.MOUSE_B1_DRAG_HANDLER)
        self.DICOM_CANVAS.bind('<ButtonRelease-1>',self.MOUSE_B1_RELEASE_HANDLER)
        self.BTTN_MARKER.bind('<Button-3>',lambda x: self.SI_MARKER_PROCESSING(remove=True))
        self.MENU1.bind('<Any-Enter>',lambda x: self.MENU1.config(bg='#094771')); self.MENU1.bind('<Any-Leave>',lambda x: self.MENU1.config(bg='#3C3C3C'))
        self.MENU2.bind('<Any-Enter>',lambda x: self.MENU2.config(bg='#094771')); self.MENU2.bind('<Any-Leave>',lambda x: self.MENU2.config(bg='#3C3C3C'))
        self.MENU3.bind('<Any-Enter>',lambda x: self.MENU3.config(bg='#094771')); self.MENU3.bind('<Any-Leave>',lambda x: self.MENU3.config(bg='#3C3C3C'))
        self.BTTN_MARKER.bind('<Any-Enter>',lambda x: self.Current_Working_File.set('Point selction(marker)') ); self.BTTN_MARKER.bind('<Any-Leave>',lambda x: self.Current_Working_File.set(self.IMAGEs.FILE_PATH[self.Current_File.get()]) )
        self.BTTN_ROI_FREE.bind('<Any-Enter>',lambda x: self.Current_Working_File.set('Freehand selection') ); self.BTTN_ROI_FREE.bind('<Any-Leave>',lambda x: self.Current_Working_File.set(self.IMAGEs.FILE_PATH[self.Current_File.get()]) )  
        self.BTTN_ROI_POLY.bind('<Any-Enter>',lambda x: self.Current_Working_File.set('Polygon selection')); self.BTTN_ROI_POLY.bind('<Any-Leave>',lambda x: self.Current_Working_File.set(self.IMAGEs.FILE_PATH[self.Current_File.get()]))
        self.BTTN_ROI_RECT.bind('<Any-Enter>',lambda x: self.Current_Working_File.set('Oval selection')); self.BTTN_ROI_RECT.bind('<Any-Leave>',lambda x: self.Current_Working_File.set(self.IMAGEs.FILE_PATH[self.Current_File.get()]))
        self.BTTN_ROI_CIRCLE.bind('<Any-Enter>',lambda x: self.Current_Working_File.set('Rectangle selection')); self.BTTN_ROI_CIRCLE.bind('<Any-Leave>',lambda x: self.Current_Working_File.set(self.IMAGEs.FILE_PATH[self.Current_File.get()]))
        self.BTTN_ROI_AUTO.bind('<Any-Enter>',lambda x: self.Current_Working_File.set('Selection by using threshold')); self.BTTN_ROI_AUTO.bind('<Any-Leave>',lambda x: self.Current_Working_File.set(self.IMAGEs.FILE_PATH[self.Current_File.get()]))
        self.BTTN_ROI_EDIT.bind('<Any-Enter>',lambda x: self.Current_Working_File.set('Edit selection / View selection')); self.BTTN_ROI_EDIT.bind('<Any-Leave>',lambda x: self.Current_Working_File.set(self.IMAGEs.FILE_PATH[self.Current_File.get()]))
        self.BTTN_ROI_CLEAR.bind('<Any-Enter>',lambda x: self.Current_Working_File.set('Remove all selection')); self.BTTN_ROI_CLEAR.bind('<Any-Leave>',lambda x:self.Current_Working_File.set(self.IMAGEs.FILE_PATH[self.Current_File.get()]))
        self.BTTN_ROI_OPEN.bind('<Any-Enter>',lambda x: self.Current_Working_File.set('Import selction')); self.BTTN_ROI_OPEN.bind('<Any-Leave>',lambda x: self.Current_Working_File.set(self.IMAGEs.FILE_PATH[self.Current_File.get()]))
        self.BTTN_ROI_SAVE.bind('<Any-Enter>',lambda x: self.Current_Working_File.set('Export selection')); self.BTTN_ROI_SAVE.bind('<Any-Leave>',lambda x: self.Current_Working_File.set(self.IMAGEs.FILE_PATH[self.Current_File.get()]))

    def MENU_FILE_POPUP(self):
        self.MENU_FILE.tk_popup(self.WINDOW.winfo_x()+110, self.WINDOW.winfo_y()+70, 0)
        self.MENU_FILE.grab_release()

    def MENU_CEST_POPUP(self):
        self.MENU_CEST.tk_popup(self.WINDOW.winfo_x()+117, self.WINDOW.winfo_y()+70, 0)
        self.MENU_CEST.grab_release()

    def MENU_TOOL_POPUP(self):
        self.MENU_TOOL.tk_popup(self.WINDOW.winfo_x()+168, self.WINDOW.winfo_y()+70, 0)
        self.MENU_TOOL.grab_release()

    def FILE_OPEN_DICOMS(self):
        FOLDER = filedialog.askdirectory(initialdir=os.getcwd(), title='Choose directory containing DICOM files')
        if FOLDER!='':
            FILE_LIST = os.listdir(FOLDER)
            for idx in range(len(FILE_LIST)-1,-1,-1):
                FILE_LIST[idx] = FOLDER+'/'+FILE_LIST[idx]
                if os.path.isdir(FILE_LIST[idx]): del(FILE_LIST[idx])
            os.chdir(os.path.dirname(FILE_LIST[0]))
            self.GO = False; S0 = None
            TEMP = sub_windows.ASK_PRESETTINGS_WINDOW(self, len(FILE_LIST))
            self.WINDOW.wait_window(TEMP.ASK_PRESETTINGS)
            if self.GO:
                PLZ_WAIT = self.DICOM_CANVAS.create_text(315,325,font='Arial 10 bold', text='Loading...',fill='yellow')
                NEW_IMAGEs = data_structure.IMAGES()
                try:    self.LIST = sorted(FILE_LIST, key = lambda LIST: int(LIST.split('.')[-1])) #DICOM 확장자(1,2,...,860)
                except: self.LIST = sorted(FILE_LIST, key = lambda LIST: (LIST.split('.')[0]))     #DICOM 파일명(i38491035)
                TEST = sub_windows.IM_ALIVE(self)
                for index in range( 0 ,len(self.LIST)//self.Vol_Size ):
                    INDEX = index*self.Vol_Size+self.Slice-1
                    if   index==self.Dummy_Vol-1: continue
                    elif index==self.S0_Vol   -1: S0 = (pydicom.dcmread(self.LIST[INDEX])).pixel_array
                    else:
                        if NEW_IMAGEs.DICOM_IMPORTER(self.LIST[INDEX]):
                            self.Total_File.set(self.Total_File.get()+1)
                        else: 
                            TEST.DESTROY(); del(TEST)
                            self.DICOM_CANVAS.delete(PLZ_WAIT); self.Status.set("IDLE"); del(NEW_IMAGEs)
                            return None
                    TEST.STEP(((len(self.LIST)//self.Vol_Size)))
                TEST.DESTROY(); del(TEST)
                self.Current_File.set(0); self.Total_File.set(NEW_IMAGEs.IMGs.shape[-1])
                self.IMAGEs = NEW_IMAGEs
                if type(S0) == type(None): S0 = np.ones(self.IMAGEs.IMGs.shape[:2])
                self.IMAGEs.Z_IMAGEs_Generator(S0)
                self.DICOM_CANVAS.delete(PLZ_WAIT)
                self.FILE_OPENED()
    
    def FILE_OPEN_NIFTI(self):
        PATH = filedialog.askopenfilename(initialdir=os.getcwd(), title='Choose NiFTI file')
        if PATH!='':
            os.chdir(os.path.dirname(PATH))
            PLZ_WAIT = self.DICOM_CANVAS.create_text(315,325,font='Arial 10 bold', text='Loading...',fill='yellow')
            NEW_IMAGEs = data_structure.IMAGES()
            if NEW_IMAGEs.NIFTI_IMPORTER(PATH)==False: 
                self.DICOM_CANVAS.delete(PLZ_WAIT); del(NEW_IMAGEs); return None
            else: 
                self.GO = False
                TEMP = sub_windows.ASK_PRESETTINGS_WINDOW(self, NEW_IMAGEs.IMGs.shape[-1])
                self.WINDOW.wait_window(TEMP.ASK_PRESETTINGS)
                if self.GO:
                    self.IMAGEs = NEW_IMAGEs
                    self.Current_File.set(0); self.Total_File.set(self.IMAGEs.IMGs.shape[-1])
            self.Status.set("IDLE"); self.DICOM_CANVAS.delete(PLZ_WAIT)
            self.FILE_OPENED()

    def FILE_OPENED(self):
        for idx in range(len(self.MTR_Windows),-1,-1):
            try: 
                self.MTR_Windows[idx].POPUP.destroy(); del(self.MTR_Windows[idx])
                self.MTR_Windows2[idx].POPUP.destroy(); del(self.MTR_Windows2[idx])
                self.PTR_Windows[idx].POPUP.destroy(); del(self.PTR_Windows)
            except: pass
        try: self.Correction_Result_Windows.destroy(); del(self.Correction_Result_Windows)
        except: pass
        finally: self.Correction_Result_Windows = None
        self.MTR_Windows = [None for _ in range(self.Total_File.get()//2+1)]
        self.MTR_Windows2 = [None for _ in range(self.Total_File.get()//2+1)]
        self.PTR_Windows = [None for _ in range(self.Total_File.get()//2+1)]
        self.DISPLAY_GRAPH()
        self.BIND_Initializer()
        self.IMAGEs.Convert_DISPLAY(mode='RAW' if self.IMG_Mode.get()==0 else 'Z')
        self.Select_Image(Index=self.Current_File.get())
        if self.MOUSE_MODE==6: self.Set_Mouse_Mode()
        self.BTTN_MARKER.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #SI_Marker
        self.BTTN_ROI_FREE.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_FREE
        self.BTTN_ROI_POLY.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_POLY
        self.BTTN_ROI_CIRCLE.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_CIRCLE
        self.BTTN_ROI_RECT.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_RECT
        self.BTTN_ROI_EDIT.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_EDIT
        self.BTTN_ROI_AUTO.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_AUTO
        self.BTTN_ROI_OPEN.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_OPEN
        self.FILE_HANDLE.config(from_=0, to=self.Total_File.get()-1, state='normal')
        self.IMAGE_RAW_SELECT_BTTN.config(state='normal')
        self.IMAGE_Z_SELECT_BTTN.config(state='normal')
        self.GRAPH_RAW_SELECT_BTTN.config(state='normal')
        self.GRAPH_Z_SELECT_BTTN.config(state='normal')
        self.GRAPH_MTR_SELECT_BTTN.config(state='normal')
        self.GRAPH_Z_MTR_SELECT_BTTN.config(state='normal')        
        self.MENU_FILE.entryconfig("Export Z-spectrum as NiFTI" ,state='normal',command=self.IMAGEs.NIFTI_EXPORTER)
        self.MENU_FILE.entryconfig("Export MTR_aysm as NiFTI", state='normal',command=self.IMAGEs.MTR_EXPORTER)
        self.MENU_CEST_B0.entryconfig("Spline Correction" ,state='normal')
        self.MENU_CEST_B0.entryconfig("Lorentzian Correction", state='normal')
        #self.MENU_CEST_B0.entryconfig("WASSR Correction" ,command=nothing, state='disabled')
        self.MENU_CEST_B0.entryconfig("IDE-LF Correction" ,state='normal')
        self.MENU_CEST_CMAPPING.entryconfig("MTR_asym" ,state='normal')
        self.MENU_CEST_CMAPPING.entryconfig("MTR_Rex" , state='normal')
        self.MENU_CEST_CMAPPING.entryconfig("PTR" , state='normal')
        self.MENU_TOOL.entryconfig("SNR Mapping",state='normal')

    def Select_Image(self,Index=0,chmod=False):
        if chmod==True: self.IMAGEs.Convert_DISPLAY(mode='RAW' if self.IMG_Mode.get()==0 else 'Z')
        self.DICOM_CANVAS.itemconfig(self.DICOM_IMAGE, image=self.IMAGEs.IMGs_Display[Index])
        self.DICOM_CANVAS.delete(self.DICOM_CANVAS.CWD)
        self.DICOM_CANVAS.delete(self.DICOM_CANVAS.PPM)
        self.DICOM_CANVAS.CWD = self.DICOM_CANVAS.create_text(600,20,font='Arial 10 bold', text='(%04d/%04d)'%(self.Current_File.get()+1,self.Total_File.get()),fill='yellow')
        self.DICOM_CANVAS.PPM = self.DICOM_CANVAS.create_text(600,40,font='Arial 10 bold', 
                            text='   %0.3f ppm'%(self.RF[self.Current_File.get()]) if self.Total_File.get()==len(self.RF) else '',fill='yellow')
        if self.SI_MARKERED:
            try: self.DICOM_CANVAS.delete(self.DICOM_CANVAS_TEXT0); self.DICOM_CANVAS.delete(self.DICOM_MARKER_INTENSITY1)
            except: pass
            self.DICOM_CANVAS_TEXT0 =self.DICOM_CANVAS.create_text(50,20,fill='white',font="Arial 10",text='({0}, {1})'.format(self.Marker_X,self.Marker_Y))    
            self.DICOM_MARKER_INTENSITY1 = self.DICOM_CANVAS.create_text(140,20,font='Arial 10', fill='white',
                                                text='%3.3f'%(self.IMAGEs.IMGs[self.Marker_Y, self.Marker_X, self.Current_File.get()] if self.Graph_Mode.get()==0 else self.IMAGEs.Z_IMGs[self.Marker_Y, self.Marker_X, self.Current_File.get()]))
            
        if self.IMAGEs.FILE_TYPE=='DICOM': self.Current_Working_File.set(self.IMAGEs.FILE_PATH[self.Current_File.get()])
        elif self.IMAGEs.FILE_TYPE=='NIFTI': self.Current_Working_File.set(self.IMAGEs.FILE_PATH[0])
    
    def Set_Mouse_Mode(self,mode=0):
        self.MOUSE_MODE = mode if self.MOUSE_MODE!=mode else 0
        self.BTTN_MARKER.config(relief=TK.SUNKEN if self.MOUSE_MODE==1 else TK.RAISED, bg='#094771' if self.MOUSE_MODE==1 else '#3C3C3C')
        self.BTTN_ROI_FREE.config(relief=TK.SUNKEN if self.MOUSE_MODE==2 else TK.RAISED, bg='#094771' if self.MOUSE_MODE==2 else '#3C3C3C') #ROI_FREE
        self.BTTN_ROI_POLY.config(relief=TK.SUNKEN if self.MOUSE_MODE==3 else TK.RAISED, bg='#094771' if self.MOUSE_MODE==3 else '#3C3C3C') #ROI_POLY
        self.BTTN_ROI_CIRCLE.config(relief=TK.SUNKEN if self.MOUSE_MODE==4 else TK.RAISED, bg='#094771' if self.MOUSE_MODE==4 else '#3C3C3C') #ROI_CIRCLE
        self.BTTN_ROI_RECT.config(relief=TK.SUNKEN if self.MOUSE_MODE==5 else TK.RAISED, bg='#094771' if self.MOUSE_MODE==5 else '#3C3C3C') #ROI_RECT
        self.BTTN_ROI_EDIT.config(relief=TK.SUNKEN if self.MOUSE_MODE==6 else TK.RAISED, bg='#094771' if self.MOUSE_MODE==6 else '#3C3C3C') #ROI_MOVE 

    def BTTN_Command(self, _mode):      #BUTTON 1~6
        self.CURRENT_LINE = None
        self.Set_Mouse_Mode(mode=_mode)
        self.Remove_Control_Point()
        if self.Drawing==True:
            self.Drawing = False
            self.DICOM_CANVAS.delete(*self.LINES); 
            try: self.DICOM_CANVAS.delete(self.END_POINT)
            except: pass
            del(self.ROI_LIST[-1])
        self.LINES, self.ROI_POINTS, self.ROI_POINTS_X, self.ROI_POINTS_Y = [], [], [], []
        #self.DISPLAY_GRAPH()

    def BTTN7_Command(self):
        self.Threshold_Settings = sub_windows.Thresholder(self,self.IMAGEs.IMGs[:,:,self.Current_File.get()])
        self.WINDOW.wait_window(self.Threshold_Settings.MAIN)
            
    def BTTN8_Command(self):
        FILE = filedialog.askopenfilename(initialdir=os.getcwd(), title='Choose ROI file',filetypes=[("ROI files","*.roi")])
        if FILE!='':
            os.chdir(os.path.dirname(FILE))
            with open(FILE,"rb") as f: DATA = pickle.load(f)
            if (True if len(self.ROI_LIST)==0 else messagebox.askyesno('Warning!','All current ROIs will be removed!.\nAre you sure want to continue?')):
                self.ROI_Selected=-1; self.Remove_ROI()
                for idx in range(len(DATA)):
                    self.ROI_LIST.append(data_structure.ROI(self.IMAGEs.IMGs.shape[:2]),data_structure.PLOT_COLOR.pop(0))
                    THIS = DATA[idx] #ROI_X, ROI_Y, ROI_TK
                    if THIS[3]=='ROI_CIRCLE': self.CURRENT_LINE = self.DICOM_CANVAS.create_oval(   *THIS[2],fill='',outline=self.ROI_LIST[-1].Color)
                    else:                     self.CURRENT_LINE = self.DICOM_CANVAS.create_polygon(*THIS[2],fill='',outline=self.ROI_LIST[-1].Color)  
                    self.ROI_LIST[-1].Make_ROI(THIS[3],np.array(THIS[0]), np.array(THIS[1]), np.array(THIS[2]), self.CURRENT_LINE)
                    if self.ROI_LIST[-1].Measure_ROI(self.IMAGEs.IMGs if self.Graph_Mode.get()==0 else self.IMAGEs.Z_IMGs)==False:
                        del(self.ROI_LIST[-1]); self.DICOM_CANVAS.delete(self.CURRENT_LINE)
                    self.DISPLAY_GRAPH()

    def BTTN9_Command(self):
        if len(self.ROI_LIST)!=0:
            FILE = filedialog.asksaveasfilename(initialdir=os.getcwd(), title='Save ROI as file',initialfile='ROI.roi',filetypes=[("ROI files","*.roi")])
            if FILE!='':
                os.chdir(os.path.dirname(FILE))
                DATA = []
                for idx in range(len(self.ROI_LIST)): DATA.append(self.ROI_LIST[idx].SAVE_ROI())
                with open(FILE,'wb') as f: pickle.dump(DATA, f)

    def BTTN10_Command(self): 
        if messagebox.askyesno('Warning!','All of ROIs will be removed!\nAre you sure want to continue?'):
            self.ROI_Selected=-1; self.Remove_ROI()
            self.DISPLAY_GRAPH()

    def SNR_MAKER(self):
        TEMP = sub_windows.SNR_SELECT_WINDOW(self, self.IMAGEs.IMGs[:,:,0])
        self.WINDOW.wait_window(TEMP.MAIN)

    def GET_IMAGE_POSITION(self, x, y):
        O_size = self.IMAGEs.IMGs.shape[:2]
        return int(x / 650 * O_size[0]), int(y / 650 * O_size[1])

    def MOUSE_WHEEL_HANDLER(self, event):
        TOTAL, CURRENT = self.Total_File.get(),self.Current_File.get()
        if TOTAL>0:
            dN = -1 if event.delta>0 else 1
            if CURRENT+dN==TOTAL: self.Current_File.set(0)
            elif CURRENT+dN<0: self.Current_File.set(TOTAL-1)
            else: self.Current_File.set(CURRENT+dN)
            self.Select_Image(Index=self.Current_File.get())
    
    def MOUSE_MOTION_HANDLER(self,event):
        self.Canvas_X, self.Canvas_Y = event.x, event.y
        self.IMG_X, self.IMG_Y = self.GET_IMAGE_POSITION(event.x, event.y)
        self.Location.set('( %3d, %3d ), %3.2f'%(self.IMG_X, self.IMG_Y,self.IMAGEs.IMGs[self.IMG_Y, self.IMG_X,self.Current_File.get()] if self.Graph_Mode.get()==0 else self.IMAGEs.Z_IMGs[self.IMG_Y, self.IMG_X,self.Current_File.get()]))
        if self.MOUSE_MODE==3: #ROI_Poly
            if self.Drawing==True:
                self.DICOM_CANVAS.coords(self.LINES[-1], *self.START_POINT, self.Canvas_X, self.Canvas_Y)
                THIS = self.DICOM_CANVAS.find_enclosed(self.Canvas_X-8,self.Canvas_Y-8,self.Canvas_X+8,self.Canvas_Y+8)
                if len(THIS)!=0 and THIS[0]==self.END_POINT: self.MOUSE_IN = True
                else: self.MOUSE_IN = False 
        elif self.MOUSE_MODE==6: #ROI_EDIT
            if self.ROI_Selected!=-1:
                try:
                    TEMP = self.DICOM_CANVAS.find_enclosed(self.Canvas_X-10,self.Canvas_Y-10, self.Canvas_X+10, self.Canvas_Y+10)
                    if TEMP[0] in self.CONTROL_POINTS: 
                        self.DICOM_CANVAS.config(cursor='hand1')
                        self.Edit_CP = TEMP[0]
                        self.CP = self.CONTROL_POINTS.index(self.Edit_CP)
                        return None
                except: self.Edit_CP, self.CP = False, None
            if self.Drawing==False and self.ROI_MOVING==False:
                for idx in range(len(self.ROI_LIST)-1,-1,-1):
                    if self.ROI_LIST[idx].MASK[self.IMG_Y][self.IMG_X]==1:
                        self.DICOM_CANVAS.config(cursor='hand2')
                        self.ROI_Selected = idx
                        return None
                self.ROI_Selected = -1
                self.DICOM_CANVAS.config(cursor='crosshair')
                    
    def MOUSE_B1_CLICK_HANDLER(self, event):
        self.Canvas_X, self.Canvas_Y = event.x, event.y
        self.IMG_X, self.IMG_Y = self.GET_IMAGE_POSITION(event.x, event.y)
        if   self.MOUSE_MODE==1: self.Marker_X, self.Marker_Y = self.GET_IMAGE_POSITION(event.x, event.y); self.SI_MARKER_PROCESSING() #1: Point
        elif self.MOUSE_MODE>1 and self.MOUSE_MODE<6:
            if self.MOUSE_MODE!=3: #Not ROI_Poly
                self.ROI_LIST.append(data_structure.ROI(self.IMAGEs.IMGs.shape[:2],data_structure.PLOT_COLOR.pop(0)))
                self.START_POINT = (self.Canvas_X, self.Canvas_Y)
                self.Drawing = True
                if self.MOUSE_MODE==2: #2: ROI_Free_shape
                    self.LINES, self.ROI_POINTS, self.ROI_POINTS_X, self.ROI_POINTS_Y = [], [], [], []
                    self.LINES.append( self.DICOM_CANVAS.create_polygon(self.Canvas_X,self.Canvas_Y,fill='',outline='yellow') )
                    self.ROI_POINTS.extend([self.Canvas_X,self.Canvas_Y]); self.ROI_POINTS_X.append(self.Canvas_X); self.ROI_POINTS_Y.append(self.Canvas_Y)
                elif self.MOUSE_MODE==4: #4: ROI_Rect
                    self.CURRENT_LINE = self.DICOM_CANVAS.create_polygon(self.Canvas_X,self.Canvas_Y,self.Canvas_X,self.Canvas_Y+1,self.Canvas_X+1, self.Canvas_Y+1,self.Canvas_X+1,self.Canvas_Y,fill='',outline='yellow')                                                                
                elif self.MOUSE_MODE==5: #5: Circle
                    self.CURRENT_LINE = self.DICOM_CANVAS.create_oval(self.Canvas_X,self.Canvas_Y,self.Canvas_X+1,self.Canvas_Y+1,fill='',outline='yellow')
            elif self.MOUSE_MODE==3: #ROI_Poly
                if self.MOUSE_IN==True: return None
                self.START_POINT = (self.Canvas_X, self.Canvas_Y)
                if self.Drawing==False:
                    self.ROI_LIST.append(data_structure.ROI(self.IMAGEs.IMGs.shape[:2],data_structure.PLOT_COLOR.pop(0)))
                    self.ROI_POINTS, self.ROI_POINTS_X, self.ROI_POINTS_Y = [], [], []
                    self.END_POINT = self.DICOM_CANVAS.create_oval(self.Canvas_X-3,self.Canvas_Y-3,self.Canvas_X+3, self.Canvas_Y+3, fill='white',outline='yellow')
                    self.Drawing = True
                self.ROI_POINTS.extend([self.Canvas_X,self.Canvas_Y]); self.ROI_POINTS_X.append(self.Canvas_X); self.ROI_POINTS_Y.append(self.Canvas_Y)
                self.LINES.append( self.DICOM_CANVAS.create_polygon(*self.START_POINT,self.Canvas_X+1,self.Canvas_Y+1, outline='yellow') )
        elif self.MOUSE_MODE==6: #6: ROI_EDIT
            self.Remove_Control_Point()
            self.START_POINT = (self.Canvas_X, self.Canvas_Y)
            if self.ROI_Selected!=-1: self.Draw_Control_Point(self.ROI_Selected)
            else: self.Edit_CP, self.CP = False, None
        else: pass

    def MOUSE_B1_DRAG_HANDLER(self, event):
        self.Canvas_X, self.Canvas_Y = event.x, event.y
        if self.MOUSE_MODE>1 and self.MOUSE_MODE<6:
            if self.MOUSE_MODE==2: #2: ROI_Free_shape
                self.LINES.append( self.DICOM_CANVAS.create_polygon(self.Canvas_X,self.Canvas_Y,fill='',outline='yellow') )
                self.ROI_POINTS.extend([self.Canvas_X,self.Canvas_Y]); self.ROI_POINTS_X.append(self.Canvas_X); self.ROI_POINTS_Y.append(self.Canvas_Y)
            elif self.MOUSE_MODE==4: #4: ROI_Rect
                self.DICOM_CANVAS.coords(self.CURRENT_LINE,*self.START_POINT, self.START_POINT[0], self.Canvas_Y, self.Canvas_X, self.Canvas_Y, self.Canvas_X, self.START_POINT[1])                                                                           
            elif self.MOUSE_MODE==5: #5: Circle
                self.DICOM_CANVAS.coords(self.CURRENT_LINE,*self.START_POINT,self.Canvas_X, self.Canvas_Y)
        elif self.MOUSE_MODE==6: #6: ROI_EDIT
            if self.Edit_CP:
                dx, dy = self.Canvas_X - self.START_POINT[0], self.Canvas_Y - self.START_POINT[1]
                self.START_POINT = (self.Canvas_X, self.Canvas_Y)
                self.ROI_LIST[self.ROI_Selected].EDIT_ROI(self.CP, dx, dy)
                self.DICOM_CANVAS.coords(self.Edit_CP,*self.ROI_LIST[self.ROI_Selected].ROI_for_TK)
                self.DICOM_CANVAS.coords(self.ROI_LIST[self.ROI_Selected].TK_INDEX,*self.ROI_LIST[self.ROI_Selected].ROI_for_TK)
                self.Draw_Control_Point(self.ROI_Selected)
            elif self.ROI_Selected!=-1:
                self.ROI_MOVING = True
                dx, dy = self.Canvas_X - self.START_POINT[0], self.Canvas_Y - self.START_POINT[1]
                self.START_POINT = (self.Canvas_X, self.Canvas_Y)
                self.ROI_LIST[self.ROI_Selected].MOVE_ROI(dx,dy,False)
                self.DICOM_CANVAS.coords(self.ROI_LIST[self.ROI_Selected].TK_INDEX,*self.ROI_LIST[self.ROI_Selected].ROI_for_TK)
                self.Draw_Control_Point(self.ROI_Selected)
        else: pass

    def MOUSE_B1_RELEASE_HANDLER(self, event):
        self.Canvas_X, self.Canvas_Y = event.x, event.y
        if self.MOUSE_MODE>1 and self.MOUSE_MODE<6:
            if   self.MOUSE_MODE==2: #2: ROI_Free_shape
                self.DICOM_CANVAS.delete(*self.LINES)
                if len(self.ROI_POINTS)//2>2:
                    self.CURRENT_LINE = self.DICOM_CANVAS.create_polygon(*self.ROI_POINTS,fill='',outline=self.ROI_LIST[-1].Color)
                    self.ROI_LIST[-1].Make_ROI('ROI_FREE',np.array(self.ROI_POINTS_X), np.array(self.ROI_POINTS_Y), self.ROI_POINTS, self.CURRENT_LINE)
                    self.DISPLAY_GRAPH()
                    self.Drawing = False
                else: del(self.ROI_LIST[-1])
            elif self.MOUSE_MODE==3: #3: ROI_Poly
                if self.MOUSE_IN==True:
                    self.DICOM_CANVAS.delete(self.END_POINT); self.DICOM_CANVAS.delete(*self.LINES)
                    self.CURRENT_LINE = self.DICOM_CANVAS.create_polygon(*self.ROI_POINTS, *self.ROI_POINTS[:2], fill='',outline=self.ROI_LIST[-1].Color)
                    self.Drawing,self.MOUSE_IN = False, False
                    self.ROI_LIST[-1].Make_ROI('ROI_POLY',np.array(self.ROI_POINTS_X), np.array(self.ROI_POINTS_Y), self.ROI_POINTS, self.CURRENT_LINE)
                    self.DISPLAY_GRAPH()
                else: return None
            elif self.MOUSE_MODE==4: #4: ROI_Rect
                X,Y, X2,Y2  = self.START_POINT[0], self.START_POINT[1], self.Canvas_X, self.Canvas_Y
                ROI_X, ROI_Y = np.array([X,X,X2,X2]), np.array([Y,Y2,Y2,Y])
                ROI_POINTS = np.array([X,Y,X,Y2,X2,Y2,X2,Y])
                self.Drawing = False
                if abs(X-X2)>3 and abs(Y-Y2)>3:
                    self.DICOM_CANVAS.itemconfig(self.CURRENT_LINE,outline=self.ROI_LIST[-1].Color)
                    self.ROI_LIST[-1].Make_ROI('ROI_RECT',ROI_X, ROI_Y, ROI_POINTS, self.CURRENT_LINE)
                    self.ROI_LIST[-1].Measure_ROI(self.IMAGEs.IMGs if self.Graph_Mode.get()==0 else self.IMAGEs.Z_IMGs)
                    self.DISPLAY_GRAPH()
                else:
                    self.DICOM_CANVAS.delete(self.CURRENT_LINE)
                    del(self.ROI_LIST[-1])
            elif self.MOUSE_MODE==5: #5: Circle
                X,Y,X2,Y2 = self.START_POINT[0], self.START_POINT[1], self.Canvas_X, self.Canvas_Y
                ROI_X, ROI_Y = np.array([X,X2]), np.array([Y,Y2])
                ROI_POINTS = np.array([X,Y,X2,Y2])
                self.Drawing = False
                if abs(X-X2)>3 and abs(Y-Y2)>3:
                    self.DICOM_CANVAS.itemconfig(self.CURRENT_LINE,outline=self.ROI_LIST[-1].Color)
                    self.ROI_LIST[-1].Make_ROI('ROI_CIRCLE',ROI_X, ROI_Y, ROI_POINTS, self.CURRENT_LINE)
                    self.ROI_LIST[-1].Measure_ROI(self.IMAGEs.IMGs if self.Graph_Mode.get()==0 else self.IMAGEs.Z_IMGs)
                    self.DISPLAY_GRAPH()
                else:
                    self.DICOM_CANVAS.delete(self.CURRENT_LINE)
                    del(self.ROI_LIST[-1])
        elif self.MOUSE_MODE==6: #6: ROI_EDIT
            if self.Edit_CP:
                dx, dy = self.Canvas_X - self.START_POINT[0], self.Canvas_Y - self.START_POINT[1]
                self.START_POINT = (self.Canvas_X, self.Canvas_Y)
                self.ROI_LIST[self.ROI_Selected].EDIT_ROI(self.CP, dx, dy, True)
                self.DICOM_CANVAS.coords(self.Edit_CP,*self.ROI_LIST[self.ROI_Selected].ROI_for_TK)
                self.DICOM_CANVAS.coords(self.ROI_LIST[self.ROI_Selected].TK_INDEX,*self.ROI_LIST[self.ROI_Selected].ROI_for_TK)
                self.Draw_Control_Point(self.ROI_Selected)
                self.Edit_CP, self.CP = False, None
                self.ROI_LIST[-1].Measure_ROI(self.IMAGEs.IMGs if self.Graph_Mode.get()==0 else self.IMAGEs.Z_IMGs)
            elif self.ROI_MOVING==True:
                dx, dy = self.Canvas_X - self.START_POINT[0], self.Canvas_Y - self.START_POINT[1]
                self.START_POINT = (self.Canvas_X, self.Canvas_Y)
                self.ROI_LIST[self.ROI_Selected].MOVE_ROI(dx,dy,True)
                self.DICOM_CANVAS.coords(self.ROI_LIST[self.ROI_Selected].TK_INDEX,*self.ROI_LIST[self.ROI_Selected].ROI_for_TK)
                self.ROI_MOVING=False
                self.ROI_LIST[-1].Measure_ROI(self.IMAGEs.IMGs if self.Graph_Mode.get()==0 else self.IMAGEs.Z_IMGs)
                self.ROI_Selected = -1
            self.DISPLAY_GRAPH(index=self.ROI_Selected)
        else: pass
        self.LINES, self.ROI_POINTS, self.ROI_POINTS_X, self.ROI_POINTS_Y = [], [], [], []
        self.CURRENT_LINE = None

    def MOUSE_B3_CLICK_HANDLER(self, event):
        self.RIGHT_CLK_MENU.entryconfig("ROI 삭제",state='normal' if self.ROI_Selected!=-1 else 'disabled')
        self.RIGHT_CLK_MENU.tk_popup(event.x_root+80, event.y_root, 0)
        self.RIGHT_CLK_MENU.grab_release()

    def SI_MARKER_PROCESSING(self, event=None, remove=False):
        try:
            self.DICOM_CANVAS.delete(self.DICOM_CANVAS_CROSS1)
            self.DICOM_CANVAS.delete(self.DICOM_CANVAS_CROSS2)
            self.DICOM_CANVAS.delete(self.DICOM_CANVAS_TEXT0)
            self.DICOM_CANVAS.delete(self.DICOM_MARKER_INTENSITY1)
            self.DICOM_CANVAS.delete(self.DICOM_MARKER_NUMS)
        except: pass
        finally:
            if remove==True: self.Marker_Intensities=None; self.SI_MARKERED = False; self.DISPLAY_GRAPH() ; return None
            self.SI_MARKERED = True
            self.DISPLAY_GRAPH(marker_only=True)    
            self.DICOM_CANVAS_CROSS1=self.DICOM_CANVAS.create_line(self.Canvas_X-10, self.Canvas_Y, self.Canvas_X+10, self.Canvas_Y, fill='red')
            self.DICOM_CANVAS_CROSS2=self.DICOM_CANVAS.create_line(self.Canvas_X, self.Canvas_Y-10, self.Canvas_X, self.Canvas_Y+10, fill='red')
            self.DICOM_MARKER_NUMS = self.DICOM_CANVAS.create_text(10,20,font='Arial 10 bold',text='+', fill='red')
            self.DICOM_CANVAS_TEXT0 =self.DICOM_CANVAS.create_text(50,20,fill='white',font="Arial 10",text='({0}, {1})'.format(self.Marker_X,self.Marker_Y))    
            self.DICOM_MARKER_INTENSITY1 = self.DICOM_CANVAS.create_text(140,20,font='Arial 10', fill='white',
                                                text='%3.3f'%(self.IMAGEs.IMGs[self.Marker_Y, self.Marker_X, self.Current_File.get()] if self.Graph_Mode.get()==0 else self.IMAGEs.Z_IMGs[self.Marker_Y, self.Marker_X, self.Current_File.get()]))

    def DISPLAY_GRAPH(self, index=-1, marker_only=False):
        self.GENERATE_MASK()
        plt.figure(0),plt.cla()
        self.SI_AX.clear()
        self.SI_AX.set_title(self.IMAGEs.Name if type(self.IMAGEs.Name)!=type(None) else "Welcome to CEST Analyzer")
        self.SI_AX.set_ylabel("Intensity" if self.Graph_Mode.get()==0 else "S/S0")
        self.BTTN_ROI_SAVE.config(  state='disabled' if len(self.ROI_LIST)==0 else 'normal')
        self.BTTN_ROI_CLEAR.config( state='disabled' if len(self.ROI_LIST)==0 else 'normal')
        if self.Total_File.get()==len(self.RF): X = self.RF; self.SI_AX.invert_xaxis(); self.SI_AX.set_xlabel("Frequency offset(ppm)")
        else: X=[i for i in range(self.Total_File.get())]; self.SI_AX.set_xlabel("Slice #")
        if self.SI_MARKERED and index!=-1: 
            self.Marker_Intensities = self.IMAGEs.IMGs[self.Marker_Y, self.Marker_X, :] if self.Graph_Mode.get()==0 else self.IMAGEs.Z_IMGs[self.Marker_Y, self.Marker_X, :]
            self.SI_AX.plot(X,self.Marker_Intensities)
        for idx in range(0 if index==-1 else index,len(self.ROI_LIST) if index==-1 else index+1): 
            if marker_only==False: self.ROI_LIST[idx].Measure_ROI(self.IMAGEs.IMGs if self.Graph_Mode.get()==0 else self.IMAGEs.Z_IMGs, self.Graph_Mode.get())
            if self.Graph_Mode.get()!=2: self.SI_AX.plot(X,self.ROI_LIST[idx].Intensities,color=self.ROI_LIST[idx].Color)           
            if self.Graph_Mode.get()>1:  self.SI_AX.plot(X[:self.Total_File.get()//2+1],self.ROI_LIST[idx].MTR_Intensities,color=self.ROI_LIST[idx].Color)    
            if type(self.B0_MAP)!=type(None) and index!=-1 and (self.Graph_Mode.get()==1 or self.Graph_Mode.get()==3): 
                self.ROI_LIST[index].Measure_ROI(self.IMAGEs.Z_IMGs_Backup,1)
                self.SI_AX.scatter(X,self.ROI_LIST[idx].Original_Intensities,color='black',marker='x')
        self.SI_CANVAS.draw()
        
    def Draw_Control_Point(self, index):
        try: self.DICOM_CANVAS.delete(*self.CONTROL_POINTS)
        except: pass
        self.CONTROL_POINTS = []
        if self.ROI_LIST[index].ROI_TYPE!='ROI_FREE':
            if self.ROI_LIST[index].ROI_TYPE=='ROI_POLY':
                for idx in range(0,len(self.ROI_LIST[index].ROI_for_TK), 2):
                    X1,Y1 = self.ROI_LIST[index].ROI_for_TK[idx],self.ROI_LIST[index].ROI_for_TK[idx+1]
                    self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X1-1,Y1-1,X1-1,Y1+1,X1+1,Y1+1,X1+1,Y1-1,fill='white',outline='white', width=2))
            elif self.ROI_LIST[index].ROI_TYPE=='ROI_RECT':
                X1,Y1,X2,Y2 = self.ROI_LIST[index].ROI_for_TK[0],self.ROI_LIST[index].ROI_for_TK[1],self.ROI_LIST[index].ROI_for_TK[4],self.ROI_LIST[index].ROI_for_TK[5]
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X1-1,Y1-1,X1-1,Y1+1,X1+1,Y1+1,X1+1,Y1-1,fill='white',outline='white', width=2))
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X1-1,Y2-1,X1-1,Y2+1,X1+1,Y2+1,X1+1,Y2-1,fill='white',outline='white', width=2))
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X2-1,Y2-1,X2-1,Y2+1,X2+1,Y2+1,X2+1,Y2-1,fill='white',outline='white', width=2))
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X2-1,Y1-1,X2-1,Y1+1,X2+1,Y1+1,X2+1,Y1-1,fill='white',outline='white', width=2))
            elif self.ROI_LIST[index].ROI_TYPE=='ROI_CIRCLE': 
                X1, X2 = self.ROI_LIST[index].ROI_for_TK[0], self.ROI_LIST[index].ROI_for_TK[2]
                X3     = (X1+X2)//2
                Y1, Y2 = self.ROI_LIST[index].ROI_for_TK[1], self.ROI_LIST[index].ROI_for_TK[3]
                Y3     = (Y1+Y2)//2
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X3-1,Y1-1,X3-1,Y1+1,X3+1,Y1+1,X3+1,Y1-1,fill='white',outline='white', width=2))
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X1-1,Y3-1,X1-1,Y3+1,X1+1,Y3+1,X1+1,Y3-1,fill='white',outline='white', width=2))
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X3-1,Y2-1,X3-1,Y2+1,X3+1,Y2+1,X3+1,Y2-1,fill='white',outline='white', width=2))
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X2-1,Y3-1,X2-1,Y3+1,X2+1,Y3+1,X2+1,Y3-1,fill='white',outline='white', width=2))
    
    def Remove_Control_Point(self):
        try: 
            self.DICOM_CANVAS.delete(*self.CONTROL_POINTS)
            self.CONTROL_POINTS = []
        except: pass

    def Remove_ROI(self):
        try: self.DICOM_CANVAS.delete(*self.CONTROL_POINTS)
        except: pass
        for idx in range(len(self.ROI_LIST)-1 if self.ROI_Selected==-1 else self.ROI_Selected, -1 if self.ROI_Selected==-1 else self.ROI_Selected-1, -1):
            data_structure.PLOT_COLOR.insert(0,self.ROI_LIST[idx].Color)
            try: self.DICOM_CANVAS.delete(self.ROI_LIST[idx].TK_INDEX)
            except: pass
            del(self.ROI_LIST[idx])
        self.DISPLAY_GRAPH()

    def AUTO_ROI(self, contour):
        if len(self.ROI_LIST)!=0:
            rtn = messagebox.askyesno('Warning!','All current ROIs will be replaced!\nAre you sure want to continue?'.format(data_structure.PLOT_COLOR_TOTAL))
            if rtn==False: return False
        self.ROI_Selected = -1
        self.Remove_Control_Point()
        self.Remove_ROI()
        contour = sorted(contour, key=lambda x: cv2.contourArea(x), reverse=True)
        for i in range(len(contour)):
            self.ROI_POINTS, self.ROI_POINTS_X, self.ROI_POINTS_Y = [], [], []
            self.ROI_LIST.append(data_structure.ROI(self.IMAGEs.IMGs.shape[:2],data_structure.PLOT_COLOR.pop(0)))
            Contour = contour[i][:,0]
            for ct in Contour:
                self.ROI_POINTS.extend([ct[0]/self.IMAGEs.IMGs.shape[1]*650,ct[1]/self.IMAGEs.IMGs.shape[0]*650])
                self.ROI_POINTS_X.append(ct[0]/self.IMAGEs.IMGs.shape[1]*650); self.ROI_POINTS_Y.append(ct[1]/self.IMAGEs.IMGs.shape[0]*650)
            self.CURRENT_LINE = self.DICOM_CANVAS.create_polygon(*self.ROI_POINTS,fill='',outline=self.ROI_LIST[-1].Color)
            self.ROI_LIST[-1].Make_ROI('ROI_FREE',np.array(self.ROI_POINTS_X), np.array(self.ROI_POINTS_Y), self.ROI_POINTS, self.CURRENT_LINE)
            if self.ROI_LIST[-1].Measure_ROI(self.IMAGEs.IMGs if self.Graph_Mode.get()==0 else self.IMAGEs.Z_IMGs)==False:
                del(self.ROI_LIST[-1]); self.DICOM_CANVAS.delete(self.CURRENT_LINE)
            if len(self.ROI_LIST)==data_structure.PLOT_COLOR_TOTAL: break
        plt.rc('font', size=10)
        self.SI_FIG = plt.figure(0,[5+1,4+1])
        self.DISPLAY_GRAPH()
        return True
    
    def GENERATE_MASK(self):
        self.MASK = np.ones(self.IMAGEs.IMGs.shape[:2]) if len(self.ROI_LIST)==0 else np.zeros(self.IMAGEs.IMGs.shape[:2])
        for idx in range(len(self.ROI_LIST)):
            PT = np.where(self.ROI_LIST[idx].MASK==1)
            self.MASK[PT] = 1

    def GET_MASTER_LOCATION(self):
        return (self.WINDOW.winfo_x()+650, self.WINDOW.winfo_y()+396)

    def About_Program(self):
        messagebox.showinfo('About',"""
        {0}
        Ver: {1}\n
        Developed by Kim Yun Heung
        (techman011@gmail.com)
        KNU BMRLab (http://bmr.knu.ac.kr)\n
            --Main modules--
        Pydicom, OpenCV, matplotlib, scipy, numpy, SimpleITK\n
        """.format(__TITLE__,__version__))

if __name__ == "__main__": 
    print("Starting {0}...".format(__TITLE__))
    import matplotlib; matplotlib.use("Agg")
    matplotlib.style.use('bmh')
    plt.rc('font', size=10)
    """
    plt.rcParams['text.color'] = '#ffffff'
    plt.rcParams['axes.labelcolor'] = '#ffffff'
    plt.rcParams['xtick.color'] = '#ffffff'
    plt.rcParams['ytick.color'] = '#ffffff'
    plt.rcParams['figure.facecolor'] = '#122229'
    plt.rcParams['axes.facecolor'] = '#122229'
    #plt.rcParams['savefig.facecolor']='#122229'
    """
    MAIN_WINDOW = MAIN_PROGRAM()