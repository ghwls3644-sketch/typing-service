# 한글/영어 타자 연습 서비스

> Web(PWA) 기반 한글/영어 타자 연습 서비스 — 연습 모드 6종 + 60초 챌린지

## 🚀 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | Vite + React + TypeScript, PWA |
| Backend | Django + Django REST Framework, PostgreSQL |
| Infra | Docker Compose, Nginx |
| Mobile | Capacitor (Android/iOS) — 선택 |

## 🎯 주요 기능

### 연습 모드 (PracticePage)
- **📝 문장 연습** — 한글/영어 문장을 따라 입력
- **🔤 단어 연습** — 짧은 단어를 빠르게 반복 입력
- **⏱️ 타임어택** — 30/60/120초 시간 제한
- **🎯 정확도 챌린지** — 오타 5/10/무제한 제한
- **🇰🇷 한글 드릴** — 받침/겹받침 패턴 훈련
- **💪 약점 훈련** — 이전 오타 기반 맞춤 연습

### 60초 챌린지 (ChallengePage)
- 🔥 **60초 타임어택** + 콤보 점수 시스템
- 🕶️ **블라인드 모드** — 입력 내용 비표시
- 📊 최고기록/최근 10판 로컬 저장

### 결과 분석 (ResultPage)
- 🏆 등급 시스템 (S~F) + 피드백
- 📈 WPM / 정확도 / 오타 수 / 소요시간
- 🔍 오타 Top5 분석 + 약점 훈련 연결
- 📋 오답 노트 (단어별 diff 카드)

### 대시보드 (HomePage)
- 🔥 연속 출석 (스트릭)
- 🎯 오늘의 목표 (30분 기준)
- 📊 오늘 세션 / 평균 WPM / 평균 정확도

### 기록 관리 (HistoryPage)
- 연습 / 챌린지 탭 분리
- 챌린지 최고기록 카드 (Score / MaxCombo / WPM)

## 📁 프로젝트 구조

```
typing-service/
├── frontend/          # React + PWA 프론트엔드
│   └── src/
│       ├── pages/     # Home, Practice, Challenge, Result, History, Leaderboard
│       ├── hooks/     # useTypingEngine, useChallengeEngine
│       └── lib/       # API 클라이언트, 로컬 저장, 유틸리티
├── backend/           # Django 백엔드
│   └── apps/          # users, texts, sessions
├── document/          # 📄 프로젝트 문서
│   ├── plan/          # 서비스 계획서, 챌린지 계획서, 콘텐츠 스펙
│   ├── db/            # 데이터베이스 스키마 (SoT)
│   ├── feature/       # 연습모드 확장, 랭킹 기능
│   └── roadmap/       # 추천 기능 로드맵
├── infra/             # Docker, Nginx 설정
└── docker-compose.yml
```

## 🛠️ 개발 환경 설정

### 사전 요구사항
- Node.js 18+
- Python 3.10+ (백엔드 실행 시)
- PostgreSQL 14+ (백엔드 실행 시)
- Docker & Docker Compose (선택)

### Frontend 실행
```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### Backend 실행
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Docker로 전체 실행
```bash
docker-compose up --build
```

## 📱 앱 빌드 (Capacitor)

```bash
cd frontend
npm run build
npx cap sync
npx cap open android  # Android Studio
npx cap open ios      # Xcode (macOS only)
```

## 📖 문서

프로젝트 상세 문서는 `document/` 폴더에 있습니다:

| 문서 | 설명 |
|------|------|
| [프로젝트 마스터문서](document/프로젝트%20마스터문서.md) | 전체 현황 인덱스 |
| [서비스 계획서](document/plan/서비스%20계획서.md) | 폴더 구조, 환경 변수, 개발 흐름 |
| [콘텐츠 스펙 v4.0](document/plan/타자연습%20콘텐츠%20스펙%20v4.0.md) | 2모드×3난이도 콘텐츠 정의 |
| [데이터베이스 스키마](document/db/데이터베이스%20스키마.md) | 테이블 정의서 (SoT) |

## 📄 라이선스

MIT License
