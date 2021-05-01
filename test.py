import time, ujson, os
from constants import *

#TODO: test.py should be renamed to main.py so that the bootloader loads it on startup
############configuration settings########################
rfOnTime = 50
rfOffTime = 2000
readPower = 2700
baudrate = 115200 # 115200 is default for m6e nano
filename = "settings.json"
##########################################################

def getOrSetSettingsData():
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

getOrSetSettingsData()

from RFID import RFID
time.sleep(3) ##### give time for m6e nano to boot before initializing #####
rf = RFID(rfOnTime, rfOffTime, readPower, baudrate)
rf.stopReading() # stop reading if it is reading
rf.setTagProtocol(TMR_TAG_PROTOCOL_GEN2)
rf.setAntennaPort()
rf.setRegion(REGION_EU3)
rf.setReadPower(readPower)

rf.startReading(rfOnTime,rfOffTime)
#rf.getVersion()

