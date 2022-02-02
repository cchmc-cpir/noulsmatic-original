#!/usr/bin/python
import time
import multiprocessing as mp 
import numpy as np
import csv
import spidev
import RPi.GPIO as GPIO
    
    
class TimedDataFetcher:
  def __init__(self, fetchperiod):
    self.start_time = time.time()
    self.BUFFERSIZE = 5000
    self.FETCHPERIOD = fetchperiod
    self.isFetching = False
    
    # Open SPI bus
    #spi = spidev.SpiDev()
    #spi.open(0,0)
    
    # Create lock to prevent clashes between graphing/fetching processes
    self.indexLock = mp.Lock()

    # Setup an array to buffer values that are read off the pressure monitors 
    self.indexLock.acquire()
    
    self.sync_time_buf = mp.Array('d',range(self.BUFFERSIZE))
    self.sync_canula_buf = mp.Array('d',range(self.BUFFERSIZE))
    
    self.sync_bufferStartIdx = mp.Value('I', 0)
    self.sync_bufferLength = mp.Value('I', 0)
    self.sync_bufferEndIdx = mp.Value('I', -1)
    self.sync_bufferFull = mp.Value('I', 0)  # SHOULD BE BOOLEAN
    self.indexLock.release() 
    
    self.fetch_process = mp.Process(target=self.fetchData, args=(), 
                           name='FetchProcess')
                           
  def newStartTime(self,newStartTime):
    self.indexLock.acquire()
    self.start_time = newStartTime
    self.sync_bufferStartIdx = mp.Value('I', 0)
    self.sync_bufferLength = mp.Value('I', 0)
    self.sync_bufferEndIdx = mp.Value('I', -1)
    self.sync_bufferFull = mp.Value('I', 0)  # SHOULD BE BOOLEAN
    self.indexLock.release()

  def getDataFromChannel(self,channel):
    spi = spidev.SpiDev()
    spi.open(0,0)
    #adc = self.spi.xfer2([1,(8+channel)<<4,0]) 
    adc=spi.xfer2([1,(8+channel)<<4,0])
    #print("adc = %f",adc)
    data=((adc[1]&3) << 8) + adc[2]
    #print("data = %f", data)
    #p1=(((data*5000)/float(1023))*0.3)/5000
    #print("p1 = %f",p1)
    spi.close()
    #GPIO.setmode(GPIO.BCM)
    #GPIO.setup(channel, GPIO.IN)
    #test = GPIO.input(channel)
    #print("test = %f",test)
    #PJN change data to p1
    return data
    #GPIO.setmode(GPIO.BCM)
    #GPIO.setup(channel, GPIO.IN)
    #GPIO.add_event_detect(channel, CIP.BOTH, callback=self.getDataFromChannel, bouncetime=1)
    # adc=((adc[1]&3)<<8)+adc[2]
    # return ((adc[1]&3) << 8) + adc[2]
   # p1=(((adc*5000)/float(1023))*0.3)/5000
   # print("p1 = %f",p1)
    # pressure=((p1)/0.01422)-1.79
    # pressure=round(pressure,4)
    # return pressure
      
  def fetchData(self):
    i = 0
      # Fetch new data until the end of time, or when the user closes the window
    while self.isFetching:
      # Get timestamp for data
      t_stamp = time.time() - self.start_time
    
      # Fetch new data
      # canula = self.getDataFromChannel(0)
      # channel 7 was the original
      canula=self.getDataFromChannel(7)
      #print("Canula Value = %f",canula)
      #canula=canula*0.02-14# 161228 Calibration this is for ventilator 1.0
      #canula=(canula-70)*0.02
      
      #canula=canula 

      canula=(canula-85.589)/37.984 # benchtop calibration (7/25/17)
      # canula=(canula-94.527)/38.563 # 7T calibration (7/14/17)
      
      #GPIO.setmode(GPIO.BCM)
      #GPIO.setup(7,GPIO.IN)
      #canula=GPIO.input(7)
      #canula=canula*1;
      
      #print("canula = %f",canula)
      
      # Add data to buffer and increment index under lock
      self.indexLock.acquire()
      self.sync_bufferEndIdx.value += 1
      self.sync_bufferLength.value += 1
      
      if(self.sync_bufferLength.value >= (self.BUFFERSIZE)):
        # Buffer has overrun! (will be reset when/if plotting catches up)
        self.sync_bufferFull.value = 1
        self.sync_bufferLength.value = self.BUFFERSIZE
        print "   BUFFER FULL !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        
      # Buffer has space, so add new data
      if(self.sync_bufferEndIdx.value >= self.BUFFERSIZE):
        while(self.sync_bufferEndIdx.value >= self.BUFFERSIZE):
          self.sync_bufferEndIdx.value = self.sync_bufferEndIdx.value - self.BUFFERSIZE
      self.indexLock.release()
      
      self.sync_time_buf[self.sync_bufferEndIdx.value] = t_stamp
      self.sync_canula_buf[self.sync_bufferEndIdx.value] = canula
      # Write to csvfile
      i += 1
      if i % 5 == 0:
        self.csvwriter.writerow([t_stamp,canula])
      #self.csvwriter.writerow([t_stamp,canula])
      time.sleep(self.FETCHPERIOD)
      
  def startFetching(self):
      if not self.isFetching:
          self.csvfile = open('/home/pi/Desktop/noulsmatic_v2/VentilatorData.csv','w')
          self.csvwriter = csv.writer(self.csvfile)
          self.isFetching = True
          self.fetch_process.start()
          spi = spidev.SpiDev()
          spi.open(0,0)
          
    
  def stopFetching(self):
      if self.isFetching:
          self.fetch_process.terminate()
          self.fetch_process.join()
          self.isFetching = False
          self.csvfile.close()
  

