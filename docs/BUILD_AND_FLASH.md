# Raspberry Pi Pico 빌드 및 플래시 가이드

이 문서는 Raspberry Pi Pico/Pico W에 코드를 빌드하고 업로드하는 전체 과정을 설명합니다.

## 목차

- [1. 개발 환경 준비](#1-개발-환경-준비)
- [2. Pico SDK 설치](#2-pico-sdk-설치)
- [3. 프로젝트 빌드](#3-프로젝트-빌드)
- [4. Pico에 플래시](#4-pico에-플래시)
- [5. 시리얼 모니터링](#5-시리얼-모니터링)
- [6. 문제 해결](#6-문제-해결)

---

## 1. 개발 환경 준비

### 1.1 필수 패키지 설치

```bash
# Ubuntu/Debian 기반
sudo apt update
sudo apt install -y \
    cmake \
    gcc-arm-none-eabi \
    libnewlib-arm-none-eabi \
    build-essential \
    libstdc++-arm-none-eabi-newlib \
    git \
    python3
```

### 1.2 버전 확인

```bash
# ARM GCC 컴파일러 확인 (9.3.1 또는 호환 버전 권장)
arm-none-eabi-gcc --version

# CMake 확인 (3.12 이상)
cmake --version
```

**중요**: 이 프로젝트의 사전 컴파일된 micro-ROS 라이브러리는 `arm-none-eabi-gcc 9.3.1`로 빌드되었습니다. 다른 버전을 사용하면 링킹 오류가 발생할 수 있습니다.

---

## 2. Pico SDK 설치

### 2.1 Pico SDK 다운로드

```bash
# 홈 디렉토리로 이동
cd ~

# Pico SDK 클론
git clone https://github.com/raspberrypi/pico-sdk.git

# 서브모듈 초기화 (중요!)
cd pico-sdk
git submodule update --init
```

### 2.2 환경 변수 설정

**임시 설정 (현재 터미널 세션만)**:
```bash
export PICO_SDK_PATH=$HOME/pico-sdk
```

**영구 설정 (권장)**:

bash 사용 시:
```bash
echo 'export PICO_SDK_PATH=$HOME/pico-sdk' >> ~/.bashrc
source ~/.bashrc
```

### 2.3 설정 확인

```bash
echo $PICO_SDK_PATH
# 출력: /home/사용자명/pico-sdk

ls $PICO_SDK_PATH
# pico-sdk의 파일 및 디렉토리가 표시되어야 함
```

---

## 3. 프로젝트 빌드

### 3.1 프로젝트 디렉토리로 이동

```bash
cd ~/projects/micro_ros_raspberrypi_pico_sdk
```

### 3.2 빌드 디렉토리 생성

```bash
# 처음 빌드하는 경우
mkdir build
cd build

# 이미 빌드 디렉토리가 있는 경우 (클린 빌드)
rm -rf build
mkdir build
cd build
```

### 3.3 CMake 설정

```bash
cmake ..
```

**예상 출력**:
```
-- The C compiler identification is GNU 9.3.1
-- The CXX compiler identification is GNU 9.3.1
-- PICO_SDK_PATH is /home/anton/pico-sdk
-- Pico board: pico_w
...
-- Configuring done
-- Generating done
```

### 3.4 빌드 실행

전체 프로젝트 빌드:
```bash
make -j4
```

특정 예제만 빌드:
```bash
# RFID 예제만 빌드
make rfid_reader_example

# LED 예제만 빌드
make led_blink_example

# 초음파 센서 예제만 빌드
make hcsr04_distance_example
```

### 3.5 빌드 결과 확인

```bash
ls *.uf2
```

**예상 출력**:
```
rfid_reader_example.uf2
rfid_test_simple.uf2
```

`.uf2` 파일이 생성되면 빌드 성공입니다!

---

## 4. Pico에 플래시

### 4.1 BOOTSEL 모드로 진입

1. **BOOTSEL 버튼을 누른 상태로** Pico를 USB에 연결
2. 또는 Pico가 이미 연결된 경우:
   - BOOTSEL 버튼을 누른 상태로
   - RESET 버튼을 누르거나 전원을 재연결

### 4.2 마운트 확인

Pico가 USB 저장장치로 인식되어야 합니다:

```bash
# 마운트 위치 확인
ls /media/$USER/

# 또는
lsblk
```

**예상 출력**:
```
RPI-RP2
```

### 4.3 UF2 파일 복사

**방법 1: 명령줄 (권장)**
```bash
cp rfid_reader_example.uf2 /media/$USER/RPI-RP2/
```

**방법 2: 파일 관리자**
- 파일 관리자에서 `RPI-RP2` 드라이브 열기
- `rfid_reader_example.uf2` 파일을 드래그 앤 드롭

### 4.4 플래시 완료 확인

- 파일이 복사되면 Pico가 자동으로 **재부팅**됩니다
- `RPI-RP2` 드라이브가 **자동으로 언마운트**됩니다
- Pico의 LED가 프로그램에 따라 동작하기 시작합니다

---

## 5. 시리얼 모니터링

### 5.1 시리얼 포트 확인

```bash
# Pico 연결 전
ls /dev/ttyACM*

# Pico 연결 후
ls /dev/ttyACM*
```

일반적으로 `/dev/ttyACM0`으로 나타납니다.

### 5.2 시리얼 모니터 실행

**방법 1: minicom**
```bash
# minicom 설치
sudo apt install minicom

# 실행 (115200 baud)
minicom -D /dev/ttyACM0 -b 115200

# 종료: Ctrl+A, X
```

**방법 2: screen**
```bash
screen /dev/ttyACM0 115200

# 종료: Ctrl+A, K
```

### 5.3 권한 문제 해결

시리얼 포트 접근 권한이 없는 경우:

```bash
# 임시 해결
sudo chmod 666 /dev/ttyACM0

# 영구 해결 (권장)
sudo usermod -a -G dialout $USER
# 로그아웃 후 다시 로그인 필요
```

---

## 6. 문제 해결

### 6.1 빌드 오류

#### `PICO_SDK_PATH is not defined`
```bash
# 환경 변수 설정 확인
echo $PICO_SDK_PATH

# 설정되지 않은 경우
export PICO_SDK_PATH=$HOME/pico-sdk

# 또는 .bashrc에 추가
echo 'export PICO_SDK_PATH=$HOME/pico-sdk' >> ~/.bashrc
source ~/.bashrc
```

#### `arm-none-eabi-gcc: command not found`
```bash
# ARM GCC 툴체인 설치
sudo apt install gcc-arm-none-eabi libnewlib-arm-none-eabi
```

#### CMake 버전 오류
```bash
# CMake 최신 버전 설치
sudo apt remove cmake
sudo snap install cmake --classic
```

#### 링킹 오류 (undefined reference)
```bash
# GCC 버전 확인
arm-none-eabi-gcc --version

# 9.3.1이 아닌 경우, libmicroros.a 재빌드 필요
# 자세한 내용은 PROJECT_OVERVIEW.md 참조
```

### 6.2 플래시 오류

#### `RPI-RP2` 드라이브가 보이지 않음
- BOOTSEL 버튼을 **확실히** 누른 상태로 USB 연결
- USB 케이블 확인 (데이터 전송 지원 케이블 사용)
- 다른 USB 포트 시도

### 6.3 실행 오류

#### LED가 켜지지 않음
- Pico W는 내부 LED가 CYW43 칩에 연결되어 있음
- 코드에서 `pico_cyw43_arch_none` 라이브러리 사용 확인
- GPIO 25 대신 `cyw43_arch_gpio_put()` 사용

#### 시리얼 출력이 보이지 않음
```bash
# USB stdio가 활성화되었는지 CMakeLists.txt 확인
pico_enable_stdio_usb(프로젝트명 1)

# 올바른 baud rate 사용 (115200)
minicom -D /dev/ttyACM0 -b 115200
```

---

## 7. 빠른 참조

### 전체 빌드 및 플래시 과정 (요약)

```bash
# 1. 프로젝트 디렉토리로 이동
cd ~/projects/micro_ros_raspberrypi_pico_sdk

# 2. 빌드
cd build
cmake ..
make rfid_reader_example

# 3. BOOTSEL 모드로 Pico 연결

# 4. 플래시
cp rfid_reader_example.uf2 /media/$USER/RPI-RP2/

# 5. 시리얼 모니터 (선택)
minicom -D /dev/ttyACM0 -b 115200
```

### 재빌드 (코드 수정 후)

```bash
cd build
make rfid_reader_example
cp rfid_reader_example.uf2 /media/$USER/RPI-RP2/
```

### 클린 빌드 (처음부터 다시)

```bash
rm -rf build
mkdir build
cd build
cmake ..
make
```

---

## 8. 추가 자료

### 공식 문서
- [Raspberry Pi Pico 시작하기](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html)
- [Pico SDK 문서](https://raspberrypi.github.io/pico-sdk-doxygen/)
- [Pico W 데이터시트](https://datasheets.raspberrypi.com/picow/pico-w-datasheet.pdf)

### 프로젝트별 가이드
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - 프로젝트 개요 및 micro-ROS 설정
- [RFID_GUIDE.md](RFID_GUIDE.md) - RFID 예제 상세 가이드
- [EXAMPLES.md](EXAMPLES.md) - 예제 프로그램 목록

### 유용한 도구
- [Picotool](https://github.com/raspberrypi/picotool) - Pico 정보 확인 도구
- [OpenOCD](https://openocd.org/) - 디버깅 도구 (Debug Probe 사용 시)
- [Thonny IDE](https://thonny.org/) - MicroPython 개발 (선택사항)

---

**작성일**: 2025-11-05
**대상**: Raspberry Pi Pico / Pico W
**SDK 버전**: Pico SDK 1.5.x 이상
**툴체인**: arm-none-eabi-gcc 9.3.1
