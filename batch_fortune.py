"""
여러 명 일괄 운세 생성 스크립트
CSV 파일로 여러 명의 정보를 입력받아 각각 HTML 운세 결과 생성
"""
import sys
import asyncio
import csv
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, date
from generate_fortune_html import generate_complete_fortune_html, analyze_elements
from app.database_mongo import connect_to_mongo, init_db
import zipfile
import os


async def generate_single_fortune(person_data: dict, output_dir: str) -> str:
    """개인별 운세 생성"""
    name = person_data['name']
    birth_date = person_data['birth_date']
    birth_time = person_data.get('birth_time')
    premium = person_data.get('premium', False)
    saju_info = person_data['saju_info']
    
    print(f"\n🔮 {name}님의 운세 생성 중...")
    
    # 운세 생성 (원본 함수 호출)
    from app.database_mongo import connect_to_mongo, init_db
    from app.models.mongo import HoroscopeDocument
    from app.utils import get_zodiac_sign, format_date_korean
    from app.config import settings
    from openai import OpenAI
    import webbrowser
    
    client = OpenAI(api_key=settings.openai_api_key)
    
    # 별자리 계산
    zodiac_sign = get_zodiac_sign(birth_date)
    
    # 오늘의 별자리 운세 조회
    horoscope = await HoroscopeDocument.find_one(
        HoroscopeDocument.zodiac_sign == zodiac_sign,
        sort=[("date", -1)]
    )
    
    if horoscope:
        horoscope_text = horoscope.horoscope_text
        if any(ord(char) < 128 for char in horoscope_text[:50]):
            prompt = f"""다음 별자리 운세를 자연스러운 한국어로 번역해주세요. 
번역할 때 존댓말을 사용하고, 운세 특유의 따뜻하고 희망적인 톤을 유지해주세요.

원문:
{horoscope_text}

한국어 번역:"""
            
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            horoscope_text = response.choices[0].message.content.strip()
        
        horoscope_today = {
            "text": horoscope_text,
            "lucky_number": horoscope.lucky_number or 7,
            "lucky_color": horoscope.lucky_color or "파란색"
        }
    else:
        horoscope_today = {
            "text": "오늘은 새로운 시작의 날입니다.",
            "lucky_number": 7,
            "lucky_color": "파란색"
        }
    
    # AI 운세 생성
    from generate_fortune_html import generate_saju_fortune, generate_year_fortune, generate_personality, get_zodiac_emoji, get_zodiac_korean, create_html_template
    
    saju_fortune = generate_saju_fortune(saju_info, birth_date)
    year_fortune = generate_year_fortune(zodiac_sign, saju_info, birth_date)
    personality = generate_personality(zodiac_sign, saju_info, birth_date, premium)
    
    # HTML 데이터 준비
    시주_display = f", 시주 {saju_info['시주']}" if saju_info.get('시주') else ""
    html_data = {
        'name': name,
        'birth_date': format_date_korean(birth_date),
        'birth_time': birth_time,
        'zodiac_sign': zodiac_sign,
        'zodiac_emoji': get_zodiac_emoji(zodiac_sign),
        'zodiac_korean': get_zodiac_korean(zodiac_sign),
        'saju_display': f"년주 {saju_info['년주']}, 월주 {saju_info['월주']}, 일주 {saju_info['일주']}{시주_display}",
        'saju_fortune': saju_fortune,
        'horoscope_fortune': horoscope_today['text'],
        'lucky_number': horoscope_today['lucky_number'],
        'lucky_color': horoscope_today['lucky_color'],
        'year_fortune': year_fortune,
        'personality': personality,
        'elements': saju_info['오행'],
        'premium': premium
    }
    
    # HTML 생성 (이름 포함 템플릿 사용)
    html_content = create_html_template_with_name(html_data)
    
    # HTML 파일 저장
    premium_suffix = "_프리미엄" if premium else ""
    safe_name = name.replace(" ", "_")
    output_file = os.path.join(output_dir, f"운세결과_{safe_name}_{birth_date.strftime('%Y%m%d')}{premium_suffix}.html")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ {name}님 완료: {output_file}")
    return output_file


def create_html_template_with_name(data: dict) -> str:
    """이름이 포함된 HTML 템플릿 생성"""
    return f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔮 운세 결과 - {data['name']} ({data['birth_date']})</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #ff6b6b, #feca57);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .user-info {{
            background: rgba(255,255,255,0.2);
            padding: 20px;
            border-radius: 15px;
            margin-top: 20px;
        }}
        
        .user-info h2 {{
            font-size: 1.8em;
            margin-bottom: 15px;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .info-item {{
            background: rgba(255,255,255,0.3);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .content {{
            padding: 40px 30px;
        }}
        
        .section {{
            margin-bottom: 40px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 15px;
            border-left: 5px solid #667eea;
        }}
        
        .section h3 {{
            color: #333;
            font-size: 1.5em;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .section-icon {{
            font-size: 1.2em;
        }}
        
        .section p {{
            line-height: 1.8;
            color: #555;
            font-size: 1.1em;
            white-space: pre-wrap;
        }}
        
        .lucky-info {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }}
        
        .lucky-item {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .lucky-item h4 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .lucky-value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        
        .premium-badge {{
            background: linear-gradient(45deg, #ff6b6b, #feca57);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
            margin-left: 10px;
        }}
        
        .footer {{
            background: #333;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 15px;
            }}
            
            .header {{
                padding: 30px 20px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .content {{
                padding: 30px 20px;
            }}
            
            .lucky-info {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔮 {data['name']}님의 운세</h1>
            <div class="user-info">
                <h2>{data['zodiac_emoji']} {data['zodiac_korean']}</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>📅 생년월일</strong><br>
                        {data['birth_date']}
                    </div>
                    {f'<div class="info-item"><strong>⏰ 출생시간</strong><br>{data["birth_time"]}</div>' if data.get('birth_time') else ''}
                    <div class="info-item">
                        <strong>🎴 사주</strong><br>
                        {data['saju_display']}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="content">
            <div class="section">
                <h3><span class="section-icon">🌟</span>오늘의 운세 - 사주 기반</h3>
                <p>{data['saju_fortune']}</p>
            </div>
            
            <div class="section">
                <h3><span class="section-icon">⭐</span>오늘의 운세 - 별자리 기반</h3>
                <p>{data['horoscope_fortune']}</p>
            </div>
            
            <div class="section">
                <h3><span class="section-icon">🍀</span>오늘의 행운</h3>
                <div class="lucky-info">
                    <div class="lucky-item">
                        <h4>🎲 행운의 숫자</h4>
                        <div class="lucky-value">{data['lucky_number']}</div>
                    </div>
                    <div class="lucky-item">
                        <h4>🎨 행운의 색</h4>
                        <div class="lucky-value">{data['lucky_color']}</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h3><span class="section-icon">📅</span>{datetime.now().year}년 한 해 운세</h3>
                <p>{data['year_fortune']}</p>
            </div>
            
            <div class="section">
                <h3>
                    <span class="section-icon">👤</span>내 성향은?
                    {f'<span class="premium-badge">프리미엄</span>' if data.get('premium') else ''}
                </h3>
                <p>{data['personality']}</p>
            </div>
        </div>
        
        <div class="footer">
            <p>🔮 운세 생성 서비스 | 생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</p>
            <p style="margin-top: 10px; font-size: 0.85em; opacity: 0.8;">
                ⚠️ 본 서비스의 사주 계산은 참고용이며, 정확한 사주는 전문가에게 확인하시기 바랍니다.
            </p>
        </div>
    </div>
</body>
</html>
"""


async def batch_generate_fortunes(csv_file: str, premium: bool = False):
    """CSV 파일로부터 일괄 운세 생성"""
    # MongoDB 연결
    await connect_to_mongo()
    await init_db()
    
    # 출력 디렉토리 생성
    output_dir = f"운세결과_일괄_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("🔮 일괄 운세 생성 시작")
    print("=" * 60)
    
    generated_files = []
    
    # CSV 파일 읽기
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for idx, row in enumerate(reader, 1):
            try:
                # 데이터 파싱
                name = row['이름']
                birth_date = datetime.strptime(row['생년월일'], "%Y-%m-%d").date()
                birth_time = row.get('출생시간', '').strip() or None
                
                # 사주 정보
                saju_info = {
                    "년주": row['년주'],
                    "월주": row['월주'],
                    "일주": row['일주'],
                    "시주": row.get('시주', '').strip() or None,
                }
                saju_info["오행"] = analyze_elements(
                    saju_info["년주"],
                    saju_info["월주"],
                    saju_info["일주"],
                    saju_info["시주"]
                )
                
                person_data = {
                    'name': name,
                    'birth_date': birth_date,
                    'birth_time': birth_time,
                    'saju_info': saju_info,
                    'premium': premium
                }
                
                # 운세 생성
                output_file = await generate_single_fortune(person_data, output_dir)
                generated_files.append(output_file)
                
            except Exception as e:
                print(f"❌ {idx}번째 행 처리 실패: {e}")
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


async def main():
    """메인 함수"""
    print("🔮 일괄 운세 생성 서비스")
    print("=" * 60)
    
    csv_file = input("CSV 파일 경로를 입력하세요 (예: people.csv): ").strip()
    
    if not os.path.exists(csv_file):
        print(f"❌ 파일을 찾을 수 없습니다: {csv_file}")
        return
    
    premium_input = input("프리미엄 버전으로 생성? (y/n, 기본: n): ").strip().lower()
    premium = premium_input == 'y'
    
    await batch_generate_fortunes(csv_file, premium)


if __name__ == "__main__":
    asyncio.run(main())
