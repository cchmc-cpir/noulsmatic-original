#!/usr/bin/env python by TA


import spidev
import time
import sys
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Reader:
        def __init__(self, channel=7):
                self.channel = channel
        def _readChannel(self):
                adc = spi.xfer2([1,(8+self.channel)<<4,0])
                data = ((adc[1]&3) << 8) + adc[2]
                return data
        def ConvertVolts(self,level,places):
                volts=((data*5000)/float(1023))-500.62 #this is for ventilator 1.0
                volts=round(volts,places)
                #print (" pressure voltage: %f",volts))
                return volts
        def ConvertPressure(self,level,places):
                pressure = (((level*5000)/float(1023))*0.3)/5000
                psi=pressure
                pressure=((pressure)/0.01422)-1.79 #empirical calibration for ventilator 1.0
                pressure=round(pressure,places)
                return pressure
        def getPressure(self):
                level=self._readChannel()
                press=self.ConvertPressure(level,3)
                return press

class rtPlot:
        def __init__(self, seconds=10, windowSize=10):
                self.xlim = seconds
                self.fig = plt.figure()
                
                self.ax = plt.axes(xlim=(0,seconds), ylim=(-5,30))
                self.ax.set_ylabel("Pressure")
                self.ax.set_xlabel("Seconds Elapsed")
                self.line, = self.ax.plot([],[],'b-')
                self.x = np.array([])
                self.y = np.array([])
                self.window = np.ones(windowSize)/float(windowSize)
        
                self.vr = Reader()
        def initPlot(self):
                self.line.set_data([],[])
                return self.line,

        def updatePlot(self,i):
                for i in range(100):
                        curTime = time.time()
                        self.x = np.append(self.x, [curTime])
                        self.y = np.append(self.y, [self.vr.getPressure()])
                        time.sleep(0.00006)
                whereOver = np.where(curTime-self.x > self.xlim)[0]
                if np.any(whereOver):
                        minOver = whereOver[0]
                        self.x = self.x[minOver:]
                        self.y = self.y[minOver:]
                if len(self.x) > len(self.window):
                        self.line.set_data(curTime-self.x, self.y)
                        
                else:
                        self.line.set_data(curTime-self.x, self.y)
                return self.line,

if __name__ == "__main__":
        try:
                # open SPI bus
                spi = spidev.SpiDev()
                spi.open(0,0)
                rtp = rtPlot(seconds=6)
                # start animation
                ani = animation.FuncAnimation(rtp.fig, rtp.updatePlot,
                                              init_func=rtp.initPlot, interval=0.000003, blit=True)
                try:
                        plt.show()
                except:
                        spi.close()
                        
        except KeyboardInterrupt:
                spi.close()
                plt.close()
        
