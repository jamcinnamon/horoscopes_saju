"""
사주 계산 검증
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import date
from saju_calculator import calculate_saju

# 1963년 9월 8일
birth_date = date(1963, 9, 8)
birth_time = None

result = calculate_saju(birth_date, birth_time)

print("=" * 60)
print("사주 계산 결과: 1963년 9월 8일")
print("=" * 60)
print(f"년주: {result['년주']}")
print(f"월주: {result['월주']}")
print(f"일주: {result['일주']}")
print(f"시주: {result['시주']}")
print("=" * 60)
print("\n정확한 사주 (만세력 기준):")
print("년주: 갑진 (甲辰)")
print("월주: 신유 (辛酉)")
print("일주: 계미 (癸未)")
print("=" * 60)
