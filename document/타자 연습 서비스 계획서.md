# 한글/영어 타자 연습 서비스 계획서 (폴더 구조 + 핵심 설정 목록)

> 목표: Web(PWA)로 먼저 완성 → 동일 프론트 빌드 결과로 Capacitor(Android/iOS) 앱 패키징까지 연결  
> 방식: Frontend(React/PWA) + Backend(Django/DRF API) 분리, DB(PostgreSQL)

---

## 📊 구현 상태 (2026-01-16 기준)

### ✅ 완료된 항목

| 구분 | 항목 | 파일/폴더 | 상태 |
|------|------|----------|------|
| **Frontend** | package.json | `frontend/package.json` | ✅ |
| | vite.config.ts | `frontend/vite.config.ts` | ✅ |
| | tsconfig.json | `frontend/tsconfig.json` | ✅ |
| | manifest.webmanifest | `frontend/public/manifest.webmanifest` | ✅ |
| | HomePage | `frontend/src/pages/HomePage.tsx/.css` | ✅ |
| | PracticePage | `frontend/src/pages/PracticePage.tsx/.css` | ✅ |
| | ResultPage | `frontend/src/pages/ResultPage.tsx/.css` | ✅ |
| | HistoryPage | `frontend/src/pages/HistoryPage.tsx/.css` | ✅ |
| | Layout 컴포넌트 | `frontend/src/components/Layout/` | ✅ |
| | API 클라이언트 | `frontend/src/lib/api.ts` | ✅ |
| | 유틸리티 | `frontend/src/lib/utils.ts` | ✅ |
| **Backend** | requirements.txt | `backend/requirements.txt` | ✅ |
| | Django 설정 | `backend/config/settings/base.py, local.py, prod.py` | ✅ |
| | URL 설정 | `backend/config/urls.py` | ✅ |
| | WSGI/ASGI | `backend/config/wsgi.py, asgi.py` | ✅ |
| | users 앱 | `backend/apps/users/` (models, views, urls, admin, serializers) | ✅ |
| | texts 앱 | `backend/apps/texts/` (models, views, urls, admin, serializers) | ✅ |
| | sessions 앱 | `backend/apps/sessions/` (models, views, urls, admin, serializers) | ✅ |
| **Infra** | docker-compose.yml | `docker-compose.yml` | ✅ |
| | Backend Dockerfile | `infra/docker/backend.Dockerfile` | ✅ |
| | Frontend Dockerfile | `infra/docker/frontend.Dockerfile` | ✅ |
| | Nginx Dockerfile | `infra/docker/nginx.Dockerfile` | ✅ |
| | nginx.conf | `infra/nginx/nginx.conf` | ✅ |
| | api.conf | `infra/nginx/sites-enabled/api.conf` | ✅ |
| | web.conf | `infra/nginx/sites-enabled/web.conf` | ✅ |
| **Ops** | .env.example | `ops/env/.env.example` | ✅ |
| **Root** | README.md | `README.md` | ✅ |
| | .gitignore | `.gitignore` | ✅ |

### 🔄 실행 상태
- **Frontend**: ✅ 실행 확인됨 (`npm run dev` → http://localhost:5173)
- **Backend**: ⏳ 코드 완성, 실행 안 함 (Python + PostgreSQL 필요)
- **Docker**: ⏳ 설정 완성, 테스트 안 함

### ⏳ 미완료 항목 (선택)
| 항목 | 상태 | 비고 |
|------|------|------|
| Capacitor 설정 | ❌ | Android/iOS 앱 빌드 시 필요 |
| PWA 아이콘 | ❌ | 실제 아이콘 이미지 필요 |
| challenges 앱 | ❌ | 선택 기능 (데일리 챌린지) |
| entrypoint 스크립트 | ❌ | 선택 (Docker 배포 시 필요) |
| API 명세 문서 | ❌ | 선택 (ops/docs/api-spec.md) |

---

## 1) 모노레포 폴더 구조(권장)

```
typing-service/
  README.md
  .gitignore

  frontend/
    README.md
    package.json
    vite.config.*
    tsconfig.json
    public/
      icons/                 # PWA 아이콘
      manifest.webmanifest   # PWA 매니페스트
    src/
      app/                   # 라우팅/전역 설정
      pages/                 # Home / Practice / Result / History / Login
      components/            # UI 컴포넌트
      features/
        typing/              # 타자 엔진 로직(계산/렌더)
        texts/               # 문장팩 로딩/캐싱
        sessions/            # 결과 저장/조회
        auth/                # 로그인/JWT 관리
      lib/                   # API 클라이언트, 유틸
      styles/
    pwa/                     # (선택) 서비스워커/캐시 전략 관련

    capacitor/               # (선택) Capacitor 설정을 여기로 모아도 됨
      capacitor.config.*

  backend/
    README.md
    manage.py
    requirements.txt
    config/                  # Django project (settings/urls/asgi/wsgi)
      settings/
        base.py
        local.py
        prod.py
      urls.py
      asgi.py
      wsgi.py
    apps/
      users/                 # 사용자/인증(선택)
      texts/                 # 문장팩(TextItem)
      sessions/              # 타자 세션(TypingSession)
      challenges/            # (선택) 데일리 챌린지
    static/                  # (선택) 정적
    media/                   # (선택) 업로드

  infra/
    docker/
      backend.Dockerfile
      frontend.Dockerfile
      nginx.Dockerfile
    nginx/
      nginx.conf
      sites-enabled/
        api.conf
        web.conf
    scripts/
      entrypoint-backend.sh
      entrypoint-frontend.sh

  ops/
    env/
      .env.example           # 환경변수 템플릿(공유용)
    docs/
      api-spec.md            # API 명세
      release.md             # 배포/앱 빌드 절차

  docker-compose.yml
```

---

## 2) 핵심 설정 파일 “목록” (내용은 여기서 작성하지 않음)

### 2.1 Frontend (React + PWA)
- `frontend/package.json`
  - build/dev 스크립트
  - PWA 플러그인/Capacitor 의존성
- `frontend/vite.config.*`
  - 빌드 출력 폴더(dist)
  - 환경변수(API Base URL) 연결
  - PWA 플러그인 설정 연결(선택)
- `frontend/tsconfig.json`
  - 경로 별칭(@/components 등)
- `frontend/public/manifest.webmanifest`
  - 앱 이름/아이콘/시작 URL
- `frontend/pwa/*` (선택)
  - 서비스 워커, 캐시 전략 문서/구성

### 2.2 Capacitor (앱 패키징)
- `frontend/capacitor.config.*`
  - appId, appName
  - webDir(= dist)
  - 서버/네트워크 옵션(개발환경)
- (자동 생성) `frontend/android/`, `frontend/ios/`
  - 실제 빌드 산출물/IDE 프로젝트 폴더 (Git 포함 여부 정책 필요)

---

### 2.3 Backend (Django + DRF)
- `backend/requirements.txt`
  - Django, DRF, JWT, CORS, PostgreSQL 드라이버 등
- `backend/config/settings/base.py`
  - 공통 설정(앱 등록, 미들웨어, REST_FRAMEWORK 기본)
- `backend/config/settings/local.py`
  - 개발환경 설정(DEBUG, 로컬 CORS, 로깅)
- `backend/config/settings/prod.py`
  - 운영환경 설정(보안, ALLOWED_HOSTS, HTTPS 옵션)
- `backend/config/urls.py`
  - `/api/` 라우팅, admin 라우팅
- `backend/apps/*`
  - `texts`: 문장팩 모델/관리자/조회 API
  - `sessions`: 세션 저장/조회 API
  - `users`(선택): 회원/프로필 확장
- `backend/static/`, `backend/media/` (선택)
  - 운영 시 파일 처리 정책 포함

---

### 2.4 Infra / 배포(Docker + Nginx)
- `docker-compose.yml`
  - postgres + backend + frontend + nginx(선택) 구성
- `infra/docker/*.Dockerfile`
  - backend / frontend / nginx 이미지 정의
- `infra/nginx/nginx.conf`
  - 기본 설정(압축, 캐시, 업로드 제한 등)
- `infra/nginx/sites-enabled/api.conf`
  - API 리버스 프록시(`/api/ -> backend`)
- `infra/nginx/sites-enabled/web.conf`
  - 프론트 정적 파일 서빙(또는 별도 호스팅 연동)
- `ops/env/.env.example`
  - DB 접속정보, SECRET_KEY, API URL, CORS 허용 도메인 등 템플릿

---

## 3) 환경변수 설계(예시 항목만)
> 실제 값은 `.env`에 넣고, 저장소에는 `.env.example`만 포함

### Backend
- `DJANGO_SECRET_KEY`
- `DJANGO_SETTINGS_MODULE` (local/prod)
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `JWT_*`(만료시간 등)

### Frontend
- `VITE_API_BASE_URL` (예: https://api.example.com)

---

## 4) 개발/배포 흐름(코드 없이 절차만)
### 개발(로컬)
1. `docker-compose up` 또는 프론트/백 분리 실행
2. 프론트: API Base URL을 로컬 Django로 연결
3. 백엔드: CORS로 프론트 주소 허용
4. 타자 UI는 프론트에서 실시간 계산, 결과만 API로 저장

### 운영(서버)
1. Postgres + Django(API) 컨테이너 운영
2. 프론트는 정적 호스팅 또는 Nginx로 서빙
3. HTTPS 적용 및 도메인 연결

### 앱 빌드
1. 프론트 `build`로 dist 생성
2. Capacitor `sync`
3. Android Studio / Xcode에서 빌드/서명/배포

---

## 5) Git 정책(권장)
- 포함: `frontend/src`, `backend/apps`, `infra/*`, `ops/docs/*`
- 제외: `.env`, `dist`, `__pycache__`, `node_modules`, `media`(운영 정책에 따라)
- Capacitor 생성물(android/ios):
  - 팀/배포 방식에 따라 “포함 또는 제외” 결정(초기엔 포함이 관리 편함)

---

## 6) MVP 작업 순서(핵심)
1. Frontend: Home → Practice → Result 화면 골격 + 타자 엔진 기본 동작
2. Backend: TextItem API + TypingSession 저장/조회 API
3. Frontend: 기록 화면(History) + 로그인(선택)
4. PWA: manifest + 설치 + 캐시 최소 적용
5. Capacitor: Android 먼저 빌드 연결 → iOS

---
