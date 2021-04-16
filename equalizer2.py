from PyQt5 import QtWidgets, QtCore, uic, QtGui, QtPrintSupport
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import *   
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from os import path
import scipy.fft
import queue as Q
import pandas as pd
import numpy as np
import sys
import os
import pyqtgraph.exporters
from scipy import signal
from scipy.io.wavfile import read
from scipy.io.wavfile import write
import wave
from scipy.signal import firwin,freqz
import math
#cant install this
#import simpleaudio as sa

from fpdf import FPDF
import sounddevice as sd
from scipy.fft import fft, fftfreq, rfft, rfftfreq
from matplotlib import pyplot as plt
import librosa
from scipy.signal import butter, lfilter

MAIN_WINDOW,_=loadUiType(path.join(path.dirname(__file__),"equalizer.ui"))

class MainApp(QMainWindow,MAIN_WINDOW):
    ##default color pallete
    RGB_Pallete1 = (0, 182, 188, 255)
    RGB_Pallete2 = (246, 111, 0, 255)
    RGB_Pallete3 = (75, 0, 113, 255)
    
    ## min , max pixel intensity
    min_list = [0.0,0.0,0.0]
    max_list = [1.0,1.0,1.0]
    
    vSliders = []
    
    labels = []
    
    gainArrays = []
    
    beforWidget_list = []
    afterWidger_list = []
    spectroWidget_list = []
    
    comboBox_list = []
    
    samples_list = [None,None,None]
    sampling_rate_list = [None,None,None]
    T_list = [None,None,None]
    dataLength_list = [None,None,None]
    
    graph_rangeMin = [0,0,0]
    graph_rangeMax = [1000,1000,1000]
    
    current_samples = []
    
    ##for graph speed
    step = 10
    
    def __init__(self,parent=None):
        super(MainApp,self).__init__(parent)
        QMainWindow.__init__(self)
        
        self.setupUi(self)
        
        ## lists of everything
        self.comboBox_list = [self.comboBox , self.comboBox_2 , self.comboBox_3]
        
        self.beforeWidget_list = [self.beforeWidget , self.beforeWidget_2 , self.beforeWidget_3]
        
        self.afterWidget_list = [self.afterWidget , self.afterWidget_2 , self.afterWidget_3]
        
        self.spectroWidget_list = [self.spectroWidget , self.spectroWidget_2 , self.spectroWidget_3]
        
        self.spectroSlider1_list = [self.spectroSlider1, self.spectroSlider1_2, self.spectroSlider1_3]
        self.spectroSlider2_list = [self.spectroSlider2, self.spectroSlider2_2, self.spectroSlider2_3]
        
        self.vSliders = [[self.vSlider1,self.vSlider2,self.vSlider3,self.vSlider4,self.vSlider5,self.vSlider6,self.vSlider7,self.vSlider8,self.vSlider9,self.vSlider10]
                        ,[self.vSlider1_2,self.vSlider2_2,self.vSlider3_2,self.vSlider4_2,self.vSlider5_2,self.vSlider6_2,self.vSlider7_2,self.vSlider8_2,self.vSlider9_2,self.vSlider10_2]
                        ,[self.vSlider1_3,self.vSlider2_3,self.vSlider3_3,self.vSlider4_3,self.vSlider5_3,self.vSlider6_3,self.vSlider7_3,self.vSlider8_3,self.vSlider9_3,self.vSlider10_3]]
        
        self.labels = [self.label,self.label_2,self.label_3,self.label_4,self.label_5,self.label_6,self.label_7,self.label_8,self.label_9,self.label_10]
        
        self.connect_func()
        
    def connect_func(self):
        ##connectng each button by its function
        
        self.playBtn.triggered.connect(self.start)
        self.OpenSignalBtn.triggered.connect(self.BrowseSignal)
        self.saveBtn.triggered.connect(self.export)
        self.pauseBtn.triggered.connect(self.pause)
        self.stopBtn.triggered.connect(self.stop)
        self.zoomInBtn.triggered.connect(self.zoom_in)
        self.zoomOutBtn.triggered.connect(self.zoom_out)
        self.leftBtn.triggered.connect(self.move_left)
        self.rightBtn.triggered.connect(self.move_right)
        self.speedBtn.triggered.connect(self.speedUp)
        self.slowBtn.triggered.connect(self.speedDown)
        self.spectroSliderLabel1.setText("0.0")
        self.spectroSliderLabel2.setText("1.0")
        
        for i in range(3):
            self.spectroSlider1_list[i].valueChanged.connect(self.setMin_Max)
            self.spectroSlider2_list[i].valueChanged.connect(self.setMin_Max)
            
            self.comboBox_list[i].currentIndexChanged.connect(self.check_pallete)
            
            temp = self.vSliders[i]
            for x in range(10):
                temp[x].valueChanged.connect(self.slidersGains) 

    def BrowseSignal(self):
        ##browse audio file
        
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,"QFileDialog.getOpenFileName()", "","WAV Files (*.wav)")
        
        ##read the audio file and store it in samples and sampling rate lists
        self.samples_list[self.tabWidget.currentIndex()], self.sampling_rate_list[self.tabWidget.currentIndex()] = librosa.load(fileName, sr=None, mono=True, offset=0.0, duration=None)
        samples = self.samples_list[self.tabWidget.currentIndex()]
        self.current_samples = samples
        sampling_rate = self.sampling_rate_list[self.tabWidget.currentIndex()]
        ## store length and time on their lists
        l=len(samples)
        self.T_list[self.tabWidget.currentIndex()] = int(l / sampling_rate)
        T = self.T_list[self.tabWidget.currentIndex()]
        self.dataLength_list[self.tabWidget.currentIndex()] = l
        
        ##plot spectro and audio before equalizing
        self.plot_spectro(samples[:T*sampling_rate],sampling_rate)
        self.plotBefore(samples,sampling_rate,l)
        ##save a pic of spectro before equalizing
        exporter = pg.exporters.ImageExporter(self.spectroWidget_list[self.tabWidget.currentIndex()].plotItem)
        exporter.export('spectroBefore'+str(self.tabWidget.currentIndex()+1)+'.png')
        

    def plotBefore(self,file,sampling_rate,length):
        ##plot before equalizing
        global n,yf
        n=length
        T=1/sampling_rate
        yf = fft(file)
        #xf = fftfreq(n,T)
        #print(n,T,yf,xf)
        # phase = np.angle(file)
        # print(phase)

        self.beforeWidget_list[self.tabWidget.currentIndex()].clear()
        
        #self.beforeWidget_list[self.tabWidget.currentIndex()].plot(xf, np.abs(yf),pen="r")
        self.beforeWidget_list[self.tabWidget.currentIndex()].plot(file[0:sampling_rate],pen="r")
        #self.beforeWidget_list[self.tabWidget.currentIndex()].setLabel('bottom', "Frequency", units='Hz')
        self.beforeWidget_list[self.tabWidget.currentIndex()].setLabel('bottom', "Time", units='s')
        #self.beforeWidget_list[self.tabWidget.currentIndex()].setLabel('left', "Magnitude")
        self.beforeWidget_list[self.tabWidget.currentIndex()].setLabel('left', "Amplitude")
        
        self.beforeWidget_list[self.tabWidget.currentIndex()].setLimits(xMin = 0, xMax=xf[-1])
        self.beforeWidget_list[self.tabWidget.currentIndex()].plotItem.setTitle("Before")
        self.beforeWidget_list[self.tabWidget.currentIndex()].enableAutoRange(axis='y')

    def plotAfter(self,file,sampling_rate,length):
        ##plot after equalizing
        
        # n=length
        #T=1/sampling_rate
        # yf = rfft(file)
        #xf = fftfreq(n,T)
        
        self.afterWidget_list[self.tabWidget.currentIndex()].clear()
        
        #self.afterWidget_list[self.tabWidget.currentIndex()].plot(xf, np.abs(yf),pen="b")
        self.afterWidget_list[self.tabWidget.currentIndex()].plot(file[0:sampling_rate],pen="b")
        #self.afterWidget_list[self.tabWidget.currentIndex()].setLabel('bottom', "Frequency", units='Hz')
        self.afterWidget_list[self.tabWidget.currentIndex()].setLabel('bottom', "Time", units='s')
        #self.afterWidget_list[self.tabWidget.currentIndex()].setLabel('left', "Magnitude")
        self.afterWidget_list[self.tabWidget.currentIndex()].setLabel('left', "Amplitude")
        
        self.afterWidget_list[self.tabWidget.currentIndex()].setLimits(xMin = 0, xMax=xf[-1])
        self.afterWidget_list[self.tabWidget.currentIndex()].plotItem.setTitle("After")
        self.afterWidget_list[self.tabWidget.currentIndex()].enableAutoRange(axis = "y")
        sd.play(file, sampling_rate)

    def play_audio(self):
        sd.play(self.samples_list[self.tabWidget.currentIndex()], self.sampling_rate_list[self.tabWidget.currentIndex()])

    def plot_spectro(self,file , fs):
        #### self.spectroWidget is the plot widget u can change it
        self.spectroWidget_list[self.tabWidget.currentIndex()].clear()
        # Interpret image data as row-major instead of col-major
        pg.setConfigOptions(imageAxisOrder='row-major')
        
        # the function that plot spectrogram of the selected signal
        f, t, Sxx = signal.spectrogram(file,fs)
        
        # Item for displaying image data
        img = pg.ImageItem()
        self.spectroWidget_list[self.tabWidget.currentIndex()].addItem(img)
        # Add a histogram with which to control the gradient of the image
        hist = pg.HistogramLUTItem()
        # Link the histogram to the image
        hist.setImageItem(img)
        # Fit the min and max levels of the histogram to the data available
        hist.setLevels(min = np.min(Sxx) , max = np.max(Sxx))
        # This gradient is roughly comparable to the gradient used by Matplotlib
        # You can adjust it and then save it using hist.gradient.saveState()
        hist.gradient.restoreState(
        {'mode': 'rgb','ticks': [(0.5, self.RGB_Pallete1)
                                ,(self.max_list[self.tabWidget.currentIndex()], self.RGB_Pallete2)
                                ,(self.min_list[self.tabWidget.currentIndex()], self.RGB_Pallete3)]})
        
        # Sxx contains the amplitude for each pixel
        img.setImage(Sxx)
        # Scale the X and Y Axis to time and frequency (standard is pixels)
        img.scale(t[-1]/np.size(Sxx, axis=1),f[-1]/np.size(Sxx, axis=0))
        # Limit panning/zooming
        self.spectroWidget_list[self.tabWidget.currentIndex()].setLimits(xMin=t[0], xMax=t[-1], yMin=f[0], yMax=f[-1])
        #self.spectroWidget_list[self.tabWidget.currentIndex()].setYRange(np.min(f),np.max(f)-100)
        self.spectroWidget_list[self.tabWidget.currentIndex()].setLabel('bottom', "Time", units='s')
        self.spectroWidget_list[self.tabWidget.currentIndex()].setLabel('left', "Frequency", units='Hz')
        self.spectroWidget_list[self.tabWidget.currentIndex()].plotItem.setTitle("Spectrogram")
    
    def setMin_Max(self):
        samples = self.current_samples
        sampling_rate = self.sampling_rate_list[self.tabWidget.currentIndex()]
        T = self.T_list[self.tabWidget.currentIndex()]
        
        self.min_list[self.tabWidget.currentIndex()] = self.spectroSlider1_list[self.tabWidget.currentIndex()].value()/10
        self.max_list[self.tabWidget.currentIndex()] = self.spectroSlider2_list[self.tabWidget.currentIndex()].value()/10
        
        self.spectroSliderLabel1.setText(str(self.min_list[0]))
        self.spectroSliderLabel2.setText(str(self.max_list[0]))
        
        self.plot_spectro(samples[:T*sampling_rate],sampling_rate)
    
    def slidersGains(self):
        ##check sliders gains
        
        gainArray1 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        gainArray2 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        gainArray3 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        
        self.gainArrays = [gainArray1,gainArray2,gainArray3]
        
        tempgainArray = []
        temp = self.vSliders[self.tabWidget.currentIndex()]
        
        for i in range(10):
            tempgainArray.append(temp[i].value())
            
        self.gainArrays[self.tabWidget.currentIndex()] = tempgainArray
        #print(self.gainArrays[self.tabWidget.currentIndex()])
        
        self.processing(*self.gainArrays[self.tabWidget.currentIndex()])

    def check_pallete(self):
        ##to change color pallete of spectro
        
        samples = self.current_samples
        sampling_rate = self.sampling_rate_list[self.tabWidget.currentIndex()]
        T = self.T_list[self.tabWidget.currentIndex()]
        
        ##setting new values of rgb for each combobox option
        if self.comboBox_list[self.tabWidget.currentIndex()].currentText() == "Default":
            self.RGB_Pallete1 = (0, 182, 188, 255)
            self.RGB_Pallete2 = (246, 111, 0, 255)
            self.RGB_Pallete3 = (75, 0, 113, 255)
            self.plot_spectro(samples[:T*sampling_rate],sampling_rate)
            
        if self.comboBox_list[self.tabWidget.currentIndex()].currentText() == "Palette1":
            self.RGB_Pallete1 = (108, 79, 60, 255)
            self.RGB_Pallete2 = (100, 83, 148, 255)
            self.RGB_Pallete3 = (0, 166, 140, 255)
            self.plot_spectro(samples[:T*sampling_rate],sampling_rate)
            
        if self.comboBox_list[self.tabWidget.currentIndex()].currentText() == "Palette2":
            self.RGB_Pallete1 = (0, 255, 0, 255)
            self.RGB_Pallete2 = (255, 0, 0, 255)
            self.RGB_Pallete3 = (0, 0, 255, 255)
            self.plot_spectro(samples[:T*sampling_rate],sampling_rate)
            
        if self.comboBox_list[self.tabWidget.currentIndex()].currentText() == "Palette3":
            self.RGB_Pallete1 = (219, 178, 209, 255)
            self.RGB_Pallete2 = (147, 71, 66, 255)
            self.RGB_Pallete3 = (108, 160, 220, 255)
            self.plot_spectro(samples[:T*sampling_rate],sampling_rate)
            
        if self.comboBox_list[self.tabWidget.currentIndex()].currentText() == "Palette4":
            self.RGB_Pallete1 = (236, 219, 83, 255)
            self.RGB_Pallete2 = (227, 65, 50, 255)
            self.RGB_Pallete3 = (219, 178, 209, 255)
            self.plot_spectro(samples[:T*sampling_rate],sampling_rate)

    def processing(self,gain1,gain2,gain3,gain4,gain5,gain6,gain7,gain8,gain9,gain10):
        ## multiplay the gain of sliders to the audio list
        
        sampling_rate = self.sampling_rate_list[self.tabWidget.currentIndex()]
        T = self.T_list[self.tabWidget.currentIndex()]
        freq = np.arange(sampling_rate * 0.5)
        size = len(freq) / 10
        
        ## setting the ranges of hz that changing for each slider
        self.labels[0].setText(str(freq[21])+"-"+str(freq[int(size)]))
        for i in range(8):
            self.labels[i+1].setText(str(freq[(i+1)*int(size)])+"-"+str(freq[(i+2)*int(size)]))
        self.labels[9].setText(str(freq[9 * int(size)])+"-"+str(freq[-1]))
        
        eq_range = int(n/10)
        band1=[]
        band2=[]
        band3=[]
        band4=[]
        band5=[]
        band6=[]
        band7=[]
        band8=[]
        band9=[]
        band10=[]
        ##cutting audio list into bands and multiplay it by sliders gain
        i=0
        for i in range(eq_range):
            band1.append(yf[i]*gain1)
        for i in range(2*eq_range):
            band2.append(yf[i]*gain2)
        for i in range(3*eq_range):
            band3.append(yf[i]*gain3)
        for i in range(4*eq_range):
            band4.append(yf[i]*gain4)
        for i in range(5*eq_range):
            band5.append(yf[i]*gain5)
        for i in range(6*eq_range):
            band6.append(yf[i]*gain6)
        for i in range(7*eq_range):
            band7.append(yf[i]*gain7)
        for i in range(8*eq_range):
            band8.append(yf[i]*gain8)
        for i in range(9*eq_range):
            band9.append(yf[i]*gain9)
        for i in range(10*eq_range):
            band10.append(yf[i]*gain10)
        # band1 = self.create_band(freq[21], freq[int(size)]) * gain1
        # band2 = self.create_band(freq[int(size)], freq[2 * int(size)]) * gain2
        # band3 = self.create_band(freq[2 * int(size)], freq[3 * int(size)]) * gain3
        # band4 = self.create_band(freq[3 * int(size)], freq[4 * int(size)]) * gain4
        # band5 = self.create_band(freq[4 * int(size)], freq[5 * int(size)]) * gain5
        # band6 = self.create_band(freq[5 * int(size)], freq[6 * int(size)]) * gain6
        # band7 = self.create_band(freq[6 * int(size)], freq[7 * int(size)]) * gain7
        # band8 = self.create_band(freq[7 * int(size)], freq[8 * int(size)]) * gain8
        # band9 = self.create_band(freq[8 * int(size)], freq[9 * int(size)]) * gain9
        # band10 = self.create_band(freq[9 * int(size)], freq[-1], order=3) * gain10
        
        samples_after = band1 + band2 + band3 + band4 + band5 + band6 + band7 + band8 + band9 + band10
        l_after = len(samples_after)
        print(l_after,samples_after)
        phase=np.angle(samples_after)
        print(phase)
        after_=[]
        for i in range(l_after):
            after_[i]=samples_after[i]*(math.cos(phase)+1*j*math.sin(phase))
        after=np.real(scipy.fft.ifft(after_))
        print(after)
        self.current_samples = after
        
        self.plotAfter(after,sampling_rate,l_after)
        self.plot_spectro(samples_after[:T*sampling_rate],sampling_rate)

    def create_band(self, lowcut, highcut, order=4):
        #a function for band filtering
        
        samples = self.samples_list[self.tabWidget.currentIndex()]
        sampling_rate = self.sampling_rate_list[self.tabWidget.currentIndex()]
        
        nyquistfreq = 0.5 * sampling_rate
        
        low = lowcut / nyquistfreq
        high = highcut / nyquistfreq
        
        b, a = butter(order, [low, high], btype='band', analog=False)
        
        filtered = lfilter(b, a, samples)
        return filtered

    def speedUp(self):
        if self.step <= 100 :
            self.step +=5
        else:
            pass
    def speedDown(self):
        if self.step >= 0:
            self.step -=5
        else:
            pass

    def start(self):
        # the function that makes the graph starts to move
        self.isPaused = False
        self.isStoped = False
        data_length = self.dataLength_list[self.tabWidget.currentIndex()]
        self.play_audio()
        for x in range(0, data_length, self.step):
            #increasing the x-axis range by x
            self.beforeWidget_list[self.tabWidget.currentIndex()].setXRange(self.graph_rangeMin[self.tabWidget.currentIndex()] + x, self.graph_rangeMax[self.tabWidget.currentIndex()] + x)
            self.afterWidget_list[self.tabWidget.currentIndex()].setXRange(self.graph_rangeMin[self.tabWidget.currentIndex()] + x, self.graph_rangeMax[self.tabWidget.currentIndex()] + x)
            QtWidgets.QApplication.processEvents()

            if self.isPaused == True:
                #saving the new x-axis ranges
                self.graph_rangeMin[self.tabWidget.currentIndex()] += x
                self.graph_rangeMax[self.tabWidget.currentIndex()] += x
                break
            if self.isStoped == True:
                break

    def pause(self):
        self.isPaused = True
    
    def stop(self):
        #the function that stops the graph
        
        self.isStoped = True
        # reset the graph ranges
        self.beforeWidget_list[self.tabWidget.currentIndex()].enableAutoRange(axis = "x")
        self.afterWidget_list[self.tabWidget.currentIndex()].enableAutoRange(axis = "x")
        self.graph_rangeMin[self.tabWidget.currentIndex()] = 0
        self.graph_rangeMax[self.tabWidget.currentIndex()] = 1000
        
    def zoom_in(self):
        ##zooming in by changing x-axis scale
        self.beforeWidget_list[self.tabWidget.currentIndex()].plotItem.getViewBox().scaleBy(x = 0.5, y = 1)
        self.afterWidget_list[self.tabWidget.currentIndex()].plotItem.getViewBox().scaleBy(x = 0.5, y = 1)
    
    def zoom_out(self):
        ##zooming out by changing x-axis scale
        self.beforeWidget_list[self.tabWidget.currentIndex()].plotItem.getViewBox().scaleBy(x = 2, y = 1)
        self.afterWidget_list[self.tabWidget.currentIndex()].plotItem.getViewBox().scaleBy(x = 2, y = 1)
    
    def move_right(self):
        self.afterWidget_list[self.tabWidget.currentIndex()].plotItem.getViewBox().translateBy(x = 100)
        self.beforeWidget_list[self.tabWidget.currentIndex()].plotItem.getViewBox().translateBy(x = 100)
        
    def move_left(self):
        self.afterWidget_list[self.tabWidget.currentIndex()].plotItem.getViewBox().translateBy(x = -100)
        self.beforeWidget_list[self.tabWidget.currentIndex()].plotItem.getViewBox().translateBy(x = -100) 

    def export(self):
        ##create the pdf
        
        self.stop()
        
        ##pdf function
        pdf = FPDF()
        
        ## before equalizing Page
        pdf.add_page()
        ## set pdf title
        pdf.set_font('Arial', 'B', 15)
        pdf.cell(70)
        pdf.cell(60, 10, 'Equalizer Report', 1, 0, 'C')
        pdf.ln(20)
        
        ##take pics of drwan graphs
        exporter1 = pg.exporters.ImageExporter(self.spectroWidget_list[self.tabWidget.currentIndex()].plotItem)
        exporter1.export('spectroAfter.png')
        exporter2 = pg.exporters.ImageExporter(self.beforeWidget_list[self.tabWidget.currentIndex()].plotItem)
        exporter2.export('before.png')
        exporter3 = pg.exporters.ImageExporter(self.afterWidget_list[self.tabWidget.currentIndex()].plotItem)
        exporter3.export('after.png')
        
        ## put before equalizing graph
        pdf.image('before.png', 10, 50, 190, 50)
        os.remove('before.png')
        pdf.image("spectroBefore"+str(self.tabWidget.currentIndex()+1)+".png", 10, 140, 190, 100)
        os.remove("spectroBefore"+str(self.tabWidget.currentIndex()+1)+".png")
        
        ## After equalizing Page
        pdf.add_page()
        ## write the gains of the equalizer
        pdf.set_font('Arial', 'B', 15)
        pdf.cell(90)
        pdf.cell(60, 10, "Gains")
        pdf.ln(10)
        pdf.cell(70)
        pdf.cell(60, 10, str(self.gainArrays[self.tabWidget.currentIndex()]))
        ## put after equalizing graphs
        pdf.image('after.png', 10, 50, 190, 50)
        os.remove('after.png')
        pdf.image("spectroAfter.png", 10, 140, 190, 100)
        os.remove("spectroAfter.png")
        
        ## export Pdf file
        pdf.output("report"+str(self.tabWidget.currentIndex()+1)+".pdf", "F") 
        
        print("Report PDF is ready")

if __name__=='__main__':
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())