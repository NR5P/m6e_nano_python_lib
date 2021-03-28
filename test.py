import time
from constants import *

############configuration settings########################
rfOnTime = 200
rfOffTime = 1000
readPower = 2700
baudrate = 115200 # 115200 is default for m6e nano
##########################################################

from RFID import RFID
rf = RFID(baudrate)
#rf.stopReading() # stop reading if it is reading
#rf.setBaudRate(baudrate)
print("before")
rf.setTagProtocol(TMR_TAG_PROTOCOL_GEN2)
print("after")
rf.setAntennaPort()
rf.setRegion(REGION_EU3)
rf.setReadPower(readPower)

#rf.readTagEPC()
#time.sleep(1)
#rf.getReadPower()
rf.startReading(rfOnTime,rfOffTime)
#rf.stopReading()

#rf.getVersion()