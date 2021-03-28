from constants import *
from machine import UART
from machine import Pin
from Bluetooth import Bluetooth
import time

class RFID:
    def __init__(self, baud=115200):
        self.debug = True
        self.opcode = ''
        self.uart = UART(
            1,
            baudrate=baud,
            tx=17,
            rx=16
        )
        #self.bluetooth = Bluetooth()

    def sendOverBluetooth(data):
        if self.bluetooth.is_connected():
            self.bluetooth.send(data)

    def startReading(self, rfOnTime, rfOffTime):
        while self.uart.any() > 0:
            print("clearing buffer")
            self.uart.read()
        self.disableReadFilter()

        configBlob = [0x00, 0x00, 0x01, 0x22, 0x00, 0x00, 0x05, 0x0b, 0x22, 0x10, 0x05, 0x1B] 
        configBlob.append(rfOnTime >> 8 & 0xFF)
        configBlob.append(rfOnTime & 0xFF)
        configBlob.append(rfOffTime >> 8 & 0xFF)
        configBlob.append(rfOffTime & 0xFF)
        configBlob.append(0)
        configBlob.append(87)
        configBlob.append(1)
        configBlob.append(0)

        self.sendMessage(TMR_SR_OPCODE_MULTI_PROTOCOL_TAG_OP, configBlob, timeout=None)

    def getSignalLevelDB(self, msgArray) -> int:
        if len(msgArray) > 13 and msgArray[12] != 0:
            return msgArray[12] - 256

    def getEpcTagNumber(self, msgArray) -> str:
        epcTagNum = ""
        if len(msgArray) > 19:
            epcLength = msgArray[20] / 8
            for i in range(22,len(msgArray)-4):
                if msgArray[i] < 0x10:
                    epcTagNum += "0"
                epcTagNum += hex(msgArray[i])[2:]
        return epcTagNum

    def setAntennaPort(self):
        configBlob = [0x01, 0x01]
        self.sendMessage(TMR_SR_OPCODE_SET_ANTENNA_PORT, configBlob)

    # Sets the protocol of the module
    # Currently only GEN2 has been tested and supported but others are listed here for reference
    # and possible future support
    def setTagProtocol(self, protocol = TMR_TAG_PROTOCOL_GEN2):
        data = []
        data.append(0) # Opcode expects 16-bits
        data.append(protocol)

        self.sendMessage(TMR_SR_OPCODE_SET_TAG_PROTOCOL, data)

    def printMessageArray(self, msg) -> None:
        #print(self.getSignalLevelDB(msg))
        print("epc #: " + self.getEpcTagNumber(msg))
        if self.debug == True:
            amtToPrint = msg[1] + 5
            if amtToPrint > MAX_MSG_SIZE:
                amtToPrint = MAX_MSG_SIZE
            
            printMsg = ""
            for i in range(amtToPrint):
                printMsg += " ["
                if msg[i] < 0x10:
                    printMsg += "0"
                printMsg += hex(msg[i])[2:]
                printMsg += "]"
            print(printMsg)

    def readTagEPC(self) -> str:
        bank = 0x01
        address = 0x02
        return self.readData(bank, address, 3)    

    #Get the version number from the module
    def getVersion(self):
        self.sendMessage(TMR_SR_OPCODE_VERSION, [])

    def getPowerMode(self):
        self.sendMessage(TMR_SR_OPCODE_GET_POWER_MODE, [])

    def setRegion(self, region):
        data = bytearray()
        data.append(region)
        self.sendMessage(TMR_SR_OPCODE_SET_REGION, data)

    def readData(self, bank, address, timeOut):
        data = bytearray()
        data.append(timeOut >> 8 & 0xFF)
        data.append(timeOut & 0xFF)
        data.append(bank)

        for i in range(4):
            data.append(address >> (8 * (3-0)) & 0xFF)
        data.append(0x00)
        if (bank == 0x03):
            data[7] = 0x00
        
        receivedMsg = self.sendMessage(TMR_SR_OPCODE_READ_TAG_DATA, data)

        returnArray = []
        if receivedMsg[0] == ALL_GOOD:
            status = ((receivedMsg[3] << 8) & 0xFFFF) | receivedMsg[4]
            if status == 0x0000:
                responseLength = receivedMsg[1]
                for i in range(responseLength):
                    returnArray.append(receivedMsg[i + 5])
                return returnArray

    def disableReadFilter(self):
        self.setReaderConfiguration(0x0C, 0x00)

    def setReaderConfiguration(self, option1, option2):
        data = []
        data.append(1)
        data.append(option1)
        data.append(option2)
        self.sendMessage(TMR_SR_OPCODE_SET_READER_OPTIONAL_PARAMS, data)

    def setBaudRate(self, baudRate: int) -> None:
        data = bytearray()
        for i in range(2):
            data.append(0xFF & (baudRate >> (8 * (2 - 1 - i))))

        self.sendMessage(TMR_SR_OPCODE_SET_BAUD_RATE, data, waitforresponse=False)

    def readTag(self) -> Tuple[str, int]:
        """
            @returns tuple
                (tag id, signal strength)
        """
        configBlob = [0x00, 0x00, 0x01, 0x22, 0x00, 0x00, 0x05, 0x07, 0x22, 0x10, 0x00, 0x1B, 0x03, 0xE8, 0x01, 0xFF]
        received = self.sendMessage(TMR_SR_OPCODE_MULTI_PROTOCOL_TAG_OP, configBlob)
        if received != None:
            pass

    def stopReading(self) -> None:
        configBlob = [0x00, 0x00, 0x02]
        self.sendMessage(TMR_SR_OPCODE_MULTI_PROTOCOL_TAG_OP, configBlob, waitforresponse=False) #Do not wait for response

    # maximum read power is 2700 for 27db
    def setReadPower(self, powerSetting: int) -> None:
        if powerSetting > 32767:
            powerSetting = 2700
        if powerSetting < -32768:
            powerSetting = 0

        data = bytearray()
        for i in range(2):
            data.append(0xFF & (powerSetting >> (8 * (2 - 1 - i))))
        self.sendMessage(TMR_SR_OPCODE_SET_READ_TX_POWER, data)

    def getReadPower(self):
        data = bytearray()
        data.append(0x00)
        self.sendMessage(TMR_SR_OPCODE_GET_READ_TX_POWER, data)

    def getWritePower(self):
        data = bytearray()
        data.append(0x00)
        self.sendMessage(TMR_SR_OPCODE_GET_WRITE_TX_POWER, data)

    def sendMessage(self, opcode: int, data: List[int], timeout: int = COMMAND_TIME_OUT, waitforresponse: bool = True) -> List:
        msg = bytearray()
        msg.append(0xFF) # universal header at beginnning
        msg.append(len(data))
        msg.append(opcode)
        for i in data:
            msg.append(i)
        print("before send command")
        return self.sendCommand(timeout, waitforresponse, msg)

    def checkTimeOut(self, startTime, timeout):
        if timeout != None and (time.time() - startTime) > timeout:
            return True 
        return False

    def sendCommand(self, timeout: int, waitforresponse: bool, msg: bytearray) -> List:
        msgLength = msg[1]
        opcode = msg[2]

        # attach crc
        crc = self.calculateCRC(msg)
        msg.append(crc >> 8)
        msg.append(crc & 0xFF)
        while self.uart.any() > 0:
            print("clearing buffer")
            self.uart.read()
        self.uart.write(msg)

        # wait for response with timeout
        startTime = time.time()
        while self.uart.any() < 1:
            if self.checkTimeOut(startTime, timeout):
                print("NO RESPONSE FROM MODULE")
                msg[0] = ERROR_COMMAND_RESPONSE_TIMEOUT
                return

        while True:
            msgLength = MAX_MSG_SIZE - 1
            spot = 0
            receiveArray = []
            while spot < msgLength:
                print(receiveArray)
                if self.checkTimeOut(startTime, timeout):
                    receiveArray.append(ERROR_COMMAND_RESPONSE_TIMEOUT)
                    return receiveArray
                if self.uart.any() > 0:
                    receiveArray.append(int.from_bytes(self.uart.read(1),"little"))
                    if spot == 1:
                        msgLength = receiveArray[1] + 7
                    spot += 1
            #self.sendOverBluetooth(receiveArray)
            if self.debug == True:
                self.printMessageArray(receiveArray)

            # check crc for corrupted response
            crc = self.calculateCRC(receiveArray[:-2]) # remove the header(0xff) and 2 crc bytes
            if (receiveArray[msgLength - 2] != (crc >> 8)) or (receiveArray[msgLength - 1] != (crc & 0xFF)):
                receiveArray[0] = ERROR_CORRUPT_RESPONSE
                if (self.debug == True):
                    print("CORRUPT RESPONSE")
                    #return receiveArray

            # check that opcode matches (did we get a response to the command we sent or a different one?)
            if (receiveArray[2] != opcode):
                receiveArray[0] = ERROR_WRONG_OPCODE_RESPONSE
                if (self.debug == True and timeout != None):
                    print("WRONG OPCODE RESPONSE")
                    #return receiveArray

            if timeout != None:
                return receiveArray

    def calculateCRC(self, buf):
        crc = 0xFFFF
        for i in range(1,len(buf)):
            crc = (((crc << 4) & 0xFFFF) | (buf[i] >> 4)) ^ crctable[crc >> 12]
            crc = (((crc << 4) & 0xFFFF) | (buf[i] & 0x0F)) ^ crctable[crc >> 12]

        return crc


