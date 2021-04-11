from PyQt5 import QtWidgets, QtCore, uic, QtGui, QtPrintSupport
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import *   
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from os import path
import queue as Q
import pandas as pd
import numpy as np
import sys
import os
from scipy import signal
from scipy.io.wavfile import read
from scipy.io.wavfile import write
import wave
from scipy.signal import firwin,freqz

#cant install this
#import simpleaudio as sa

import sounddevice as sd
from scipy.fft import fft, fftfreq, rfft, rfftfreq
from matplotlib import pyplot as plt
import librosa
from scipy.signal import butter, lfilter

MAIN_WINDOW,_=loadUiType(path.join(path.dirname(__file__),"equalizer.ui"))

class MainApp(QMainWindow,MAIN_WINDOW):
    
    RGB_Pallete1 = (0, 182, 188, 255)
    RGB_Pallete2 = (246, 111, 0, 255)
    RGB_Pallete3 = (75, 0, 113, 255)
    vSliders = []
    labels = []
    def __init__(self,parent=None):
        super(MainApp,self).__init__(parent)
        QMainWindow.__init__(self)
        
        self.setupUi(self)
        
        self.Toolbar()
        self.comboBox.currentIndexChanged.connect(self.check_palette)
        self.vSliders = [self.vSlider1,self.vSlider2,self.vSlider3,self.vSlider4,self.vSlider5,self.vSlider6,self.vSlider7,self.vSlider8,self.vSlider9,self.vSlider10]
        self.labels = [self.label,self.label_2,self.label_3,self.label_4,self.label_5,self.label_6,self.label_7,self.label_8,self.label_9,self.label_10]
        self.spectroSlider1.valueChanged.connect(self.setMin_Max)
        self.spectroSlider2.valueChanged.connect(self.setMin_Max)
        for i in range(10):
            self.vSliders[i].valueChanged.connect(self.slidersGains)  
        
        # self.beforeWidget.plotItem.showGrid(True, True, alpha=0.8)
        #self.spectroWidget.setBackground('w')
        


    def Toolbar(self):
        self.PlayBtn.triggered.connect(self.play_audio)
        self.OpenSignalBtn.triggered.connect(self.BrowseSignal)

    def BrowseSignal(self):
        global fileName , samples , sampling_rate , T 
        
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,"QFileDialog.getOpenFileName()", "","WAV Files (*.wav)")
        
        samples, sampling_rate = librosa.load(fileName, sr=None, mono=True, offset=0.0, duration=None)
        l=len(samples)
        T = int(l / sampling_rate)
        
        self.plotBefore(samples,sampling_rate,l)
        self.plot_spectro(samples[:T*sampling_rate],sampling_rate)
        
        #print(samples)
        #print(l)

    def plotBefore(self,file,sampling_rate,length):
        n=length
        T=1/sampling_rate
        yf = rfft(file)
        xf = rfftfreq(n,T)
        
        self.beforeWidget.clear()
        self.beforeWidget.plot(xf, np.abs(yf),pen="r")
        #self.beforeWidget.plot(file[0:length],pen="r")
        self.beforeWidget.setLabel('bottom', "Frequency", units='Hz')
        #self.beforeWidget.setLabel('bottom', "Time", units='s')
        self.beforeWidget.setLabel('left', "Magnitude")
        #self.beforeWidget.setLabel('left', "Amplitude")
        self.beforeWidget.plotItem.setTitle("Before")

    def plotAfter(self,file,sampling_rate,length):
        n=length
        T=1/sampling_rate
        yf = rfft(file)
        xf = rfftfreq(n,T)
        
        self.afterWidget.clear()
        self.afterWidget.plot(xf, np.abs(yf),pen="b")
        #self.afterWidget.plot(file[0:length],pen="b")
        self.afterWidget.setLabel('bottom', "Frequency", units='Hz')
        #self.afterWidget.setLabel('bottom', "Time", units='s')
        self.afterWidget.setLabel('left', "Magnitude")
        #self.afterWidget.setLabel('left', "Amplitude")
        self.afterWidget.plotItem.setTitle("After")
        
        sd.play(file, sampling_rate)

    
    def play_audio(self):
        sd.play(samples, sampling_rate)

    def plot_spectro(self,file , fs):
        #self.check_palette
        #### self.spectroWidget is the plot widget u can change it
        self.spectroWidget.clear()
        # Interpret image data as row-major instead of col-major
        pg.setConfigOptions(imageAxisOrder='row-major')
        
        # the function that plot spectrogram of the selected signal
        f, t, Sxx = signal.spectrogram(file,fs)
        
        # Item for displaying image data
        img = pg.ImageItem()
        self.spectroWidget.addItem(img)
        # Add a histogram with which to control the gradient of the image
        hist = pg.HistogramLUTItem()
        # Link the histogram to the image
        hist.setImageItem(img)
        # Fit the min and max levels of the histogram to the data available
        hist.setLevels(min = np.min(Sxx) , max = np.max(Sxx))
        # This gradient is roughly comparable to the gradient used by Matplotlib
        # You can adjust it and then save it using hist.gradient.saveState()
        hist.gradient.restoreState(
        {'mode': 'rgb','ticks': [(0.5, self.RGB_Pallete1),(1.0, self.RGB_Pallete2),(0.0, self.RGB_Pallete3)]})
        
        # Sxx contains the amplitude for each pixel
        img.setImage(Sxx)
        # Scale the X and Y Axis to time and frequency (standard is pixels)
        img.scale(t[-1]/np.size(Sxx, axis=1),f[-1]/np.size(Sxx, axis=0))
        # Limit panning/zooming
        self.spectroWidget.setLimits(xMin=t[0], xMax=t[-1], yMin=f[0], yMax=f[-1])
        self.spectroWidget.setYRange(np.min(f),np.max(f)-100)
        self.spectroWidget.setLabel('bottom', "Time", units='s')
        self.spectroWidget.setLabel('left', "Frequency", units='Hz')
        self.spectroWidget.plotItem.setTitle("Spectrogram")
    
    def setMin_Max(self):
        pass
    
    def slidersGains(self):

        gainArray = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        for i in range(10):
            gainArray[i] = (self.vSliders[i].value())
            
        print(gainArray)
        
        self.processing(*gainArray)

    
    def check_palette(self):
        
        if self.comboBox.currentText() == "Default":
            self.RGB_Pallete1 = (0, 182, 188, 255)
            self.RGB_Pallete2 = (246, 111, 0, 255)
            self.RGB_Pallete3 = (75, 0, 113, 255)
            self.plot_spectro(samples[:T*sampling_rate],sampling_rate)
            
        if self.comboBox.currentText() == "Palette1":
            self.RGB_Pallete1 = (108, 79, 60, 255)
            self.RGB_Pallete2 = (100, 83, 148, 255)
            self.RGB_Pallete3 = (0, 166, 140, 255)
            self.plot_spectro(samples[:T*sampling_rate],sampling_rate)
            
        if self.comboBox.currentText() == "Palette2":
            self.RGB_Pallete1 = (191, 216, 51, 255)
            self.RGB_Pallete2 = (188, 108, 167, 255)
            self.RGB_Pallete3 = (235, 225, 223, 255)
            self.plot_spectro(samples[:T*sampling_rate],sampling_rate)
            
        if self.comboBox.currentText() == "Palette3":
            self.RGB_Pallete1 = (219, 178, 209, 255)
            self.RGB_Pallete2 = (147, 71, 66, 255)
            self.RGB_Pallete3 = (108, 160, 220, 255)
            self.plot_spectro(samples[:T*sampling_rate],sampling_rate)
            
        if self.comboBox.currentText() == "Palette4":
            self.RGB_Pallete1 = (236, 219, 83, 255)
            self.RGB_Pallete2 = (227, 65, 50, 255)
            self.RGB_Pallete3 = (219, 178, 209, 255)
            self.plot_spectro(samples[:T*sampling_rate],sampling_rate)

    def processing(self,gain1,gain2,gain3,gain4,gain5,gain6,gain7,gain8,gain9,gain10):
        freq = np.arange(sampling_rate * 0.5)
        size = len(freq) / 10
        
        self.labels[0].setText(str(freq[21])+"-"+str(freq[int(size)]))
        for i in range(8):
            self.labels[i+1].setText(str(freq[(i+1)*int(size)])+"-"+str(freq[(i+2)*int(size)]))
        self.labels[9].setText(str(freq[9 * int(size)])+"-"+str(freq[-1]))
        
        band1 = self.create_band(freq[21], freq[int(size)]) * gain1
        band2 = self.create_band(freq[int(size)], freq[2 * int(size)]) * gain2
        band3 = self.create_band(freq[2 * int(size)], freq[3 * int(size)]) * gain3
        band4 = self.create_band(freq[3 * int(size)], freq[4 * int(size)]) * gain4
        band5 = self.create_band(freq[4 * int(size)], freq[5 * int(size)]) * gain5
        band6 = self.create_band(freq[5 * int(size)], freq[6 * int(size)]) * gain6
        band7 = self.create_band(freq[6 * int(size)], freq[7 * int(size)]) * gain7
        band8 = self.create_band(freq[7 * int(size)], freq[8 * int(size)]) * gain8
        band9 = self.create_band(freq[8 * int(size)], freq[9 * int(size)]) * gain9
        band10 = self.create_band(freq[9 * int(size)], freq[-1], order=3) * gain10
        
        samples_after = band1 + band2 + band3 + band4 + band5 + band6 + band7 + band8 + band9 + band10
        l_after = len(samples_after)
        
        self.plotAfter(samples_after,sampling_rate,l_after)
        self.plot_spectro(samples_after[:T*sampling_rate],sampling_rate)

    def create_band(self, lowcut, highcut, order=4):
        nyquistfreq = 0.5 * sampling_rate
        
        low = lowcut / nyquistfreq
        high = highcut / nyquistfreq
        
        b, a = butter(order, [low, high], btype='band', analog=False)
        
        filtered = lfilter(b, a, samples)
        return filtered



if __name__=='__main__':
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
