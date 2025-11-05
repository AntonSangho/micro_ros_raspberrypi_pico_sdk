#include <stdio.h>
#include <time.h>
#include "pico/stdlib.h"

#include <uxr/client/profile/transport/custom/custom_transport.h>

// 내장 LED 핀 (Raspberry Pi Pico)
const uint ONBOARD_LED_PIN = 25;

void usleep(uint64_t us)
{
    sleep_us(us);
}

int clock_gettime(clockid_t unused, struct timespec *tp)
{
    uint64_t m = time_us_64();
    tp->tv_sec = m / 1000000;
    tp->tv_nsec = (m % 1000000) * 1000;
    return 0;
}

bool pico_serial_transport_open(struct uxrCustomTransport * transport)
{
    // Ensure that stdio_init_all is only called once on the runtime
    static bool require_init = true;
    if(require_init)
    {
        stdio_init_all();

        // 내장 LED 초기화
        gpio_init(ONBOARD_LED_PIN);
        gpio_set_dir(ONBOARD_LED_PIN, GPIO_OUT);
        gpio_put(ONBOARD_LED_PIN, 0);  // LED 끄기

        require_init = false;
    }

    return true;
}

bool pico_serial_transport_close(struct uxrCustomTransport * transport)
{
    return true;
}

size_t pico_serial_transport_write(struct uxrCustomTransport * transport, uint8_t *buf, size_t len, uint8_t *errcode)
{
    for (size_t i = 0; i < len; i++)
    {
        if (buf[i] != putchar(buf[i]))
        {
            *errcode = 1;
            return i;
        }
    }
    return len;
}

size_t pico_serial_transport_read(struct uxrCustomTransport * transport, uint8_t *buf, size_t len, int timeout, uint8_t *errcode)
{
    uint64_t start_time_us = time_us_64();
    for (size_t i = 0; i < len; i++)
    {
        int64_t elapsed_time_us = timeout * 1000 - (time_us_64() - start_time_us);
        if (elapsed_time_us < 0)
        {
            *errcode = 1;
            return i;
        }

        int character = getchar_timeout_us(elapsed_time_us);
        if (character == PICO_ERROR_TIMEOUT)
        {
            *errcode = 1;
            return i;
        }
        buf[i] = character;

        // 데이터 수신 시 LED 토글
        gpio_put(ONBOARD_LED_PIN, !gpio_get(ONBOARD_LED_PIN));
    }
    return len;
}
