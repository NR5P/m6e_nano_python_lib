import time
from constants import *

############configuration settings########################
rfOnTime = 500
rfOffTime = 500
readPower = 2700
##########################################################

from RFID import RFID
rf = RFID()
rf.setBaudRate(115200)
print("set baud rate")
rf.setTagProtocol(TMR_TAG_PROTOCOL_GEN2)
rf.setAntennaPort()
rf.setRegion(REGION_EU3)
rf.setReadPower(readPower)

#rf.readTagEPC()
#time.sleep(1)
#rf.getReadPower()
rf.startReading(rfOnTime,rfOffTime)
#rf.stopReading()

#rf.getVersion()