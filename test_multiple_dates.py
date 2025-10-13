"""
여러 날짜의 사주 계산 테스트
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import date
from saju_calculator import calculate_saju

# 테스트 케이스 (만세력 사이트에서 확인한 정확한 사주)
test_cases = [
    {
        "date": date(1963, 9, 8),
        "correct": {"년주": "갑진", "월주": "신유", "일주": "계미"},
        "name": "1963년 9월 8일"
    },
    {
        "date": date(1991, 11, 25),
        "correct": {"년주": "신미", "월주": "기해", "일주": "기축"},
        "name": "1991년 11월 25일"
    },
    {
        "date": date(1990, 5, 15),
        "correct": {"년주": "경오", "월주": "신사", "일주": "기묘"},
        "name": "1990년 5월 15일"
    },
    {
        "date": date(2000, 7, 13),
        "correct": {"년주": "경진", "월주": "계미", "일주": "신축"},
        "name": "2000년 7월 13일"
    }
]

print("=" * 80)
print("사주 자동 계산 정확도 테스트")
print("=" * 80)

total = len(test_cases)
correct_count = 0

for test in test_cases:
    result = calculate_saju(test["date"], None)
    
    print(f"\n{test['name']}")
    print("-" * 80)
    
    년주_match = result['년주'] == test['correct']['년주']
    월주_match = result['월주'] == test['correct']['월주']
    일주_match = result['일주'] == test['correct']['일주']
    
    print(f"년주: {result['년주']} {'✅' if 년주_match else '❌ (정답: ' + test['correct']['년주'] + ')'}")
    print(f"월주: {result['월주']} {'✅' if 월주_match else '❌ (정답: ' + test['correct']['월주'] + ')'}")
    print(f"일주: {result['일주']} {'✅' if 일주_match else '❌ (정답: ' + test['correct']['일주'] + ')'}")
    
    if 년주_match and 월주_match and 일주_match:
        correct_count += 1
        print("결과: ✅ 정확")
    else:
        print("결과: ❌ 오류")

print("\n" + "=" * 80)
print(f"정확도: {correct_count}/{total} ({correct_count/total*100:.1f}%)")
print("=" * 80)

if correct_count < total:
    print("\n⚠️ 자동 계산이 정확하지 않습니다!")
    print("💡 해결 방법:")
    print("   1. 만세력 사이트에서 사주 확인 (https://www.sajuplus.com)")
    print("   2. 자동 계산 후 반드시 확인 및 수정")
    print("   3. quick_fortune.py 사용 (사주 직접 입력)")
