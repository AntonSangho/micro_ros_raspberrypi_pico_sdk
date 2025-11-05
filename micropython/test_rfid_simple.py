"""
MFRC522 간단한 초기화 테스트

MFRC522를 초기화하고 기본 설정을 확인합니다.
"""

from machine import Pin, SPI
import time

class MFRC522Simple:
    """간단한 MFRC522 테스트 클래스"""

    def __init__(self):
        """초기화"""
        print("MFRC522 초기화 중...")

        # SPI0 초기화 (Pico W에서 동작 확인됨)
        self.spi = SPI(0, baudrate=4000000, polarity=0, phase=0,
                      sck=Pin(2), mosi=Pin(3), miso=Pin(4))

        # 제어 핀
        self.cs = Pin(1, Pin.OUT, value=1)
        self.rst = Pin(0, Pin.OUT, value=1)

        # 하드웨어 리셋
        self.reset()

    def reset(self):
        """하드웨어 리셋"""
        print("  하드웨어 리셋...")
        self.rst.value(0)
        time.sleep_ms(10)
        self.rst.value(1)
        time.sleep_ms(50)

    def read_reg(self, addr):
        """레지스터 읽기"""
        self.cs.value(0)
        tx = bytes([0x80 | (addr << 1), 0x00])
        rx = bytearray(2)
        self.spi.write_readinto(tx, rx)
        self.cs.value(1)
        return rx[1]

    def write_reg(self, addr, val):
        """레지스터 쓰기"""
        self.cs.value(0)
        self.spi.write(bytes([addr << 1, val]))
        self.cs.value(1)

    def check_version(self):
        """버전 확인"""
        print("  버전 레지스터 확인...")
        version = self.read_reg(0x37)
        print(f"  MFRC522 펌웨어 버전: 0x{version:02X}")

        if version == 0x91:
            print("  ✓ MFRC522 Version 1.0")
            return True
        elif version == 0x92:
            print("  ✓ MFRC522 Version 2.0")
            return True
        elif version == 0x00:
            print("  ✗ 통신 실패: MISO 연결 문제 (0x00)")
            return False
        elif version == 0xFF:
            print("  ✗ 통신 실패: MISO floating (0xFF)")
            return False
        else:
            print(f"  ✗ 알 수 없는 버전: 0x{version:02X}")
            return False

    def soft_reset(self):
        """소프트웨어 리셋"""
        print("  소프트웨어 리셋...")
        self.write_reg(0x01, 0x0F)  # CommandReg: SoftReset
        time.sleep_ms(50)

    def configure(self):
        """기본 설정"""
        print("  타이머 설정...")
        self.write_reg(0x2A, 0x80)  # TModeReg
        self.write_reg(0x2B, 0xA9)  # TPrescalerReg
        self.write_reg(0x2C, 0x03)  # TReloadRegH
        self.write_reg(0x2D, 0xE8)  # TReloadRegL

        print("  변조 설정...")
        self.write_reg(0x15, 0x40)  # TxASKReg
        self.write_reg(0x11, 0x3D)  # ModeReg

    def antenna_on(self):
        """안테나 켜기"""
        print("  안테나 활성화...")
        val = self.read_reg(0x14)  # TxControlReg
        if (val & 0x03) != 0x03:
            self.write_reg(0x14, val | 0x03)

        # 안테나 게인 최대로 설정
        self.write_reg(0x26, 0x07 << 4)  # RFCfgReg: RxGain = 48dB
        print("  안테나 게인: 최대 (48dB)")

    def init(self):
        """완전 초기화"""
        print("\nMFRC522 완전 초기화")
        print("-" * 40)

        if not self.check_version():
            return False

        self.soft_reset()
        self.configure()
        self.antenna_on()

        print("-" * 40)
        print("✓ MFRC522 초기화 완료!\n")
        return True


# 메인 테스트
if __name__ == "__main__":
    print("=" * 50)
    print("MFRC522 간단한 초기화 테스트")
    print("=" * 50)
    print()

    try:
        rfid = MFRC522Simple()

        if rfid.init():
            print("다음 테스트: test_card_scan.py")
            print("카드 스캔을 테스트하려면 위 파일을 실행하세요.")
        else:
            print("초기화 실패!")
            print("\n배선을 확인하세요:")
            print("  SDA (MFRC522) → GP1 (Pico)")
            print("  SCK (MFRC522) → GP2 (Pico)")
            print("  MOSI(MFRC522) → GP3 (Pico)")
            print("  MISO(MFRC522) → GP4 (Pico)")
            print("  RST (MFRC522) → GP0 (Pico)")
            print("  3.3V(MFRC522) → 3V3 (Pico)")
            print("  GND (MFRC522) → GND (Pico)")

    except Exception as e:
        print(f"\n오류 발생: {e}")

    print("\n" + "=" * 50)
