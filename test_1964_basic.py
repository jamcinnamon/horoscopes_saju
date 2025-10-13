"""
테스트: 1964년 3월 5일 여자 - 베이직 버전
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
    birth_time = None
    
    saju_info = {
        "년주": "갑진",
        "월주": "병인",
        "일주": "무진",
        "시주": None,
        "오행": analyze_elements("갑진", "병인", "무진", None)
    }
    
    print("=" * 60)
    print("테스트: 1964년 3월 5일 여자 - 베이직 버전")
    print("=" * 60)
    
    # 베이직 버전으로 생성
    await generate_complete_fortune_html(birth_date, saju_info, birth_time, premium=False)


if __name__ == "__main__":
    asyncio.run(test())
