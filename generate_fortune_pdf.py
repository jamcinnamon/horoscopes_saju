"""
운세 생성 스크립트 - PDF 출력 버전
HTML 없이 바로 PDF로 생성합니다.
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
import os

# ReportLab PDF 라이브러리
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

# OpenAI 클라이언트
client = OpenAI(api_key=settings.openai_api_key)


def setup_korean_font():
    """한글 폰트 설정"""
    try:
        # Windows 기본 폰트
        pdfmetrics.registerFont(TTFont('Malgun', 'malgun.ttf'))
        pdfmetrics.registerFont(TTFont('MalgunBold', 'malgunbd.ttf'))
        return 'Malgun', 'MalgunBold'
    except:
        try:
            # 다른 한글 폰트 시도
            pdfmetrics.registerFont(TTFont('NanumGothic', 'NanumGothic.ttf'))
            return 'NanumGothic', 'NanumGothic'
        except:
            # 폰트 없으면 기본 폰트
            return 'Helvetica', 'Helvetica-Bold'


def translate_color_to_korean(color: str) -> str:
    """영어 색상을 한글로 번역"""
    color_map = {
        "red": "빨간색", "blue": "파란색", "green": "초록색", "yellow": "노란색",
        "purple": "보라색", "pink": "분홍색", "orange": "주황색", "white": "흰색",
        "black": "검은색", "brown": "갈색", "gray": "회색", "grey": "회색",
        "gold": "금색", "silver": "은색", "navy": "남색", "turquoise": "청록색",
    }
    return color_map.get(color.lower().strip(), color)


async def get_today_horoscope(zodiac_sign: str) -> dict:
    """오늘의 별자리 운세 조회"""
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
        horoscope_text = horoscope.horoscope_text
        
        # 영어인 경우 번역
        if any(ord(char) < 128 for char in horoscope_text[:50]):
            prompt = f"""다음 별자리 운세를 자연스러운 한국어로 번역해주세요.
존댓말을 사용하고, 운세 특유의 따뜻하고 희망적인 톤을 유지해주세요.

원문: {horoscope_text}

한국어 번역:"""
            
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            horoscope_text = response.choices[0].message.content.strip()
        
        lucky_color = translate_color_to_korean(horoscope.lucky_color) if horoscope.lucky_color else "파란색"
        
        return {
            "text": horoscope_text,
            "lucky_number": horoscope.lucky_number or 7,
            "lucky_color": lucky_color
        }
    
    return {
        "text": "오늘은 새로운 시작의 날입니다.",
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
    """사주 기반 오늘의 운세 생성"""
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
    """한 해 운세 생성"""
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


def generate_personality(zodiac_sign: str, saju_info: dict, birth_date: date, premium: bool = False) -> str:
    """성향 분석 생성"""
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
    """별자리 이모지"""
    emoji_map = {
        "Aries": "♈", "Taurus": "♉", "Gemini": "♊", "Cancer": "♋",
        "Leo": "♌", "Virgo": "♍", "Libra": "♎", "Scorpio": "♏",
        "Sagittarius": "♐", "Capricorn": "♑", "Aquarius": "♒", "Pisces": "♓"
    }
    return emoji_map.get(zodiac_sign, "⭐")


def get_zodiac_korean(zodiac_sign: str) -> str:
    """별자리 한국어 이름"""
    korean_map = {
        "Aries": "양자리", "Taurus": "황소자리", "Gemini": "쌍둥이자리", "Cancer": "게자리",
        "Leo": "사자자리", "Virgo": "처녀자리", "Libra": "천칭자리", "Scorpio": "전갈자리",
        "Sagittarius": "사수자리", "Capricorn": "염소자리", "Aquarius": "물병자리", "Pisces": "물고기자리"
    }
    return korean_map.get(zodiac_sign, zodiac_sign)


def create_pdf(data: dict, filename: str):
    """PDF 생성"""
    # 한글 폰트 설정
    font_normal, font_bold = setup_korean_font()
    
    # PDF 문서 생성
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # 스타일 정의
    styles = getSampleStyleSheet()
    
    # 제목 스타일
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_bold,
        fontSize=24,
        textColor=HexColor('#ff6b6b'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    # 부제목 스타일
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontName=font_bold,
        fontSize=16,
        textColor=HexColor('#667eea'),
        spaceAfter=10
    )
    
    # 본문 스타일
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontName=font_normal,
        fontSize=11,
        leading=18,
        spaceAfter=15
    )
    
    # 정보 스타일
    info_style = ParagraphStyle(
        'CustomInfo',
        parent=styles['BodyText'],
        fontName=font_normal,
        fontSize=10,
        textColor=HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=10
    )
    
    # 내용 구성
    story = []
    
    # 제목
    story.append(Paragraph(f"🔮 운세 결과", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # 기본 정보
    story.append(Paragraph(f"{data['zodiac_emoji']} {data['zodiac_korean']}", subtitle_style))
    story.append(Paragraph(f"생년월일: {data['birth_date']}", info_style))
    if data.get('birth_time'):
        story.append(Paragraph(f"출생시간: {data['birth_time']}", info_style))
    story.append(Paragraph(f"사주: {data['saju_display']}", info_style))
    story.append(Spacer(1, 1*cm))
    
    # 오늘의 운세 - 사주 기반
    story.append(Paragraph("🌟 오늘의 운세 - 사주 기반", subtitle_style))
    story.append(Paragraph(data['saju_fortune'], body_style))
    story.append(Spacer(1, 0.5*cm))
    
    # 오늘의 운세 - 별자리 기반
    story.append(Paragraph("⭐ 오늘의 운세 - 별자리 기반", subtitle_style))
    story.append(Paragraph(data['horoscope_fortune'], body_style))
    story.append(Spacer(1, 0.5*cm))
    
    # 오늘의 행운
    story.append(Paragraph("🍀 오늘의 행운", subtitle_style))
    story.append(Paragraph(f"행운의 숫자: {data['lucky_number']}", body_style))
    story.append(Paragraph(f"행운의 색: {data['lucky_color']}", body_style))
    story.append(Spacer(1, 0.5*cm))
    
    # 한 해 운세
    story.append(Paragraph(f"📅 {datetime.now().year}년 한 해 운세", subtitle_style))
    story.append(Paragraph(data['year_fortune'], body_style))
    story.append(Spacer(1, 0.5*cm))
    
    # 성향 분석
    premium_badge = " [프리미엄]" if data.get('premium') else ""
    story.append(Paragraph(f"👤 내 성향은?{premium_badge}", subtitle_style))
    story.append(Paragraph(data['personality'], body_style))
    story.append(Spacer(1, 1*cm))
    
    # 푸터
    footer_text = f"생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}<br/>⚠️ 본 서비스의 사주 계산은 참고용이며, 정확한 사주는 전문가에게 확인하시기 바랍니다."
    story.append(Paragraph(footer_text, info_style))
    
    # PDF 생성
    doc.build(story)


async def generate_complete_fortune_pdf(birth_date: date, saju_info: dict, birth_time: str = None, premium: bool = False):
    """완전한 운세 생성 - PDF 출력"""
    print("=" * 60)
    print("🔮 운세 생성 중...")
    print("=" * 60)
    
    # 별자리 계산
    zodiac_sign = get_zodiac_sign(birth_date)
    print(f"\n📅 생년월일: {format_date_korean(birth_date)}")
    if birth_time:
        print(f"⏰ 출생 시간: {birth_time}")
    print(f"♈ 별자리: {get_zodiac_korean(zodiac_sign)}")
    
    # 사주 정보 출력
    시주_display = f", 시주 {saju_info['시주']}" if saju_info.get('시주') else ""
    print(f"🎴 사주: 년주 {saju_info['년주']}, 월주 {saju_info['월주']}, 일주 {saju_info['일주']}{시주_display}")
    
    # 운세 조회 및 생성
    print("\n📖 오늘의 운세 조회 중...")
    horoscope_today = await get_today_horoscope(zodiac_sign)
    
    print("🤖 AI 운세 생성 중...")
    saju_fortune = generate_saju_fortune(saju_info, birth_date)
    year_fortune = generate_year_fortune(zodiac_sign, saju_info, birth_date)
    
    if premium:
        print("✨ 프리미엄 성향 분석 생성 중...")
    personality = generate_personality(zodiac_sign, saju_info, birth_date, premium)
    
    # PDF 데이터 준비
    pdf_data = {
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
        'premium': premium
    }
    
    # PDF 생성
    premium_suffix = "_프리미엄" if premium else ""
    base_filename = f"운세결과_{birth_date.strftime('%Y%m%d')}{premium_suffix}"
    output_file = f"{base_filename}.pdf"
    
    # 파일이 이미 존재하면 번호 추가
    counter = 1
    while os.path.exists(output_file):
        output_file = f"{base_filename}_{counter}.pdf"
        counter += 1
    
    print("\n📄 PDF 생성 중...")
    create_pdf(pdf_data, output_file)
    
    print("\n" + "=" * 60)
    print("✨ PDF 운세 결과 생성 완료!")
    print("=" * 60)
    print(f"📄 파일: {output_file}")
    if premium:
        print("⭐ 프리미엄 버전: 상세한 성향 분석 포함")
    
    # PDF 자동으로 열기
    os.startfile(output_file)
    
    return output_file


async def main():
    """메인 함수"""
    await connect_to_mongo()
    await init_db()
    
    print("🔮 운세 생성 서비스 (PDF 버전)")
    print("=" * 60)
    
    # 사용자 입력
    date_str = input("\n생년월일을 입력하세요 (예: 1990-05-15): ").strip()
    
    try:
        birth_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print("❌ 날짜 형식이 올바르지 않습니다.")
        return
    
    time_str = input("출생 시간을 입력하세요 (예: 14:30, Enter로 건너뛰기): ").strip()
    birth_time = time_str if time_str else None
    
    # 사주 입력
    print("\n" + "=" * 60)
    print("🎴 사주 정보를 입력하세요")
    print("=" * 60)
    
    년주 = input("년주: ").strip()
    월주 = input("월주: ").strip()
    일주 = input("일주: ").strip()
    
    시주 = None
    if birth_time:
        시주_input = input("시주 (Enter로 건너뛰기): ").strip()
        시주 = 시주_input if 시주_input else None
    
    saju_info = {
        "년주": 년주,
        "월주": 월주,
        "일주": 일주,
        "시주": 시주,
        "오행": analyze_elements(년주, 월주, 일주, 시주)
    }
    
    premium_input = input("\n프리미엄 버전? (y/n): ").strip().lower()
    premium = premium_input == 'y'
    
    # 운세 생성
    await generate_complete_fortune_pdf(birth_date, saju_info, birth_time, premium)


if __name__ == "__main__":
    asyncio.run(main())
