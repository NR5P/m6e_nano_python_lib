import time, ujson, os
from constants import *


############configuration settings########################
rfOnTime = 50
rfOffTime = 2000
readPower = 2700
baudrate = 115200 # 115200 is default for m6e nano
filename = "settings.json"
##########################################################

def getOrSetSettingsData(rfOnTime, rfOffTime, readPower, filename):
    if "settings.json" in os.listdir():
        file = open(filename, "r")
        settingsDict = ujson.loads(file.read())
        file.close()
        rfOnTime = settingsDict["rfontime"]
        rfOffTime = settingsDict["rfofftime"]
        readPower = settingsDict["readpower"]
    else:
        settingsDict = {}
        file = open(filename, "w")
        settingsDict["rfontime"] = rfOnTime
        settingsDict["rfofftime"] = rfOffTime
        settingsDict["readpower"] = readPower
        ujson.dump(settingsDict, file)
        file.close()

getOrSetSettingsData(rfOnTime, rfOffTime, readPower, filename)

from RFID import RFID
rf = RFID(rfOnTime, rfOffTime, readPower, baudrate)
rf.stopReading() # stop reading if it is reading
rf.setTagProtocol(TMR_TAG_PROTOCOL_GEN2)
rf.setAntennaPort()
rf.setRegion(REGION_EU3)
rf.setReadPower(readPower)

rf.startReading(rfOnTime,rfOffTime)
#rf.getVersion()

