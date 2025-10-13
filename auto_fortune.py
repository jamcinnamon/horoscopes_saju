"""
자동 사주 계산 운세 생성
생년월일과 시간만 입력하면 사주를 자동으로 계산하고 확인 후 생성합니다.

📝 사용 방법:
1. 고객에게 생년월일, 출생시간만 받기
2. 아래 정보 입력
3. python auto_fortune.py 실행
4. 자동 계산된 사주 확인 (수정 가능)
5. 생성된 HTML 파일을 고객에게 전달

⚠️ 사주 계산은 참고용입니다. 정확한 사주는 만세력 사이트에서 확인하세요.
"""
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, date
from generate_fortune_html import generate_complete_fortune_html
from saju_calculator import calculate_saju
from app.database_mongo import connect_to_mongo, init_db


# ============================================
# 여기에 고객 정보를 입력하세요!
# ============================================

# 기본 정보
NAME = "김흥모"  # 이름 (선택사항)
BIRTH_DATE = "1963-09-08"  # 생년월일 (YYYY-MM-DD 형식)
BIRTH_TIME = ""  # 출생 시간 (HH:MM 형식) - 모르면 빈칸 ""

# 버전 선택
PREMIUM = True  # True: 프리미엄 (80,000원), False: 베이직 (50,000원)

# ============================================
# 아래는 수정하지 마세요!
# ============================================


async def generate():
    """운세 생성"""
    # MongoDB 연결
    await connect_to_mongo()
    await init_db()
    
    # 날짜 파싱
    birth_date = datetime.strptime(BIRTH_DATE, "%Y-%m-%d").date()
    birth_time = BIRTH_TIME if BIRTH_TIME else None
    
    print("=" * 60)
    print("🔮 자동 사주 계산 운세 생성")
    print("=" * 60)
    print(f"이름: {NAME}")
    print(f"생년월일: {BIRTH_DATE}")
    print(f"출생시간: {BIRTH_TIME if BIRTH_TIME else '모름'}")
    print(f"버전: {'프리미엄' if PREMIUM else '베이직'}")
    print("=" * 60)
    
    # 사주 자동 계산
    print("\n🤖 사주 자동 계산 중...")
    saju_info = calculate_saju(birth_date, birth_time)
    
    print("\n" + "=" * 60)
    print("📋 계산된 사주 정보")
    print("=" * 60)
    print(f"년주: {saju_info['년주']}")
    print(f"월주: {saju_info['월주']}")
    print(f"일주: {saju_info['일주']}")
    print(f"시주: {saju_info['시주'] if saju_info['시주'] else '모름'}")
    print(f"오행: {saju_info['오행']}")
    print("=" * 60)
    
    print("\n⚠️ 사주 계산은 참고용입니다.")
    print("💡 정확한 사주는 https://www.sajuplus.com 에서 확인하세요.")
    print("\n이대로 진행하시겠습니까?")
    print("1. 예 (이대로 생성)")
    print("2. 아니오 (사주 수정)")
    
    choice = input("\n선택 (1 또는 2): ").strip()
    
    if choice == "2":
        print("\n" + "=" * 60)
        print("사주 정보를 수정하세요 (Enter: 그대로 유지)")
        print("=" * 60)
        
        년주_input = input(f"년주 [{saju_info['년주']}]: ").strip()
        if 년주_input:
            saju_info['년주'] = 년주_input
        
        월주_input = input(f"월주 [{saju_info['월주']}]: ").strip()
        if 월주_input:
            saju_info['월주'] = 월주_input
        
        일주_input = input(f"일주 [{saju_info['일주']}]: ").strip()
        if 일주_input:
            saju_info['일주'] = 일주_input
        
        if birth_time:
            시주_input = input(f"시주 [{saju_info['시주']}]: ").strip()
            if 시주_input:
                saju_info['시주'] = 시주_input
        
        # 오행 재계산
        from saju_calculator import analyze_elements
        saju_info['오행'] = analyze_elements(
            saju_info['년주'],
            saju_info['월주'],
            saju_info['일주'],
            saju_info['시주']
        )
        
        print("\n✅ 수정된 사주:")
        print(f"년주: {saju_info['년주']}")
        print(f"월주: {saju_info['월주']}")
        print(f"일주: {saju_info['일주']}")
        print(f"시주: {saju_info['시주'] if saju_info['시주'] else '모름'}")
    
    # 운세 생성
    print("\n" + "=" * 60)
    print("🎨 운세 생성 시작...")
    print("=" * 60)
    
    await generate_complete_fortune_html(birth_date, saju_info, birth_time, PREMIUM)
    
    print("\n✅ 완료!")


if __name__ == "__main__":
    asyncio.run(generate())
