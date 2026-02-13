# 타자 연습 웹서비스 — DB 테이블 정의서 (Refined)
*(작성일: 2026-01-16, 기준 앱: users / texts / sessions)*

> 목적: 프로젝트가 커질 때(랭킹/챌린지/뱃지/오타분석/공유 등) **마이그레이션 비용을 최소화**하고,
> API/집계/성능을 안정적으로 확장할 수 있도록 **핵심 스키마를 표준화**한다.

---

## 0) 공통 규칙(필수)

### 0.1 기본 컬럼 표준
모든 테이블(또는 거의 모든 테이블)에 아래 컬럼을 둔다.
- `id`: `BIGSERIAL`(권장) 또는 `UUID`
- `created_at`: `timestamptz`, default `now()`
- `updated_at`: `timestamptz`, default `now()` (Django `auto_now=True` 등으로 관리)

### 0.2 시간대/타임스탬프
- 서버/DB는 `timestamptz` 고정
- 프론트에서 전송하는 시간은 ISO8601(UTC) 권장
- 집계(일/주간)는 **Asia/Seoul** 기준으로 계산하되, 저장은 `timestamptz`로 유지

### 0.3 삭제 정책(권장)
- **텍스트(문장/문장팩)는 soft delete 권장**: `is_active` 또는 `deleted_at`
- **세션(연습 기록)은 원칙적으로 보존**: 통계/랭킹/챌린지의 근거 데이터이므로 hard delete 최소화
- FK 삭제 규칙(권장)
  - 근거 데이터 보존이 필요한 FK: `PROTECT`
  - 선택 관계/유저 탈퇴 대비: `SET NULL`
  - 하위 로그가 세션에 종속: `CASCADE` (예: TypingEvent)

### 0.4 네이밍 규칙(권장)
- 테이블: `{app_label}_{model}` (Django 기본)
- 인덱스/제약: 의미가 드러나도록 `idx_...`, `uq_...` 형태

---

## 1) users 앱

> 실제 구현은 Custom User 또는 Django 기본 User를 사용할 수 있음.
> 아래는 “서비스 확장” 관점에서 필요한 속성만 정리.

### 1.1 `users_user`
| 컬럼 | 타입 | NULL | 기본값 | 제약/인덱스 | 설명 |
|---|---|---:|---|---|---|
| id | bigint/uuid | N |  | PK | 사용자 PK |
| email | varchar(255) | Y/N |  | UNIQUE(선택) | 이메일 로그인 사용 시 |
| username | varchar(50) | Y/N |  | UNIQUE(선택) | 닉네임/표시 이름 |
| password | (Django) |  |  |  | Django 인증 기본 |
| is_active | boolean | N | true | idx(선택) | 활성 상태 |
| is_staff | boolean | N | false |  | 관리자 |
| last_login | timestamptz | Y |  |  | Django 기본 |
| created_at | timestamptz | N | now |  | 생성 시각 |
| updated_at | timestamptz | N | now |  | 수정 시각 |

**메모(확장 포인트)**
- 소셜 로그인 확장 시: `provider`, `provider_id` 또는 별도 `users_social_account`
- 프로필(아바타/소개/키보드 레이아웃 등)을 분리하고 싶으면 `users_profile` 테이블로 분리 가능

---

## 2) texts 앱 — 문장/문장팩

### 2.1 `texts_text_pack`
| 컬럼 | 타입 | NULL | 기본값 | 제약/인덱스 | 설명 |
|---|---|---:|---|---|---|
| id | bigint/uuid | N |  | PK | 문장팩 PK |
| title | varchar(100) | N |  | idx | 문장팩 이름 |
| language | varchar(10) | N |  | idx | 예: `ko`, `en` |
| difficulty | smallint | Y |  | idx | 1~5(또는 1~10) |
| source | varchar(50) | Y |  |  | 예: `admin`, `user`, `import` |
| is_active | boolean | N | true | idx | 노출 여부 |
| created_by_id | FK(users_user) | Y |  | idx | 유저 생성팩이면 user FK |
| created_at | timestamptz | N | now |  | |
| updated_at | timestamptz | N | now |  | |

**권장 인덱스**
- `idx_pack_lang_active_diff`: `(language, is_active, difficulty)`
- `idx_pack_created_by`: `(created_by_id)`

**메모**
- “공개/비공개”가 필요하면 `visibility`(`public/private/unlisted`) 컬럼을 추가해도 좋음.

---

### 2.2 `texts_text_item`
| 컬럼 | 타입 | NULL | 기본값 | 제약/인덱스 | 설명 |
|---|---|---:|---|---|---|
| id | bigint/uuid | N |  | PK | 문장 PK |
| pack_id | FK(text_pack) | N |  | idx | 소속 문장팩 |
| content | text | N |  |  | 문장 본문 |
| length | int | Y |  | idx(선택) | 글자수(난이도/추천/통계용) |
| punctuation_level | smallint | Y |  |  | 기호/특수문자 난이도 |
| is_active | boolean | N | true | idx | 비활성/신고 반영 |
| order | int | Y |  | idx(선택) | 팩 내 고정 순서(사용 시) |
| created_at | timestamptz | N | now |  | |
| updated_at | timestamptz | N | now |  | |

**권장 인덱스**
- `idx_item_pack_active`: `(pack_id, is_active)`
- `idx_item_pack_order`: `(pack_id, order)` *(order를 실제로 쓰는 경우만)*

**메모(운영/검수 확장)**
- 유저 문장팩 공유/검수 시 아래 중 택1
  - A안: `status(pending/approved/rejected)`, `reported_count`, `moderated_at` 컬럼 추가
  - B안: 별도 `texts_moderation` 테이블(신고/처리 이력 보관)

---

## 3) sessions 앱 — 연습 기록(가장 중요)

> 이 앱의 핵심은 `TypingSession`을 **진실 소스(Source of Truth)**로 고정하는 것.
> 랭킹/챌린지/통계는 `TypingSession`에서 집계하거나, 집계 테이블로 **요약**한다.

### 3.1 `sessions_typing_session`
| 컬럼 | 타입 | NULL | 기본값 | 제약/인덱스 | 설명 |
|---|---|---:|---|---|---|
| id | bigint/uuid | N |  | PK | 세션 PK |
| user_id | FK(users_user) | Y |  | idx | 비로그인 허용 시 NULL |
| pack_id | FK(text_pack) | Y |  | idx | 선택형(팩 기반 연습 시) |
| text_item_id | FK(text_item) | Y |  | idx | 단일 문장 모드 연결 |
| mode | varchar(20) | N |  | idx | `practice`, `challenge`, `ranked` 등 |
| language | varchar(10) | N |  | idx | `ko`, `en` |
| started_at | timestamptz | N | now | idx | 시작 시각 |
| ended_at | timestamptz | Y |  |  | 종료 시각 |
| duration_ms | int | Y |  |  | 세션 소요(ms) |
| input_length | int | N | 0 |  | 총 입력 길이 |
| correct_length | int | N | 0 |  | 정확 입력 길이 |
| error_count | int | N | 0 |  | 오타 수 |
| accuracy | numeric(5,2) | N | 0 | idx(선택) | 정확도(%) |
| wpm | numeric(6,2) | N | 0 | idx(선택) | WPM |
| cpm | numeric(6,2) | Y |  |  | CPM |
| metadata | jsonb | Y |  |  | 기기/브라우저/키보드 등 확장 |
| created_at | timestamptz | N | now |  | |
| updated_at | timestamptz | N | now |  | |

**권장 제약(선택)**
- `CHECK (accuracy >= 0 AND accuracy <= 100)`
- `CHECK (wpm >= 0)`
- `CHECK (error_count >= 0)`

**권장 인덱스(강력 추천)**
- `idx_session_user_started`: `(user_id, started_at DESC)` → HistoryPage 기본 경로
- `idx_session_mode_lang_started`: `(mode, language, started_at DESC)` → 랭킹/챌린지 집계
- `idx_session_pack_started`: `(pack_id, started_at DESC)` → 팩별 통계/추천

**정렬 인덱스(주의)**
- `(wpm)`/`(accuracy)` 인덱스는 “실시간 랭킹”을 DB에서 직접 뽑을 때만 고려.
  보통은 아래 **Leaderboard Snapshot** 방식이 성능/운영에 유리.

**메모(데이터 폭증/확장)**
- `metadata`에 너무 큰 데이터를 넣지 말 것(로그/이벤트는 분리)
- 유저 탈퇴 시 `user_id`를 `SET NULL`로 두면 기록 보존과 개인정보 분리가 쉬움

---

### 3.2 (선택) `sessions_typing_event` — 오타/키 입력 로그
> 오타 패턴 분석, 키보드 교정, 학습 추천을 위한 “원천 이벤트” 저장.
> 데이터 폭증 가능성이 매우 높으므로 기본 OFF 또는 기간 제한 정책 권장.

| 컬럼 | 타입 | NULL | 기본값 | 제약/인덱스 | 설명 |
|---|---|---:|---|---|---|
| id | bigint/uuid | N |  | PK | 이벤트 PK |
| session_id | FK(typing_session) | N |  | idx | 세션 FK |
| t_ms | int | N |  |  | 세션 시작 기준 ms |
| expected | varchar(5) | Y |  |  | 기대 문자 |
| typed | varchar(5) | Y |  |  | 입력 문자 |
| is_correct | boolean | N |  | idx | 정오타 |
| position | int | Y |  |  | 문장 내 위치 |
| created_at | timestamptz | N | now |  | |
| updated_at | timestamptz | N | now |  | |

**권장 인덱스**
- `idx_event_session_t`: `(session_id, t_ms)`
- `idx_event_session_correct`: `(session_id, is_correct)`

**권장 운영 정책**
- 저장 옵션: (A) 전체 저장 (B) 유저가 “오타 분석” 기능 켠 경우만 저장
- 보관 기간: 30~180일 등으로 제한 가능(필요 시 파티셔닝 고려)

---

## 4) 집계/랭킹 확장(추천 테이블)

### 4.1 `stats_user_daily` — 사용자 일 단위 집계(추천)
> 세션 테이블을 매번 GROUP BY 하지 않도록 “요약 테이블”을 둔다.

| 컬럼 | 타입 | NULL | 제약/인덱스 | 설명 |
|---|---|---:|---|---|
| user_id | FK(users_user) | N | PK(복합) | |
| date | date | N | PK(복합) | Asia/Seoul 기준 날짜 |
| language | varchar(10) | N | PK(복합) | `ko`, `en` |
| total_sessions | int | N |  | 세션 수 |
| total_duration_ms | bigint | N |  | 총 연습 시간 |
| avg_wpm | numeric(6,2) | N |  | 평균 WPM |
| avg_accuracy | numeric(5,2) | N |  | 평균 정확도 |
| best_wpm | numeric(6,2) | Y |  | 최고 WPM |
| best_accuracy | numeric(5,2) | Y |  | 최고 정확도 |
| created_at | timestamptz | N | now |  | |
| updated_at | timestamptz | N | now |  | |

**제약**
- `UNIQUE(user_id, date, language)` (또는 복합 PK)

**메모**
- 이 테이블은 Celery/cron 또는 요청 시(Write-through)로 업데이트 가능

---

### 4.2 `leaderboard_snapshot` + `leaderboard_entry` — 랭킹 스냅샷(추천)
> 랭킹을 “실시간 쿼리”로 뽑으면 비용이 급증하므로, 스냅샷/기간 집계를 권장.

#### 4.2.1 `leaderboard_snapshot`
| 컬럼 | 타입 | NULL | 제약/인덱스 | 설명 |
|---|---|---:|---|---|
| id | bigint/uuid | N | PK | |
| period | varchar(10) | N | idx | `daily`, `weekly`, `monthly` |
| start_date | date | N | idx | 기간 시작 |
| end_date | date | N |  | 기간 끝 |
| mode | varchar(20) | N | idx | `ranked` 등 |
| language | varchar(10) | N | idx | `ko`, `en` |
| generated_at | timestamptz | N | now |  | 생성 시각 |
| created_at | timestamptz | N | now |  | |
| updated_at | timestamptz | N | now |  | |

**권장 제약**
- `UNIQUE(period, start_date, end_date, mode, language)`

#### 4.2.2 `leaderboard_entry`
| 컬럼 | 타입 | NULL | 제약/인덱스 | 설명 |
|---|---|---:|---|---|
| id | bigint/uuid | N | PK | |
| snapshot_id | FK(leaderboard_snapshot) | N | idx | 스냅샷 FK |
| user_id | FK(users_user) | N | idx | 사용자 FK |
| rank | int | N | idx | 순위 |
| score_wpm | numeric(6,2) | N |  | 기준 WPM |
| score_accuracy | numeric(5,2) | N |  | 정확도 |
| session_count | int | N |  | 기간 내 세션 수 |
| created_at | timestamptz | N | now |  | |
| updated_at | timestamptz | N | now |  | |

**권장 제약**
- `UNIQUE(snapshot_id, user_id)`
- `UNIQUE(snapshot_id, rank)`

---

## 5) 챌린지 확장(선택)

### 5.1 `challenges_daily_challenge`
| 컬럼 | 타입 | NULL | 설명 |
|---|---|---:|---|
| id | bigint/uuid | N | |
| date | date | N | 오늘의 날짜(Asia/Seoul 기준) |
| language | varchar(10) | N | |
| pack_id | FK(text_pack) | Y | |
| text_item_id | FK(text_item) | Y | |
| created_at | timestamptz | N | |
| updated_at | timestamptz | N | |

### 5.2 `challenges_user_challenge`
| 컬럼 | 타입 | NULL | 설명 |
|---|---|---:|---|
| id | bigint/uuid | N | |
| user_id | FK(users_user) | N | |
| challenge_id | FK(daily_challenge) | N | |
| session_id | FK(typing_session) | Y | 실제 플레이 세션 연결 |
| status | varchar(20) | N | `started`, `completed` |
| created_at | timestamptz | N | |
| updated_at | timestamptz | N | |

**메모**
- 챌린지는 `typing_session.mode='challenge'`로도 식별 가능하게 유지하면 운영이 편해짐

---

## 6) 빠른 체크리스트(프로젝트가 커지기 전에 확정할 것)

- [ ] `TypingSession`이 “원천 데이터”임을 확정했는가?
- [ ] 비로그인 세션을 허용하는가? (허용 시 `user_id NULL` 전략)
- [ ] 랭킹은 실시간인가, 스냅샷인가? (권장: 스냅샷)
- [ ] 오타 이벤트 로그(`TypingEvent`)를 저장할 것인가? (기본 OFF 권장)
- [ ] texts는 soft delete 정책을 적용할 것인가?
- [ ] History 조회용 인덱스 `(user_id, started_at)`를 확정했는가?

---

## 7) 부록: 권장 enum 값(예시)

- `language`: `ko`, `en`
- `mode`: `practice`, `challenge`, `ranked`
- `period`: `daily`, `weekly`, `monthly`
- `visibility`(추가 시): `public`, `private`, `unlisted`

---

> 다음 단계(선택):  
> 1) Django 모델/마이그레이션에 바로 반영할 “컬럼 타입/제약/on_delete” 정리  
> 2) API 명세(`ops/docs/api-spec.md`)에 스키마 기반 응답 예시 추가  
> 3) 집계/랭킹 생성 배치(관리 커맨드 or Celery) 설계
