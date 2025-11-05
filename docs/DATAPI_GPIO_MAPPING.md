# DataPi 보드 GPIO 핀 할당 맵

이 문서는 DataPi 개발 보드에 연결된 Raspberry Pi Pico W의 GPIO 핀 사용 현황과 추가 센서/모듈을 위한 사용 가능한 핀을 정리합니다.

## 사용 중인 GPIO 핀

### I2C 통신 (I2C0)

**공통 버스**: GP4 (SCL), GP5 (SDA)

| 장치 | 모델 | SCL | SDA | 주소 | 용도 |
|------|------|-----|-----|------|------|
| RTC | DS3231 | GP4 | GP5 | 0x68 | 실시간 시계 |
| Light Sensor | BH1750 | GP4 | GP5 | 0x23 | 조도 센서 |
| Temp/Humidity | AHT20 | GP4 | GP5 | 0x38 | 온습도 센서 |

### SPI 통신 (SPI0)

| 장치 | 핀 이름 | GPIO | 기능 |
|------|---------|------|------|
| SDCard | MISO | GP16 | SPI0 RX |
| SDCard | CS (SC) | GP17 | Chip Select |
| SDCard | SCK | GP18 | SPI0 SCK |
| SDCard | MOSI | GP19 | SPI0 TX |

### 1-Wire 통신

| 장치 | 모델 | GPIO | 용도 |
|------|------|------|------|
| NeoPixel | WS2812B | GP21 | LED 제어 |

### 디지털 출력

| 장치 | 모델 | GPIO | 용도 |
|------|------|------|------|
| Buzzer | MLT-7525 | GP22 | 부저 |

### 디지털 입력

| 장치 | 이름 | GPIO | 용도 |
|------|------|------|------|
| Button | SW1 | GP20 | 택타일 스위치 |

### 아날로그 입력 (ADC)

| 장치 | 핀 이름 | GPIO | ADC 채널 | 용도 |
|------|---------|------|---------|------|
| Battery Monitor | BAT_DIV | GP27 | ADC1 | 배터리 전압 분배 |

## 사용 가능한 GPIO 핀

### 디지털 I/O 사용 가능

| GPIO | 대체 기능 | 추천 용도 |
|------|----------|----------|
| GP0 | UART0 TX | UART 통신, 디지털 I/O |
| GP1 | UART0 RX | UART 통신, 디지털 I/O |
| GP2 | I2C1 SDA | I2C 확장, 디지털 I/O |
| GP3 | I2C1 SCL | I2C 확장, 디지털 I/O |
| GP6 | SPI0 SCK | 디지털 I/O |
| GP7 | SPI0 TX | 디지털 I/O |
| GP8 | SPI1 RX | SPI 확장, 디지털 I/O |
| GP9 | SPI1 CSn | SPI 확장, 디지털 I/O |
| GP10 | SPI1 SCK | **SPI1 사용 가능** |
| GP11 | SPI1 TX | **SPI1 사용 가능** |
| GP12 | SPI1 RX | **SPI1 사용 가능** |
| GP13 | SPI1 CSn | **SPI1 사용 가능** |
| GP14 | - | 디지털 I/O |
| GP15 | - | 디지털 I/O |
| GP26 | ADC0 | ADC 입력, 디지털 I/O |
| GP28 | ADC2 | ADC 입력, 디지털 I/O |

### 내부 사용 (사용 불가)

| GPIO | 용도 |
|------|------|
| GP23 | SMPS 전원 제어 (Pico W) |
| GP24 | VBUS 감지 |
| GP25 | 내장 LED (Pico W에서는 CYW43 제어) |
| GP29 | VSYS ADC |

## 추가 모듈 연결 권장 사항

### MFRC522 RFID 리더 (현재 프로젝트)

**SPI1 사용** (SDCard와 충돌 방지)

| MFRC522 핀 | GPIO | 기능 |
|-----------|------|------|
| MISO | GP12 | SPI1 RX |
| CS | GP13 | Chip Select |
| SCK | GP10 | SPI1 SCK |
| MOSI | GP11 | SPI1 TX |
| RST | GP14 | Reset |

### I2C 확장 장치

I2C1 버스 사용 권장 (GP2, GP3):
- 기존 I2C0 (GP4, GP5)에 이미 3개 장치 연결됨
- I2C1을 사용하면 버스 부하 분산 가능

### UART 통신

UART0 사용 가능 (GP0 TX, GP1 RX):
- GPS 모듈
- 시리얼 디스플레이
- 다른 마이크로컨트롤러와 통신

## 핀 충돌 주의사항

### SPI 버스 분리

- **SPI0 (GP16-GP19)**: SDCard 전용
  - GP16: MISO
  - GP17: CS
  - GP18: SCK
  - GP19: MOSI
- **SPI1 (GP10-GP13)**: MFRC522 및 추가 SPI 장치용
  - GP10: SCK
  - GP11: MOSI
  - GP12: MISO
  - GP13: CS

이렇게 분리하면 SDCard와 RFID를 동시 사용 가능하고 충돌 없음

## 전원 핀

| 핀 이름 | 전압 | 최대 전류 | 용도 |
|--------|------|---------|------|
| 3V3(OUT) | 3.3V | 300mA | 외부 센서 전원 |
| VSYS | 1.8-5.5V | - | 시스템 전원 입력 |
| VBUS | 5V | 500mA | USB 전원 |
| GND | 0V | - | 접지 |

**전원 주의사항**:
- 3V3(OUT)에서 공급 가능한 최대 전류: 약 300mA
- 여러 센서 사용 시 전류 소비량 고려
- MFRC522, BH1750, AHT20, DS3231 등 합산하면 약 100-150mA

## GPIO 핀 맵 요약

```
         Raspberry Pi Pico W (DataPi)

    GP0  [ ] [ ] VBUS      GP1  [ ] [ ] VSYS
    GP2  [ ] [ ] GND       GP3  [ ] [ ] 3V3_EN
    GP4  [I] [I] ADC_VREF  GP5  [I] [ ] GP28 [A]
    GND  [ ] [ ] GND       GP6  [ ] [ ] AGND
    GP7  [ ] [ ] GP27 [A]  GP8  [ ] [ ] GP26 [A]
    GP9  [ ] [ ] RUN       GP10 [R] [ ] GP22 [B]
    GP11 [R] [R] GP21 [N]  GP12 [R] [D] GP20
    GP13 [R] [S] GP19 [S]  GND  [ ] [S] GP18 [S]
    GP14 [R] [S] GP17 [S]  GP15 [ ] [S] GP16 [S]

범례:
[I] I2C 사용 중 (DS3231, BH1750, AHT20)
[S] SPI0 사용 중 (SDCard)
[R] RFID (SPI1)
[N] NeoPixel
[B] Buzzer
[D] Button
[A] ADC 사용 중/가능
[ ] 사용 가능
```

## 참고 자료

- [DataPi PCB 저장소](https://github.com/AntonSangho/DataPi_PCB_v0_3)
- [Raspberry Pi Pico W 핀아웃](https://datasheets.raspberrypi.com/picow/pico-w-datasheet.pdf)
- [RP2040 데이터시트](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
