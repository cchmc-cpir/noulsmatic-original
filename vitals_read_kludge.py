import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import time
# - BJA - 05/18/2020
# - No idea why this works, but believe it pings something to allow
# - the SPI module write out reasonable values in the ventilator data display
 
# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
 
# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D25)
 
# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P7)

ping_variable = chan.value
print('If respiratory wave form does not work, try 1) closing ventilator software and try reopening; or 2) run "vitals_read_kludge.py"')