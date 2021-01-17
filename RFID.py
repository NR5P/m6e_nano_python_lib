from constants import *
from typing import Tuple, List
from ctypes import sizeof
import serial
import time
import codecs
import chardet

class RFID:
    def __init__(self):
        self.debug = False
        self.opcode = ''
        self.ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=115200,
            parity=serial.PARITY_ODD,
            #stopbits=serial.STOPBITS_TWO,
            #bytesize=serial.SEVENBITS
        )

    def startReading(self):
        #self.ser.reset_input_buffer()
        self.disableReadFilter()
        configBlob = [0x00, 0x00, 0x01, 0x22, 0x00, 0x00, 0x05, 0x07, 0x22, 0x10, 0x00, 0x1B, 0x03, 0xE8, 0x01, 0xFF]
        self.sendMessage(TMR_SR_OPCODE_MULTI_PROTOCOL_TAG_OP, configBlob)

    def printByteArray(self, tag):
        txt = ""
        amtToPrint = int.from_bytes(tag[1],"little") + 5
        if amtToPrint > MAX_MSG_SIZE:
            amtToPrint = MAX_MSG_SIZE

        for i in tag:
            if int.from_bytes(i,"little") < 0x10:
                txt += i
            else:
                txt += i

        print("[ " + txt + " ]")

    def receiveOneTag(self):
        msg = []
        spot = 0
        message_length = MAX_MSG_SIZE - 1
        while spot < message_length:
            if self.ser.inWaiting() > 0:
                msg.append(self.ser.read(size=1))
                if spot == 1:
                    message_length = int.from_bytes(msg[1],"little") + 7
                spot+=1
                spot %= MAX_MSG_SIZE
        return msg

    def readTagEPC(epc, epcLength, timeOut):
        bank = 0x01
        address = 0x02
        return readData(bank, address, epc, epcLength, timeOut)    

    def readData(bank, address, epc, epcLength, timeOut):
        data = bytearray
        data.append(timeOut >> 8 & 0xFF)
        data.append(timeOut & 0xFF)
        data.append(bank)

        data.append(address >> (8 * (3-0)) & 0xFF)

    def disableReadFilter(self):
        self.setReaderConfiguration(0x0C, 0x00)

    def setReaderConfiguration(self, option1, option2):
        data = []
        data.append(1)
        data.append(option1)
        data.append(option2)
        self.sendMessage(TMR_SR_OPCODE_SET_READER_OPTIONAL_PARAMS, data)

    def setBaud(self, baudRate: int) -> None:
        pass

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

    def setOutputPower(self, powerOut: int) -> None:
        pass

    def getRate(self) -> int:
        pass

    def sendMessage(self, opcode: int, data: List[int], timeout: int = COMMAND_TIME_OUT, waitforresponse: bool = True) -> None:
        msg = bytearray()
        msg.append(len(data))
        msg.append(opcode)
        for i in data:
            msg.append(i)
        self.sendCommand(timeout, waitforresponse, msg)

    def sendCommand(self, timeout: int, waitforresponse: bool, msg: bytearray) -> None:
        #self.opcode = msg[1] # to see if response from module has same opcode
        msg.insert(0,0xFF) # universal header at beginnning

        # attach crc
        crc = self.calculateCRC(msg)
        msg.append(crc >> 8)
        msg.append(crc & 0xFF)
        #if self.debug == True:
            #printMessage(msg)
        self.ser.write(msg)

    def calculateCRC(self, buf):
        crc = 0xFFFF
        for i in range(1,len(buf)):
            crc = (((crc << 4) & 0xFFFF) | (buf[i] >> 4)) ^ crctable[crc >> 12]
            crc = (((crc << 4) & 0xFFFF) | (buf[i] & 0x0F)) ^ crctable[crc >> 12]

        return crc

    def receiveMessage(self) -> List[str]:
        i = 0
        msg = [None] * MAX_MSG_SIZE
        while self.uart.any() > 0:
            msg[i] = self.uart.read(1).decode("utf-8")
            i = i + 1

    def sendToUART(self, msg: List[int]) -> None:
        for i in msg:
            uart.write(i)