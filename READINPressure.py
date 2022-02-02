import spidev
import time
import os

import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn


spi=spidev.SpiDev()
spi.open(0,0)

spi1 = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D25)
 
# create the mcp object
mcp = MCP.MCP3008(spi1, cs)

chan = AnalogIn(mcp, MCP.P7)
test = chan.value
 
def ReadChannel(channel):
    adc=spi.xfer2([1,(8+channel)<<4,0])
    data=((adc[1]&3) << 8)+adc[2]
    return data

def ConvertVolts(data,places):
    volts=(data*5100)/float(1023) #multiply by 5000mV/1023 because The MCP3008 is a 10-bit ADC. That means it will read a value from 0 to 1023 (2^^10 = 1024 values)
                                #where 0 is the same as 'ground' and '1023' is the same as '5 volts'
    volts=round(volts,places)
    return volts

def ConvertPressure(data,places):
    pressure = ((data*5100)/float(1023))*0.3/5000 -.22#transfer function from fujikura manual
    pressure =round(pressure,places)
    return pressure

pressure_channel=6
delay=0.25 #in sec

while True:
    pressure_level=ReadChannel(pressure_channel)
    pressure_volts=ConvertVolts(pressure_level,2)
    pressure = ConvertPressure(pressure_level,2)

   # print (" pressure: {} ({}mV) {} psi". format( pressure_level, pressure_volts, pressure))
    print (" pressure: %f, %f, %f",pressure_level, pressure_volts, pressure)
    time.sleep(delay)
