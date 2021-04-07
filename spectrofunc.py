def plot_spectro(self,file):
        
        #### self.graphicsView_4 is the plot widget u can change it
        
        
        # Interpret image data as row-major instead of col-major
        pyqtgraph.setConfigOptions(imageAxisOrder='row-major')
        
        # the function that plot spectrogram of the selected signal
        f, t, Sxx = signal.spectrogram(file,10)
        
        # Item for displaying image data
        img = pyqtgraph.ImageItem()
        self.graphicsView_4.addItem(img)
        # Add a histogram with which to control the gradient of the image
        hist = pyqtgraph.HistogramLUTItem()
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
        self.graphicsView_4.setLimits(xMin=t[0], xMax=t[-1], yMin=f[0], yMax=f[-1])
        
        self.graphicsView_4.setLabel('bottom', "Time", units='s')
        self.graphicsView_4.setLabel('left', "Frequency", units='Hz')
        self.graphicsView_4.plotItem.setTitle("Spectrogram")
        
        #########old one#########
        self.check_widget
        plt.specgram(file,Fs=10)
        plt.xlabel('Time')
        plt.ylabel('Frequency')
        plt.savefig('images/spectro'+str(self.current_widget + 1)+'.png')
        self.spectroImg_list[self.current_widget] = 'images/spectro'+str(self.current_widget + 1)+'.png'
        plt.show()
