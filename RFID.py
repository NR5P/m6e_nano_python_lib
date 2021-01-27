from constants import *
from typing import Tuple, List
import serial
import time

class RFID:
    def __init__(self):
        self.debug = True
        self.opcode = ''
        self.ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=115200,
        )

    def startReading(self):
        self.ser.reset_input_buffer()
        self.disableReadFilter()
        configBlob = [0x00, 0x00, 0x01, 0x22, 0x00, 0x00, 0x05, 0x07, 0x22, 0x10, 0x00, 0x1B, 0x03, 0xE8, 0x01, 0xFF]
        self.sendMessage(TMR_SR_OPCODE_MULTI_PROTOCOL_TAG_OP, configBlob)

    def setAntennaPort(self):
        configBlob = [0x01, 0x01]
        self.sendMessage(TMR_SR_OPCODE_SET_ANTENNA_PORT, configBlob)

    # Sets the protocol of the module
    # Currently only GEN2 has been tested and supported but others are listed here for reference
    # and possible future support
    # TMR_TAG_PROTOCOL_NONE              = 0x00
    # TMR_TAG_PROTOCOL_ISO180006B        = 0x03
    # TMR_TAG_PROTOCOL_GEN2              = 0x05
    # TMR_TAG_PROTOCOL_ISO180006B_UCODE  = 0x06
    # TMR_TAG_PROTOCOL_IPX64             = 0x07
    # TMR_TAG_PROTOCOL_IPX256            = 0x08
    # TMR_TAG_PROTOCOL_ATA               = 0x1D
    def setTagProtocol(self, protocol = 0x05):
        data = []
        data.append(0) # Opcode expects 16-bits
        data.append(protocol)

        self.sendMessage(TMR_SR_OPCODE_SET_TAG_PROTOCOL, data)

    def printMessageArray(self, msg) -> None:
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

    def setRegion(self):
        # 0x04 = IN
        # 0x05 = JP
        # 0x06 = PRC
        # 0x08 = EU3
        # 0x09 = KR2
        # 0x0B = AU
        # 0x0C = NZ
        # 0x0D = NAS2 (North America)
        # 0xFF = OPEN
        data = bytearray()
        data.append(0x08)
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

    def sendMessage(self, opcode: int, data: List[int], timeout: int = COMMAND_TIME_OUT, waitforresponse: bool = True) -> List:
        msg = bytearray()
        msg.append(len(data))
        msg.append(opcode)
        for i in data:
            msg.append(i)
        return self.sendCommand(timeout, waitforresponse, msg)

    def sendCommand(self, timeout: int, waitforresponse: bool, msg: bytearray) -> List:
        msg.insert(0,0xFF) # universal header at beginnning
        msgLength = msg[1]
        opcode = msg[2]

        # attach crc
        crc = self.calculateCRC(msg)
        msg.append(crc >> 8)
        msg.append(crc & 0xFF)
        self.ser.reset_input_buffer() # clear anything in buffer
        self.ser.write(msg)

        # wait for response with timeout
        startTime = time.time()
        while self.ser.inWaiting() < 1:
            if (time.time() - startTime) > timeout:
                print("NO RESPONSE FROM MODULE")
                msg[0] = ERROR_COMMAND_RESPONSE_TIMEOUT
                return

        msgLength = MAX_MSG_SIZE - 1
        spot = 0
        receiveArray = []
        while spot < msgLength:
            if (time.time() - startTime) > timeout:
                receiveArray.append(ERROR_COMMAND_RESPONSE_TIMEOUT)
                return receiveArray
            if self.ser.inWaiting() > 0:
                receiveArray.append(int.from_bytes(self.ser.read(size=1),"little"))
                if spot == 1:
                    msgLength = receiveArray[1] + 7
                spot += 1
        if self.debug == True:
            print("response: ")
            self.printMessageArray(receiveArray)

        crc = self.calculateCRC(receiveArray[:-2]) # remove the header(0xff) and 2 crc bytes
        if (receiveArray[msgLength - 2] != (crc >> 8)) or (receiveArray[msgLength - 1] != (crc & 0xFF)):
            receiveArray[0] = ERROR_CORRUPT_RESPONSE
            if (self.debug == True):
                print("CORRUPT RESPONSE")
                return receiveArray

        # If crc is ok, check that opcode matches (did we get a response to the command we sent or a different one?)
        if (receiveArray[2] != opcode):
            receiveArray[0] = ERROR_WRONG_OPCODE_RESPONSE
            if (self.debug == True):
                print("WRONG OPCODE RESPONSE")
                return receiveArray

        # If everything is ok, load all ok into msg array
        receiveArray[0] = ALL_GOOD
        return receiveArray

    def calculateCRC(self, buf):
        crc = 0xFFFF
        for i in range(1,len(buf)):
            crc = (((crc << 4) & 0xFFFF) | (buf[i] >> 4)) ^ crctable[crc >> 12]
            crc = (((crc << 4) & 0xFFFF) | (buf[i] & 0x0F)) ^ crctable[crc >> 12]

        return crc


