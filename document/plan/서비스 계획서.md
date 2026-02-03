# 한글/영어 타자 연습 서비스 계획서

> **최종 갱신**: 2026-01-30  
> **역할**: 서비스 전체 계획, 폴더 구조, 환경 변수, 개발/배포 흐름의 **단일 진실(SoT)**  
> **DB 스키마**: [../db/SCHEMA.md](../db/SCHEMA.md) 참조

---

## 1) 서비스 방향

- **목표**: Web(PWA)로 먼저 완성 → 동일 프론트 빌드 결과로 Capacitor(Android/iOS) 앱 패키징
- **방식**: Frontend(React/PWA) + Backend(Django/DRF API) 분리, DB(PostgreSQL)

---

## 2) 모노레포 폴더 구조

```
typing-service/
  README.md
  .gitignore

  document/                  # 📄 프로젝트 문서
    PROJECT_MASTER.md        # 전체 현황/인덱스
    plan/                    # 계획/운영 문서
    db/                      # DB 스키마 (SoT)
    feature/                 # 기능 요구사항
    roadmap/                 # 로드맵/추천 기능

  frontend/
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
    capacitor/               # (선택) Capacitor 설정

  backend/
    manage.py
    requirements.txt
    config/                  # Django project
      settings/
        base.py
        local.py
        prod.py
      urls.py
      asgi.py
      wsgi.py
    apps/
      users/                 # 사용자/인증
      texts/                 # 문장팩(TextPack/TextItem)
      sessions/              # 타자 세션(TypingSession)
      challenges/            # (선택) 데일리 챌린지
    static/
    media/

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
      .env.example           # 환경변수 템플릿
    docs/
      api-spec.md            # API 명세 (선택)
      release.md             # 배포/앱 빌드 절차

  docker-compose.yml
```

---

## 3) 핵심 설정 파일 목록

### 3.1 Frontend (React + PWA)
- `frontend/package.json`: build/dev 스크립트, PWA 플러그인/Capacitor 의존성
- `frontend/vite.config.*`: 빌드 출력, 환경변수 연결, PWA 플러그인 설정
- `frontend/tsconfig.json`: 경로 별칭 (`@/components` 등)
- `frontend/public/manifest.webmanifest`: 앱 이름/아이콘/시작 URL

### 3.2 Capacitor (앱 패키징)
- `frontend/capacitor.config.*`: appId, appName, webDir
- (자동 생성) `frontend/android/`, `frontend/ios/`

### 3.3 Backend (Django + DRF)
- `backend/requirements.txt`: Django, DRF, JWT, CORS, PostgreSQL 드라이버
- `backend/config/settings/base.py`: 공통 설정
- `backend/config/settings/local.py`: 개발환경 설정
- `backend/config/settings/prod.py`: 운영환경 설정
- `backend/config/urls.py`: `/api/` 라우팅

### 3.4 Infra / 배포
- `docker-compose.yml`: postgres + backend + frontend + nginx
- `infra/docker/*.Dockerfile`: 이미지 정의
- `infra/nginx/*.conf`: 리버스 프록시 설정
- `ops/env/.env.example`: 환경변수 템플릿

---

## 4) 환경변수 설계

> 실제 값은 `.env`에 넣고, 저장소에는 `.env.example`만 포함

### Backend
| 변수 | 설명 |
|------|------|
| `DJANGO_SECRET_KEY` | Django 시크릿 키 |
| `DJANGO_SETTINGS_MODULE` | 설정 모듈 (local/prod) |
| `DB_HOST`, `DB_PORT`, `DB_NAME` | PostgreSQL 접속 정보 |
| `DB_USER`, `DB_PASSWORD` | PostgreSQL 인증 |
| `ALLOWED_HOSTS` | 허용 호스트 |
| `CORS_ALLOWED_ORIGINS` | CORS 허용 도메인 |
| `JWT_*` | JWT 만료시간 등 |

### Frontend
| 변수 | 설명 |
|------|------|
| `VITE_API_BASE_URL` | API 서버 URL |

---

## 5) 개발/배포 흐름

### 5.1 개발 (로컬)
1. `docker-compose up` 또는 프론트/백 분리 실행
2. 프론트: API Base URL을 로컬 Django로 연결
3. 백엔드: CORS로 프론트 주소 허용
4. 타자 UI는 프론트에서 실시간 계산, 결과만 API로 저장

### 5.2 운영 (서버)
1. Postgres + Django(API) 컨테이너 운영
2. 프론트는 정적 호스팅 또는 Nginx로 서빙
3. HTTPS 적용 및 도메인 연결

### 5.3 앱 빌드
1. 프론트 `build`로 dist 생성
2. Capacitor `sync`
3. Android Studio / Xcode에서 빌드/서명/배포

---

## 6) Git 정책

### 포함
- `frontend/src`, `backend/apps`, `infra/*`, `ops/docs/*`, `document/*`

### 제외
- `.env`, `dist`, `__pycache__`, `node_modules`, `media`

### Capacitor 생성물
- 팀/배포 방식에 따라 포함/제외 결정 (초기엔 포함 권장)

---

## 7) MVP 작업 순서

1. Frontend: Home → Practice → Result 화면 골격 + 타자 엔진 기본 동작
2. Backend: TextItem API + TypingSession 저장/조회 API
3. Frontend: 기록 화면(History) + 로그인(선택)
4. PWA: manifest + 설치 + 캐시 최소 적용
5. Capacitor: Android 먼저 빌드 연결 → iOS

---

## 관련 문서

- [프로젝트 마스터](../PROJECT_MASTER.md): 전체 현황/인덱스
- [DB 스키마](../db/SCHEMA.md): 테이블 정의서 (SoT)
- [연습 모드 확장](../feature/PRACTICE_MODE_EXTENSION.md): 연습 모드 요구사항
- [추천 기능 로드맵](../roadmap/RECOMMENDED_FEATURES.md): Phase 1~3 로드맵
