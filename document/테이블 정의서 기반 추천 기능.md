# 타자 연습 웹서비스 — 추천 기능 정리 (DB 정의서 기반)
*(작성일: 2026-01-16 / 기준 스키마: Users · Texts · Sessions + Stats · Leaderboard · Challenges 확장)*

> 이 문서는 **DB 테이블 정의서(스키마 초안)**를 바탕으로,
> 기능을 추가할 때 **어떤 테이블을 쓰고(또는 추가하고)** 어떤 화면/API가 필요한지까지 한 번에 정리한 로드맵이다.

---

## 0) 현재 기준(완료된 구성)
- **Frontend**: Home / Practice / Result / History, API 클라이언트, PWA manifest
- **Backend**: `users`, `texts`, `sessions` 앱 구성 완료 (실행/도커 테스트는 아직)
- **확장 스키마(정의서 포함)**:
  - `stats_user_daily` (일 단위 집계)
  - `leaderboard_snapshot`, `leaderboard_entry` (랭킹 스냅샷)
  - `challenges_daily_challenge`, `challenges_user_challenge` (데일리 챌린지)
  - `sessions_typing_event` (선택: 키 입력/오타 이벤트)

---

## 1) 우선순위 로드맵(추천)

### Phase 1 — “바로 체감 + 유지율” (가성비 최고)
1. **목표/루틴 + 스트릭(연속 기록)**
2. **오타 Top/패턴 분석 + 맞춤 훈련 추천(기본형)**
3. **주간 랭킹(스냅샷 방식)**

### Phase 2 — “재미/바이럴”
4. **데일리 챌린지**
5. **뱃지/레벨(성취 시스템)**
6. **결과 공유 카드(이미지)**

### Phase 3 — “콘텐츠/운영 확장”
7. **문장팩 즐겨찾기/최근 사용**
8. **유저 문장팩 업로드 + 검수/신고**
9. **데이터 내보내기(내 기록 다운로드) + 관리자 대시보드**

---

## 2) 추천 기능 상세(테이블/화면/API 관점)

### 2.1 목표/루틴 + 스트릭(연속 기록) ✅ 강추
**핵심 가치**
- 매일 “조금씩” 하게 만들고, History가 단순 기록 → 습관/달성으로 변함

**DB(기존/활용)**
- ✅ `stats_user_daily` (정의서에 포함됨)
  - 하루 단위로 `total_sessions`, `total_duration_ms`, `avg_wpm`, `avg_accuracy` 업데이트

**DB(추가 추천: 매우 작음)**
- `goals_user_goal`
  - `user_id`, `goal_type`(time/sessions), `target_value`, `language`(optional), `is_active`
- `goals_user_streak` *(선택)*
  - 스트릭을 계산으로도 가능하지만, 성능/편의상 캐싱 테이블이 있으면 좋음

**API(예시)**
- `GET /api/goals/me` : 내 목표 조회
- `POST /api/goals/me` : 목표 설정/수정
- `GET /api/stats/daily?from=YYYY-MM-DD&to=...` : 캘린더/차트 데이터
- (집계 업데이트는 배치 or 세션 저장 시 write-through)

**UI(페이지 변경)**
- HomePage: 오늘 목표/진행률, 스트릭 뱃지
- HistoryPage: 스트릭 캘린더(일별 세션/시간)

---

### 2.2 오타 Top/패턴 분석 + 맞춤 훈련 추천 ✅ 강추
**핵심 가치**
- “그냥 치는 것” → “교정/성장” 경험 제공

**DB(기본형: 이벤트 로그 없이 가능)**
- ✅ `sessions_typing_session`
  - 결과 기반: 오타 수, 정확도, WPM, 모드/언어/팩 정보를 활용해 추천

**DB(고급형: 정밀 분석)**
- (선택) ✅ `sessions_typing_event`
  - 기대 문자 vs 입력 문자 로그로 “어떤 패턴”에서 틀리는지 분석

**추천 구현 전략**
- 1단계(빠름): ResultPage에 **오타 Top N(간단)** = “자주 틀리는 글자/조합”을 프론트에서 추정(가능하면)
- 2단계(정확): `TypingEvent` 저장을 켠 유저에 한해 서버 분석 제공(데이터 폭증 방지)

**API(예시)**
- `GET /api/insights/summary?range=7d&lang=ko`
- `GET /api/training/recommendations?lang=en`
- `POST /api/sessions` 저장 시 (옵션) `events` 배열 수신

**UI(페이지 변경)**
- ResultPage: 오타 Top5 / “추천 훈련 시작” 버튼
- PracticePage: 추천 코스(특정 키/조합 집중)

---

### 2.3 주간 랭킹(스냅샷) ✅ 강추
**핵심 가치**
- 경쟁 요소는 유지율을 크게 올림
- 실시간 정렬보다 “스냅샷”이 운영/성능/공정성에 유리

**DB(필수)**
- ✅ `leaderboard_snapshot`, `leaderboard_entry`
- 근거 데이터: `sessions_typing_session(mode='ranked' 또는 필터 조건)`

**배치 작업(추천)**
- 주 1회/일 1회 스냅샷 생성
- Django management command 또는 Celery beat로 실행

**API(예시)**
- `GET /api/leaderboard?period=weekly&lang=ko`
- `GET /api/leaderboard/me?period=weekly&lang=ko` : 내 순위/근처 랭커

**UI(페이지 추가 추천)**
- `LeaderboardPage` (신규): 주간/일간 탭, 내 순위 강조

---

### 2.4 데일리 챌린지 ✅ 재미 + 습관 결합
**핵심 가치**
- “오늘의 문제”는 일일 재방문을 강하게 만듦

**DB(필수)**
- ✅ `challenges_daily_challenge`
- ✅ `challenges_user_challenge`
- 플레이 기록은 `sessions_typing_session(mode='challenge')`로 연결

**API(예시)**
- `GET /api/challenges/today?lang=ko`
- `POST /api/challenges/today/start`
- `POST /api/challenges/today/complete` (또는 세션 저장과 함께 처리)

**UI(페이지 변경)**
- HomePage: 오늘의 챌린지 카드
- ResultPage: 챌린지 결과 + 랭킹(선택)

---

### 2.5 뱃지/레벨(성취 시스템) ✅ 동기부여
**핵심 가치**
- 스트릭과 함께 쓰면 강력함(꾸준함/성장 보상)

**DB(추가 추천)**
- `achievements_badge`
  - `code`, `title`, `description`, `icon_key`, `condition_json`
- `achievements_user_badge`
  - `user_id`, `badge_id`, `earned_at`

**근거 데이터**
- `stats_user_daily`, `sessions_typing_session`

**API(예시)**
- `GET /api/achievements/me`
- `GET /api/achievements/catalog`

**UI(페이지 추가/변경)**
- Profile/Settings 페이지(신규) 또는 HomePage에 “최근 획득 뱃지”

---

### 2.6 결과 공유 카드(이미지) ✅ 바이럴
**핵심 가치**
- 공유 → 유입, 기록 자랑 → 참여 유도

**DB**
- 별도 테이블 없이도 가능(세션/랭킹/스트릭 데이터 사용)
- (선택) `shares_share_log`로 공유 이벤트만 로그 가능

**API(예시)**
- `GET /api/share/card?session_id=...` (서버 렌더링) 또는 프론트 캔버스로 생성

**UI**
- ResultPage: “공유하기” 버튼

---

### 2.7 문장팩 즐겨찾기/최근 사용 ✅ 콘텐츠 UX
**DB(추가 추천)**
- `texts_pack_favorite(user_id, pack_id, created_at)` UNIQUE(user_id, pack_id)
- 최근 사용은 `sessions_typing_session(pack_id)` 기반으로도 가능

**API**
- `POST /api/texts/packs/{id}/favorite`
- `GET /api/texts/packs?sort=recent|popular|favorite`

**UI**
- HomePage: 최근 사용 팩 / 즐겨찾기

---

### 2.8 유저 문장팩 업로드 + 검수/신고 ✅ 커뮤니티/운영
**DB(간단안)**
- `texts_text_pack`/`texts_text_item`에 `status`, `reported_count` 컬럼 추가

**DB(정석안)**
- `texts_report` (신고: reporter, target, reason, created_at)
- `texts_moderation_log` (처리 이력)

**API**
- `POST /api/texts/packs` (유저 업로드)
- `POST /api/texts/items`
- `POST /api/texts/reports`
- `GET /api/admin/moderation/queue`

**UI**
- 팩 생성/편집 페이지(신규)
- 신고 버튼(문장/팩)

---

### 2.9 데이터 내보내기(내 기록 다운로드) + 관리자 대시보드 ✅ 신뢰/운영
**DB**
- `sessions_typing_session`, `stats_user_daily`

**API**
- `GET /api/export/sessions.csv`
- `GET /api/export/stats_daily.csv`

**UI**
- Settings/Profile: “내 데이터 다운로드”
- Admin: 기본 통계, 신고 큐, 챌린지 생성

---

## 3) 구현 순서 추천(현실적인 개발 흐름)

1) **DB/백엔드 실행 안정화**
- Docker compose로 Postgres + Django + Nginx를 실제로 올려서 “세션 저장/조회”가 정상인지 확인

2) **stats_user_daily 도입**
- 세션 저장 시 write-through 또는 배치로 일 집계 업데이트
- HistoryPage/대시보드의 기반 완성

3) **Goals(목표/스트릭) + UI 반영**
- Home/History에 “오늘 목표 + 스트릭”만 붙여도 체감이 큼

4) **Leaderboard Snapshot**
- 스냅샷 생성 커맨드/배치 + LeaderboardPage

5) **Daily Challenge**
- 챌린지 생성/참여 기록 + mode 연결

6) (선택) **TypingEvent 기반 정밀 오타분석**
- 데이터 폭증 방지 정책(옵션 저장/보관기간)부터 적용

---

## 4) 체크리스트(스키마 기준 확정 포인트)
- [ ] `TypingSession`을 **원천 데이터**로 유지(랭킹/통계/챌린지 근거)
- [ ] `user_id` NULL 허용 여부(게스트 지원/기록 이관)
- [ ] 랭킹은 스냅샷(권장) vs 실시간(비권장)
- [ ] TypingEvent 저장 정책(기본 OFF + opt-in + 보관기간)
- [ ] texts soft delete(`is_active`) 정책 확정
- [ ] 핵심 인덱스 `(user_id, started_at DESC)` 적용

---

## 5) 부록: 추천 앱/모듈 구조(선택)
- `apps/stats` : `stats_user_daily` + 통계 API
- `apps/goals` : 목표/스트릭
- `apps/leaderboard` : 스냅샷/엔트리 + 배치
- `apps/challenges` : 데일리 챌린지
- `apps/achievements` : 뱃지/레벨
- `apps/moderation` : 신고/검수(콘텐츠 확장 시)

---

> 다음 단계로 원하면:
> - 위 로드맵을 기준으로 **각 앱별 “테이블 + API 명세 + 화면 플로우”**를 `ops/docs/` 하위에
>   실제 파일로 쪼개서(예: `api-spec.md`, `leaderboard.md`) 정리해줄 수도 있음.
