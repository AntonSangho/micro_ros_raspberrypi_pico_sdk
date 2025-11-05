# Raspberry Pi Pico W + micro-ROS 센서 통합 프로젝트

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Raspberry Pi Pico W에서 micro-ROS를 사용하여 다양한 센서를 제어하고 ROS 2와 실시간 통신하는 통합 프로젝트입니다.

## 프로젝트 개요

이 프로젝트는 RP2040 기반의 Raspberry Pi Pico W 마이크로컨트롤러에서 micro-ROS 클라이언트를 실행하여 ROS 2 시스템과 통신합니다. RFID 리더, 초음파 센서 등 다양한 센서 데이터를 ROS 2 토픽으로 퍼블리시할 수 있습니다.

### 주요 특징

- **micro-ROS 지원**: ROS 2 Humble과 호환되는 micro-ROS 클라이언트
- **Pico W 최적화**: CYW43 WiFi 칩 활용 (내부 LED 제어)
- **센서 통합**:
  - MFRC522 RFID 리더 (SPI0)
  - HC-SR04 초음파 거리 센서
- **유연한 통신**: USB 또는 UART 시리얼 전송
- **MicroPython 지원**: C/C++ 외에 MicroPython 구현 제공

### 아키텍처

```
┌─────────────────────┐         ┌──────────────────┐
│  Raspberry Pi Pico W│         │   Host PC/SBC    │
│  ┌───────────────┐  │  USB/   │  ┌────────────┐  │
│  │ micro-ROS     │  │  UART   │  │ micro-ROS  │  │
│  │ Client        │◄─┼─────────┼─►│ Agent      │  │
│  │               │  │         │  │            │  │
│  │  ┌─────────┐  │  │         │  └─────┬──────┘  │
│  │  │ RFID    │  │  │         │        │         │
│  │  │ Sensor  │  │  │         │  ┌─────▼──────┐  │
│  │  │ etc.    │  │  │         │  │  ROS 2     │  │
│  │  └─────────┘  │  │         │  │  (Humble)  │  │
│  └───────────────┘  │         │  └────────────┘  │
└─────────────────────┘         └──────────────────┘
```

## 빠른 시작

### 1️⃣ 개발 환경 준비

```bash
# 필수 패키지 설치
sudo apt update
sudo apt install -y cmake gcc-arm-none-eabi libnewlib-arm-none-eabi \
    build-essential git python3

# Pico SDK 설치
cd ~
git clone https://github.com/raspberrypi/pico-sdk.git
cd pico-sdk
git submodule update --init

# 환경 변수 설정
echo 'export PICO_SDK_PATH=$HOME/pico-sdk' >> ~/.bashrc
source ~/.bashrc
```

### 2️⃣ 프로젝트 빌드

```bash
# 프로젝트 디렉토리로 이동
cd micro_ros_raspberrypi_pico_sdk

# 빌드
mkdir build && cd build
cmake ..
make rfid_reader_example
```

### 3️⃣ Pico에 플래시

```bash
# BOOTSEL 버튼을 누른 상태로 Pico를 USB에 연결

# UF2 파일 복사
cp rfid_reader_example.uf2 /media/$USER/RPI-RP2/
```

### 4️⃣ micro-ROS Agent 실행

```bash
# Docker로 micro-ROS Agent 실행
docker run -it --rm -v /dev:/dev --privileged --net=host \
  microros/micro-ros-agent:humble serial --dev /dev/ttyACM0 -b 115200
```

### 5️⃣ ROS 2에서 데이터 확인

```bash
# 토픽 리스트 확인
ros2 topic list

# RFID 데이터 모니터링
ros2 topic echo /rfid_card_uid

# 출력 예시:
# data: C9:31:B5:B1
# ---
```

## 예제 프로그램

### RFID 리더 (MFRC522)

RFID 카드 UID를 읽어 ROS 2 토픽으로 퍼블리시합니다.

```bash
make rfid_reader_example
cp rfid_reader_example.uf2 /media/$USER/RPI-RP2/
```

**ROS 2 토픽**: `/rfid_card_uid` (std_msgs/String)

**하드웨어 연결**: [RFID 가이드 참조](docs/RFID_GUIDE.md)

### 초음파 센서 (HC-SR04)

거리 측정 데이터를 ROS 2 토픽으로 퍼블리시합니다.

```bash
make hcsr04_distance_example
cp hcsr04_distance_example.uf2 /media/$USER/RPI-RP2/
```

### LED 제어

Pico W 내부 LED를 제어합니다.

```bash
make led_blink_example
cp led_blink_example.uf2 /media/$USER/RPI-RP2/
```

## 프로젝트 구조

```
micro_ros_raspberrypi_pico_sdk/
├── docs/                          # 📚 모든 문서
│   ├── BUILD_AND_FLASH.md        # 빌드 및 플래시 상세 가이드
│   ├── PROJECT_OVERVIEW.md       # 프로젝트 아키텍처 및 개요
│   ├── RFID_GUIDE.md             # RFID 하드웨어 연결 및 사용법
│   ├── EXAMPLES.md               # 예제 프로그램 설명
│   └── MFRC522_INTEGRATION.md    # MFRC522 통합 과정
├── examples/                      # 🔬 예제 프로그램
│   ├── rfid_reader_example.c     # RFID 리더 예제
│   ├── hcsr04_distance_example.c # 초음파 센서 예제
│   └── led_blink_example.c       # LED 제어 예제
├── external/                      # 📦 외부 라이브러리
│   └── pico-mfrc522/             # MFRC522 RFID 라이브러리
├── micropython/                   # 🐍 MicroPython 구현
│   ├── lib/mfrc522.py            # MFRC522 라이브러리
│   └── test_*.py                 # 테스트 스크립트
├── libmicroros/                   # 🤖 micro-ROS 라이브러리
│   ├── libmicroros.a             # 사전 컴파일된 라이브러리
│   └── include/                  # micro-ROS 헤더 파일
├── CMakeLists.txt                # CMake 빌드 설정
├── pico_uart_transport.c         # UART 전송 구현
└── README.md                     # 이 파일
```

## 📖 문서

### 시작하기
- [빌드 및 플래시 가이드](docs/BUILD_AND_FLASH.md) - Pico SDK 설치부터 플래시까지 전체 과정
- [프로젝트 개요](docs/PROJECT_OVERVIEW.md) - 아키텍처, 빌드 시스템, 전송 계층 설명

### 하드웨어 연결
- [RFID 가이드](docs/RFID_GUIDE.md) - MFRC522 핀 연결 및 사용법
- [예제 프로그램](docs/EXAMPLES.md) - 모든 예제 프로그램 설명

### 개발 참고
- [MFRC522 통합](docs/MFRC522_INTEGRATION.md) - RFID 모듈 통합 과정

## 시스템 요구사항

### 하드웨어
- Raspberry Pi Pico W (권장) 또는 Pico
- MFRC522 RFID 리더 모듈 (선택)
- HC-SR04 초음파 센서 (선택)
- USB 케이블 (데이터 전송 지원)

### 소프트웨어
- Ubuntu 20.04 이상 (또는 Debian 기반 Linux)
- arm-none-eabi-gcc 9.3.1 (필수)
- CMake 3.12 이상
- Pico SDK 1.5.x 이상
- Docker (micro-ROS Agent 실행용)

## 핀 배치 (MFRC522 RFID)

Pico W에서 **SPI0 사용이 검증**되었습니다:

| MFRC522 핀 | Pico W GPIO | 기능 |
|-----------|-------------|------|
| SDA (CS)  | GP1         | Chip Select |
| SCK       | GP2         | SPI0 SCK |
| MOSI      | GP3         | SPI0 TX |
| MISO      | GP4         | SPI0 RX |
| RST       | GP0         | Reset |
| 3.3V      | 3V3         | 전원 |
| GND       | GND         | 접지 |

**중요**: CYW43 WiFi 칩은 PIO를 사용하므로 SPI0/SPI1과 충돌하지 않습니다.

## 문제 해결

### 빌드 오류

**`PICO_SDK_PATH is not defined`**
```bash
export PICO_SDK_PATH=$HOME/pico-sdk
echo 'export PICO_SDK_PATH=$HOME/pico-sdk' >> ~/.bashrc
```

**GCC 버전 불일치**
```bash
arm-none-eabi-gcc --version  # 9.3.1 확인
```

### 플래시 오류

**RPI-RP2 드라이브가 보이지 않음**
- BOOTSEL 버튼을 확실히 누른 상태로 USB 연결
- USB 케이블이 데이터 전송을 지원하는지 확인

### 실행 오류

**Agent 연결 실패**
```bash
# 시리얼 포트 확인
ls /dev/ttyACM*

# Agent 재시작
docker run -it --rm -v /dev:/dev --privileged --net=host \
  microros/micro-ros-agent:humble serial --dev /dev/ttyACM0 -b 115200
```

자세한 문제 해결은 [BUILD_AND_FLASH.md](docs/BUILD_AND_FLASH.md#6-문제-해결)를 참조하세요.

## 커스터마이징

### 새로운 ROS 2 메시지 타입 추가

1. `microros_static_library/library_generation/extra_packages/`에 패키지 추가
2. 라이브러리 재빌드:
   ```bash
   docker pull microros/micro_ros_static_library_builder:humble
   docker run -it --rm -v $(pwd):/project microros/micro_ros_static_library_builder:humble
   ```

### UART 전송 사용

`CMakeLists.txt`에서 전송 방식 변경:
```cmake
pico_enable_stdio_usb(프로젝트명 0)   # USB 비활성화
pico_enable_stdio_uart(프로젝트명 1)  # UART 활성화
```

## 기여 및 라이센스

### 원본 프로젝트
이 프로젝트는 [micro-ROS/micro_ros_raspberrypi_pico_sdk](https://github.com/micro-ROS/micro_ros_raspberrypi_pico_sdk)를 기반으로 합니다.

### 라이센스
Apache License 2.0 - 자세한 내용은 [LICENSE](LICENSE) 파일 참조

### 주의사항
이 소프트웨어는 프로덕션 환경을 위한 것이 아니며, 프로토타이핑 및 개발 목적으로 사용됩니다. 안전 관련 환경에서 사용하기 전에 적절한 안전 표준(예: ISO 26262)에 따라 소프트웨어를 검토하고 조정하세요.

## 참고 자료

### 공식 문서
- [Raspberry Pi Pico Documentation](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html)
- [Pico SDK Documentation](https://raspberrypi.github.io/pico-sdk-doxygen/)
- [micro-ROS Documentation](https://micro.ros.org/)
- [ROS 2 Humble Documentation](https://docs.ros.org/en/humble/)

### 관련 프로젝트
- [pico-mfrc522](https://github.com/BenjaminModica/pico-mfrc522) - MFRC522 RFID 라이브러리
- [micro-ROS](https://github.com/micro-ROS) - micro-ROS 공식 저장소

---

**문의 및 이슈**: GitHub Issues를 통해 문의하거나 문제를 보고해주세요.

**업데이트**: 2025-11-05 | **타겟 보드**: Raspberry Pi Pico W | **ROS 2**: Humble
