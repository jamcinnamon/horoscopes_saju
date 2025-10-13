"""
MongoDB 데이터 확인
"""
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.database_mongo import connect_to_mongo, init_db
from app.models.mongo import HoroscopeDocument

async def check():
    await connect_to_mongo()
    await init_db()
    
    # 전체 개수
    total = await HoroscopeDocument.count()
    print(f"📊 총 운세 데이터: {total}개")
    
    # 별자리별 개수
    print("\n별자리별 데이터:")
    zodiac_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    for sign in zodiac_signs:
        count = await HoroscopeDocument.find(HoroscopeDocument.zodiac_sign == sign).count()
        print(f"  {sign}: {count}개")
    
    # 샘플 데이터 확인
    print("\n샘플 데이터:")
    sample = await HoroscopeDocument.find_one()
    if sample:
        print(f"  날짜: {sample.date}")
        print(f"  별자리: {sample.zodiac_sign}")
        print(f"  운세: {sample.horoscope_text[:100]}...")
        print(f"  행운의 숫자: {sample.lucky_number}")
        print(f"  행운의 색: {sample.lucky_color}")

if __name__ == "__main__":
    asyncio.run(check())
