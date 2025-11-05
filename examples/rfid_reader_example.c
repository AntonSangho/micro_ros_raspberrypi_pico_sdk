#include <stdio.h>

#include <rcl/rcl.h>
#include <rcl/error_handling.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>
#include <std_msgs/msg/string.h>
#include <rmw_microros/rmw_microros.h>

#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "hardware/spi.h"
#include "pico_uart_transports.h"
#include "../external/pico-mfrc522/mfrc522.h"

// MFRC522 핀 설정 (SPI0 사용, Pico W에서 동작 확인됨)
#define SPI_PORT spi0
#define PIN_MISO 4  // SPI0 RX
#define PIN_CS   1  // Chip Select
#define PIN_SCK  2  // SPI0 SCK
#define PIN_MOSI 3  // SPI0 TX
#define PIN_RST  0  // Reset

rcl_publisher_t rfid_publisher;
std_msgs__msg__String rfid_msg;
MFRC522Ptr_t mfrc522;

// LED 제어용 (Pico W 내부 LED)
bool led_state = false;

void timer_callback(rcl_timer_t *timer, int64_t last_call_time)
{
    (void)last_call_time;
    static int scan_count = 0;

    // LED 토글
    led_state = !led_state;
    cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, led_state);

    // 10초마다 스캔 상태 출력 (100ms 간격이므로 100번 = 10초)
    scan_count++;
    if (scan_count % 100 == 0) {
        printf("카드 스캔 중... (%d초)\n", scan_count / 10);
    }

    // RFID 리더가 초기화되었는지 확인
    if (mfrc522 == NULL) {
        return;
    }

    // 새 카드가 있는지 확인
    if (PICC_IsNewCardPresent(mfrc522)) {
        printf("카드 감지됨!\n");

        // 카드 선택 및 UID 읽기
        if (PICC_ReadCardSerial(mfrc522)) {
            printf("UID 읽기 성공\n");
            // UID를 문자열로 변환
            char uid_str[32];
            int offset = 0;
            for (int i = 0; i < mfrc522->uid.size && i < 10; i++) {
                offset += snprintf(uid_str + offset, sizeof(uid_str) - offset,
                                   "%02X", mfrc522->uid.uidByte[i]);
                if (i < mfrc522->uid.size - 1) {
                    offset += snprintf(uid_str + offset, sizeof(uid_str) - offset, ":");
                }
            }

            // ROS 메시지 퍼블리시
            rfid_msg.data.data = uid_str;
            rfid_msg.data.size = strlen(uid_str);
            rfid_msg.data.capacity = sizeof(uid_str);

            rcl_ret_t ret = rcl_publish(&rfid_publisher, &rfid_msg, NULL);

            if (ret == RCL_RET_OK) {
                printf("퍼블리시 성공: %s\n", uid_str);

                // LED 빠르게 깜박여서 카드 읽힘 표시
                for (int i = 0; i < 3; i++) {
                    cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 1);
                    sleep_ms(100);
                    cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 0);
                    sleep_ms(100);
                }
            } else {
                printf("퍼블리시 실패: %d\n", ret);
            }
        } else {
            printf("UID 읽기 실패\n");
        }
    }
}

int main()
{
    // 기본 예제와 동일한 순서로 시작
    rmw_uros_set_custom_transport(
        true,
        NULL,
        pico_serial_transport_open,
        pico_serial_transport_close,
        pico_serial_transport_write,
        pico_serial_transport_read
    );

    // CYW43 초기화 (내부 LED 사용)
    if (cyw43_arch_init()) {
        return -1;
    }

    rcl_timer_t timer;
    rcl_node_t node;
    rcl_allocator_t allocator;
    rclc_support_t support;
    rclc_executor_t executor;

    allocator = rcl_get_default_allocator();

    // Agent 연결 대기 (2분)
    const int timeout_ms = 1000;
    const uint8_t attempts = 120;

    rcl_ret_t ret = rmw_uros_ping_agent(timeout_ms, attempts);

    if (ret != RCL_RET_OK)
    {
        // Agent 연결 실패
        return ret;
    }

    // RFID 하드웨어 초기화
    printf("\n=== RFID 초기화 시작 ===\n");

    spi_init(SPI_PORT, 4000000); // 4MHz
    gpio_set_function(PIN_MISO, GPIO_FUNC_SPI);
    gpio_set_function(PIN_SCK, GPIO_FUNC_SPI);
    gpio_set_function(PIN_MOSI, GPIO_FUNC_SPI);
    printf("SPI0 초기화 완료\n");

    gpio_init(PIN_CS);
    gpio_set_dir(PIN_CS, GPIO_OUT);
    gpio_put(PIN_CS, 1);
    printf("CS 핀(GP%d) 초기화\n", PIN_CS);

    gpio_init(PIN_RST);
    gpio_set_dir(PIN_RST, GPIO_OUT);
    gpio_put(PIN_RST, 1);
    sleep_ms(50);
    printf("RST 핀(GP%d) 초기화\n", PIN_RST);

    mfrc522 = MFRC522_Init();
    if (mfrc522 != NULL) {
        PCD_Init(mfrc522, SPI_PORT);

        // 펌웨어 버전 확인
        uint8_t version = PCD_ReadRegister(mfrc522, VersionReg);
        printf("MFRC522 버전: 0x%02X ", version);
        if (version == 0x91 || version == 0x92) {
            printf("(정상)\n");
        } else if (version == 0x00 || version == 0xFF) {
            printf("(통신 실패 - 배선 확인!)\n");
        } else {
            printf("(알 수 없는 버전)\n");
        }

        PCD_SetAntennaGain(mfrc522, RxGain_max);
        printf("안테나 게인: 최대 (48dB)\n");
        printf("=== RFID 준비 완료 ===\n");
    } else {
        printf("MFRC522 초기화 실패!\n");
    }

    // micro-ROS 초기화 (기본 예제와 동일)
    rclc_support_init(&support, 0, NULL, &allocator);
    rclc_node_init_default(&node, "pico_rfid_node", "", &support);

    rclc_publisher_init_default(
        &rfid_publisher,
        &node,
        ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, String),
        "rfid_card_uid");

    rclc_timer_init_default(
        &timer,
        &support,
        RCL_MS_TO_NS(100),  // 100ms로 변경하여 더 자주 스캔
        timer_callback);

    rclc_executor_init(&executor, &support.context, 1, &allocator);
    rclc_executor_add_timer(&executor, &timer);

    // LED 켜서 준비 완료 표시
    cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 1);

    // 메인 루프 (기본 예제와 동일)
    while (true)
    {
        rclc_executor_spin_some(&executor, RCL_MS_TO_NS(100));
    }

    return 0;
}
