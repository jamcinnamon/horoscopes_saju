"""
출생 시간을 모르는 경우 테스트
2000년 7월 13일 (시간 모름)
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
    birth_date = date(2000, 7, 13)
    birth_time = None  # 출생 시간 모름
    
    # 2000년 7월 13일의 사주 (만세력 기준)
    # https://www.sajuplus.com 에서 확인
    # 년주: 경진(庚辰)
    # 월주: 계미(癸未)
    # 일주: 신축(辛丑)
    # 시주: 모름 (입력 안 함)
    
    saju_info = {
        "년주": "경진",
        "월주": "계미",
        "일주": "신축",
        "시주": None,  # 시간 모름
        "오행": analyze_elements("경진", "계미", "신축", None)
    }
    
    print("=" * 60)
    print("테스트: 2000년 7월 13일 (출생 시간 모름)")
    print("=" * 60)
    print(f"년주: {saju_info['년주']}")
    print(f"월주: {saju_info['월주']}")
    print(f"일주: {saju_info['일주']}")
    print(f"시주: 모름")
    print(f"오행: {saju_info['오행']}")
    print("=" * 60)
    
    # 베이직 버전으로 생성
    await generate_complete_fortune_html(birth_date, saju_info, birth_time, premium=False)


if __name__ == "__main__":
    asyncio.run(test())
