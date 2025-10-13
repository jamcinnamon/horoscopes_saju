"""
사주 직접 입력 테스트
"""
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, date
from generate_fortune_html import generate_complete_fortune_html, analyze_elements
from app.database_mongo import connect_to_mongo, init_db


async def test():
    """테스트 함수"""
    # MongoDB 연결
    await connect_to_mongo()
    await init_db()
    
    # 테스트 데이터
    birth_date = date(1991, 11, 25)
    birth_time = "12:00"
    
    # 제미나이가 확인한 정확한 사주
    saju_info = {
        "년주": "신미",
        "월주": "을해",
        "일주": "기축",
        "시주": "경오",
        "오행": analyze_elements("신미", "을해", "기축", "경오")
    }
    
    print("=" * 60)
    print("테스트: 1991년 11월 25일 12시 - 정확한 사주 입력")
    print("=" * 60)
    print(f"년주: {saju_info['년주']}")
    print(f"월주: {saju_info['월주']}")
    print(f"일주: {saju_info['일주']}")
    print(f"시주: {saju_info['시주']}")
    print(f"오행: {saju_info['오행']}")
    print("=" * 60)
    
    # 프리미엄 버전으로 생성
    await generate_complete_fortune_html(birth_date, saju_info, birth_time, premium=True)


if __name__ == "__main__":
    asyncio.run(test())
