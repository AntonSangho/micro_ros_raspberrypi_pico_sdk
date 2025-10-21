# micro-ROS Examples for Raspberry Pi Pico

이 폴더에는 다양한 micro-ROS 예제들이 포함되어 있습니다.

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
