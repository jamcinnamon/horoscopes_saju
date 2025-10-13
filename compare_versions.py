"""
베이직 vs 프리미엄 비교용
같은 사람의 베이직과 프리미엄 버전을 모두 생성합니다.
"""
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, date
from generate_fortune_pdf import generate_complete_fortune_pdf
from saju_calculator import calculate_saju
from app.database_mongo import connect_to_mongo, init_db


# ============================================
# 여기에 고객 정보를 입력하세요!
# ============================================

NAME = "김연정"
BIRTH_DATE = "1991-11-25"
BIRTH_TIME = "12:10"

# ============================================


async def generate_both():
    """베이직과 프리미엄 모두 생성"""
    await connect_to_mongo()
    await init_db()
    
    birth_date = datetime.strptime(BIRTH_DATE, "%Y-%m-%d").date()
    birth_time = BIRTH_TIME if BIRTH_TIME else None
    
    print("=" * 60)
    print("🔮 베이직 vs 프리미엄 비교 생성")
    print("=" * 60)
    print(f"이름: {NAME}")
    print(f"생년월일: {BIRTH_DATE}")
    print(f"출생시간: {BIRTH_TIME if BIRTH_TIME else '모름'}")
    print("=" * 60)
    
    # 사주 자동 계산
    print("\n🤖 사주 자동 계산 중...")
    saju_info = calculate_saju(birth_date, birth_time)
    
    print("\n📋 계산된 사주:")
    print(f"년주: {saju_info['년주']}")
    print(f"월주: {saju_info['월주']}")
    print(f"일주: {saju_info['일주']}")
    print(f"시주: {saju_info['시주'] if saju_info['시주'] else '모름'}")
    
    # 베이직 버전 생성
    print("\n" + "=" * 60)
    print("📄 1. 베이직 버전 생성 중...")
    print("=" * 60)
    await generate_complete_fortune_pdf(birth_date, saju_info, birth_time, premium=False)
    
    print("\n⏳ 잠시 대기 중... (3초)")
    await asyncio.sleep(3)
    
    # 프리미엄 버전 생성
    print("\n" + "=" * 60)
    print("💎 2. 프리미엄 버전 생성 중...")
    print("=" * 60)
    await generate_complete_fortune_pdf(birth_date, saju_info, birth_time, premium=True)
    
    print("\n" + "=" * 60)
    print("✨ 완료! 두 파일을 비교해보세요!")
    print("=" * 60)
    print(f"📄 베이직: 운세결과_{birth_date.strftime('%Y%m%d')}.pdf")
    print(f"💎 프리미엄: 운세결과_{birth_date.strftime('%Y%m%d')}_프리미엄.pdf")
    print("\n💡 두 파일을 나란히 열어서 비교해보세요!")
    print("   차이점: '내 성향은?' 섹션의 분량과 깊이")


if __name__ == "__main__":
    asyncio.run(generate_both())
