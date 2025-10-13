# Horoscope & Saju Fortune Service

별자리(Horoscope)와 사주(Saju)를 결합한 AI 기반 운세 서비스

## ✨ 새로운 기능: HTML 운세 생성 & 일괄 처리

### 🎨 HTML 운세 생성 (개인)
예쁜 HTML 형식으로 운세 결과를 생성합니다.

```bash
python generate_fortune_html.py
```

**입력 정보:**
1. 생년월일 (예: 1990-05-15)
2. 출생 시간 (선택사항, 예: 14:30)
3. **사주 정보 직접 입력** (만세력 사이트에서 확인)
   - 년주 (예: 신미)
   - 월주 (예: 을해)
   - 일주 (예: 기축)
   - 시주 (예: 경오)
4. 프리미엄 여부 (y/n)

**출력:**
- 예쁜 HTML 파일 자동 생성
- 브라우저에서 자동으로 열림
- 프리미엄 버전: 상세한 성향 분석 (20줄 이상)
- 일반 버전: 간단한 성향 분석 (5-7줄)

**사주 확인 사이트:**
- https://www.sajuplus.com
- https://www.saju.co.kr

### 📦 일괄 운세 생성 (여러 명)
CSV 파일로 여러 명의 운세를 한 번에 생성합니다.

```bash
python batch_fortune.py
```

**CSV 파일 형식:**
```csv
이름,생년월일,출생시간,년주,월주,일주,시주
김철수,1990-05-15,14:30,경오,신사,기묘,신미
이영희,1991-11-25,12:00,신미,을해,기축,경오
박민수,1985-03-20,09:00,을축,기묘,병진,계사
```

**출력:**
- 각 사람별 HTML 파일 생성
- 폴더에 모두 저장
- ZIP 파일로 자동 압축

**샘플 파일:** `sample_people.csv` 참고

---

## 📋 개요

이 프로젝트는 두 개의 독립적인 AI 모델을 활용하여 사용자에게 개인화된 운세를 제공합니다:
- **별자리 모델**: 서양 점성술 기반 운세 예측
- **사주 모델**: 동양 사주팔자 기반 성향 분석 및 운세

## 🚀 주요 기능

- 오늘의 운세 제공
- 올해 운세 제공
- 성향 분석 (강점, 약점, 오행 균형)
- 사용자 피드백 수집
- 모델 지속적 개선

## 🛠️ 기술 스택

- **Backend**: FastAPI, Python 3.9+
- **Database**: MongoDB (Motor + Beanie ODM)
- **AI/ML**: OpenAI API (GPT-4), scikit-learn, pandas
- **Testing**: pytest, pytest-asyncio

## 📦 설치

1. 저장소 클론
```bash
git clone <repository-url>
cd horoscopes_saju
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. MongoDB 설치 및 실행
```bash
# Windows (Chocolatey)
choco install mongodb

# macOS (Homebrew)
brew tap mongodb/brew
brew install mongodb-community

# MongoDB 실행
mongod
```

5. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 열어 OPENAI_API_KEY, MONGODB_URL 등을 설정
```

## 🏃 실행

### 개발 서버 실행
```bash
python -m app.main
```

또는

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버가 실행되면 다음 주소에서 접근 가능합니다:
- API: http://localhost:8000
- API 문서 (Swagger): http://localhost:8000/docs
- API 문서 (ReDoc): http://localhost:8000/redoc

## 📚 API 엔드포인트

### 운세 조회
- `POST /fortune` - 전체 운세 조회
- `GET /fortune/today` - 오늘의 운세
- `GET /fortune/year` - 올해 운세
- `GET /personality` - 성향 분석

### 피드백
- `POST /feedback` - 사용자 피드백 제출

### 관리자
- `POST /admin/retrain` - 모델 재학습 트리거

## 🧪 테스트

```bash
pytest tests/
```

## 📁 프로젝트 구조

```
horoscopes_saju/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱
│   ├── config.py            # 설정
│   ├── models/              # 데이터베이스 모델
│   ├── services/            # 비즈니스 로직
│   ├── repositories/        # 데이터 접근 계층
│   └── utils/               # 유틸리티
├── tests/                   # 테스트
├── data/                    # 데이터 파일
├── models/                  # 학습된 모델
├── .env.example             # 환경 변수 예시
├── requirements.txt         # 의존성
└── README.md
```

## 🔑 환경 변수

주요 환경 변수는 `.env.example` 파일을 참고하세요.

필수 환경 변수:
- `OPENAI_API_KEY`: OpenAI API 키
- `DATABASE_URL`: 데이터베이스 연결 URL

## 📝 라이선스

MIT License

## 👥 기여

이슈와 PR을 환영합니다!
