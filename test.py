import time
from constants import *

############configuration settings########################
rfOnTime = 50
rfOffTime = 2000
readPower = 2700
baudrate = 115200 # 115200 is default for m6e nano
##########################################################

from RFID import RFID
rf = RFID(baudrate)
rf.stopReading() # stop reading if it is reading
#rf.setBaudRate(baudrate)
rf.setTagProtocol(TMR_TAG_PROTOCOL_GEN2)
rf.setAntennaPort()
rf.setRegion(REGION_EU3)
rf.setReadPower(readPower)

#rf.getReadPower()
rf.startReading(rfOnTime,rfOffTime)
#rf.stopReading()

#rf.getVersion()