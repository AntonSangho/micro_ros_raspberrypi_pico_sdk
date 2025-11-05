"""
MFRC522 GPIO 기본 테스트

CS(GP13)와 RST(GP14) 핀을 토글하여 GPIO가 정상 작동하는지 확인합니다.
멀티미터나 오실로스코프로 전압 변화를 확인할 수 있습니다.
"""

from machine import Pin
import time

print("=" * 50)
print("MFRC522 GPIO 토글 테스트")
print("=" * 50)

# MFRC522 핀 정의
cs = Pin(13, Pin.OUT)
rst = Pin(14, Pin.OUT)

print("\n핀 설정:")
print(f"  CS:  GP13")
print(f"  RST: GP14")

print("\n10회 토글 시작 (멀티미터로 전압 확인)")
print("각 핀이 0V ↔ 3.3V로 변경되어야 합니다.\n")

for i in range(10):
    # HIGH 상태
    cs.value(1)
    rst.value(1)
    print(f"[{i+1:2d}] CS=HIGH (3.3V), RST=HIGH (3.3V)")
    time.sleep(0.5)

    # LOW 상태
    cs.value(0)
    rst.value(0)
    print(f"[{i+1:2d}] CS=LOW  (0V),   RST=LOW  (0V)")
    time.sleep(0.5)

# 정상 상태로 복귀
cs.value(1)   # CS는 평상시 HIGH
rst.value(1)  # RST는 평상시 HIGH

print("\n" + "=" * 50)
print("GPIO 테스트 완료")
print("정상 상태: CS=HIGH, RST=HIGH")
print("=" * 50)
