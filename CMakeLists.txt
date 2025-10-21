cmake_minimum_required(VERSION 3.12)

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

# 빌드할 예제 선택
# 원하는 예제만 주석 해제하세요

# 기본 예제
#add_micro_ros_executable(pico_micro_ros_example pico_micro_ros_example.c)

# Examples 디렉토리의 예제들
# add_micro_ros_executable(led_blink_example examples/led_blink_example.c)
add_micro_ros_executable(hcsr04_distance_example examples/hcsr04_distance_example.c)
