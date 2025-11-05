"""
MFRC522 카드 스캔 테스트

실제 RFID 카드를 스캔하고 UID를 출력합니다.
"""

from mfrc522 import MFRC522
import time

def format_uid(uid):
    """UID를 읽기 쉬운 형식으로 변환"""
    return ":".join([f"{byte:02X}" for byte in uid])

def main():
    print("=" * 50)
    print("MFRC522 카드 스캔 테스트")
    print("=" * 50)
    print()

    # MFRC522 초기화
    print("MFRC522 초기화 중...")
    try:
        rfid = MFRC522()
    except Exception as e:
        print(f"초기화 실패: {e}")
        return

    # 버전 확인
    version = rfid.get_version()
    print(f"MFRC522 펌웨어 버전: 0x{version:02X}")

    if version == 0x91:
        print("✓ MFRC522 Version 1.0 감지")
    elif version == 0x92:
        print("✓ MFRC522 Version 2.0 감지")
    elif version == 0x00:
        print("✗ 통신 실패: MISO 연결 확인 필요 (0x00)")
        return
    elif version == 0xFF:
        print("✗ 통신 실패: MISO floating (0xFF)")
        return
    else:
        print(f"⚠ 알 수 없는 버전: 0x{version:02X}")

    print()
    print("-" * 50)
    print("카드를 리더에 가까이 대세요...")
    print("(Ctrl+C로 종료)")
    print("-" * 50)
    print()

    last_uid = None
    scan_count = 0

    try:
        while True:
            scan_count += 1

            # 매 100번마다 상태 출력
            if scan_count % 100 == 0:
                print(f"스캔 중... ({scan_count // 10}초)")

            # 카드 감지 요청
            (status, tag_type) = rfid.request()

            if status:
                print("\n>>> 카드 감지됨! <<<")

                # 충돌 방지 및 UID 읽기
                (status, uid) = rfid.anticoll()

                if status:
                    uid_str = format_uid(uid)

                    # 같은 카드가 계속 감지되는 것 방지
                    if uid != last_uid:
                        print(f"  UID: {uid_str}")
                        print(f"  UID (raw): {uid}")

                        if tag_type:
                            print(f"  Tag Type: 0x{tag_type[0]:02X}{tag_type[1]:02X}")

                        # 카드 선택
                        if rfid.select_tag(uid):
                            print("  ✓ 카드 선택 성공")
                        else:
                            print("  ✗ 카드 선택 실패")

                        last_uid = uid

                        # 카드 HALT
                        rfid.halt()

                        print()
                        print("다시 카드를 대세요...")
                        print()

                        # 중복 읽기 방지를 위한 대기
                        time.sleep(1)

                else:
                    print("  ✗ UID 읽기 실패")

            # 다음 카드가 감지되면 last_uid 초기화
            elif last_uid is not None:
                last_uid = None

            time.sleep(0.1)  # 100ms 대기

    except KeyboardInterrupt:
        print("\n\n종료")
    except Exception as e:
        print(f"\n오류 발생: {e}")

    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
