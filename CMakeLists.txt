cmake_minimum_required(VERSION 3.12)

# Pico W 보드 설정 (내부 LED 사용을 위해 필요) - pico_sdk_import 전에 설정해야 함
set(PICO_BOARD pico_w CACHE STRING "Board type")

include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(pico_micro_ros_example C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

link_directories(libmicroros)

SET(CMAKE_C_FLAGS  "${CMAKE_C_FLAGS} -ffunction-sections -fdata-sections")
SET(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} -ffunction-sections -fdata-sections")

# 공통 컴파일 정의
add_compile_definitions(PICO_UART_ENABLE_CRLF_SUPPORT=0)
add_compile_definitions(PICO_STDIO_ENABLE_CRLF_SUPPORT=0)
add_compile_definitions(PICO_STDIO_DEFAULT_CRLF=0)

# 공통 설정을 위한 함수
function(add_micro_ros_executable NAME SOURCE_FILE)
    add_executable(${NAME}
        ${SOURCE_FILE}
        pico_uart_transport.c
    )
    target_link_libraries(${NAME}
        pico_stdlib
        microros
    )
    target_include_directories(${NAME} PUBLIC
        libmicroros/include
        ${CMAKE_SOURCE_DIR}  # 프로젝트 루트 디렉토리 (pico_uart_transports.h 위치)
    )
    # Configure Pico
    pico_enable_stdio_usb(${NAME} 1)
    pico_enable_stdio_uart(${NAME} 0)
    # Generate UF2
    pico_add_extra_outputs(${NAME})
endfunction()

# CYW43 지원이 필요한 실행파일을 위한 함수 (내부 LED 사용)
function(add_micro_ros_executable_with_cyw43 NAME SOURCE_FILE)
    add_executable(${NAME}
        ${SOURCE_FILE}
        pico_uart_transport.c
    )
    target_link_libraries(${NAME}
        pico_stdlib
        pico_cyw43_arch_none
        microros
    )
    target_include_directories(${NAME} PUBLIC
        libmicroros/include
        ${CMAKE_SOURCE_DIR}  # 프로젝트 루트 디렉토리 (pico_uart_transports.h 위치)
    )
    # Configure Pico
    pico_enable_stdio_usb(${NAME} 1)
    pico_enable_stdio_uart(${NAME} 0)
    # Generate UF2
    pico_add_extra_outputs(${NAME})
endfunction()

# CYW43 + MFRC522 RFID 지원이 필요한 실행파일을 위한 함수
function(add_micro_ros_executable_with_rfid NAME SOURCE_FILE)
    add_executable(${NAME}
        ${SOURCE_FILE}
        pico_uart_transport.c
        external/pico-mfrc522/mfrc522.c
    )
    target_link_libraries(${NAME}
        pico_stdlib
        pico_cyw43_arch_none
        hardware_spi
        microros
    )
    target_include_directories(${NAME} PUBLIC
        libmicroros/include
        ${CMAKE_SOURCE_DIR}  # 프로젝트 루트 디렉토리
        ${CMAKE_SOURCE_DIR}/external/pico-mfrc522  # MFRC522 헤더
    )
    # Configure Pico
    pico_enable_stdio_usb(${NAME} 1)
    pico_enable_stdio_uart(${NAME} 0)
    # Generate UF2
    pico_add_extra_outputs(${NAME})
endfunction()

# 빌드할 예제 선택
# 원하는 예제만 주석 해제하세요

# 기본 예제
#add_micro_ros_executable(pico_micro_ros_example pico_micro_ros_example.c)

# Examples 디렉토리의 예제들
#add_micro_ros_executable_with_cyw43(led_blink_example examples/led_blink_example.c)
add_micro_ros_executable_with_rfid(rfid_reader_example examples/rfid_reader_example.c)
#add_micro_ros_executable(hcsr04_distance_example examples/hcsr04_distance_example.c)

# RFID 단독 테스트 (micro-ROS 없이)
add_executable(rfid_test_simple
    examples/rfid_test_simple.c
    external/pico-mfrc522/mfrc522.c
)
target_link_libraries(rfid_test_simple
    pico_stdlib
    pico_cyw43_arch_none
    hardware_spi
)
target_include_directories(rfid_test_simple PUBLIC
    ${CMAKE_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/external/pico-mfrc522
)
pico_enable_stdio_usb(rfid_test_simple 1)
pico_enable_stdio_uart(rfid_test_simple 0)
pico_add_extra_outputs(rfid_test_simple)

# RFID GPIO/SPI 기본 테스트 (CYW43 없이)
add_executable(rfid_gpio_test
    examples/rfid_gpio_test.c
)
target_link_libraries(rfid_gpio_test
    pico_stdlib
    hardware_spi
)
pico_enable_stdio_usb(rfid_gpio_test 1)
pico_enable_stdio_uart(rfid_gpio_test 0)
pico_add_extra_outputs(rfid_gpio_test)

# RFID 전원/연결 진단 테스트
add_executable(rfid_power_test
    examples/rfid_power_test.c
)
target_link_libraries(rfid_power_test
    pico_stdlib
    hardware_adc
)
pico_enable_stdio_usb(rfid_power_test 1)
pico_enable_stdio_uart(rfid_power_test 0)
pico_add_extra_outputs(rfid_power_test)
