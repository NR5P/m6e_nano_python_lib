import time, ujson, os
from constants import *


############configuration settings########################
rfOnTime = 50
rfOffTime = 2000
readPower = 2700
baudrate = 115200 # 115200 is default for m6e nano
##########################################################

def getOrSetSettingsData():
    if os.path.exists("settings.json"):
        file = open(self.filename, "r")
        settingsDict = ujson.load(file)
        file.close()
        rfOnTime = settingsDict["rfontime"]
        rfOffTime = settingsDict["rfofftime"]
        readPower = settingsDict["readpower"]
    else:
        file = open(self.filename, "w")
        settingsDict = ujson.load(file)
        settingsDict["rfontime"] = rfOnTime
        settingsDict["rfofftime"] = rfOffTime
        settingsDict["readpower"] = readPower
        ujson.dump(settingsDict, file)
        file.close()

getOrSetSettingsData()

from RFID import RFID
rf = RFID(rfontime, rfOffTime, readPower, baudrate)
rf.stopReading() # stop reading if it is reading
rf.setTagProtocol(TMR_TAG_PROTOCOL_GEN2)
rf.setAntennaPort()
rf.setRegion(REGION_EU3)
rf.setReadPower(readPower)

rf.startReading(rfOnTime,rfOffTime)
#rf.getVersion()

