# 타자 연습 웹서비스 — PROJECT MASTER DOCUMENT

> **최종 갱신**: 2026-01-30  
> **목적**: 프로젝트 전체 현황을 한 눈에 파악하고, 각 문서의 **단일 진실(SoT)** 위치를 명확히 하는 "인덱스 문서"

---

## 0) 핵심 결정 5줄

| # | 결정 | 근거/효과 |
|---|------|-----------|
| 1 | **TypingSession이 원천 데이터(Source of Truth)** | 랭킹/통계/챌린지 모두 세션 기반 집계, 스키마 안정성 확보 |
| 2 | **테이블 정의서(`db/SCHEMA.md`)가 DB 스키마 SoT** | 중복 제거, 변경 시 단일 문서만 수정 |
| 3 | **확장 정보는 `metadata(jsonb)`에 저장, 핵심 지표는 기본 컬럼 유지** | 마이그레이션 비용 최소화 + 쿼리 성능 확보 |
| 4 | **랭킹은 스냅샷 방식(leaderboard_snapshot), 실시간 쿼리 지양** | DB 부하 감소, 공정성/운영 편의 |
| 5 | **문서 구조: plan / db / feature / roadmap 분리, 중복 링크로 대체** | 문서 크기 관리, 역할별 빠른 접근 |

---

## 1) 프로젝트 개요

### 1.1 비전
- **Web(PWA)** 기반 한글/영어 타자 연습 서비스
- 동일 빌드 결과로 **Capacitor(Android/iOS)** 앱 패키징까지 연결

### 1.2 기술 스택
| 구분 | 기술 |
|------|------|
| Frontend | React (Vite), TypeScript, PWA(service worker) |
| Backend | Django, Django REST Framework, PostgreSQL |
| Infra | Docker Compose, Nginx Reverse Proxy |
| Mobile | Capacitor (Android/iOS) — 선택 |

### 1.3 핵심 원칙
- **프론트 계산, 백엔드 저장**: 타자 입력/오타 계산은 프론트, 결과만 API로 저장
- **세션 기반 기록**: 모든 연습 결과는 `TypingSession` 1개로 저장
- **확장 스키마 점진 도입**: 집계(`stats`)·랭킹(`leaderboard`)·챌린지(`challenges`)는 필요 시 활성화

---

## 2) 현재 구현 상태 (2026-01-30 기준)

### 2.1 완료된 항목 ✅

| 영역 | 항목 | 상태 |
|------|------|------|
| **Frontend** | HomePage / PracticePage / ResultPage / HistoryPage | ✅ |
| | Layout 컴포넌트, API 클라이언트, 유틸리티 | ✅ |
| | PWA manifest | ✅ |
| **Backend** | users / texts / sessions 앱 (models, views, serializers) | ✅ |
| | Django 설정 (base/local/prod), URL 라우팅 | ✅ |
| **Infra** | docker-compose, Dockerfile(backend/frontend/nginx), nginx.conf | ✅ |
| **Docs** | 계획서, 테이블 정의서, 추천 기능 문서, 연습 모드 확장 계획서 | ✅ |

### 2.2 실행 상태

| 항목 | 상태 | 비고 |
|------|------|------|
| Frontend (dev) | ✅ 확인 | `npm run dev` → localhost:5173 |
| Backend (dev) | ⏳ 미실행 | Python + PostgreSQL 환경 필요 |
| Docker 전체 | ⏳ 미테스트 | `docker-compose up` 확인 필요 |

### 2.3 미완료 항목 (선택)

| 항목 | 우선순위 |
|------|----------|
| Capacitor 설정 (Android/iOS) | Later |
| PWA 아이콘 이미지 | Next |
| challenges 앱 (데일리 챌린지) | Next |
| API 명세 문서 (`ops/docs/api-spec.md`) | Next |
| 집계 테이블 (`stats_user_daily`) | **MVP** |
| 랭킹 스냅샷 테이블 | Next |

---

## 3) 아키텍처 / 데이터 흐름 요약

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER BROWSER (PWA)                        │
├─────────────────────────────────────────────────────────────────────┤
│  React App (Vite)                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐│
│  │  HomePage   │  │ PracticePage│  │ ResultPage  │  │ HistoryPage ││
│  │ (목표/스트릭)│  │ (타자 엔진) │  │ (결과 표시) │  │ (기록 조회) ││
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘│
│         │                │                │                │        │
│         └────────────────┴───────┬────────┴────────────────┘        │
│                                  │                                   │
│                         ┌────────▼────────┐                          │
│                         │   API Client    │                          │
│                         │ (lib/api.ts)    │                          │
│                         └────────┬────────┘                          │
└──────────────────────────────────┼──────────────────────────────────┘
                                   │ HTTP/HTTPS
                          ┌────────▼────────┐
                          │      Nginx      │
                          │ (Reverse Proxy) │
                          └────────┬────────┘
                                   │
┌──────────────────────────────────┼──────────────────────────────────┐
│                           BACKEND (Django/DRF)                      │
├──────────────────────────────────┼──────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  users 앱    │  │  texts 앱    │  │ sessions 앱  │               │
│  │ (인증/프로필)│  │ (문장팩/아이템)│  │ (연습 기록)  │               │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
│         │                 │                 │                        │
│         └─────────────────┴─────────┬───────┘                        │
│                                     │                                │
│                            ┌────────▼────────┐                       │
│                            │   PostgreSQL    │                       │
│                            │   (DB Server)   │                       │
│                            └─────────────────┘                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 데이터 흐름

1. **연습 시작**: PracticePage에서 모드/팩 선택 → texts API로 문장 로딩
2. **입력 처리**: 프론트에서 실시간 WPM/정확도 계산
3. **결과 저장**: 종료 시 `POST /api/sessions` → TypingSession 저장
4. **기록 조회**: HistoryPage에서 `GET /api/sessions` → 목록/상세 표시

---

## 4) Decision Log (결정 사항)

| 날짜 | 결정 | 근거 | 상태 |
|------|------|------|------|
| 2026-01-16 | TypingSession을 원천 데이터로 확정 | 랭킹/통계 일관성, 집계 용이 | ✅ 확정 |
| 2026-01-16 | 비로그인 세션 허용 (`user_id NULL`) | 회원가입 전 체험 유도 | ✅ 확정 |
| 2026-01-16 | 랭킹은 스냅샷 방식 | 실시간 쿼리 부하 방지, 공정성 | ✅ 확정 |
| 2026-01-16 | TypingEvent 기본 OFF, opt-in 저장 | 데이터 폭증 방지 | ✅ 확정 |
| 2026-01-16 | texts soft delete (`is_active`) 적용 | 세션 FK 보호, 운영 유연성 | ✅ 확정 |
| 2026-01-30 | 문서 구조 4단 분리 (plan/db/feature/roadmap) | 중복 제거, 역할별 접근성 | ✅ 확정 |

---

## 5) 우선순위 로드맵

### MVP (핵심 체감 기능)
- [ ] Backend 실행 안정화 (Docker Compose 테스트)
- [ ] `stats_user_daily` 집계 테이블 도입
- [ ] HomePage: 오늘 목표/스트릭 표시
- [ ] PracticePage: 연습 모드 UI (문장/타임어택/정확도챌린지)
- [ ] ResultPage: 오타 Top5 표시

### Next (재미/유지율)
- [ ] 주간 랭킹 (스냅샷 방식)
- [ ] 데일리 챌린지
- [ ] 뱃지/레벨 시스템
- [ ] 결과 공유 카드

### Later (콘텐츠/운영)
- [ ] 유저 문장팩 업로드 + 검수
- [ ] 데이터 내보내기
- [ ] Capacitor 앱 빌드
- [ ] TypingEvent 정밀 오타분석 (opt-in)

---

## 6) 문서 링크 (Document Index)

> **원칙**: 각 문서는 해당 영역의 **단일 진실(SoT)**. 중복 내용은 링크로 참조.

### 6.1 계획/운영 (`document/plan/`)

| 문서 | 설명 | SoT 여부 |
|------|------|----------|
| [SERVICE_PLAN.md](./plan/SERVICE_PLAN.md) | 서비스 전체 계획, 폴더 구조, 환경 변수, 개발 흐름 | ✅ 계획/구조 SoT |

### 6.2 데이터베이스 (`document/db/`)

| 문서 | 설명 | SoT 여부 |
|------|------|----------|
| [SCHEMA.md](./db/SCHEMA.md) | 테이블 정의서 (컬럼/타입/제약/인덱스) | ✅ DB 스키마 SoT |

### 6.3 기능 요구사항 (`document/feature/`)

| 문서 | 설명 | SoT 여부 |
|------|------|----------|
| [PRACTICE_MODE_EXTENSION.md](./feature/PRACTICE_MODE_EXTENSION.md) | 연습 모드 확장 요구사항 | ✅ 연습 모드 SoT |
| [RANKING_FEATURE.md](./feature/RANKING_FEATURE.md) | 주간 랭킹 기능 요구사항 | ✅ 랭킹 기능 SoT |

### 6.4 로드맵 (`document/roadmap/`)

| 문서 | 설명 | SoT 여부 |
|------|------|----------|
| [RECOMMENDED_FEATURES.md](./roadmap/RECOMMENDED_FEATURES.md) | 추천 기능 로드맵 (Phase 1~3) | ✅ 로드맵 SoT |

---

## 7) 가정/근거 목록

| # | 가정 | 근거 |
|---|------|------|
| 1 | MVP는 1~2명 개발자가 2~4주 내 구현 가능한 범위 | 현재 완료 상태 + 연습 모드 다양화 핵심 |
| 2 | 랭킹/챌린지는 MVP 이후 점진 도입 | 유저 기반 확보 후 경쟁 요소 추가가 효과적 |
| 3 | TypingEvent 저장은 기본 OFF | 데이터 폭증 위험, 필요 유저만 opt-in |
| 4 | 테스트 코드는 현재 미작성 상태로 가정 | 문서에 테스트 언급 없음, 구현 상태만 확인됨 |
| 5 | 문서 간 중복은 링크로 대체 가능 | 문서 유지보수 비용 ↓, 일관성 ↑ |

---

## 부록: 빠른 체크리스트

- [ ] TypingSession이 "원천 데이터"임을 팀 전체 공유
- [ ] 비로그인 세션 허용 정책 확정
- [ ] 랭킹 스냅샷 배치 주기 결정 (일/주)
- [ ] TypingEvent 저장 정책 (opt-in + 보관 기간)
- [ ] texts soft delete 운영 정책 확정
- [ ] History 조회용 인덱스 `(user_id, started_at)` 적용 확인
