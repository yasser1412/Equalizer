from PyQt5 import QtWidgets, QtCore, uic, QtGui, QtPrintSupport
from pyqtgraph import PlotWidget, plot
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import *   
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from scipy import signal
from os import path
import pyqtgraph as pg
import queue as Q
import pandas as pd
import numpy as np
import sys
import os
from scipy.io.wavfile import read
from scipy import signal
from scipy.io.wavfile import read
from scipy.io.wavfile import write
import wave
from scipy.signal import firwin,freqz
import simpleaudio as sa
from scipy.fft import fft, fftfreq
from matplotlib import pyplot as plt


MAIN_WINDOW,_=loadUiType(path.join(path.dirname(__file__),"equalizer.ui"))

class MainApp(QMainWindow,MAIN_WINDOW):
    
    def __init__(self,parent=None):
        super(MainApp,self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.Toolbar()
        
    def Toolbar(self):
        #self.PlayBtn.triggered.connect(self.play_audio)
        self.OpenSignalBtn.triggered.connect(self.BrowseSignal)

    def BrowseSignal(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,"QFileDialog.getOpenFileName()", "","WAV Files (*.wav)")
        audio_file = read(fileName) 
        sampling_rate = audio_file[0] 
        audio = audio_file[1]
        audio2= audio.astype(float)
        l=len(audio)
        
        self.plotAudio(audio2,l)
        self.fft(audio2,sampling_rate,l)
        self.play_audio(fileName)
        #self.plot_spectro(audio,sampling_rate)
        
        print(audio_file[1])
        print(len(audio))

    def plotAudio(self,file,length):
        self.graphWidget.plot(file[0:length],pen="b")

    def fft(self,file,sampling_rate,length):
        n=length
        T=1/sampling_rate
        yf = fft(file)
        xf = fftfreq(n,T)
        plt.plot(xf, np.abs(yf))
        plt.grid()
        """ plt.xlable("Frequency -->")
        plt.ylable("Magnitude") """
        plt.show()
        print(n)

    def play_audio(self,file):
        wave_obj = sa.WaveObject.from_wave_file(file)
        play_obj = wave_obj.play()
        play_obj.wait_done()  # Wait until sound has finished playing    

    #def plot_spectro(self,file,sampling_rate):

        # plt.specgram(file,Fs=sampling_rate)
        # plt.xlabel('Time')
        # plt.ylabel('Frequency')
        # plt.show()
        # print("spectro")
        # #### self.graphicsView_4 is the plot widget u can change it
        
        # # Interpret image data as row-major instead of col-major
        # pyqtgraph.setConfigOptions(imageAxisOrder='col-major')
        
        # # the function that plot spectrogram of the selected signal
        # f, t, Sxx = signal.spectrogram(file,10)
        
        # # Item for displaying image data
        # img = pyqtgraph.ImageItem()
        # self.graphWidget_2.addItem(img)
        # # Add a histogram with which to control the gradient of the image
        # hist = pyqtgraph.HistogramLUTItem()
        # # Link the histogram to the image
        # hist.setImageItem(img)
        # # Fit the min and max levels of the histogram to the data available
        # hist.setLevels(np.min(Sxx), np.max(Sxx))
        # # This gradient is roughly comparable to the gradient used by Matplotlib
        # # You can adjust it and then save it using hist.gradient.saveState()
        # hist.gradient.restoreState(
        # {'mode': 'rgb','ticks': [(0.5, (0, 182, 188, 255)),(1.0, (246, 111, 0, 255)),(0.0, (75, 0, 113, 255))]})
        
        # # Sxx contains the amplitude for each pixel
        # img.setImage(Sxx)
        # # Scale the X and Y Axis to time and frequency (standard is pixels)
        # img.scale(t[-1]/np.size(Sxx, axis=1),f[-1]/np.size(Sxx, axis=0))
        # # Limit panning/zooming
        # self.graphWidget_2.setLimits(xMin=t[0], xMax=t[-1], yMin=f[0], yMax=f[-1])
        
        # self.graphWidget_2.setLabel('bottom', "Time", units='s')
        # self.graphWidget_2.setLabel('left', "Frequency", units='Hz')
        # self.graphWidget_2.plotItem.setTitle("Spectrogram")


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())


if __name__=='__main__':
    main()