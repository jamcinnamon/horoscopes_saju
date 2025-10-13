"""
테스트: 1964년 3월 5일 여자
사주 정보는 https://www.sajuplus.com 에서 확인
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
    birth_date = date(1964, 3, 5)
    birth_time = None  # 출생 시간 모름
    
    # 1964년 3월 5일의 사주 (만세력 기준)
    # https://www.sajuplus.com 에서 확인한 정보
    # 년주: 갑진(甲辰)
    # 월주: 병인(丙寅)
    # 일주: 무진(戊辰)
    # 시주: 모름
    
    saju_info = {
        "년주": "갑진",
        "월주": "병인",
        "일주": "무진",
        "시주": None,
        "오행": analyze_elements("갑진", "병인", "무진", None)
    }
    
    print("=" * 60)
    print("테스트: 1964년 3월 5일 여자 (출생 시간 모름)")
    print("=" * 60)
    print(f"년주: {saju_info['년주']}")
    print(f"월주: {saju_info['월주']}")
    print(f"일주: {saju_info['일주']}")
    print(f"시주: 모름")
    print(f"오행: {saju_info['오행']}")
    print(f"별자리: 물고기자리 (Pisces)")
    print("=" * 60)
    
    # 프리미엄 버전으로 생성
    await generate_complete_fortune_html(birth_date, saju_info, birth_time, premium=True)


if __name__ == "__main__":
    asyncio.run(test())
