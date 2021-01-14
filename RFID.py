from constants import *
from typing import Tuple, List
from ctypes import sizeof
import serial
import time

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
        self.disableReadFilter()
        configBlob = [0x00, 0x00, 0x01, 0x22, 0x00, 0x00, 0x05, 0x07, 0x22, 0x10, 0x00, 0x1B, 0x03, 0xE8, 0x01, 0xFF]
        self.sendMessage(TMR_SR_OPCODE_MULTI_PROTOCOL_TAG_OP, configBlob)
        time.sleep(.1)
        while True:
            returnMsg = self.ser.read()
            #print(returnMsg)

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
        print(msg)
        self.ser.write(msg)

    def calculateCRC(self, buf):
        crc = 0xFFFF
        for i in range(1,len(buf)):
            crc = (((crc << 4) & 0xFFFF) | (buf[i] >> 4)) ^ crctable[crc >> 12]
            crc = (((crc << 4) & 0xFFFF) | (buf[i] & 0x0F)) ^ crctable[crc >> 12]

        return crc

    def printMessage(self, msg: List[int]) -> None:
        print(msg)

    def receiveMessage(self) -> List[str]:
        i = 0
        msg = [None] * MAX_MSG_SIZE
        while self.uart.any() > 0:
            msg[i] = self.uart.read(1).decode("utf-8")
            i = i + 1

    def sendToUART(self, msg: List[int]) -> None:
        for i in msg:
            uart.write(i)