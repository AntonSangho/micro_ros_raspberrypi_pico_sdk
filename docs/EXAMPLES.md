# micro-ROS Examples for Raspberry Pi Pico

이 폴더에는 다양한 micro-ROS 예제들이 포함되어 있습니다.

## 공통 빌드 및 실행 방법

### 1. 예제 선택

`CMakeLists.txt`에서 빌드할 예제를 선택합니다:

```cmake
# 원하는 예제의 주석(#)을 제거하세요
add_micro_ros_executable(led_blink_example examples/led_blink_example.c)
# add_micro_ros_executable(hcsr04_distance_example examples/hcsr04_distance_example.c)
```

### 2. 빌드

```bash
cd build
cmake ..
make
```

각 예제는 독립적인 `.uf2` 파일로 생성됩니다:
- `led_blink_example.uf2`
- `hcsr04_distance_example.uf2`

### 3. 펌웨어 플래시

**중요:** 예제에 맞는 UF2 파일을 플래시해야 합니다!

```bash
# 1. BOOTSEL 버튼을 누른 채로 USB 연결
# 2. RPI-RP2 드라이브가 마운트되면 해당 예제의 UF2 파일 복사
cp build/led_blink_example.uf2 /media/$USER/RPI-RP2
# 또는
cp build/hcsr04_distance_example.uf2 /media/$USER/RPI-RP2
```

### 4. 리셋

**플래시 후 반드시 Pico를 리셋하세요:**
- USB 케이블을 뽑았다가 다시 연결
- 또는 Pico의 RUN 버튼 누르기 (있는 경우)

### 5. micro-ROS Agent 실행

```bash
docker run -it --rm -v /dev:/dev --privileged --net=host \
  microros/micro-ros-agent:humble serial --dev /dev/ttyACM0 -b 115200
```

---

## 목차

1. [led_blink_example.c](#led_blink_examplec) - LED 깜박임 예제
2. [hcsr04_distance_example.c](#hcsr04_distance_examplec) - HC-SR04 초음파 센서 예제

---

## led_blink_example.c

GPIO 20에 연결된 외부 LED를 1초마다 깜박이면서 ROS 2 토픽을 발행하는 예제입니다.

### 하드웨어 연결

```
Pico GPIO 20 (Pin 26) ---> 저항 (220Ω~1kΩ) ---> LED (+) ---> LED (-) ---> GND
```

### 기능

- **노드 이름**: `pico_node`
- **토픽 이름**: `/pico_publisher`
- **메시지 타입**: `std_msgs/msg/Int32`
- **발행 주기**: 1초
- **LED 깜박임**: 1초마다 토글

### 빌드 방법

CMakeLists.txt에서 예제 파일을 변경:

```cmake
add_executable(pico_micro_ros_example
    examples/led_blink_example.c
    pico_uart_transport.c
)
```

그리고 빌드:

```bash
cd build
cmake ..
make
```

### 실행

1. micro-ROS Agent 실행:
```bash
docker run -it --rm -v /dev:/dev --privileged --net=host \
  microros/micro-ros-agent:humble serial --dev /dev/ttyACM0 -b 115200
```

2. Pico에 펌웨어 플래시

3. ROS 토픽 확인:
```bash
ros2 topic echo /pico_publisher
```

---

## hcsr04_distance_example.c

HC-SR04 초음파 센서로 거리를 측정하여 ROS 2 토픽으로 발행하는 예제입니다.

### 하드웨어 연결

```
HC-SR04        Raspberry Pi Pico
--------       -----------------
VCC      --->  5V (VBUS, Pin 40)
TRIG     --->  GPIO 16 (Pin 21)
ECHO     --->  GPIO 17 (Pin 22)
GND      --->  GND (Pin 23)
```

**중요:** HC-SR04의 ECHO 핀은 5V 출력이므로, 3.3V Pico에 직접 연결하면 손상될 수 있습니다.
안전하게 사용하려면 **전압 분배기(voltage divider)** 사용을 권장합니다:

```
ECHO ---> 저항1 (1kΩ) ---> GPIO 17
                      |
                  저항2 (2kΩ)
                      |
                     GND
```

또는 5V 허용 HC-SR04 모듈을 사용하세요.

### 기능

- **노드 이름**: `hcsr04_node`
- **토픽 이름**: `/ultrasonic_distance`
- **메시지 타입**: `std_msgs/msg/Float32`
- **발행 주기**: 100ms (10Hz)
- **측정 범위**: 2cm ~ 400cm
- **에러 값**: -1.0 (측정 실패 시)

### 동작 원리

1. **Trigger 신호 발생**: TRIG 핀을 10μs 동안 HIGH로 설정
2. **초음파 송신**: 센서가 40kHz 초음파 8펄스 송신
3. **Echo 수신 대기**: ECHO 핀이 HIGH가 되면 반사파 수신 시작
4. **시간 측정**: ECHO 핀이 HIGH인 시간 측정
5. **거리 계산**: `거리(cm) = (펄스 시간(μs) × 0.034) / 2`
   - 음속: 340 m/s = 0.034 cm/μs
   - 왕복 거리이므로 2로 나눔

### 빌드 방법

CMakeLists.txt에서 예제 파일을 변경:

```cmake
add_executable(pico_micro_ros_example
    examples/hcsr04_distance_example.c
    pico_uart_transport.c
)
```

그리고 빌드:

```bash
cd build
cmake ..
make
```

### 실행

1. micro-ROS Agent 실행:
```bash
docker run -it --rm -v /dev:/dev --privileged --net=host \
  microros/micro-ros-agent:humble serial --dev /dev/ttyACM0 -b 115200
```

2. Pico에 펌웨어 플래시

3. ROS 토픽 확인:
```bash
# 거리 데이터 실시간 확인
ros2 topic echo /ultrasonic_distance

# 토픽 주파수 확인 (약 10Hz)
ros2 topic hz /ultrasonic_distance

# 토픽 정보 확인
ros2 topic info /ultrasonic_distance
```

### 문제 해결

**측정값이 -1.0만 나오는 경우:**
- TRIG, ECHO 핀 연결 확인
- 센서 전원(5V) 연결 확인
- 센서 앞에 장애물이 있는지 확인 (2cm ~ 400cm 범위 내)

**불안정한 측정값:**
- 측정 표면이 각도가 너무 크거나 흡음 재질인지 확인
- 센서를 안정적으로 고정
- 주변 초음파 간섭 확인

**센서가 작동하지 않는 경우:**
- 전압 분배기 저항 값 확인 (1kΩ + 2kΩ)
- GND 연결 확인
