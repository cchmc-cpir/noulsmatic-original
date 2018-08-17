#!/usr/bin/env python

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from mainwidget import Ui_MainWidget
import datafetcher as df
import multiprocessing as mp 
import time

# Version
VERSION_STRING = "1.0"

class DataMonitoringWindow(QtGui.QWidget):
    def __init__(self):
        # Setup UI 
        QtGui.QWidget.__init__(self)
        self.ui = Ui_MainWidget()
        self.ui.setupUi(self)
        self.setWindowTitle("CPIR Animal Monitor v" + VERSION_STRING)
        
        # CONSTANTS
        self.MIN_DATA_FETCH_PERIOD = 0.0005
        self.MIN_PLOT_UPDATE_PERIOD = 0.25 # A little more than 60Hz
        self.PLOT_TIME_RANGE = 6 # Total seconds of display
        self.QUEUE_SIZE = int(round(self.PLOT_TIME_RANGE/self.MIN_DATA_FETCH_PERIOD))
        self.TIME_SHIFT_PCT = 0.75
        self.TEXT_UPDATE_PERIOD = 1
        self.NEXT_TEXT_UPDATE = 1
        self.SLOW_UPDATE_PERIOD = 5
        self.NEXT_SLOW_UPDATE = 1 

        self.canulaPressureSlope=1;
        self.canulaPressureIntercept=0;

        # Create data fetching process
        self.dataFetcher = df.TimedDataFetcher(self.MIN_DATA_FETCH_PERIOD)
                
        # Setup queues for plotting data as all NaNs
        self.time_queue = np.zeros(self.QUEUE_SIZE)
        self.canula_queue = np.zeros(self.QUEUE_SIZE)
        #self.trigger_queue=np.zeros(self.QUEUE_SIZE)
        # Setup for slow plot data
        self.slow_time_queue = []
        self.slow_minPressure_queue = []
        self.slow_maxPressure_queue = []
        # self.slow_tidalVolume_queue = []
        
        self.ui.fastUpdatePeriod.valueChanged.connect(self.updatePlotTimeRange)
        self.ui.slowUpdatePeriod.valueChanged.connect(self.updateSlowPlotRefreshRate)
        
        # Initialize graphs
        self.ui.pressurePlot.setMouseEnabled(x=False, y=True)
        self.ui.pressurePlot.enableAutoRange(x=False,y=True)
        self.ui.pressurePlot.setLabel('left', "Canula Pressure", units='cmH20')
        self.ui.pressurePlot.getAxis('left').enableAutoSIPrefix(False)
        self.ui.pressurePlot.setLabel('bottom', "Time", units='sec')
        self.minXlim = 0
        self.updatePlotTimeRange()
        self.updateSlowPlotRefreshRate()
        self.maxXlim = self.minXlim + self.PLOT_TIME_RANGE
        self.ui.pressurePlot.setXRange(0,self.PLOT_TIME_RANGE,padding=0)
            
        # Initialize pressure line
        self.pressureLine = pg.PlotCurveItem(x=[],y=[], \
           pen=pg.mkPen({'color': "0FF"}),antialias=True)
        self.ui.pressurePlot.addItem(self.pressureLine)     
        
        # Initialize Min and Max pressure axis
        self.pressureSlowPlot = self.ui.vitalsPlot.plotItem
        self.pressureSlowPlot.getAxis('left').setLabel("Canula Pressure", units='cmH20')
        self.pressureSlowPlot.getAxis('left').enableAutoSIPrefix(False)
        #self.pressureSlowPlot.showAxis('right')
                
        # Add empty lines
        self.minPressureLine = pg.PlotCurveItem(x=[],y=[], \
           pen=pg.mkPen({'color': "FFF"}),antialias=True)
        self.maxPressureLine = pg.PlotCurveItem(x=[],y=[], \
           pen=pg.mkPen({'color': "FFF"}),antialias=True)
        self.pressureSlowPlot.addItem(self.minPressureLine)
        self.pressureSlowPlot.addItem(self.maxPressureLine)
       
        # Setup dynamic plotting process
        self.isGraphing = False
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.updateUI) 
        self.timer.start(self.MIN_PLOT_UPDATE_PERIOD)

    def updateSlowPlotRefreshRate(self):
       self.NEXT_SLOW_UPDATE = self.NEXT_SLOW_UPDATE-self.SLOW_UPDATE_PERIOD+self.ui.slowUpdatePeriod.value()
       self.SLOW_UPDATE_PERIOD = self.ui.slowUpdatePeriod.value()

    def updatePlotTimeRange(self):
        self.PLOT_TIME_RANGE =  self.ui.fastUpdatePeriod.value()
        
        # Update plotting size
        old_queue_size = self.QUEUE_SIZE
        new_queue_size = int(round(2*self.PLOT_TIME_RANGE/self.MIN_DATA_FETCH_PERIOD))
        copySize = min(old_queue_size, new_queue_size)
                
        new_time_queue = np.zeros(new_queue_size)
        new_canula_queue = np.zeros(new_queue_size)
    
        new_time_queue[0:(copySize-1)] = self.time_queue[0:(copySize-1)] 
        new_canula_queue[0:(copySize-1)] = self.canula_queue[0:(copySize-1)]  
     
        self.time_queue = new_time_queue
        self.canula_queue = new_canula_queue

        # Update buffer size
        self.QUEUE_SIZE = new_queue_size
        
        # Update axes
        self.maxXlim = self.minXlim + self.PLOT_TIME_RANGE
        self.ui.pressurePlot.setXRange(self.minXlim,self.maxXlim,padding=0)

    def startGraphing(self):
        if (not self.isGraphing):
            self.isGraphing = True
            self.start_time = time.time() 
            self.dataFetcher.newStartTime(self.start_time)
            self.dataFetcher.startFetching() 
            self.timer.start(5)
        self.isGraphing = False             


    def stopGraphing(self):
        if self.isGraphing:
            self.dataFetcher.stopFetching()
            self.isGraphing = False
            self.startTime = []
            self.timer.stop()
              
    def updateUI(self):
        
        elapsed_time = time.time() - self.start_time

        # Under lock, find how much data we have to read
        self.dataFetcher.indexLock.acquire()
        nDataToRead = np.int32(self.dataFetcher.sync_bufferLength.value);

        lastIdx = self.dataFetcher.sync_bufferEndIdx.value
        endRead = lastIdx + 1
        if(self.dataFetcher.sync_bufferFull.value):
          startRead = 0
        else:
          startRead = self.dataFetcher.sync_bufferStartIdx.value
        stopReading = min(startRead+nDataToRead,self.dataFetcher.BUFFERSIZE)
        self.dataFetcher.indexLock.release()

        # We can now copy from the buffer safely.
        if(nDataToRead > 0):
          copyIdx = 0
          for i in range(startRead,stopReading): 
              self.time_queue[copyIdx] = self.dataFetcher.sync_time_buf[i]
              self.canula_queue[copyIdx] = self.canulaPressureSlope*self.dataFetcher.sync_canula_buf[i]+self.canulaPressureIntercept
              copyIdx += 1
        
          # In case data has wrapped... read the wrapped data too
          if(endRead <= startRead):
            for i in range(0,endRead):
              self.time_queue[copyIdx] = self.dataFetcher.sync_time_buf[i]
              self.canula_queue[copyIdx] = self.canulaPressureSlope*self.dataFetcher.sync_canula_buf[i]+self.canulaPressureIntercept
              copyIdx += 1
          
          # Data is copied, so move pointer to free up buffer space under lock
          self.dataFetcher.indexLock.acquire()
          self.dataFetcher.sync_bufferStartIdx.value = endRead
          self.dataFetcher.sync_bufferLength.value = self.dataFetcher.sync_bufferLength.value - nDataToRead 
          self.dataFetcher.indexLock.release()
 
          # Now we can take all the time we want to plot the data; the 
          # fetching process will keep taking new data while this slow plot 
          # operation occurs. Nevertheless, we try to update the plotted 
          # line quickly 
        
          # Roll data to put newest data last
          self.time_queue = np.roll(self.time_queue,-nDataToRead)
          self.canula_queue = np.roll(self.canula_queue,-nDataToRead)
                
          # Show the new data
          self.pressureLine.setData(self.time_queue,self.canula_queue)
          
        # Update time axis if necessary
        if(elapsed_time > self.maxXlim):
            # Update axes
            while(elapsed_time > self.maxXlim):
              self.minXlim += self.TIME_SHIFT_PCT*self.PLOT_TIME_RANGE
              self.maxXlim = self.minXlim + self.PLOT_TIME_RANGE
            self.ui.pressurePlot.setXRange(self.minXlim,self.maxXlim,padding=0) 
            
        # Update text and slow graph
        if(elapsed_time > min(self.NEXT_TEXT_UPDATE,self.NEXT_SLOW_UPDATE)):
          min_val = min(self.canula_queue)
          max_val = max(self.canula_queue)
          
          if(elapsed_time > self.NEXT_SLOW_UPDATE):
            while(elapsed_time > self.NEXT_SLOW_UPDATE):
                self.NEXT_SLOW_UPDATE += self.SLOW_UPDATE_PERIOD
          
          if(elapsed_time > self.NEXT_TEXT_UPDATE):
            while(elapsed_time > self.NEXT_TEXT_UPDATE):
                self.NEXT_TEXT_UPDATE += self.TEXT_UPDATE_PERIOD
            self.slow_time_queue.append(elapsed_time)
            self.slow_minPressure_queue.append(min_val)
            self.slow_maxPressure_queue.append(max_val)
            self.minPressureLine.setData(self.slow_time_queue,self.slow_minPressure_queue)
            self.maxPressureLine.setData(self.slow_time_queue,self.slow_maxPressure_queue)
      
           
    def closeEvent(self, ce):
        self.stopGraphing()
        self.dataFetcher.stopFetching()    
        

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app = QtGui.QApplication([])
        win = DataMonitoringWindow()
        win.show()
        win.startGraphing()
        sys.exit(app.exec_())

