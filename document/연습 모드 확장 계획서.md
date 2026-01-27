# 연습 모드 확장 요구사항.md (타자 연습 웹 서비스)

*(기준: 2026-01-16 계획서/정의서의 구조와 확장 철학을 그대로 따름)*

## 0) 배경
- Frontend(React/PWA)에 **HomePage / PracticePage / ResultPage / HistoryPage** 화면이 존재한다.
- Backend(Django/DRF)는 `users`, `texts`, `sessions` 앱을 기본으로 구성한다.
- 연습 기록은 `sessions_typing_session(TypingSession)`을 **원천 데이터(Source of Truth)** 로 유지하며, 확장 정보는 `metadata(jsonb)`에 담는 방식으로 마이그레이션 비용을 최소화한다.
- 오타 패턴의 정밀 분석은 데이터 폭증 위험이 있으므로, 기본은 “결과 기반(세션 단위)”으로 운영하고, 필요 시에만 `sessions_typing_event`를 opt-in으로 사용한다.

---

## 1) 목표
1. PracticePage에서 여러 연습 모드를 선택할 수 있다.
2. 타자 입력 처리/오타 판정/통계 계산은 **공통 타자 엔진**을 재사용하고, 모드별로 규칙(시간 제한, 오타 제한 등)만 교체한다.
3. 모든 모드는 ResultPage에서 결과를 보여주고, HistoryPage에 기록이 남는다.
4. 저장 단위는 TypingSession 1개로 통일한다.

---

## 2) 설계 원칙 (DB/API 호환)
### 2.1 mode / submode 전략
- TypingSession의 `mode`는 크게 3가지로 운용한다.
  - `practice`: 일반 연습(대부분의 모드)
  - `challenge`: 데일리/미션성 모드
  - `ranked`: 랭킹 경쟁 모드(스냅샷 집계 기반)
- 세부 연습 형태(단어/타임어택 등)는 `metadata.submode`로 구분한다.

### 2.2 저장 최소 원칙
- 공통 지표는 TypingSession 기본 컬럼에 저장한다: `duration_ms`, `input_length`, `correct_length`, `error_count`, `accuracy`, `wpm`, `cpm`.
- 모드별 설정값/추가 지표는 `metadata`에 저장한다.
- 이벤트 로그(`sessions_typing_event`)는 기본 OFF, 유저가 오타 분석 기능을 켠 경우에만 저장하는 옵션으로 둔다.

### 2.3 언어/콘텐츠 로딩
- `texts_text_pack(language, difficulty, is_active)` 및 `texts_text_item(pack_id, content, length...)`를 활용해 난이도/언어별 콘텐츠를 구성한다.
- 단어 연습처럼 “단어 DB”가 필요해지면, 1차에서는 `TextItem`을 단어 단위로 만든 전용 팩으로 대체할 수 있다(추후 words 테이블 분리 가능).

---
## 3) 연습 모드 구성

### 3.1 MVP (4~6개 권장)
MVP에서는 “구현 난이도 대비 체감 효과”가 큰 모드 위주로, 성격이 겹치지 않게 6개를 선정한다.

1) **문장 연습(기존 고도화)** (`practice` / `submode=sentence`)
- 기존 기능을 “세트/난이도/팩” 중심으로 확장해 기본 모드로 유지

2) **단어 연습** (`practice` / `submode=word`)
- 단어 단위 템포 훈련(정확도/속도)

3) **타임어택** (`practice` / `submode=time_attack`)
- 30/60/120초 동안 최대 입력량

4) **정확도 챌린지** (`practice` / `submode=accuracy_challenge`)
- 오타 제한 또는 목표 정확도 유지

5) **한글 특화 드릴** (`practice` / `submode=kor_drill`)
- 받침/띄어쓰기/자주 틀리는 조합 등 패턴 반복

6) **약점 훈련(오타 기반 추천 훈련)** (`practice` / `submode=weakness_drill`)
- ResultPage의 오타 Top(기본형) 또는 서버 인사이트(2차)로 약점을 모아 반복 연습

### 3.2 확장(로드맵)
- **데일리 챌린지** (`challenge` / `submode=daily`)
- **랭킹/레이스** (`ranked` / `submode=race|ranked`) + 스냅샷 집계
- **랜덤 문자/숫자/기호** (`practice` / `submode=random_chars`)
- **따라치기(리듬/속도 고정)** (`practice` / `submode=pace`) : 텍스트가 자동 진행
- (선택) **TypingEvent 기반 정밀 오타분석** : opt-in + 보관기간 정책

---

## 4) 모드별 요구사항(규칙/설정/지표)

> 공통: 모든 모드는 종료 시 TypingSession을 저장하고(ResultPage), HistoryPage에서 모드/언어 필터 조회가 가능해야 한다.

### 4.1 문장 연습(고도화)
- **콘텐츠**: `TextPack` 선택(또는 랜덤), `difficulty` 필터, `TextItem`을 N개 이어서 플레이
- **설정값(예시)**
  - `pack_id`(선택), `difficulty`(선택), `items_per_session`(기본 5/10/20)
  - `shuffle`(true/false), `strict_spacing`(공백 엄격)
- **모드 규칙**
  - 문장 단위로 진행(완료/스킵 정책)
  - 오타 표시 + (선택) 즉시 정정 강제
- **추가 지표(옵션)**
  - 문장별 WPM/정확도(메모리 계산 후 `metadata.per_item`으로 저장 가능)

### 4.2 단어 연습
- **콘텐츠(1차)**: 단어 전용 `TextPack` + `TextItem(content=단어)` 구성
- **설정값(예시)**
  - `items_per_session`(기본 30/50/100)
  - `difficulty`(단어 길이/난이도로 매핑), `auto_next_delay_ms`(0~300)
- **모드 규칙**
  - 단어 입력 후 스페이스/엔터로 확정 → 다음 단어
  - 오타가 있어도 확정 가능(기본), 또는 “정확 입력 시에만 통과”(옵션)

### 4.3 타임어택
- **설정값(예시)**
  - `time_limit_sec`(30/60/120)
  - `content_source`(pack/random)
- **모드 규칙**
  - 제한 시간 내 최대한 많이 입력
  - 시간 종료 즉시 세션 종료(자동)
- **추가 지표(옵션)**
  - `metadata.timeline`(예: 5초 단위 WPM 샘플) — 프론트 계산 가능

### 4.4 정확도 챌린지
- **설정값(예시)**
  - `max_errors`(예: 5/10) 또는 `min_accuracy`(예: 95%)
  - `end_on_rule_break`(true/false)
- **모드 규칙**
  - 오타 제한 초과 또는 정확도 하락 시 종료(정책 선택)
- **추가 지표(옵션)**
  - 종료 사유: `metadata.fail_reason = max_errors|min_accuracy|manual`

### 4.5 한글 특화 드릴
- **목표**: 한국어에서 자주 틀리는 패턴(받침/겹받침/띄어쓰기/유사 자모)을 반복 훈련
- **설정값(예시)**
  - `drill_type`(batchim|spacing|double_consonant|similar_keys)
  - `items_per_session`(기본 20/40)
- **콘텐츠 구성(1차)**
  - 드릴 전용 팩을 미리 만들어 `TextPack`으로 관리하거나,
  - (2차) 추천 엔진이 약점 패턴에 맞는 문장을 `TextItem`에서 선별

### 4.6 약점 훈련(오타 기반)
- **데이터 입력(1차, 빠름)**
  - ResultPage에서 “오타 Top N”을 단순 집계(기대 문자 vs 입력 문자 기준)하고,
  - 다음 연습에서 해당 문자/조합이 많이 포함된 문장팩을 추천하거나, 드릴 팩으로 연결
- **데이터 입력(2차, 정확)**
  - opt-in 유저는 `sessions_typing_event`를 저장하고 서버가 패턴 분석 후 추천 제공
- **설정값(예시)**
  - `focus_targets`(배열), `items_per_session`, `time_limit_sec`(선택)

---

## 5) 공통 UI/UX 요구

### 5.1 PracticePage (모드 선택 → 설정 → 시작)
- 모드 선택 UI: 카드형(모드 설명 + 난이도/시간/수량 등 핵심 옵션 노출)
- 설정은 “간단 프리셋(추천)” + “고급 옵션(접기)” 구조 권장

### 5.2 연습 화면(타이핑 화면)
- 현재 입력 위치 커서, 정답/오답 하이라이트
- 진행률(문장/단어/시간) + 실시간 WPM/정확도 표시
- 일시정지(선택), 다시시작, 종료 버튼

### 5.3 ResultPage
- 요약 지표: WPM/CPM, 정확도, 오타 수, 소요 시간, 입력 길이
- (약점 훈련 연계) 오타 Top5 + “추천 훈련 시작” 버튼

### 5.4 HistoryPage
- 최근 기록/최고 기록/평균(기간 선택)
- 필터: `mode`(practice/challenge/ranked) + `submode` + `language`

---

## 6) 저장 스키마(세션) 설계

### 6.1 TypingSession 기본 필드(예시)
- `mode`: `practice|challenge|ranked`
- `language`: `ko|en`
- `started_at`, `ended_at`, `duration_ms`
- `input_length`, `correct_length`, `error_count`, `accuracy`, `wpm`, `cpm`
- `pack_id`(선택), `text_item_id`(선택)
- `metadata`(jsonb)

### 6.2 metadata 예시(JSON)
```json
{
  "submode": "time_attack",
  "settings": {
    "time_limit_sec": 60,
    "difficulty": 3,
    "items_per_session": 0,
    "strict_spacing": true
  },
  "device": {
    "ua": "...",
    "keyboard": "unknown"
  },
  "result_extra": {
    "fail_reason": null,
    "timeline": [
      {"t": 10, "wpm": 312.4, "accuracy": 97.2},
      {"t": 20, "wpm": 298.1, "accuracy": 96.5}
    ]
  }
}
```

> 원칙: `metadata`는 “설정/추가 지표/환경 정보” 수준까지만. 키 입력 이벤트 전체는 `sessions_typing_event`로 분리한다.

---

## 7) API 개요(최소 변경)

### 7.1 기존 흐름 유지
- 프론트에서 실시간 계산 → 종료 시 결과만 API로 저장

### 7.2 엔드포인트(예시)
- `GET /api/texts/packs?lang=ko&difficulty=3` : 팩 목록
- `GET /api/texts/packs/{id}/items` : 문장/단어 아이템
- `POST /api/sessions` : TypingSession 저장(필수)
- `GET /api/sessions?mode=practice&lang=ko&submode=time_attack` : History 조회

### 7.3 (2차) 인사이트/추천
- `GET /api/insights/summary?range=7d&lang=ko` : 오타/약점 요약
- `GET /api/training/recommendations?lang=ko` : 약점 기반 추천 코스

---

## 8) 개발 우선순위(현실적인 구현 순서)

### Phase A (이번 목표: 연습 모드 다양화 체감)
1. PracticePage: 모드 선택 UI + 공통 설정 폼
2. 문장 연습 고도화(세트/팩/난이도)
3. 타임어택 + 정확도 챌린지(룰만 추가하면 됨)
4. 단어 연습(단어 전용 팩으로 1차 구현)

### Phase B (성장/교정 경험)
5. ResultPage: 오타 Top5 + 약점 훈련 시작(기본형)
6. 한글 특화 드릴(드릴 전용 팩 + 추천 연결)

### Phase C (유지율/바이럴)
7. 데일리 챌린지(`mode=challenge`)
8. 랭킹 스냅샷(`mode=ranked`)
9. (선택) TypingEvent opt-in + 정밀 오타분석
