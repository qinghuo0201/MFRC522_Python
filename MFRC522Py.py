#!/usr/bin/env python
# -*- coding: utf8 -*-

# Study MFRC522.pdf to understand this code
# Get the book at https://www.nxp.com/docs/en/data-sheet/MFRC522.pdf

import RPi.GPIO as GPIO
import signal
import time
import spi      # spi library is from https://github.com/lthiery/SPI-Py ; credit to Louis Thiery (lthiery)

class MFRC522Py:

    ###
    ###	MFRC522.pdf, page 70, MFRC522 Command
    ###
    Idle                = 0x0	#no action, cancels current command execution
    Mem                 = 0x1	#stores 25 bytes into the internal buffer
    Generate_RandomID	= 0x2	#generates a 10-byte random ID number
    CalcCRC             = 0x3	#activates the CRC coprocessor or performs a self test
    Transmit            = 0x4	#transmits data from the FIFO buffer
    NoCmdChange         = 0x7	#no command change, can be used to modify the CommandReg register bits without affecting the command, for example, the PowerDown bit
    Receive             = 0x8	#activates the receiver circuits
    Transceive          = 0xC	#transmits data from FIFO buffer to antenna and automatically activates the receiver after transmission
    MFAuthent           = 0xE	#performs the MIFARE standard authentication as a reader
    SoftReset           = 0xF	#resets the MFRC522


    ###
    ### MFRC522.pdf, Chapter 9 MFRC522 Registers, page 35
    ###
    ### Page 0: Command and flag
    CommandReg          = 0x01   #starts and stops command execution Table 23 on page 38
    ComlEnReg           = 0x02   #enable and disable interrupt request control bits Table 25 on page 38
    DivlEnReg           = 0x03   #enable and disable interrupt request control bits Table 27 on page 39
    ComIrqReg           = 0x04   #interrupt request bits Table 29 on page 39
    DivIrqReg           = 0x05   #interrupt request bits Table 31 on page 40
    ErrorReg            = 0x06   #error bits showing the error flag of the last command executed Table 33 on page 41
    flag1Reg          = 0x07   #communication flag bits Table 35 on page 42
    flag2Reg          = 0x08   #receiver and transmitter flag bits Table 37 on page 43
    FIFODataReg         = 0x09   #input and output of 64 byte FIFO buffer Table 39 on page 44
    FIFOLevelReg        = 0x0A   #number of bytes stored in the FIFO buffer Table 41 on page 44
    WaterLevelReg       = 0x0B   #level for FIFO underflow and overflow warning Table 43 on page 44
    ControlReg          = 0x0C   #miscellaneous control registers Table 45 on page 45
    BitFramingReg       = 0x0D   #adjustments for bit-oriented frames Table 47 on page 46
    CollReg             = 0x0E   #bit position of the first bit-collision detected on the RF interface Table 49 on page 46
    ### Page 1: Command
    ModeReg             = 0x11   #defines general modes for transmitting and receiving Table 55 on page 48
    TxModeReg           = 0x12   #defines transmission data rate and framing Table 57 on page 48
    RxModeReg           = 0x13   #defines reception data rate and framing Table 59 on page 49
    TxControlReg        = 0x14   #controls the logical behavior of the antenna driver pins TX1 and TX2 Table 61 on page 50
    TxASKReg            = 0x15   #controls the setting of the transmission modulation Table 63 on page 51
    TxSelReg            = 0x16   #selects the internal sources for the antenna driver Table 65 on page 51
    RxSelReg            = 0x17   #selects internal receiver settings Table 67 on page 52
    RxThresholdReg      = 0x18   #selects thresholds for the bit decoder Table 69 on page 53
    DemodReg            = 0x19   #defines demodulator settings Table 71 on page 53
    MfTxReg             = 0x1C   #controls some MIFARE communication transmit parameters Table 77 on page 55
    MfRxReg             = 0x1D   #controls some MIFARE communication receive parameters Table 79 on page 55
    SerialSpeedReg      = 0x1F   #selects the speed of the serial UART interface Table 83 on page 55
    ### Page 2: Configuration
    CRCResultReg_High   = 0x21   #shows the MSB and LSB values of the CRC calculation Table 87 on page 57
    CRCResultReg_Low    = 0x22   #Table 89 on page 57
    ModWidthReg         = 0x24   #controls the ModWidth setting Table 93 on page 58
    RFCfgReg            = 0x26   #configures the receiver gain Table 97 on page 59
    GsNReg              = 0x27   #selects the conductance of the antenna driver pins TX1 and TX2 for modulation Table 99 on page 59
    CWGsPReg            = 0x28   #defines the conductance of the p-driver output during periods of no modulation Table 101 on page 60
    ModGsPReg           = 0x29   #defines the conductance of the p-driver output during periods of modulation Table 103 on page 60
    TModeReg            = 0x2A   #defines settings for the internal timer Table 105 on page 60
    TPrescalerReg       = 0x2B   #defines settings for the internal timer Table 107 on page 61
    TReloadReg_High     = 0x2C   #defines the 16-bit timer reload value Table 109 on page 62
    TReloadReg_Low      = 0x2D   #Table 111 on page 62
    TCounterValReg_High = 0x2E   #shows the 16-bit timer value Table 113 on page 63
    TCounterValReg_Low  = 0x2F   #Table 115 on page 63
    ### Page 3: Test register
    TestSel1Reg         = 0x31   #general test signal configuration Table 119 on page 63
    TestSel2Reg         = 0x32   #general test signal configuration and PRBS control Table 121 on page 64
    TestPinEnReg        = 0x33   #enables pin output driver on pins D1 to D7 Table 123 on page 64
    TestPinValueReg     = 0x34   #defines the values for D1 to D7 when it is used as an I/O bus Table 125 on page 65
    TestBusReg          = 0x35   #shows the flag of the internal test bus Table 127 on page 65
    AutoTestReg         = 0x36   #controls the digital self test Table 129 on page 66
    VersionReg          = 0x37   #shows the software version Table 131 on page 66
    AnalogTestReg       = 0x38   #controls the pins AUX1 and AUX2 Table 133 on page 67
    TestDAC1Reg         = 0x39   #defines the test value for TestDAC1 Table 135 on page 68
    TestDAC2Reg         = 0x3A   #defines the test value for TestDAC2 Table 137 on page 68
    TestADCReg          = 0x3B   #shows the value of ADC I and Q channels Table 139 on page 68

    ###
    ### Put your variable here
    ###
    RPiGPIO_ResetPin        = 22

    SPI_device              = '/dev/spidev0.0'
    SPI_mode                = None
    SPI_bytesPerMessage     = None
    SPI_speed               = 1000000
    SPI_delay               = None

    flag                    = None
    flag_ok                 = 0
    flag_unknown            = 1
    flag_error              = -1


    ###
    ### MFRC522.pdf, Chapter 8.1.2 (8.1.2.1, 8.1.2.2, 8.1.2.3), page 11
    ### read or write to MFRC522
    ###
    def Write(self, address, value):
        spi.transfer(((address<<1)&0x7E,value))

    def Read(self, address):
        data = spi.transfer((((address<<1) & 0x7E) | 0x80, 0))
        return data[1]

    ###
    ### Constructor and destructor
    ###
    def __init__(self):
        self.MFRC522_Construct()

    def MFRC522_Construct(self):
        spi.openSPI(device=self.SPI_device, speed=self.SPI_speed)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.RPiGPIO_ResetPin, GPIO.OUT)
        GPIO.output(self.RPiGPIO_ResetPin, 1)
        self.MFRC522_Reset()
        self.Write(self.ModeReg, 0x3D)
        self.Write(self.TxASKReg, 0x40)
        self.Write(self.TModeReg, 0x8D)
        self.Write(self.TPrescalerReg, 0x3E)
        self.Write(self.TReloadReg_High, 0x00)
        self.Write(self.TReloadReg_Low, 0x1E)
        self.MFRC522_AntennaOn()

    def __del__(self):
        self.MFRC522_Destruct()

    def MFRC522_Destruct(self):
        self.MFRC522_AntennaOff()
        self.MFRC522_Reset()
        GPIO.output(self.RPiGPIO_ResetPin, 0)
        GPIO.cleanup()
        spi.closeSPI()


    ###
    ### Your function here
    ###
    # Use SetBitMask when you want to set certain bit to 1
    def SetBitMask(self, register, mask):
        value = self.Read(register)
        self.Write(register, value | mask)

    # Use ClearBitMask when you want to set certain bit to 0
    def ClearBitMask(self, register, mask):
        value = self.Read(register);
        self.Write(register, value & (~mask))

    # Use MFRC522_Reset when you want to reset the MFRC522
    def MFRC522_Reset(self):
        self.Write(self.CommandReg, self.SoftReset)

    # Use MFRC522_AntennaOn to set pin TX2 and pin TX1 to 1
    # output signal on pin TX2 delivers the 13.56 MHz energy carrier modulated by the transmission data
    # output signal on pin TX1 delivers the 13.56 MHz energy carrier modulated by the transmission data
    def MFRC522_AntennaOn(self):
        value = self.Read(self.TxControlReg)
        if(~(value & 0x03)):
            self.SetBitMask(self.TxControlReg, 0x03)

    # Use MFRC522_AntennaOn to set pin TX2 and pin TX1 to 1
    def MFRC522_AntennaOff(self):
        self.ClearBitMask(self.TxControlReg, 0x03)

    def MFRC522_Request(self, request_mode):
        flag = None
        bits = None
        TagType = []
        self.Write(self.BitFramingReg, 0x07)
        TagType.append(request_mode);
        (flag,receiveData,bits) = self.MFRC522_SolveCommandCode(self.Transceive, TagType)
        if ((flag != self.flag_ok) | (bits != 0x10)):
            flag = self.flag_error
        return (flag,bits)


    def MFRC522_Anticoll(self):
        receiveData = []
        serNumCheck = 0
        serNum = []
        self.Write(self.BitFramingReg, 0x00)
        serNum.append(0x93)
        serNum.append(0x20)
        (flag,receiveData,bits) = self.MFRC522_SolveCommandCode(self.Transceive,serNum)
        if(flag == self.flag_ok):
            i = 0
            if len(receiveData)==5:
                while i<4:
                    serNumCheck = serNumCheck ^ receiveData[i]
                    i = i + 1
                if serNumCheck != receiveData[i]:
                    flag = self.flag_error
            else:
                flag = self.flag_error
        return (flag,receiveData)


    def MFRC522_SolveCommandCode(self,command,sendData):
        receiveData = []
        bits = 0
        flag = None
        irqEn = 0x00
        waitIrq = 0x00
        lastBit = None
        n = 0
        i = 0
        c = None
        d = 0
        if command == self.MFAuthent:
            irqEn = 0x12
            waitIrq = 0x10
        elif command == self.Transceive:
            irqEn = 0x77
            waitIrq = 0x30
        self.Write(self.ComlEnReg, irqEn|0x80)
        self.ClearBitMask(self.ComIrqReg, 0x80)
        self.SetBitMask(self.FIFOLevelReg, 0x80)
        self.Write(self.CommandReg, self.Idle);
        for c in sendData:
            self.Write(self.FIFODataReg, c)
        self.Write(self.CommandReg, command)
        if command == self.Transceive:
            self.SetBitMask(self.BitFramingReg, 0x80)
        i = 2000
        while True:
            n = self.Read(self.ComIrqReg)
            i = i - 1
            if ~((i != 0) and ~(n & 0x01) and ~(n & waitIrq)):
                break
        self.ClearBitMask(self.BitFramingReg, 0x80)
        if i != 0:
            if (self.Read(self.ErrorReg) & 0x1B)==0x00:
                flag = self.flag_ok
                if n & irqEn & 0x01:
                    flag = self.flag_unknown
                if command == self.Transceive:
                    n = self.Read(self.FIFOLevelReg)
                    lastBit = self.Read(self.ControlReg) & 0x07
                    if lastBit != 0:
                        bits = (n-1)*8 + lastBit
                    else:
                        bits = n*8
                    if n == 0:
                        n = 1
                    elif n > 16:
                        n = 16
                    for d in range(n):
                        receiveData.append(self.Read(self.FIFODataReg))
            else:
                flag = self.flag_error
        return (flag,receiveData,bits)
