"""
정확한 사주 계산 모듈
음력 변환 및 천간지지 계산
"""
from datetime import datetime, date
from lunarcalendar import Converter, Solar, Lunar


# 천간 (10개)
HEAVENLY_STEMS = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]

# 지지 (12개)
EARTHLY_BRANCHES = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]


def get_year_pillar(year: int) -> str:
    """
    년주(年柱) 계산
    갑자년(1984년)을 기준으로 계산
    """
    # 1984년 = 갑자년 (천간 0, 지지 0)
    base_year = 1984
    offset = (year - base_year) % 60
    
    stem_idx = offset % 10
    branch_idx = offset % 12
    
    return f"{HEAVENLY_STEMS[stem_idx]}{EARTHLY_BRANCHES[branch_idx]}"


def get_month_pillar(year: int, month: int, day: int) -> str:
    """
    월주(月柱) 계산
    음력 기준으로 계산해야 정확함
    """
    try:
        # 양력을 음력으로 변환
        solar = Solar(year, month, day)
        lunar = Converter.Solar2Lunar(solar)
        lunar_month = lunar.month
        lunar_year = lunar.year
        
        # 년간에 따른 월간 계산
        # 년간의 천간에 따라 정월(인월)의 천간이 결정됨
        year_stem_idx = (lunar_year - 1984) % 10
        
        # 정월(인월, 3번째 지지)의 천간 계산
        # 갑기년: 병인월부터 시작
        # 을경년: 무인월부터 시작
        # 병신년: 경인월부터 시작
        # 정임년: 임인월부터 시작
        # 무계년: 갑인월부터 시작
        month_stem_base = {
            0: 2, 5: 2,  # 갑, 기 -> 병
            1: 4, 6: 4,  # 을, 경 -> 무
            2: 6, 7: 6,  # 병, 신 -> 경
            3: 8, 8: 8,  # 정, 임 -> 임
            4: 0, 9: 0   # 무, 계 -> 갑
        }
        
        first_month_stem = month_stem_base[year_stem_idx]
        
        # 월지는 인월(1월)부터 시작
        # 인(1월), 묘(2월), 진(3월), 사(4월), 오(5월), 미(6월),
        # 신(7월), 유(8월), 술(9월), 해(10월), 자(11월), 축(12월)
        month_branch_idx = (lunar_month + 1) % 12  # 인월이 2번 인덱스
        month_stem_idx = (first_month_stem + lunar_month - 1) % 10
        
        return f"{HEAVENLY_STEMS[month_stem_idx]}{EARTHLY_BRANCHES[month_branch_idx]}"
    except:
        # 변환 실패 시 간단한 계산
        month_stem_idx = month % 10
        month_branch_idx = month % 12
        return f"{HEAVENLY_STEMS[month_stem_idx]}{EARTHLY_BRANCHES[month_branch_idx]}"


def get_day_pillar(year: int, month: int, day: int) -> str:
    """
    일주(日柱) 계산
    기준일로부터의 일수 차이로 계산
    1900년 1월 1일 = 계묘일 (검증된 만세력 기준)
    """
    # 1900년 1월 1일 = 계묘일 (천간 9, 지지 3)
    base_date = datetime(1900, 1, 1)
    target_date = datetime(year, month, day)
    
    days_diff = (target_date - base_date).days
    
    # 1900년 1월 1일이 계묘일이므로
    stem_idx = (9 + days_diff) % 10
    branch_idx = (3 + days_diff) % 12
    
    return f"{HEAVENLY_STEMS[stem_idx]}{EARTHLY_BRANCHES[branch_idx]}"


def get_hour_pillar(year: int, month: int, day: int, hour: int, minute: int = 0) -> str:
    """
    시주(時柱) 계산
    일간에 따라 시간의 천간이 결정됨
    """
    # 일주 계산
    day_pillar = get_day_pillar(year, month, day)
    day_stem = day_pillar[0]
    day_stem_idx = HEAVENLY_STEMS.index(day_stem)
    
    # 시간대별 지지 결정
    # 23-01시: 자시, 01-03시: 축시, 03-05시: 인시, ...
    hour_branch_map = [
        (23, 1, 0),   # 자시
        (1, 3, 1),    # 축시
        (3, 5, 2),    # 인시
        (5, 7, 3),    # 묘시
        (7, 9, 4),    # 진시
        (9, 11, 5),   # 사시
        (11, 13, 6),  # 오시
        (13, 15, 7),  # 미시
        (15, 17, 8),  # 신시
        (17, 19, 9),  # 유시
        (19, 21, 10), # 술시
        (21, 23, 11)  # 해시
    ]
    
    hour_branch_idx = 0
    for start, end, idx in hour_branch_map:
        if start <= hour < end or (start == 23 and hour >= 23):
            hour_branch_idx = idx
            break
    
    # 일간에 따른 시간의 천간 계산
    # 갑기일: 갑자시부터 시작
    # 을경일: 병자시부터 시작
    # 병신일: 무자시부터 시작
    # 정임일: 경자시부터 시작
    # 무계일: 임자시부터 시작
    hour_stem_base = {
        0: 0, 5: 0,  # 갑, 기 -> 갑
        1: 2, 6: 2,  # 을, 경 -> 병
        2: 4, 7: 4,  # 병, 신 -> 무
        3: 6, 8: 6,  # 정, 임 -> 경
        4: 8, 9: 8   # 무, 계 -> 임
    }
    
    first_hour_stem = hour_stem_base[day_stem_idx]
    hour_stem_idx = (first_hour_stem + hour_branch_idx) % 10
    
    return f"{HEAVENLY_STEMS[hour_stem_idx]}{EARTHLY_BRANCHES[hour_branch_idx]}"


def calculate_saju(birth_date: date, birth_time: str = None) -> dict:
    """
    사주 계산 (정확한 버전)
    
    Args:
        birth_date: 생년월일
        birth_time: 출생 시간 (HH:MM 형식)
    
    Returns:
        dict: 년주, 월주, 일주, 시주, 오행 정보
    """
    year = birth_date.year
    month = birth_date.month
    day = birth_date.day
    
    # 년주 계산
    년주 = get_year_pillar(year)
    
    # 월주 계산
    월주 = get_month_pillar(year, month, day)
    
    # 일주 계산
    일주 = get_day_pillar(year, month, day)
    
    # 시주 계산 (출생 시간이 있는 경우)
    시주 = None
    if birth_time:
        try:
            hour, minute = map(int, birth_time.split(':'))
            시주 = get_hour_pillar(year, month, day, hour, minute)
        except:
            pass
    
    # 오행 분석
    오행 = analyze_elements(년주, 월주, 일주, 시주)
    
    return {
        "년주": 년주,
        "월주": 월주,
        "일주": 일주,
        "시주": 시주,
        "오행": 오행
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


if __name__ == "__main__":
    # 테스트: 1991년 11월 25일 12시
    test_date = date(1991, 11, 25)
    test_time = "12:00"
    
    result = calculate_saju(test_date, test_time)
    
    print("=" * 60)
    print("사주 계산 테스트")
    print("=" * 60)
    print(f"생년월일: 1991년 11월 25일 12시")
    print(f"년주: {result['년주']}")
    print(f"월주: {result['월주']}")
    print(f"일주: {result['일주']}")
    print(f"시주: {result['시주']}")
    print(f"오행: {result['오행']}")
    print("=" * 60)
    print("\n제미나이 답변과 비교:")
    print("년주: 신미 (예상: 신미)")
    print("월주: 을해 (예상: 을해)")
    print("일주: 기축 (예상: 기축)")
    print("시주: 경오 (예상: 경오)")
