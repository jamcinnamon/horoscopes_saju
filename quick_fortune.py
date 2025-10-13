"""
간편 운세 생성 스크립트
코드에서 직접 정보를 입력하고 실행하면 됩니다.

📝 사용 방법:
1. 고객에게 생년월일, 출생시간 받기
2. 아래 사주 확인 사이트에서 사주 정보 확인 (30초)
3. 아래 정보 입력
4. python quick_fortune.py 실행
5. 생성된 HTML 파일을 고객에게 전달

🔗 사주 확인 사이트:
   https://www.sajuplus.com (추천)
   https://www.saju.co.kr
   
   사이트 접속 → 생년월일, 출생시간 입력 → 사주 확인
   (년주, 월주, 일주, 시주를 확인하세요)
"""
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, date
from generate_fortune_html import generate_complete_fortune_html, analyze_elements
from app.database_mongo import connect_to_mongo, init_db


# ============================================
# 여기에 고객 정보를 입력하세요!
# ============================================

# 기본 정보
NAME = "김연정"  # 이름 (선택사항, 파일명에만 사용)
BIRTH_DATE = "1991-11-25"  # 생년월일 (YYYY-MM-DD 형식)
BIRTH_TIME = "12:10"  # 출생 시간 (HH:MM 형식) - 모르면 빈칸 ""

# 사주 정보 (https://www.sajuplus.com 에서 확인)
# 사이트에서 생년월일, 출생시간 입력 후 나오는 사주 정보를 아래에 입력하세요
YEAR_PILLAR = "경진"  # 년주 (年柱)
MONTH_PILLAR = "계미"  # 월주 (月柱)
DAY_PILLAR = "신축"  # 일주 (日柱)
HOUR_PILLAR = ""  # 시주 (時柱) - 출생시간 모르면 빈칸 ""

# 버전 선택
PREMIUM = False  # True: 프리미엄 (80,000원), False: 베이직 (50,000원)

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
    hour_pillar = HOUR_PILLAR if HOUR_PILLAR else None
    
    # 사주 정보 구성
    saju_info = {
        "년주": YEAR_PILLAR,
        "월주": MONTH_PILLAR,
        "일주": DAY_PILLAR,
        "시주": hour_pillar,
        "오행": analyze_elements(YEAR_PILLAR, MONTH_PILLAR, DAY_PILLAR, hour_pillar)
    }
    
    print("=" * 60)
    print("🔮 운세 생성 시작")
    print("=" * 60)
    print(f"이름: {NAME}")
    print(f"생년월일: {BIRTH_DATE}")
    print(f"출생시간: {BIRTH_TIME if BIRTH_TIME else '모름'}")
    print(f"년주: {YEAR_PILLAR}")
    print(f"월주: {MONTH_PILLAR}")
    print(f"일주: {DAY_PILLAR}")
    print(f"시주: {HOUR_PILLAR if HOUR_PILLAR else '모름'}")
    print(f"버전: {'프리미엄' if PREMIUM else '베이직'}")
    print("=" * 60)
    
    # 운세 생성
    await generate_complete_fortune_html(birth_date, saju_info, birth_time, PREMIUM)
    
    print("\n✅ 완료!")


if __name__ == "__main__":
    asyncio.run(generate())
