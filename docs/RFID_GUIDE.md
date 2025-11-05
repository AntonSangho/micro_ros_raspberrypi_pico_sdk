# RFID 리더 예제 (rfid_reader_example.c)

이 예제는 MFRC522 RFID 리더를 사용하여 RFID 카드를 읽고, UID를 micro-ROS를 통해 ROS 2 토픽으로 퍼블리시합니다.

## 주요 기능

1. **RFID 카드 스캔**: MFRC522를 사용하여 주기적으로 RFID 카드 감지
2. **micro-ROS 퍼블리싱**: 카드 UID를 `/rfid_card_uid` 토픽으로 퍼블리시
3. **LED 상태 표시**: 내장 LED로 현재 상태를 시각적으로 표시

## LED 상태 표시

내장 LED가 다양한 상태를 표시합니다:

- **빠른 깜박임 (100ms)**: 초기화 중
- **천천히 깜박임 (1초)**: 카드 대기 중
- **빠른 깜박임 (200ms)**: 카드 감지됨
- **켜짐**: 퍼블리시 성공
- **꺼짐**: 오류 발생

## 하드웨어 연결

### MFRC522 핀 연결 (SPI0 사용 - Pico W에서 동작 확인됨)

| MFRC522 핀 | Pico W 핀 | GPIO | 기능 |
|-----------|----------|------|------|
| SDA (CS)  | GP1      | 1    | Chip Select |
| SCK       | GP2      | 2    | SPI0 SCK |
| MOSI      | GP3      | 3    | SPI0 TX |
| MISO      | GP4      | 4    | SPI0 RX |
| RST       | GP0      | 0    | Reset |
| 3.3V      | 3V3      | -    | 전원 |
| GND       | GND      | -    | 접지 |

**핀 배치 참고사항**:
- Raspberry Pi Pico W에서 SPI0 포트 사용이 확인되었습니다
- 위의 핀 배치로 정상 동작이 검증되었습니다

**주의**:
- MFRC522는 3.3V 전원을 사용합니다 (5V 연결 시 손상 가능)
- DataPi 보드 사용 시 위 핀 배치를 반드시 따라야 합니다

## 빌드 방법

```bash
cd build
cmake ..
make rfid_reader_example
```

빌드 후 `rfid_reader_example.uf2` 파일이 생성됩니다.

## 플래싱 방법

1. BOOTSEL 버튼을 누른 상태로 Pico W를 USB에 연결
2. RPI-RP2 드라이브가 마운트되면:
   ```bash
   cp rfid_reader_example.uf2 /media/$USER/RPI-RP2
   ```

## micro-ROS Agent 실행

```bash
docker run -it --rm -v /dev:/dev --privileged --net=host \
  microros/micro-ros-agent:humble serial --dev /dev/ttyACM0 -b 115200
```

## ROS 2에서 토픽 확인

```bash
# 토픽 리스트 확인
ros2 topic list

# RFID UID 메시지 확인
ros2 topic echo /rfid_card_uid
```

카드를 MFRC522 리더에 대면 다음과 같은 형식의 메시지가 표시됩니다:

```
data: '93:E3:9A:92'
---
data: '04:2F:A3:B2:C1:5D:80'
---
```

## 동작 원리

1. **초기화**
   - CYW43 (내장 LED) 초기화
   - SPI 및 MFRC522 초기화
   - micro-ROS Agent 연결 대기

2. **메인 루프**
   - 100ms마다 타이머 콜백 실행
   - LED 상태 업데이트
   - 새 카드 감지 확인
   - 카드 UID 읽기 및 퍼블리시

3. **카드 감지 시**
   - UID를 16진수 문자열로 변환 (예: "04:2F:A3:B2")
   - `/rfid_card_uid` 토픽으로 퍼블리시
   - LED를 1초간 켜서 성공 표시

## 지원되는 카드 타입

- MIFARE Classic 1K/4K
- MIFARE Ultralight
- NTAG213/215/216
- 기타 ISO 14443A 호환 카드

## 문제 해결

### MFRC522 초기화 실패
- SPI 연결 확인 (특히 MISO, MOSI, SCK)
- 전원 연결 확인 (3.3V, GND)
- RST 핀 연결 확인

### 카드가 감지되지 않음
- 카드를 리더에 충분히 가까이 대세요 (1-2cm 이내)
- MFRC522 안테나 연결 확인
- 카드가 13.56MHz RFID 카드인지 확인 (125kHz 카드는 지원 안 됨)

### Agent 연결 실패
- USB 케이블 연결 확인
- 시리얼 포트 이름 확인 (`/dev/ttyACM0`)
- micro-ROS Agent가 실행 중인지 확인

## 참고 자료

- [MFRC522 라이브러리](https://github.com/BenjaminModica/pico-mfrc522)
- [MFRC522 데이터시트](https://www.nxp.com/docs/en/data-sheet/MFRC522.pdf)
- [Pico W 핀아웃](https://datasheets.raspberrypi.com/picow/pico-w-datasheet.pdf)
