"""
MFRC522 RFID 리더 MicroPython 라이브러리

이 라이브러리는 MFRC522 RFID 리더를 제어하기 위한 간단한 드라이버입니다.
"""

from machine import Pin, SPI
import time

class MFRC522:
    """MFRC522 RFID 리더 드라이버"""

    # 레지스터 주소
    CommandReg = 0x01
    ComIEnReg = 0x02
    ComIrqReg = 0x04
    ErrorReg = 0x06
    Status2Reg = 0x08
    FIFODataReg = 0x09
    FIFOLevelReg = 0x0A
    ControlReg = 0x0C
    BitFramingReg = 0x0D
    ModeReg = 0x11
    TxControlReg = 0x14
    TxASKReg = 0x15
    RFCfgReg = 0x26
    TModeReg = 0x2A
    TPrescalerReg = 0x2B
    TReloadRegH = 0x2C
    TReloadRegL = 0x2D
    VersionReg = 0x37

    # 명령
    PCD_Idle = 0x00
    PCD_Transceive = 0x0C
    PCD_SoftReset = 0x0F

    # PICC 명령
    PICC_REQIDL = 0x26
    PICC_REQALL = 0x52
    PICC_ANTICOLL = 0x93
    PICC_SELECTTAG = 0x93
    PICC_HALT = 0x50

    def __init__(self, spi_id=0, sck=2, mosi=3, miso=4, cs=1, rst=0):
        """
        초기화 (Pico W에서 동작 확인된 SPI0 설정)

        Args:
            spi_id: SPI 버스 번호 (기본: 0)
            sck: SCK 핀 번호 (기본: 2)
            mosi: MOSI 핀 번호 (기본: 3)
            miso: MISO 핀 번호 (기본: 4)
            cs: CS 핀 번호 (기본: 1)
            rst: RST 핀 번호 (기본: 0)
        """
        self.spi = SPI(spi_id, baudrate=4000000, polarity=0, phase=0,
                      sck=Pin(sck), mosi=Pin(mosi), miso=Pin(miso))
        self.cs = Pin(cs, Pin.OUT, value=1)
        self.rst = Pin(rst, Pin.OUT, value=1)

        self.reset()
        self.init()

    def reset(self):
        """하드웨어 리셋"""
        self.rst.value(0)
        time.sleep_ms(10)
        self.rst.value(1)
        time.sleep_ms(50)

    def write_reg(self, addr, val):
        """레지스터 쓰기"""
        self.cs.value(0)
        self.spi.write(bytes([addr << 1, val]))
        self.cs.value(1)

    def read_reg(self, addr):
        """레지스터 읽기"""
        self.cs.value(0)
        tx = bytes([0x80 | (addr << 1), 0x00])
        rx = bytearray(2)
        self.spi.write_readinto(tx, rx)
        self.cs.value(1)
        return rx[1]

    def set_bitmask(self, addr, mask):
        """비트 마스크 설정"""
        val = self.read_reg(addr)
        self.write_reg(addr, val | mask)

    def clear_bitmask(self, addr, mask):
        """비트 마스크 클리어"""
        val = self.read_reg(addr)
        self.write_reg(addr, val & (~mask))

    def init(self):
        """MFRC522 초기화"""
        # 소프트웨어 리셋
        self.write_reg(self.CommandReg, self.PCD_SoftReset)
        time.sleep_ms(50)

        # 타이머 설정
        self.write_reg(self.TModeReg, 0x80)
        self.write_reg(self.TPrescalerReg, 0xA9)
        self.write_reg(self.TReloadRegH, 0x03)
        self.write_reg(self.TReloadRegL, 0xE8)

        # 변조 설정
        self.write_reg(self.TxASKReg, 0x40)
        self.write_reg(self.ModeReg, 0x3D)

        # 안테나 켜기
        self.antenna_on()

    def antenna_on(self):
        """안테나 켜기"""
        val = self.read_reg(self.TxControlReg)
        if (val & 0x03) != 0x03:
            self.write_reg(self.TxControlReg, val | 0x03)

        # 안테나 게인 최대
        self.write_reg(self.RFCfgReg, 0x07 << 4)

    def antenna_off(self):
        """안테나 끄기"""
        self.clear_bitmask(self.TxControlReg, 0x03)

    def get_version(self):
        """펌웨어 버전 확인"""
        return self.read_reg(self.VersionReg)

    def card_write(self, command, data):
        """카드에 데이터 쓰기"""
        back_data = []
        back_len = 0
        irq_en = 0x77
        wait_irq = 0x30

        # 인터럽트 설정
        self.write_reg(self.ComIEnReg, irq_en | 0x80)
        self.clear_bitmask(self.ComIrqReg, 0x80)
        self.set_bitmask(self.FIFOLevelReg, 0x80)

        self.write_reg(self.CommandReg, self.PCD_Idle)

        # FIFO에 데이터 쓰기
        for byte in data:
            self.write_reg(self.FIFODataReg, byte)

        # 명령 실행
        self.write_reg(self.CommandReg, command)

        if command == self.PCD_Transceive:
            self.set_bitmask(self.BitFramingReg, 0x80)

        # 응답 대기
        i = 2000
        while True:
            n = self.read_reg(self.ComIrqReg)
            i -= 1
            if not ((i != 0) and not (n & 0x01) and not (n & wait_irq)):
                break

        self.clear_bitmask(self.BitFramingReg, 0x80)

        if i != 0:
            if (self.read_reg(self.ErrorReg) & 0x1B) == 0x00:
                if command == self.PCD_Transceive:
                    n = self.read_reg(self.FIFOLevelReg)
                    back_len = n

                    for i in range(n):
                        back_data.append(self.read_reg(self.FIFODataReg))

                return (True, back_data, back_len)

        return (False, None, 0)

    def request(self, req_mode=0x26):
        """
        카드 감지 요청

        Args:
            req_mode: 0x26 = IDLE, 0x52 = ALL

        Returns:
            (status, tag_type)
        """
        self.write_reg(self.BitFramingReg, 0x07)

        (status, back_data, back_len) = self.card_write(self.PCD_Transceive, [req_mode])

        if status and back_len == 2:
            return (True, back_data)
        else:
            return (False, None)

    def anticoll(self):
        """
        충돌 방지 및 UID 읽기

        Returns:
            (status, uid)
        """
        self.write_reg(self.BitFramingReg, 0x00)

        serial_num = [self.PICC_ANTICOLL, 0x20]

        (status, back_data, back_len) = self.card_write(self.PCD_Transceive, serial_num)

        if status and back_len == 5:
            # 체크섬 확인
            check = 0
            for i in range(4):
                check ^= back_data[i]

            if check == back_data[4]:
                return (True, back_data[:4])

        return (False, None)

    def select_tag(self, uid):
        """
        카드 선택

        Args:
            uid: 카드 UID (4바이트)

        Returns:
            status
        """
        buf = [self.PICC_SELECTTAG, 0x70]
        buf.extend(uid)

        # 체크섬 계산
        check = 0
        for byte in uid:
            check ^= byte
        buf.append(check)

        (status, back_data, back_len) = self.card_write(self.PCD_Transceive, buf)

        return status and back_len == 1

    def halt(self):
        """카드를 HALT 상태로"""
        (status, back_data, back_len) = self.card_write(self.PCD_Transceive, [self.PICC_HALT, 0])
