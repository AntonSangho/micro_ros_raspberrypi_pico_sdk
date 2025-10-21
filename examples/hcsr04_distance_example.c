#include <stdio.h>

#include <rcl/rcl.h>
#include <rcl/error_handling.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>
#include <std_msgs/msg/float32.h>
#include <rmw_microros/rmw_microros.h>

#include "pico/stdlib.h"
#include "pico_uart_transports.h"

// HC-SR04 핀 설정
const uint TRIG_PIN = 16;  // GPIO 16 (Pin 21) - Trigger
const uint ECHO_PIN = 17;  // GPIO 17 (Pin 22) - Echo

// 타임아웃 설정 (30ms = 약 5m 거리)
const uint32_t TIMEOUT_US = 30000;

rcl_publisher_t publisher;
std_msgs__msg__Float32 msg;

/**
 * HC-SR04로 거리 측정
 * @return 거리 (cm), 에러 시 -1.0
 */
float measure_distance() {
    // 1. Trigger 핀을 LOW로 초기화
    gpio_put(TRIG_PIN, 0);
    sleep_us(2);

    // 2. Trigger 핀을 HIGH로 10us 유지 (센서 시작 신호)
    gpio_put(TRIG_PIN, 1);
    sleep_us(10);
    gpio_put(TRIG_PIN, 0);

    // 3. Echo 핀이 HIGH가 될 때까지 대기 (타임아웃 적용)
    uint64_t start_time = time_us_64();
    while (gpio_get(ECHO_PIN) == 0) {
        if ((time_us_64() - start_time) > TIMEOUT_US) {
            return -1.0;  // 타임아웃
        }
    }

    // 4. Echo 핀이 HIGH인 시간 측정 시작
    uint64_t pulse_start = time_us_64();

    // 5. Echo 핀이 LOW가 될 때까지 대기
    while (gpio_get(ECHO_PIN) == 1) {
        if ((time_us_64() - pulse_start) > TIMEOUT_US) {
            return -1.0;  // 타임아웃
        }
    }

    // 6. Echo 핀이 HIGH인 시간 측정 종료
    uint64_t pulse_end = time_us_64();
    uint64_t pulse_duration = pulse_end - pulse_start;

    // 7. 거리 계산
    // 음속: 340 m/s = 0.034 cm/us
    // 왕복 거리이므로 2로 나눔
    float distance = (pulse_duration * 0.034) / 2.0;

    return distance;
}

void timer_callback(rcl_timer_t *timer, int64_t last_call_time)
{
    // 거리 측정
    float distance = measure_distance();

    // 유효한 거리 범위: 2cm ~ 400cm (HC-SR04 스펙)
    if (distance >= 2.0 && distance <= 400.0) {
        msg.data = distance;
        rcl_publish(&publisher, &msg, NULL);
    } else {
        // 측정 실패 시 -1.0 발행
        msg.data = -1.0;
        rcl_publish(&publisher, &msg, NULL);
    }
}

int main()
{
    rmw_uros_set_custom_transport(
        true,
        NULL,
        pico_serial_transport_open,
        pico_serial_transport_close,
        pico_serial_transport_write,
        pico_serial_transport_read
    );

    // HC-SR04 핀 초기화
    gpio_init(TRIG_PIN);
    gpio_set_dir(TRIG_PIN, GPIO_OUT);
    gpio_put(TRIG_PIN, 0);

    gpio_init(ECHO_PIN);
    gpio_set_dir(ECHO_PIN, GPIO_IN);

    rcl_timer_t timer;
    rcl_node_t node;
    rcl_allocator_t allocator;
    rclc_support_t support;
    rclc_executor_t executor;

    allocator = rcl_get_default_allocator();

    // Wait for agent successful ping for 2 minutes.
    const int timeout_ms = 1000;
    const uint8_t attempts = 120;

    rcl_ret_t ret = rmw_uros_ping_agent(timeout_ms, attempts);

    if (ret != RCL_RET_OK)
    {
        // Unreachable agent, exiting program.
        return ret;
    }

    rclc_support_init(&support, 0, NULL, &allocator);

    rclc_node_init_default(&node, "hcsr04_node", "", &support);
    rclc_publisher_init_default(
        &publisher,
        &node,
        ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Float32),
        "ultrasonic_distance");

    // 100ms마다 거리 측정 (10Hz)
    rclc_timer_init_default(
        &timer,
        &support,
        RCL_MS_TO_NS(100),
        timer_callback);

    rclc_executor_init(&executor, &support.context, 1, &allocator);
    rclc_executor_add_timer(&executor, &timer);

    msg.data = 0.0;
    while (true)
    {
        rclc_executor_spin_some(&executor, RCL_MS_TO_NS(100));
    }
    return 0;
}
