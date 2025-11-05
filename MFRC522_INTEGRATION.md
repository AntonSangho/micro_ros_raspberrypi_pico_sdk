# MFRC522 RFID 리더 micro-ROS 통합 가이드

이 문서는 MFRC522 RFID 리더를 micro-ROS 프로젝트에 통합하기 위한 단계별 가이드입니다.

## 단계별 구현 계획

### 1단계: MFRC522 라이브러리 추가 및 프로젝트 구조 준비

```bash
# 프로젝트 루트에서
git submodule add https://github.com/BenjaminModica/pico-mfrc522.git external/pico-mfrc522
# 또는 직접 클론
mkdir -p external
cd external
git clone https://github.com/BenjaminModica/pico-mfrc522.git
```

### 2단계: 하드웨어 연결 계획

MFRC522는 SPI 통신을 사용합니다. Pico 핀 연결:
- **SPI0** 사용 권장
  - SCK (SPI CLK) → GPIO 2 또는 6, 18
  - MOSI (SPI TX) → GPIO 3 또는 7, 19
  - MISO (SPI RX) → GPIO 4 또는 0, 16
  - CS (Chip Select) → 임의 GPIO (예: GPIO 5)
  - RST (Reset) → 임의 GPIO (예: GPIO 22)

**주의:** UART/USB 시리얼과 충돌하지 않도록 핀 선택

### 3단계: CMakeLists.txt 수정

```cmake
# MFRC522 라이브러리 추가
add_subdirectory(external/pico-mfrc522)

# 기존 타겟에 링크
target_link_libraries(pico_micro_ros_example
    # ... 기존 라이브러리들
    pico-mfrc522  # MFRC522 라이브러리
    hardware_spi  # SPI 하드웨어 지원
)

# 인클루드 경로 추가
target_include_directories(pico_micro_ros_example PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}
    ${CMAKE_CURRENT_LIST_DIR}/external/pico-mfrc522/include
)
```

### 4단계: ROS 2 메시지 타입 결정

**옵션 A: 표준 메시지 사용 (간단)**
```c
// std_msgs/String 사용
#include <std_msgs/msg/string.h>
// UID를 문자열로 퍼블리시
```

**옵션 B: 커스텀 메시지 생성 (권장)**
```
# rfid_msgs/msg/RFIDTag.msg
uint8[] uid           # 카드 UID (4, 7, 또는 10 바이트)
uint8 uid_length      # UID 길이
uint8 sak             # Select Acknowledge
uint8 card_type       # 카드 타입 (Mifare Classic, Ultralight 등)
string card_type_name # 카드 타입 이름
```

커스텀 메시지 사용 시: `microros_static_library/library_generation/extra_packages/`에 메시지 패키지 추가 후 라이브러리 재빌드 필요

### 5단계: 예제 코드 구조 설계

```c
// rfid_reader_example.c 구조
#include <rcl/rcl.h>
#include <rclc/rclc.h>
#include <std_msgs/msg/string.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "pico_mfrc522.h"

// 전역 변수
rcl_publisher_t rfid_publisher;
std_msgs__msg__String rfid_msg;
MFRC522Ptr_t mfrc522;

// 주요 함수들:
// 1. init_rfid_hardware() - SPI 및 MFRC522 초기화
// 2. scan_rfid_card() - 카드 스캔 및 UID 읽기
// 3. publish_card_data() - ROS 2 토픽으로 퍼블리시
// 4. timer_callback() - 주기적 스캔 (rclc executor)
```

### 6단계: 구현 순서

1. **기본 RFID 테스트** (micro-ROS 없이)
   - MFRC522 라이브러리만 사용하여 카드 읽기 테스트
   - USB 시리얼로 UID 출력 확인

2. **micro-ROS 통합**
   - ROS 2 퍼블리셔 추가
   - 카드 감지 시 토픽으로 퍼블리시

3. **타이머 기반 폴링**
   - `rclc_timer_init()` 사용하여 주기적 스캔 (예: 100ms)

4. **에러 핸들링**
   - 카드 읽기 실패 처리
   - SPI 통신 오류 처리

### 7단계: 빌드 및 테스트 절차

```bash
# 1. 빌드
cd build
cmake ..
make

# 2. 플래시
cp rfid_reader_example.uf2 /media/$USER/RPI-RP2

# 3. Agent 실행
docker run -it --rm -v /dev:/dev --privileged --net=host \
  microros/micro-ros-agent:humble serial --dev /dev/ttyACM0 -b 115200

# 4. 토픽 확인
ros2 topic list
ros2 topic echo /rfid_card_uid
```

## 예상 문제점 및 해결방안

### 문제 1: SPI와 UART 핀 충돌
- **해결:** GPIO 핀맵 신중히 계획, Pinout 다이어그램 참고

### 문제 2: 타이밍 문제 (RFID 스캔이 느림)
- **해결:** 비동기 패턴 사용, rclc executor의 타이머로 주기적 폴링

### 문제 3: 메모리 부족
- **해결:** UID만 퍼블리시, 불필요한 버퍼 최소화

### 문제 4: Agent 연결 끊김
- **해결:** RFID 초기화를 micro-ROS 초기화 후에 수행

## 다음 단계 선택

구현 가능한 작업:

1. **CMakeLists.txt 수정** - MFRC522 라이브러리 통합
2. **기본 RFID 예제 작성** - micro-ROS 없이 카드 읽기 테스트
3. **micro-ROS 통합 예제 작성** - 완전한 RFID→ROS 2 퍼블리셔
4. **커스텀 메시지 생성** - ROS 2 메시지 타입 및 라이브러리 재빌드

## 참고 자료

- MFRC522 라이브러리: https://github.com/BenjaminModica/pico-mfrc522
- Raspberry Pi Pico 핀아웃: https://datasheets.raspberrypi.com/pico/Pico-R3-A4-Pinout.pdf
- micro-ROS 문서: https://micro.ros.org/
