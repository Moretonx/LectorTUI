import RPi.GPIO as GPIO
import spidev
import time
import binascii


class MFRC522:
    # =========================
    # CONFIG HARDWARE (BCM)
    # =========================
    NRSTPD = 25  # BCM25 = pin físico 22

    MAX_LEN = 16

    # =========================
    # MFRC522 COMMANDS
    # =========================
    PCD_IDLE = 0x00
    PCD_AUTHENT = 0x0E
    PCD_RECEIVE = 0x08
    PCD_TRANSMIT = 0x04
    PCD_TRANSCEIVE = 0x0C
    PCD_RESETPHASE = 0x0F
    PCD_CALCCRC = 0x03

    PICC_REQIDL = 0x26
    PICC_REQALL = 0x52
    PICC_ANTICOLL = 0x93
    PICC_SElECTTAG = 0x93
    PICC_AUTHENT1A = 0x60
    PICC_AUTHENT1B = 0x61
    PICC_READ = 0x30
    PICC_WRITE = 0xA0
    PICC_HALT = 0x50

    MI_OK = 0
    MI_NOTAGERR = 1
    MI_ERR = 2

    # =========================
    # MFRC522 REGISTERS
    # =========================
    CommandReg = 0x01
    CommIEnReg = 0x02
    CommIrqReg = 0x04
    ErrorReg = 0x06
    Status2Reg = 0x08
    FIFODataReg = 0x09
    FIFOLevelReg = 0x0A
    ControlReg = 0x0C
    BitFramingReg = 0x0D
    ModeReg = 0x11
    TxControlReg = 0x14
    TxAutoReg = 0x15
    TModeReg = 0x2A
    TPrescalerReg = 0x2B
    TReloadRegH = 0x2C
    TReloadRegL = 0x2D
    CRCResultRegM = 0x21
    CRCResultRegL = 0x22

    def __init__(self, bus=0, device=0, speed=1000000):
        # SPI
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = speed

        # GPIO BCM
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.NRSTPD, GPIO.OUT)
        GPIO.output(self.NRSTPD, 1)

        self.MFRC522_Init()

    # =========================
    # LOW LEVEL IO
    # =========================
    def Write_MFRC522(self, addr, val):
        self.spi.xfer2([(addr << 1) & 0x7E, val])

    def Read_MFRC522(self, addr):
        val = self.spi.xfer2([((addr << 1) & 0x7E) | 0x80, 0])
        return val[1]

    def SetBitMask(self, reg, mask):
        self.Write_MFRC522(reg, self.Read_MFRC522(reg) | mask)

    def ClearBitMask(self, reg, mask):
        self.Write_MFRC522(reg, self.Read_MFRC522(reg) & (~mask))

    # =========================
    # CORE FUNCTIONS
    # =========================
    def MFRC522_Reset(self):
        self.Write_MFRC522(self.CommandReg, self.PCD_RESETPHASE)

    def AntennaOn(self):
        if not (self.Read_MFRC522(self.TxControlReg) & 0x03):
            self.SetBitMask(self.TxControlReg, 0x03)

    def MFRC522_Init(self):
        self.MFRC522_Reset()
        self.Write_MFRC522(self.TModeReg, 0x8D)
        self.Write_MFRC522(self.TPrescalerReg, 0x3E)
        self.Write_MFRC522(self.TReloadRegL, 30)
        self.Write_MFRC522(self.TReloadRegH, 0)
        self.Write_MFRC522(self.TxAutoReg, 0x40)
        self.Write_MFRC522(self.ModeReg, 0x3D)
        self.AntennaOn()

    # =========================
    # CARD COMMUNICATION
    # =========================
    def MFRC522_ToCard(self, command, sendData):
        backData = []
        backLen = 0
        status = self.MI_ERR

        irqEn = 0x12 if command == self.PCD_AUTHENT else 0x77
        waitIRq = 0x10 if command == self.PCD_AUTHENT else 0x30

        self.Write_MFRC522(self.CommIEnReg, irqEn | 0x80)
        self.ClearBitMask(self.CommIrqReg, 0x80)
        self.SetBitMask(self.FIFOLevelReg, 0x80)
        self.Write_MFRC522(self.CommandReg, self.PCD_IDLE)

        for byte in sendData:
            self.Write_MFRC522(self.FIFODataReg, byte)

        self.Write_MFRC522(self.CommandReg, command)
        if command == self.PCD_TRANSCEIVE:
            self.SetBitMask(self.BitFramingReg, 0x80)

        i = 200
        while True:
            n = self.Read_MFRC522(self.CommIrqReg)
            i -= 1
            if not (i and not (n & 0x01) and not (n & waitIRq)):
                break

        self.ClearBitMask(self.BitFramingReg, 0x80)

        if i and not (self.Read_MFRC522(self.ErrorReg) & 0x1B):
            status = self.MI_OK
            if command == self.PCD_TRANSCEIVE:
                n = self.Read_MFRC522(self.FIFOLevelReg)
                backData = [self.Read_MFRC522(self.FIFODataReg) for _ in range(n)]
                backLen = n * 8

        return status, backData, backLen

    # =========================
    # CARD OPS
    # =========================
    def MFRC522_Request(self, reqMode):
        self.Write_MFRC522(self.BitFramingReg, 0x07)
        status, _, backBits = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, [reqMode])
        return status, backBits

    def MFRC522_Anticoll(self):
        self.Write_MFRC522(self.BitFramingReg, 0x00)
        status, backData, _ = self.MFRC522_ToCard(
            self.PCD_TRANSCEIVE, [self.PICC_ANTICOLL, 0x20]
        )
        return status, backData

    def MFRC522_Auth(self, authMode, blockAddr, key, uid):
        buff = [authMode, blockAddr] + key + uid[:4]
        status, _, _ = self.MFRC522_ToCard(self.PCD_AUTHENT, buff)

        if (self.Read_MFRC522(self.Status2Reg) & 0x08) == 0:
            print("AUTH ERROR(status2reg & 0x08) == 0")

        return status

    def MFRC522_StopCrypto1(self):
        self.ClearBitMask(self.Status2Reg, 0x08)

    # =========================
    # READ BLOCK (PYTHON 3 SAFE)
    # =========================
    def MFRC522_Read(self, blockAddr):
        recvData = [self.PICC_READ, blockAddr]
        crc = self.CalulateCRC(recvData)
        recvData += crc

        status, backData, _ = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, recvData)
        if status != self.MI_OK or len(backData) != 16:
            return None

        raw = bytes(backData)
        hexs = binascii.hexlify(raw).decode("ascii")
        text = raw.decode("latin-1", errors="ignore").replace("\x00", "").strip()

        # === Formato legado (como tú lo usabas) ===
        if blockAddr == 68:
            return hexs[1:9] + "-" + hexs[9:10]

        if blockAddr in (72, 73, 74, 80):
            return text

        return text

    # =========================
    # CRC
    # =========================
    def CalulateCRC(self, data):
        self.ClearBitMask(self.CommIrqReg, 0x04)
        self.SetBitMask(self.FIFOLevelReg, 0x80)

        for d in data:
            self.Write_MFRC522(self.FIFODataReg, d)

        self.Write_MFRC522(self.CommandReg, self.PCD_CALCCRC)

        i = 0xFF
        while i:
            if self.Read_MFRC522(self.CommIrqReg) & 0x04:
                break
            i -= 1

        return [
            self.Read_MFRC522(self.CRCResultRegL),
            self.Read_MFRC522(self.CRCResultRegM),
        ]

    def Close_MFRC522(self):
        self.spi.close()
        GPIO.cleanup()