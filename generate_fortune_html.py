"""
운세 생성 스크립트 - HTML 출력 버전 (한글 전용)
사용자 생년월일 입력 → 예쁜 HTML 운세 결과 출력
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
import webbrowser
import os

# OpenAI 클라이언트
client = OpenAI(api_key=settings.openai_api_key)


def translate_color_to_korean(color: str) -> str:
    """영어 색상을 한글로 번역"""
    color_map = {
        "red": "빨간색", "blue": "파란색", "green": "초록색", "yellow": "노란색",
        "purple": "보라색", "pink": "분홍색", "orange": "주황색", "white": "흰색",
        "black": "검은색", "brown": "갈색", "gray": "회색", "grey": "회색",
        "gold": "금색", "silver": "은색", "navy": "남색", "turquoise": "청록색",
        "violet": "보라색", "indigo": "남보라색", "cyan": "청록색", "magenta": "자홍색",
        "maroon": "적갈색", "olive": "올리브색", "teal": "청록색", "lime": "라임색"
    }
    
    color_lower = color.lower().strip()
    return color_map.get(color_lower, color)


async def get_today_horoscope(zodiac_sign: str) -> dict:
    """오늘의 별자리 운세 조회 (한글로 번역)"""
    today = date.today()
    
    # 오늘 날짜 기반으로 운세 선택 (113개 데이터를 순환)
    day_of_year = today.timetuple().tm_yday  # 1-365
    index = (day_of_year - 1) % 113  # 0-112 범위로 순환
    
    # MongoDB에서 해당 인덱스의 운세 조회
    horoscopes = await HoroscopeDocument.find(
        HoroscopeDocument.zodiac_sign == zodiac_sign,
        sort=[("date", 1)]
    ).to_list()
    
    horoscope = horoscopes[index] if horoscopes and len(horoscopes) > index else None
    
    # 데이터가 없으면 가장 최근 운세 사용
    if not horoscope:
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
        
        # 색상 한글 번역
        lucky_color = translate_color_to_korean(horoscope.lucky_color) if horoscope.lucky_color else "파란색"
        
        return {
            "text": horoscope_text,
            "love": horoscope.love_text or "",
            "lucky_number": horoscope.lucky_number or 7,
            "lucky_color": lucky_color
        }
    
    return {
        "text": "오늘은 새로운 시작의 날입니다.",
        "love": "사랑운이 좋습니다.",
        "lucky_number": 7,
        "lucky_color": "파란색"
    }


def analyze_elements(년주: str, 월주: str, 일주: str, 시주: str = None) -> dict:
    """오행 분석"""
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
    """OpenAI로 사주 기반 오늘의 운세 생성 (3-4줄) - 오행 분석 제외"""
    시주_info = f", 시주 {saju_info['시주']}" if saju_info.get('시주') else ""
    
    prompt = f"""당신은 전문 사주 상담가입니다.

생년월일: {format_date_korean(birth_date)}
사주: 년주 {saju_info['년주']}, 월주 {saju_info['월주']}, 일주 {saju_info['일주']}{시주_info}

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
    """OpenAI로 한 해 운세 생성 (요약)"""
    current_year = datetime.now().year
    zodiac_korean = get_zodiac_korean(zodiac_sign)
    시주_info = f", 시주 {saju_info['시주']}" if saju_info.get('시주') else ""
    
    prompt = f"""당신은 전문 운세 상담가입니다.

별자리: {zodiac_korean}
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


def generate_year_fortune_detail(zodiac_sign: str, saju_info: dict, birth_date: date) -> str:
    """OpenAI로 한 해 운세 생성 (상세) - 프리미엄 전용"""
    current_year = datetime.now().year
    zodiac_korean = get_zodiac_korean(zodiac_sign)
    시주_info = f", 시주 {saju_info['시주']}" if saju_info.get('시주') else ""
    
    prompt = f"""당신은 전문 운세 상담가입니다.

별자리: {zodiac_korean}
생년월일: {format_date_korean(birth_date)}
사주: 년주 {saju_info['년주']}, 월주 {saju_info['월주']}, 일주 {saju_info['일주']}{시주_info}
오행: {saju_info['오행']}

{current_year}년 한 해 운세를 15-20줄로 상세하게 분석해주세요.

다음 내용을 포함해주세요:
- 전반적인 운세 (상반기/하반기 구분)
- 재물운 (수입, 지출, 투자, 재테크)
- 건강운 (주의할 질병, 건강 관리 방법)
- 인간관계 (가족, 친구, 연인, 직장)
- 직업운 (승진, 이직, 창업 기회)
- 학업운 (해당되는 경우)
- 주의해야 할 시기와 기회의 시기
- 월별 또는 분기별 주요 이벤트

별자리와 사주를 종합적으로 고려하여 분석해주세요.
존댓말을 사용해주세요."""

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()


def generate_personality(zodiac_sign: str, saju_info: dict, birth_date: date, premium: bool = False) -> str:
    """OpenAI로 성향 분석 생성 - 별자리와 사주 결합 분석"""
    zodiac_korean = get_zodiac_korean(zodiac_sign)
    
    if premium:
        lines = "20줄 이상의 상세한 분석"
        detail = """
다음 내용을 포함하여 매우 상세하게 분석해주세요:
- 성격적 특징 (장점과 단점 포함)
- 대인관계 스타일 (가족, 친구, 연인, 직장)
- 적합한 직업과 환경
- 재물운과 금전 관리 스타일
- 건강 관리 포인트
- 인생의 전환점이 될 시기
- 조심해야 할 점과 극복 방법
- 별자리와 사주가 결합된 종합적 해석
"""
    else:
        lines = "5-7줄의 간단한 분석"
        detail = """
다음 내용을 간략하게 포함해주세요:
- 성격적 특징
- 강점과 약점
- 대인관계 스타일
- 적합한 직업이나 환경
"""
    
    시주_info = f", 시주 {saju_info['시주']}" if saju_info.get('시주') else ""
    
    prompt = f"""당신은 전문 성격 분석가입니다.

별자리: {zodiac_korean}
생년월일: {format_date_korean(birth_date)}
사주: 년주 {saju_info['년주']}, 월주 {saju_info['월주']}, 일주 {saju_info['일주']}{시주_info}

위 별자리와 사주 정보를 종합적으로 결합하여 이 사람의 성향을 {lines}로 분석해주세요.
서양 점성술(별자리)과 동양 명리학(사주)의 관점을 모두 고려하여 분석해주세요.
{detail}
존댓말을 사용해주세요."""

    max_tokens = 1500 if premium else 300
    
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()


def get_zodiac_emoji(zodiac_sign: str) -> str:
    """별자리 이모지 반환"""
    emoji_map = {
        "Aries": "♈", "Taurus": "♉", "Gemini": "♊", "Cancer": "♋",
        "Leo": "♌", "Virgo": "♍", "Libra": "♎", "Scorpio": "♏",
        "Sagittarius": "♐", "Capricorn": "♑", "Aquarius": "♒", "Pisces": "♓"
    }
    return emoji_map.get(zodiac_sign, "⭐")


def get_zodiac_korean(zodiac_sign: str) -> str:
    """별자리 한국어 이름 반환"""
    korean_map = {
        "Aries": "양자리", "Taurus": "황소자리", "Gemini": "쌍둥이자리", "Cancer": "게자리",
        "Leo": "사자자리", "Virgo": "처녀자리", "Libra": "천칭자리", "Scorpio": "전갈자리",
        "Sagittarius": "사수자리", "Capricorn": "염소자리", "Aquarius": "물병자리", "Pisces": "물고기자리"
    }
    return korean_map.get(zodiac_sign, zodiac_sign)


def create_html_template(data: dict) -> str:
    """HTML 템플릿 생성"""
    return f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔮 운세 결과 - {data['birth_date']}</title>
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
        
        .elements-chart {{
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
            flex-wrap: wrap;
            gap: 15px;
        }}
        
        .element {{
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            min-width: 80px;
        }}
        
        .element-name {{
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        
        .element-count {{
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
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
            <h1>🔮 운세 결과</h1>
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


async def generate_complete_fortune_html(birth_date: date, saju_info: dict, birth_time: str = None, premium: bool = False):
    """완전한 운세 생성 - HTML 출력"""
    print("=" * 60)
    print("🔮 운세 생성 중...")
    print("=" * 60)
    
    # 1. 별자리 계산
    zodiac_sign = get_zodiac_sign(birth_date)
    print(f"\n📅 생년월일: {format_date_korean(birth_date)}")
    if birth_time:
        print(f"⏰ 출생 시간: {birth_time}")
    print(f"♈ 별자리: {get_zodiac_korean(zodiac_sign)}")
    
    # 2. 사주 정보 출력
    시주_display = f", 시주 {saju_info['시주']}" if saju_info.get('시주') else ""
    print(f"🎴 사주: 년주 {saju_info['년주']}, 월주 {saju_info['월주']}, 일주 {saju_info['일주']}{시주_display}")
    
    # 3. 오늘의 별자리 운세 조회
    print("\n📖 오늘의 운세 조회 중...")
    horoscope_today = await get_today_horoscope(zodiac_sign)
    
    # 4. OpenAI로 사주 기반 운세 생성
    print("🤖 AI 운세 생성 중...")
    saju_fortune = generate_saju_fortune(saju_info, birth_date)
    
    # 5. 한 해 운세 생성
    year_fortune = generate_year_fortune(zodiac_sign, saju_info, birth_date)
    
    # 6. 성향 분석 생성
    if premium:
        print("✨ 프리미엄 성향 분석 생성 중... (상세 버전)")
    personality = generate_personality(zodiac_sign, saju_info, birth_date, premium)
    
    # HTML 데이터 준비
    html_data = {
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
    
    # HTML 생성
    html_content = create_html_template(html_data)
    
    # HTML 파일 저장
    premium_suffix = "_프리미엄" if premium else ""
    output_file = f"운세결과_{birth_date.strftime('%Y%m%d')}{premium_suffix}.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("\n" + "=" * 60)
    print("✨ HTML 운세 결과 생성 완료!")
    print("=" * 60)
    print(f"📄 파일: {output_file}")
    if premium:
        print("⭐ 프리미엄 버전: 상세한 성향 분석 포함")
    print("🌐 브라우저에서 자동으로 열립니다...")
    
    # 브라우저에서 자동으로 열기
    file_path = os.path.abspath(output_file)
    webbrowser.open(f'file://{file_path}')
    
    return output_file


async def main():
    """메인 함수"""
    # MongoDB 연결
    await connect_to_mongo()
    await init_db()
    
    print("🔮 운세 생성 서비스 (HTML 버전 - 한글 전용)")
    print("=" * 60)
    print("💡 정확한 사주는 https://www.sajuplus.com 등의 만세력 사이트에서 확인하세요!")
    print("=" * 60)
    
    # 사용자 입력
    date_str = input("\n생년월일을 입력하세요 (예: 1990-05-15): ").strip()
    
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
    
    # 사주 직접 입력
    print("\n" + "=" * 60)
    print("🎴 사주 정보를 입력하세요 (만세력 사이트에서 확인한 정보)")
    print("=" * 60)
    
    년주 = input("년주를 입력하세요 (예: 신미): ").strip()
    월주 = input("월주를 입력하세요 (예: 을해): ").strip()
    일주 = input("일주를 입력하세요 (예: 기축): ").strip()
    
    시주 = None
    if birth_time:
        시주_input = input("시주를 입력하세요 (예: 경오, 선택사항 - Enter로 건너뛰기): ").strip()
        시주 = 시주_input if 시주_input else None
    
    # 사주 정보 구성
    saju_info = {
        "년주": 년주,
        "월주": 월주,
        "일주": 일주,
        "시주": 시주,
        "오행": analyze_elements(년주, 월주, 일주, 시주)
    }
    
    premium_input = input("\n프리미엄 버전? (y/n, 기본: n): ").strip().lower()
    premium = premium_input == 'y'
    
    # 운세 생성
    await generate_complete_fortune_html(birth_date, saju_info, birth_time, premium)


if __name__ == "__main__":
    asyncio.run(main())
