"""
MFRC522 SPI 통신 테스트

SPI0을 초기화하고 MFRC522의 버전 레지스터(0x37)를 읽습니다.
정상 동작 시 0x91 또는 0x92를 반환해야 합니다.
"""

from machine import Pin, SPI
import time

print("=" * 50)
print("MFRC522 SPI 통신 테스트")
print("=" * 50)

# SPI0 초기화 (Pico W에서 동작 확인됨)
print("\n[1] SPI0 초기화")
spi = SPI(0,
          baudrate=4000000,    # 4MHz
          polarity=0,          # CPOL=0
          phase=0,             # CPHA=0
          sck=Pin(2),          # SCK: GP2
          mosi=Pin(3),         # MOSI: GP3
          miso=Pin(4))         # MISO: GP4

print(f"    SPI 설정: {spi}")
print(f"    Baudrate: 4MHz")
print(f"    Mode: 0 (CPOL=0, CPHA=0)")

# 제어 핀 초기화
cs = Pin(1, Pin.OUT, value=1)    # CS: 평상시 HIGH
rst = Pin(0, Pin.OUT, value=1)   # RST: 평상시 HIGH

print(f"    CS:  GP1 (초기값: HIGH)")
print(f"    RST: GP0 (초기값: HIGH)")

# MFRC522 리셋
print("\n[2] MFRC522 리셋")
rst.value(0)
print("    RST = LOW")
time.sleep_ms(10)
rst.value(1)
print("    RST = HIGH")
time.sleep_ms(50)
print("    리셋 완료")

# 버전 레지스터 읽기 함수
def read_register(addr):
    """레지스터 읽기"""
    cs.value(0)  # CS LOW - 통신 시작
    time.sleep_us(10)

    # 읽기 명령: 0x80 | (address << 1)
    tx = bytes([0x80 | (addr << 1), 0x00])
    rx = bytearray(2)
    spi.write_readinto(tx, rx)

    time.sleep_us(10)
    cs.value(1)  # CS HIGH - 통신 종료

    return rx[1]  # 두 번째 바이트가 실제 데이터

# 버전 레지스터 읽기
print("\n[3] MFRC522 버전 레지스터(0x37) 읽기")
print()

success = False
for attempt in range(3):
    version = read_register(0x37)

    print(f"시도 {attempt + 1}/3: ", end="")
    print(f"버전 = 0x{version:02X} ", end="")

    if version == 0x91:
        print("✓ MFRC522 Version 1.0 감지!")
        success = True
        break
    elif version == 0x92:
        print("✓ MFRC522 Version 2.0 감지!")
        success = True
        break
    elif version == 0x00:
        print("✗ FAIL: MISO 연결 안 됨 또는 전원 문제")
    elif version == 0xFF:
        print("✗ FAIL: MISO floating (연결 확인 필요)")
    else:
        print(f"✗ WARNING: 예상치 못한 값 (0x91 또는 0x92 예상)")

    if attempt < 2:
        time.sleep(0.5)

print("\n" + "=" * 50)
if success:
    print("SPI 통신 성공!")
    print("MFRC522가 정상 작동 중입니다.")
else:
    print("SPI 통신 실패")
    print("\n배선 확인:")
    print("  MISO (MFRC522) → GP4 (Pico)")
    print("  MOSI (MFRC522) → GP3 (Pico)")
    print("  SCK  (MFRC522) → GP2 (Pico)")
    print("  SDA  (MFRC522) → GP1 (Pico)")
    print("  GND  (MFRC522) → GND (Pico)")
    print("  3.3V (MFRC522) → 3V3 (Pico)")
print("=" * 50)
