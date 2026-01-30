# 타자 연습 웹서비스 — DB 테이블 정의서

> **최종 갱신**: 2026-01-30  
> **역할**: 데이터베이스 스키마의 **단일 진실(SoT)**  
> **기준 앱**: users / texts / sessions + 확장(stats / leaderboard / challenges)

---

## 0) 공통 규칙

### 0.1 기본 컬럼 표준
| 컬럼 | 타입 | 설명 |
|------|------|------|
| `id` | `BIGSERIAL` 또는 `UUID` | PK |
| `created_at` | `timestamptz`, default `now()` | 생성 시각 |
| `updated_at` | `timestamptz`, default `now()` | 수정 시각 (auto_now) |

### 0.2 시간대/타임스탬프
- DB: `timestamptz` 고정
- 프론트 전송: ISO8601 (UTC)
- 집계 기준: **Asia/Seoul**

### 0.3 삭제 정책
| 대상 | 정책 | 근거 |
|------|------|------|
| texts (문장/팩) | Soft delete (`is_active`) | 세션 FK 보호 |
| sessions (기록) | 보존 우선 | 통계/랭킹 근거 |
| FK 삭제 규칙 | `PROTECT` / `SET NULL` / `CASCADE` | 관계별 선택 |

### 0.4 네이밍 규칙
- 테이블: `{app_label}_{model}` (Django 기본)
- 인덱스: `idx_...`, 제약: `uq_...`, `chk_...`

---

## 1) users 앱

### 1.1 `users_user`

| 컬럼 | 타입 | NULL | 기본값 | 제약/인덱스 | 설명 |
|------|------|:----:|--------|-------------|------|
| id | bigint/uuid | N | | PK | |
| email | varchar(255) | Y | | UNIQUE | 이메일 로그인 |
| username | varchar(50) | Y | | UNIQUE | 닉네임/표시 이름 |
| password | (Django) | | | | Django 인증 기본 |
| is_active | boolean | N | true | idx | 활성 상태 |
| is_staff | boolean | N | false | | 관리자 |
| last_login | timestamptz | Y | | | |
| created_at | timestamptz | N | now | | |
| updated_at | timestamptz | N | now | | |

**확장 포인트**
- 소셜 로그인: `provider`, `provider_id` 또는 별도 테이블
- 프로필 분리: `users_profile` (아바타/소개/키보드 레이아웃)

---

## 2) texts 앱 — 문장/문장팩

### 2.1 `texts_text_pack`

| 컬럼 | 타입 | NULL | 기본값 | 제약/인덱스 | 설명 |
|------|------|:----:|--------|-------------|------|
| id | bigint/uuid | N | | PK | |
| title | varchar(100) | N | | idx | 문장팩 이름 |
| language | varchar(10) | N | | idx | `ko`, `en` |
| difficulty | smallint | Y | | idx | 1~5 |
| source | varchar(50) | Y | | | `admin`, `user`, `import` |
| is_active | boolean | N | true | idx | 노출 여부 |
| created_by_id | FK(users_user) | Y | | idx | 유저 생성팩 |
| created_at | timestamptz | N | now | | |
| updated_at | timestamptz | N | now | | |

**권장 인덱스**
- `idx_pack_lang_active_diff`: `(language, is_active, difficulty)`
- `idx_pack_created_by`: `(created_by_id)`

### 2.2 `texts_text_item`

| 컬럼 | 타입 | NULL | 기본값 | 제약/인덱스 | 설명 |
|------|------|:----:|--------|-------------|------|
| id | bigint/uuid | N | | PK | |
| pack_id | FK(text_pack) | N | | idx | 소속 문장팩 |
| content | text | N | | | 문장 본문 |
| length | int | Y | | idx | 글자수 |
| punctuation_level | smallint | Y | | | 기호 난이도 |
| is_active | boolean | N | true | idx | |
| order | int | Y | | idx | 팩 내 순서 |
| created_at | timestamptz | N | now | | |
| updated_at | timestamptz | N | now | | |

**권장 인덱스**
- `idx_item_pack_active`: `(pack_id, is_active)`
- `idx_item_pack_order`: `(pack_id, order)`

---

## 3) sessions 앱 — 연습 기록 ⭐ Source of Truth

### 3.1 `sessions_typing_session`

> **핵심**: 모든 랭킹/통계/챌린지의 근거 데이터

| 컬럼 | 타입 | NULL | 기본값 | 제약/인덱스 | 설명 |
|------|------|:----:|--------|-------------|------|
| id | bigint/uuid | N | | PK | |
| user_id | FK(users_user) | Y | | idx | 비로그인 허용 시 NULL |
| pack_id | FK(text_pack) | Y | | idx | 팩 기반 연습 시 |
| text_item_id | FK(text_item) | Y | | idx | 단일 문장 모드 |
| mode | varchar(20) | N | | idx | `practice`, `challenge`, `ranked` |
| language | varchar(10) | N | | idx | `ko`, `en` |
| started_at | timestamptz | N | now | idx | 시작 시각 |
| ended_at | timestamptz | Y | | | 종료 시각 |
| duration_ms | int | Y | | | 소요 시간 (ms) |
| input_length | int | N | 0 | | 총 입력 길이 |
| correct_length | int | N | 0 | | 정확 입력 길이 |
| error_count | int | N | 0 | | 오타 수 |
| accuracy | numeric(5,2) | N | 0 | idx | 정확도 (%) |
| wpm | numeric(6,2) | N | 0 | idx | WPM |
| cpm | numeric(6,2) | Y | | | CPM |
| metadata | jsonb | Y | | | 확장 정보 |
| created_at | timestamptz | N | now | | |
| updated_at | timestamptz | N | now | | |

**제약 조건**
```sql
CHECK (accuracy >= 0 AND accuracy <= 100)
CHECK (wpm >= 0)
CHECK (error_count >= 0)
```

**권장 인덱스 (필수)**
- `idx_session_user_started`: `(user_id, started_at DESC)` → HistoryPage
- `idx_session_mode_lang_started`: `(mode, language, started_at DESC)` → 랭킹/챌린지
- `idx_session_pack_started`: `(pack_id, started_at DESC)` → 팩별 통계

**metadata 구조 예시**
```json
{
  "submode": "time_attack",
  "settings": {
    "time_limit_sec": 60,
    "difficulty": 3
  },
  "device": {
    "ua": "Mozilla/5.0...",
    "keyboard": "unknown"
  },
  "result_extra": {
    "fail_reason": null,
    "timeline": [{"t": 10, "wpm": 312.4}]
  }
}
```

### 3.2 `sessions_typing_event` (선택 — 기본 OFF)

> **주의**: 데이터 폭증 위험. opt-in + 보관 기간 정책 필수

| 컬럼 | 타입 | NULL | 제약/인덱스 | 설명 |
|------|------|:----:|-------------|------|
| id | bigint/uuid | N | PK | |
| session_id | FK(typing_session) | N | idx | CASCADE |
| t_ms | int | N | | 세션 시작 기준 ms |
| expected | varchar(5) | Y | | 기대 문자 |
| typed | varchar(5) | Y | | 입력 문자 |
| is_correct | boolean | N | idx | 정오타 |
| position | int | Y | | 문장 내 위치 |
| created_at | timestamptz | N | | |
| updated_at | timestamptz | N | | |

**권장 인덱스**
- `idx_event_session_t`: `(session_id, t_ms)`
- `idx_event_session_correct`: `(session_id, is_correct)`

**운영 정책**
- 저장: 유저가 "오타 분석" 기능 켠 경우만
- 보관: 30~180일 제한 (파티셔닝 고려)

---

## 4) 집계/랭킹 확장

### 4.1 `stats_user_daily`

| 컬럼 | 타입 | NULL | 제약/인덱스 | 설명 |
|------|------|:----:|-------------|------|
| user_id | FK(users_user) | N | PK(복합) | |
| date | date | N | PK(복합) | Asia/Seoul 기준 |
| language | varchar(10) | N | PK(복합) | |
| total_sessions | int | N | | 세션 수 |
| total_duration_ms | bigint | N | | 연습 시간 |
| avg_wpm | numeric(6,2) | N | | 평균 WPM |
| avg_accuracy | numeric(5,2) | N | | 평균 정확도 |
| best_wpm | numeric(6,2) | Y | | 최고 WPM |
| best_accuracy | numeric(5,2) | Y | | 최고 정확도 |
| created_at | timestamptz | N | | |
| updated_at | timestamptz | N | | |

**제약**
- `UNIQUE(user_id, date, language)` 또는 복합 PK

### 4.2 `leaderboard_snapshot` + `leaderboard_entry`

#### `leaderboard_snapshot`
| 컬럼 | 타입 | NULL | 제약/인덱스 | 설명 |
|------|------|:----:|-------------|------|
| id | bigint/uuid | N | PK | |
| period | varchar(10) | N | idx | `daily`, `weekly`, `monthly` |
| start_date | date | N | idx | 기간 시작 |
| end_date | date | N | | 기간 끝 |
| mode | varchar(20) | N | idx | `ranked` 등 |
| language | varchar(10) | N | idx | |
| generated_at | timestamptz | N | | |
| created_at | timestamptz | N | | |
| updated_at | timestamptz | N | | |

**제약**: `UNIQUE(period, start_date, end_date, mode, language)`

#### `leaderboard_entry`
| 컬럼 | 타입 | NULL | 제약/인덱스 | 설명 |
|------|------|:----:|-------------|------|
| id | bigint/uuid | N | PK | |
| snapshot_id | FK(snapshot) | N | idx | |
| user_id | FK(users_user) | N | idx | |
| rank | int | N | idx | 순위 |
| score_wpm | numeric(6,2) | N | | |
| score_accuracy | numeric(5,2) | N | | |
| session_count | int | N | | |
| created_at | timestamptz | N | | |
| updated_at | timestamptz | N | | |

**제약**
- `UNIQUE(snapshot_id, user_id)`
- `UNIQUE(snapshot_id, rank)`

---

## 5) 챌린지 확장 (선택)

### 5.1 `challenges_daily_challenge`
| 컬럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| id | bigint/uuid | N | |
| date | date | N | Asia/Seoul 기준 |
| language | varchar(10) | N | |
| pack_id | FK(text_pack) | Y | |
| text_item_id | FK(text_item) | Y | |
| created_at | timestamptz | N | |
| updated_at | timestamptz | N | |

### 5.2 `challenges_user_challenge`
| 컬럼 | 타입 | NULL | 설명 |
|------|------|:----:|------|
| id | bigint/uuid | N | |
| user_id | FK(users_user) | N | |
| challenge_id | FK(daily_challenge) | N | |
| session_id | FK(typing_session) | Y | 실제 플레이 세션 |
| status | varchar(20) | N | `started`, `completed` |
| created_at | timestamptz | N | |
| updated_at | timestamptz | N | |

---

## 6) Enum 값 (권장)

| 필드 | 값 |
|------|-----|
| `language` | `ko`, `en` |
| `mode` | `practice`, `challenge`, `ranked` |
| `period` | `daily`, `weekly`, `monthly` |
| `visibility` (선택) | `public`, `private`, `unlisted` |

---

## 7) 체크리스트

- [ ] TypingSession이 "원천 데이터"임 확정
- [ ] 비로그인 세션 허용 (`user_id NULL`)
- [ ] 랭킹: 스냅샷 방식 (권장)
- [ ] TypingEvent: 기본 OFF + opt-in + 보관기간
- [ ] texts soft delete (`is_active`)
- [ ] 핵심 인덱스 `(user_id, started_at DESC)` 적용

---

## 관련 문서

- [프로젝트 마스터](../PROJECT_MASTER.md): 전체 현황
- [서비스 계획서](../plan/SERVICE_PLAN.md): 폴더 구조/환경 변수
- [연습 모드 확장](../feature/PRACTICE_MODE_EXTENSION.md): 모드별 요구사항
