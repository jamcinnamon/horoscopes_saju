"""
운세 생성 스크립트 - MVP
사용자 생년월일 입력 → 운세 결과 출력
"""
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, date
from app.database_mongo import connect_to_mongo, init_db
from app.models.mongo import HoroscopeDocument
from app.utils import get_zodiac_sign, format_date_korean
from app.config import settings
from openai import OpenAI

# OpenAI 클라이언트
client = OpenAI(api_key=settings.openai_api_key)


async def get_today_horoscope(zodiac_sign: str) -> dict:
    """오늘의 별자리 운세 조회 (한글로 번역)"""
    today = date.today()
    
    # MongoDB에서 가장 최근 운세 조회
    horoscope = await HoroscopeDocument.find_one(
        HoroscopeDocument.zodiac_sign == zodiac_sign,
        sort=[("date", -1)]
    )
    
    if horoscope:
        # 영어 운세를 한글로 번역
        horoscope_text = horoscope.horoscope_text
        
        # 영어인 경우 OpenAI로 번역
        if any(ord(char) < 128 for char in horoscope_text[:50]):  # 영어 포함 확인
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
        
        return {
            "text": horoscope_text,
            "love": horoscope.love_text or "",
            "lucky_number": horoscope.lucky_number or 7,
            "lucky_color": horoscope.lucky_color or "파란색"
        }
    
    return {
        "text": "오늘은 새로운 시작의 날입니다.",
        "love": "사랑운이 좋습니다.",
        "lucky_number": 7,
        "lucky_color": "파란색"
    }


def calculate_saju_simple(birth_date: date, birth_time: str = None) -> dict:
    """사주 계산 (천간지지) - 출생 시간 포함"""
    year = birth_date.year
    
    # 천간 (10개)
    천간 = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
    # 지지 (12개)
    지지 = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]
    
    # 년주 계산 (1984년 = 갑자년 기준)
    base_year = 1984
    year_offset = (year - base_year) % 60
    
    천간_idx = year_offset % 10
    지지_idx = year_offset % 12
    
    년주 = f"{천간[천간_idx]}{지지[지지_idx]}"
    
    # 월주 (간단히 월 기반)
    month = birth_date.month
    월주 = f"{천간[month % 10]}{지지[month % 12]}"
    
    # 일주 (간단히 일 기반)
    day = birth_date.day
    일주 = f"{천간[day % 10]}{지지[day % 12]}"
    
    # 시주 계산 (출생 시간이 있는 경우)
    시주 = None
    if birth_time:
        try:
            hour = int(birth_time.split(':')[0])
            # 시간대별 지지 매핑
            시간_지지 = {
                (23, 1): "자", (1, 3): "축", (3, 5): "인", (5, 7): "묘",
                (7, 9): "진", (9, 11): "사", (11, 13): "오", (13, 15): "미",
                (15, 17): "신", (17, 19): "유", (19, 21): "술", (21, 23): "해"
            }
            
            for (start, end), 지지_char in 시간_지지.items():
                if start <= hour < end or (start == 23 and hour >= 23):
                    시주 = f"{천간[hour % 10]}{지지_char}"
                    break
        except:
            pass
    
    result = {
        "년주": 년주,
        "월주": 월주,
        "일주": 일주,
        "시주": 시주,
        "오행": analyze_elements(년주, 월주, 일주, 시주)
    }
    
    return result


def analyze_elements(년주: str, 월주: str, 일주: str, 시주: str = None) -> dict:
    """오행 분석"""
    # 간단한 오행 매핑
    오행_매핑 = {
        "갑": "목", "을": "목",
        "병": "화", "정": "화",
        "무": "토", "기": "토",
        "경": "금", "신": "금",
        "임": "수", "계": "수"
    }
    
    elements = {"목": 0, "화": 0, "토": 0, "금": 0, "수": 0}
    
    pillars = [년주[0], 월주[0], 일주[0]]
    if 시주:
        pillars.append(시주[0])
    
    for char in pillars:
        if char in 오행_매핑:
            elements[오행_매핑[char]] += 1
    
    return elements


def generate_saju_fortune(saju_info: dict, birth_date: date) -> str:
    """OpenAI로 사주 기반 오늘의 운세 생성 (3-4줄)"""
    시주_info = f", 시주 {saju_info['시주']}" if saju_info.get('시주') else ""
    
    prompt = f"""당신은 전문 사주 상담가입니다.

생년월일: {format_date_korean(birth_date)}
사주: 년주 {saju_info['년주']}, 월주 {saju_info['월주']}, 일주 {saju_info['일주']}{시주_info}
오행: {saju_info['오행']}

위 사주 정보를 바탕으로 오늘의 운세를 3-4줄로 작성해주세요.
긍정적이고 희망적인 톤으로 작성하되, 구체적인 조언을 포함해주세요.
존댓말을 사용해주세요."""

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()


def generate_year_fortune(zodiac_sign: str, saju_info: dict, birth_date: date) -> str:
    """OpenAI로 한 해 운세 생성"""
    current_year = datetime.now().year
    시주_info = f", 시주 {saju_info['시주']}" if saju_info.get('시주') else ""
    
    prompt = f"""당신은 전문 운세 상담가입니다.

별자리: {zodiac_sign}
생년월일: {format_date_korean(birth_date)}
사주: 년주 {saju_info['년주']}, 월주 {saju_info['월주']}, 일주 {saju_info['일주']}{시주_info}

{current_year}년 한 해 운세를 5-6줄로 요약해주세요.
전반적인 운세, 재물운, 건강운, 인간관계를 포함해주세요.
존댓말을 사용해주세요."""

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()


def generate_html_output(filename: str, birth_date: date, birth_time: str, zodiac_sign: str,
                        saju_info: dict, saju_fortune: str, horoscope_today: dict,
                        year_fortune: str, personality: str, premium: bool):
    """HTML 형식으로 운세 결과 생성"""
    시주_display = f", 시주 {saju_info['시주']}" if saju_info.get('시주') else ""
    birth_time_display = f"<p><strong>⏰ 출생 시간:</strong> {birth_time}</p>" if birth_time else ""
    
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>운세 결과 - {format_date_korean(birth_date)}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.8;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .info-section {{
            background: #f8f9fa;
            padding: 30px;
            border-bottom: 3px solid #667eea;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .info-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .info-card strong {{
            color: #667eea;
            display: block;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .fortune-section {{
            margin-bottom: 40px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 15px;
            border-left: 5px solid #667eea;
        }}
        
        .fortune-section h2 {{
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .fortune-section p {{
            color: #333;
            font-size: 1.1em;
            line-height: 2;
            white-space: pre-wrap;
        }}
        
        .lucky-box {{
            display: flex;
            gap: 20px;
            margin-top: 15px;
        }}
        
        .lucky-item {{
            flex: 1;
            background: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .lucky-item .icon {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .lucky-item .label {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }}
        
        .lucky-item .value {{
            color: #667eea;
            font-size: 1.5em;
            font-weight: bold;
        }}
        
        .premium-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
            margin-left: 10px;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
            border-top: 3px solid #667eea;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✨ 운세 결과</h1>
            <p class="subtitle">별자리와 사주가 알려주는 당신의 운명</p>
        </div>
        
        <div class="info-section">
            <h2 style="color: #667eea; margin-bottom: 20px;">📋 기본 정보</h2>
            <div class="info-grid">
                <div class="info-card">
                    <strong>📅 생년월일</strong>
                    <p>{format_date_korean(birth_date)}</p>
                    {birth_time_display}
                </div>
                <div class="info-card">
                    <strong>♈ 별자리</strong>
                    <p>{zodiac_sign}</p>
                </div>
                <div class="info-card">
                    <strong>🎴 사주</strong>
                    <p>년주 {saju_info['년주']}<br>
                    월주 {saju_info['월주']}<br>
                    일주 {saju_info['일주']}{시주_display}</p>
                </div>
                <div class="info-card">
                    <strong>🌟 오행</strong>
                    <p>목: {saju_info['오행']['목']} | 화: {saju_info['오행']['화']}<br>
                    토: {saju_info['오행']['토']} | 금: {saju_info['오행']['금']}<br>
                    수: {saju_info['오행']['수']}</p>
                </div>
            </div>
        </div>
        
        <div class="content">
            <div class="fortune-section">
                <h2>🔮 오늘의 운세 - 사주 기반</h2>
                <p>{saju_fortune}</p>
            </div>
            
            <div class="fortune-section">
                <h2>⭐ 오늘의 운세 - 별자리 기반</h2>
                <p>{horoscope_today['text']}</p>
                
                <div class="lucky-box">
                    <div class="lucky-item">
                        <div class="icon">🎲</div>
                        <div class="label">행운의 숫자</div>
                        <div class="value">{horoscope_today['lucky_number']}</div>
                    </div>
                    <div class="lucky-item">
                        <div class="icon">🎨</div>
                        <div class="label">행운의 색</div>
                        <div class="value">{horoscope_today['lucky_color']}</div>
                    </div>
                </div>
            </div>
            
            <div class="fortune-section">
                <h2>🌈 {datetime.now().year}년 한 해 운세</h2>
                <p>{year_fortune}</p>
            </div>
            
            <div class="fortune-section">
                <h2>💫 내 성향은?{'<span class="premium-badge">프리미엄</span>' if premium else ''}</h2>
                <p>{personality}</p>
            </div>
        </div>
        
        <div class="footer">
            <p>생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</p>
            <p style="margin-top: 10px; font-size: 0.9em;">이 운세는 AI와 전통 사주학을 결합하여 생성되었습니다.</p>
        </div>
    </div>
</body>
</html>"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)


def generate_personality(zodiac_sign: str, saju_info: dict, birth_date: date, premium: bool = False) -> str:
    """OpenAI로 성향 분석 생성"""
    lines = "20줄 이상" if premium else "5-7줄"
    시주_info = f", 시주 {saju_info['시주']}" if saju_info.get('시주') else ""
    
    prompt = f"""당신은 전문 성격 분석가입니다.

별자리: {zodiac_sign}
생년월일: {format_date_korean(birth_date)}
사주: 년주 {saju_info['년주']}, 월주 {saju_info['월주']}, 일주 {saju_info['일주']}{시주_info}
오행: {saju_info['오행']}

위 정보를 바탕으로 이 사람의 성향을 {lines}로 분석해주세요.
- 성격적 특징
- 강점과 약점
- 대인관계 스타일
- 적합한 직업이나 환경
을 포함해주세요.
존댓말을 사용해주세요."""

    max_tokens = 1000 if premium else 300
    
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()


async def generate_complete_fortune(birth_date: date, birth_time: str = None, premium: bool = False):
    """완전한 운세 생성"""
    print("=" * 60)
    print("🔮 운세 생성 중...")
    print("=" * 60)
    
    # 1. 별자리 계산
    zodiac_sign = get_zodiac_sign(birth_date)
    print(f"\n📅 생년월일: {format_date_korean(birth_date)}")
    if birth_time:
        print(f"⏰ 출생 시간: {birth_time}")
    print(f"♈ 별자리: {zodiac_sign}")
    
    # 2. 사주 계산
    saju_info = calculate_saju_simple(birth_date, birth_time)
    시주_display = f", 시주 {saju_info['시주']}" if saju_info.get('시주') else ""
    print(f"🎴 사주: 년주 {saju_info['년주']}, 월주 {saju_info['월주']}, 일주 {saju_info['일주']}{시주_display}")
    print(f"🌟 오행: {saju_info['오행']}")
    
    # 3. 오늘의 별자리 운세 조회
    print("\n📖 오늘의 운세 조회 중...")
    horoscope_today = await get_today_horoscope(zodiac_sign)
    
    # 4. OpenAI로 사주 기반 운세 생성
    print("🤖 AI 운세 생성 중...")
    saju_fortune = generate_saju_fortune(saju_info, birth_date)
    
    # 5. 한 해 운세 생성
    year_fortune = generate_year_fortune(zodiac_sign, saju_info, birth_date)
    
    # 6. 성향 분석 생성
    personality = generate_personality(zodiac_sign, saju_info, birth_date, premium)
    
    # 결과 출력
    print("\n" + "=" * 60)
    print("✨ 운세 결과")
    print("=" * 60)
    
    print(f"\n【오늘의 운세 - 사주 기반】")
    print(saju_fortune)
    
    print(f"\n【오늘의 운세 - 별자리 기반】")
    print(horoscope_today['text'][:200] + "..." if len(horoscope_today['text']) > 200 else horoscope_today['text'])
    
    print(f"\n【오늘의 행운】")
    print(f"🎲 행운의 숫자: {horoscope_today['lucky_number']}")
    print(f"🎨 행운의 색: {horoscope_today['lucky_color']}")
    
    print(f"\n【{datetime.now().year}년 한 해 운세】")
    print(year_fortune)
    
    print(f"\n【내 성향은?】{'(프리미엄)' if premium else ''}")
    print(personality)
    
    print("\n" + "=" * 60)
    
    # 파일로 저장
    output_file = f"운세결과_{birth_date.strftime('%Y%m%d')}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("✨ 운세 결과\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"📅 생년월일: {format_date_korean(birth_date)}\n")
        if birth_time:
            f.write(f"⏰ 출생 시간: {birth_time}\n")
        f.write(f"♈ 별자리: {zodiac_sign}\n")
        시주_display = f", 시주 {saju_info['시주']}" if saju_info.get('시주') else ""
        f.write(f"🎴 사주: 년주 {saju_info['년주']}, 월주 {saju_info['월주']}, 일주 {saju_info['일주']}{시주_display}\n\n")
        
        f.write("【오늘의 운세 - 사주 기반】\n")
        f.write(saju_fortune + "\n\n")
        
        f.write("【오늘의 운세 - 별자리 기반】\n")
        f.write(horoscope_today['text'] + "\n\n")
        
        f.write("【오늘의 행운】\n")
        f.write(f"🎲 행운의 숫자: {horoscope_today['lucky_number']}\n")
        f.write(f"🎨 행운의 색: {horoscope_today['lucky_color']}\n\n")
        
        f.write(f"【{datetime.now().year}년 한 해 운세】\n")
        f.write(year_fortune + "\n\n")
        
        f.write(f"【내 성향은?】{'(프리미엄)' if premium else ''}\n")
        f.write(personality + "\n\n")
    
    print(f"✅ 결과가 '{output_file}' 파일로 저장되었습니다!")
    
    # HTML 파일 생성
    html_file = f"운세결과_{birth_date.strftime('%Y%m%d')}.html"
    generate_html_output(
        html_file, birth_date, birth_time, zodiac_sign, saju_info,
        saju_fortune, horoscope_today, year_fortune, personality, premium
    )
    print(f"✅ HTML 결과가 '{html_file}' 파일로 저장되었습니다!")
    
    # HTML 파일 자동 열기
    import webbrowser
    import os
    webbrowser.open('file://' + os.path.abspath(html_file))
    print(f"🌐 브라우저에서 결과를 확인하세요!")


async def main():
    """메인 함수"""
    # MongoDB 연결
    await connect_to_mongo()
    await init_db()
    
    print("🔮 운세 생성 서비스")
    print("=" * 60)
    
    # 사용자 입력
    date_str = input("생년월일을 입력하세요 (예: 1990-05-15): ").strip()
    
    try:
        birth_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print("❌ 날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요.")
        return
    
    # 출생 시간 입력 (선택사항)
    time_str = input("출생 시간을 입력하세요 (예: 14:30, 선택사항 - Enter로 건너뛰기): ").strip()
    birth_time = time_str if time_str else None
    
    if birth_time:
        try:
            # 시간 형식 검증
            datetime.strptime(birth_time, "%H:%M")
        except ValueError:
            print("⚠️ 시간 형식이 올바르지 않습니다. HH:MM 형식이어야 합니다. 시간 없이 진행합니다.")
            birth_time = None
    
    premium_input = input("프리미엄 버전? (y/n, 기본: n): ").strip().lower()
    premium = premium_input == 'y'
    
    # 운세 생성
    await generate_complete_fortune(birth_date, birth_time, premium)


if __name__ == "__main__":
    asyncio.run(main())
