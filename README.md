# 한글/영어 타자 연습 서비스

> Web(PWA) + 모바일 앱(Capacitor)을 지원하는 풀스택 타자 연습 서비스

## 🚀 기술 스택

### Frontend
- **Vite** + **React** + **TypeScript**
- **PWA** (Progressive Web App)
- **Capacitor** (Android/iOS 앱 빌드)

### Backend
- **Django** + **Django REST Framework**
- **PostgreSQL**
- **JWT 인증**

### Infra
- **Docker** + **Docker Compose**
- **Nginx** (리버스 프록시)

## 📁 프로젝트 구조

```
typing-service/
├── frontend/          # React + PWA 프론트엔드
├── backend/           # Django 백엔드
├── infra/             # Docker, Nginx 설정
├── ops/               # 환경변수 템플릿, 문서
└── docker-compose.yml
```

## 🛠️ 개발 환경 설정

### 사전 요구사항
- Node.js 18+
- Python 3.10+
- PostgreSQL 14+
- Docker & Docker Compose (선택)

### Frontend 실행
```bash
cd frontend
npm install
npm run dev
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

## 🎯 주요 기능

- **한글/영어 타자 연습**: 다양한 문장팩으로 연습
- **실시간 타자 측정**: WPM, 정확도, 소요시간
- **연습 기록 저장**: 개인별 연습 히스토리
- **PWA 지원**: 오프라인 사용 가능
- **모바일 앱**: Android/iOS 네이티브 앱

## 📱 앱 빌드 (Capacitor)

```bash
cd frontend
npm run build
npx cap sync
npx cap open android  # Android Studio
npx cap open ios      # Xcode (macOS only)
```

## 📄 라이선스

MIT License
