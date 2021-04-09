from PyQt5 import QtWidgets, QtCore, uic, QtGui, QtPrintSupport
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import *   
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from scipy import signal
from os import path
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
from scipy.fft import fft, fftfreq, rfft, rfftfreq
from matplotlib import pyplot as plt
import librosa



MAIN_WINDOW,_=loadUiType(path.join(path.dirname(__file__),"equalizer.ui"))

class MainApp(QMainWindow,MAIN_WINDOW):
    def __init__(self,parent=None):
        super(MainApp,self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.Toolbar()
        # self.graphWidget.plotItem.showGrid(True, True, alpha=0.8)
        #self.graphicsView.setBackground('w')

    def Toolbar(self):
        self.PlayBtn.triggered.connect(self.play_audio)
        self.OpenSignalBtn.triggered.connect(self.BrowseSignal)

    def BrowseSignal(self):
        global fileName
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,"QFileDialog.getOpenFileName()", "","WAV Files (*.wav)")
        samples, sampling_rate = librosa.load(fileName, sr=None, mono=True, offset=0.0, duration=None)
        l=len(samples)
        self.plotAudio(samples,l)
        self.fft(samples,sampling_rate,l)
        self.plot_spectro(samples,sampling_rate)
        
        print(samples)
        print(l)

    def plotAudio(self,file,length):
        self.graphWidget.plot(file[0:length],pen="b")

    def fft(self,file,sampling_rate,length):
        n=length
        T=1/sampling_rate
        yf = rfft(file)
        xf = rfftfreq(n,T)
        plt.plot(xf, np.abs(yf))
        plt.grid()
        plt.xlabel("Frequency")
        plt.ylabel("Magnitude")
        plt.show()
        print(n)

    def play_audio(self):
        wave_obj = sa.WaveObject.from_wave_file(fileName)
        play_obj = wave_obj.play()

    def plot_spectro(self,file,sampling_rate):
        # plt.specgram(file,Fs=sampling_rate)
        # plt.xlabel('Time')
        # plt.ylabel('Frequency')
        # plt.show()
        # print("spectro")

        #Interpret image data as row-major instead of col-major
        pg.setConfigOptions(imageAxisOrder='col-major')
        # the function that plot spectrogram of the selected signal
        f, t, Sxx = signal.spectrogram(file,10)

        # Item for displaying image data
        img = pg.ImageItem()
        self.graphicsView.addItem(img)
        # Add a histogram with which to control the gradient of the image
        hist = pg.HistogramLUTItem()
        # Link the histogram to the image
        hist.setImageItem(img)
        # Fit the min and max levels of the histogram to the data available
        hist.setLevels(np.min(Sxx), np.max(Sxx))
        # This gradient is roughly comparable to the gradient used by Matplotlib
        # You can adjust it and then save it using hist.gradient.saveState()
        hist.gradient.restoreState(
        {'mode': 'rgb','ticks': [(0.5, (0, 182, 188, 255)),(1.0, (246, 111, 0, 255)),(0.0, (75, 0, 113, 255))]})

        # Sxx contains the amplitude for each pixel
        img.setImage(Sxx)
        # Scale the X and Y Axis to time and frequency (standard is pixels)
        img.scale(t[-1]/np.size(Sxx, axis=1),f[-1]/np.size(Sxx, axis=0))
        # Limit panning/zooming
        self.graphicsView.setLimits(xMin=t[0], xMax=t[-1], yMin=f[0], yMax=f[-1])
        self.graphicsView.setLabel('bottom', "Time", units='s')
        self.graphicsView.setLabel('left', "Frequency", units='Hz')
        self.graphicsView.plotItem.setTitle("Spectrogram")


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())


if __name__=='__main__':
    main()