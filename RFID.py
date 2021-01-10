from constants import *
from typing import Tuple, List
from ctypes import sizeof
from machine import uart

class RFID:
    def __init__(self):
        self.debug = False
        self.baudRate = 9600
        self.opcode = ''
        self.uart = UART(1, self.baudRate)
        self.uart.init(baudRate=9600,bits=8,parity=None,stop=1,rx=12,tx=14)

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
        sendMessage(TMR_SR_OPCODE_MULTI_PROTOCOL_TAG_OP, configBlob, waitforresponse=false) #Do not wait for response

    def setOutputPower(self, powerOut: int) -> None:
        pass

    def getRate(self) -> int:
        pass

    def sendMessage(self, opcode: int, data: List[int], timeout: int = COMMAND_TIME_OUT, waitforresponse: bool = True) -> List[str]:
        #TODO: use bytearray
        msg = [None] * MAX_MSG_SIZE
        msg[0] = 0xFF #universal header
        msg[1] = len(data)
        msg[2] = opcode
        for i in range(len(data)):
            msg[3 + i] = data[i]
        self.sendCommand(timeout, waitforresponse, msg)
        if waitforresponse == True:
            receivedMsg = self.receiveMessage()
            #msgLength = receivedMsg[1] + 7
            #crc = self.calculateCRC(receivedMsg[1], msgLength - 3); #Remove header, remove 2 crc bytes
            return receivedMsg
        else:
            return []

    def sendCommand(self, timeout: int, waitforresponse: bool, msg: List[int]) -> None:
        msgLength = msg[1]
        self.opcode = msg[2] # to see if response from module has same opcode

        # attach crc
        crc = self.calculateCRC(msg[1], msgLength + 2)
        msg[msgLength + 3] = crc >> 8
        msg[msgLength + 4] = crc & 0xFF
        if self.debug == True:
            printMessage(msg)

        self.sendToUART(msg)


    def calculateCRC(self, buf: int, len: int) -> int:
        crc = 0xFFFF
        for i in range(len):
            crc = ((crc << 4) | (buf[i] >> 4)) ^ crctable[crc >> 12]
            crc = ((crc << 4) | (buf[i] & 0x0F)) ^ crctable[crc >> 12]

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