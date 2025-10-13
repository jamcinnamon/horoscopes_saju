"""
초간편 일괄 운세 생성
아래 리스트에 고객 정보를 추가하고 실행하면 됩니다.

📝 사용 방법:
1. 고객들에게 생년월일, 출생시간 받기
2. 각 고객별로 사주 확인 사이트에서 사주 정보 확인
3. 아래 CUSTOMERS 리스트에 정보 추가
4. python easy_batch.py 실행
5. 생성된 ZIP 파일을 고객에게 전달

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
from generate_fortune_html import analyze_elements
from batch_fortune import generate_single_fortune
from app.database_mongo import connect_to_mongo, init_db
import os
import zipfile


# ============================================
# 여기에 고객 정보를 입력하세요!
# ============================================

CUSTOMERS = [
    {
        "name": "김철수",
        "birth_date": "1990-05-15",
        "birth_time": "14:30",  # 모르면 ""
        "year_pillar": "경오",
        "month_pillar": "신사",
        "day_pillar": "기묘",
        "hour_pillar": "신미",  # 모르면 ""
        "premium": False  # True: 프리미엄, False: 베이직
    },
    {
        "name": "이영희",
        "birth_date": "1991-11-25",
        "birth_time": "12:00",
        "year_pillar": "신미",
        "month_pillar": "을해",
        "day_pillar": "기축",
        "hour_pillar": "경오",
        "premium": True
    },
    {
        "name": "박민수",
        "birth_date": "2000-07-13",
        "birth_time": "",  # 시간 모름
        "year_pillar": "경진",
        "month_pillar": "계미",
        "day_pillar": "신축",
        "hour_pillar": "",  # 시주 모름
        "premium": False
    },
]

# ============================================


async def generate_all():
    """일괄 운세 생성"""
    # MongoDB 연결
    await connect_to_mongo()
    await init_db()
    
    # 출력 디렉토리 생성
    output_dir = f"운세결과_일괄_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("🔮 일괄 운세 생성 시작")
    print("=" * 60)
    print(f"총 {len(CUSTOMERS)}명")
    print("=" * 60)
    
    generated_files = []
    
    for idx, customer in enumerate(CUSTOMERS, 1):
        print(f"\n[{idx}/{len(CUSTOMERS)}] {customer['name']}님 처리 중...")
        
        try:
            # 데이터 파싱
            birth_date = datetime.strptime(customer['birth_date'], "%Y-%m-%d").date()
            birth_time = customer['birth_time'] if customer['birth_time'] else None
            hour_pillar = customer['hour_pillar'] if customer['hour_pillar'] else None
            
            # 사주 정보
            saju_info = {
                "년주": customer['year_pillar'],
                "월주": customer['month_pillar'],
                "일주": customer['day_pillar'],
                "시주": hour_pillar,
            }
            saju_info["오행"] = analyze_elements(
                saju_info["년주"],
                saju_info["월주"],
                saju_info["일주"],
                saju_info["시주"]
            )
            
            person_data = {
                'name': customer['name'],
                'birth_date': birth_date,
                'birth_time': birth_time,
                'saju_info': saju_info,
                'premium': customer['premium']
            }
            
            # 운세 생성
            output_file = await generate_single_fortune(person_data, output_dir)
            generated_files.append(output_file)
            
        except Exception as e:
            print(f"❌ {customer['name']}님 처리 실패: {e}")
            continue
    
    # ZIP 파일로 압축
    zip_filename = f"{output_dir}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in generated_files:
            zipf.write(file, os.path.basename(file))
    
    print("\n" + "=" * 60)
    print("✨ 일괄 운세 생성 완료!")
    print("=" * 60)
    print(f"📁 출력 폴더: {output_dir}")
    print(f"📦 ZIP 파일: {zip_filename}")
    print(f"✅ 총 {len(generated_files)}명의 운세 생성 완료")
    
    return output_dir, zip_filename


if __name__ == "__main__":
    asyncio.run(generate_all())
