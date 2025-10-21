# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

이 저장소는 Pico SDK를 사용하여 Raspberry Pi Pico에서 micro-ROS를 지원합니다. 미리 컴파일된 micro-ROS 라이브러리와 퍼블리셔/구독자 패턴을 보여주는 예제 코드를 제공하여 RP2040 기반 마이크로컨트롤러에서 ROS 2 애플리케이션을 실행할 수 있게 합니다.

**핵심 아키텍처:**
- 클라이언트-서버 아키텍처: Pico는 micro-ROS 클라이언트를 실행하며, 호스트에서 별도의 micro-ROS Agent가 필요함
- `pico_uart_transport.c`를 통한 커스텀 전송 계층이 시리얼 통신(USB 또는 UART)을 구현
- 사전 컴파일된 정적 라이브러리(`libmicroros/libmicroros.a`)에 모든 micro-ROS 의존성 포함
- 표준 rclcpp 대신 rclc(ROS Client Library for C) 사용

## 빌드 명령어

### 기본 빌드 프로세스
```bash
# 프로젝트 루트에서
mkdir build
cd build
cmake ..
make
```

### Pico에 플래시
```bash
# BOOTSEL 버튼을 누른 상태로 USB 연결 후:
cp pico_micro_ros_example.uf2 /media/$USER/RPI-RP2
```

### 사전 컴파일된 라이브러리 재빌드
```bash
# Docker 빌더 사용 (Docker 필요)
docker pull microros/micro_ros_static_library_builder:humble
docker run -it --rm -v $(pwd):/project microros/micro_ros_static_library_builder:humble
```

이 명령은 `libmicroros/libmicroros.a`를 재빌드하고 `libmicroros/include/`의 헤더를 재생성합니다.

## 환경 요구사항

**필수 환경 변수:**
- `PICO_SDK_PATH`: Raspberry Pi Pico SDK 경로 (보통 `$HOME/pico-sdk`)
- `PICO_TOOLCHAIN_PATH`: (선택사항) arm-none-eabi-gcc 툴체인 경로 (표준 위치가 아닌 경우)

**툴체인:**
- `arm-none-eabi-gcc` 버전 9.3.1 또는 호환 버전 필요
- 사전 컴파일된 라이브러리는 9.3.1로 빌드됨; 호환되지 않는 버전은 링킹 오류 발생 가능

## 프로젝트 구조

**핵심 파일:**
- `pico_micro_ros_example.c`: 메인 애플리케이션 (ROS 2 퍼블리셔 예제)
- `pico_uart_transport.c`: micro-ROS용 시리얼 전송 구현
- `pico_uart_transports.h`: 전송 함수 선언
- `CMakeLists.txt`: 빌드 설정

**라이브러리:**
- `libmicroros/libmicroros.a`: 사전 컴파일된 정적 라이브러리 (8.5 MB)
- `libmicroros/include/`: 모든 micro-ROS 헤더 (rcl, rclc, std_msgs 등)

**라이브러리 생성:**
- `microros_static_library/library_generation/`: 라이브러리 재생성을 위한 Docker 기반 빌드 시스템
- `microros_static_library/library_generation/extra_packages/`: 여기에 커스텀 ROS 2 패키지 추가
- `microros_static_library/library_generation/extra_packages/extra_packages.repos`: 추가 패키지용 VCS import

## 전송 설정

`CMakeLists.txt`에서 USB와 UART 시리얼 전환:

```cmake
# USB (기본값):
pico_enable_stdio_usb(pico_micro_ros_example 1)
pico_enable_stdio_uart(pico_micro_ros_example 0)

# UART (Debug Probe용):
pico_enable_stdio_usb(pico_micro_ros_example 0)
pico_enable_stdio_uart(pico_micro_ros_example 1)
```

## Agent 실행

Pico 클라이언트는 호스트에서 실행 중인 micro-ROS Agent가 필요합니다:

```bash
docker run -it --rm -v /dev:/dev --privileged --net=host \
  microros/micro-ros-agent:humble serial --dev /dev/ttyACM0 -b 115200
```

## 커스텀 전송 구현

전송 계층(`pico_uart_transport.c`)은 다음을 구현합니다:
- `pico_serial_transport_open()`: stdio 초기화 (`stdio_init_all()` 한 번만 호출)
- `pico_serial_transport_close()`: 정리 (현재는 no-op)
- `pico_serial_transport_write()`: `putchar()`를 사용하여 시리얼에 바이트 쓰기
- `pico_serial_transport_read()`: `getchar_timeout_us()`를 사용하여 타임아웃과 함께 바이트 읽기
- `usleep()` 및 `clock_gettime()`: Pico SDK용 POSIX 호환성 shim

전송은 `main()`에서 `rmw_uros_set_custom_transport()`를 통해 등록됩니다.

## 커스텀 ROS 2 패키지 추가

추가 ROS 2 메시지 타입이나 패키지를 포함하려면:

1. `microros_static_library/library_generation/extra_packages/`에 패키지 추가
2. `microros_static_library/library_generation/extra_packages/extra_packages.repos`에 repo 추가
3. 위의 Docker 빌더 명령으로 라이브러리 재빌드

참고: `tf2_msgs`는 `library_generation.sh`의 workaround를 통해 자동으로 포함됩니다.

## Git 워크플로우

- 주요 개발 브랜치: `humble` (ROS 2 Humble)
- 기본 PR 타겟: `kilted` (main/master 아님)
- DCO 요구사항에 따라 `git commit -s`로 커밋 서명 (CONTRIBUTING.md 참조)

## 주요 제약사항

- 프로덕션 준비 안 됨: 프로토타이핑 및 개발용
- 단일 스레드 executor: `rclc_executor_spin_some()`이 콜백 처리
- Agent ping 타임아웃: 예제는 agent 연결을 위해 2분(120회 × 1초) 대기
- GPIO 25의 LED가 초기화 성공을 표시
- 올바른 시리얼 통신을 위해 CMakeLists.txt에서 CRLF 지원 명시적으로 비활성화됨
