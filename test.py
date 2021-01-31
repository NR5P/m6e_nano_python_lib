import time

from RFID import RFID
rf = RFID()
rf.setBaudRate(115200)
rf.setTagProtocol()
rf.setAntennaPort()
rf.setRegion()
rf.setReadPower(1000)

#rf.readTagEPC()
#time.sleep(1)
#rf.getReadPower()
#rf.startReading(2000,2000)
rf.stopReading()

#rf.getVersion()