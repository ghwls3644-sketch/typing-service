// 챌린지 모드 타입 정의

export interface ChallengeStats {
  score: number
  combo: number
  maxCombo: number
  wpm: number
  accuracy: number
  correctChars: number
  totalInputs: number
  errors: number
}

export interface ChallengeSessionLocal {
  id: string
  playedAt: number
  submode: 'time_attack_combo'
  base: {
    durationMs: number
    wpm: number
    accuracy: number
    errorCount: number
    correctChars: number
    totalInputs: number
  }
  extra: {
    score: number
    maxCombo: number
    timeLimitSec: number
  }
}

export interface ChallengeBest {
  bestScore: number
  bestMaxCombo: number
  bestWpm: number
  updatedAt: number
}

export interface ChallengeHistory {
  version: 1
  items: ChallengeSessionLocal[]
}

// 챌린지 결과 페이지용
export interface ChallengeResultState {
  resultType: 'challenge'
  stats: ChallengeStats
  durationMs: number
}

// 연습 결과와 통합된 타입
export type ResultState = 
  | { resultType: 'practice'; stats: import('./practice').TypingStats; text: string; userInput?: string; language: 'korean' | 'english'; mode?: import('./practice').PracticeMode; metadata?: Record<string, unknown> }
  | ChallengeResultState

// 게임 상태
export type ChallengePhase = 'ready' | 'running' | 'finished'

// 콤보 점수 계산
export function calculateMultiplier(combo: number): number {
  return Math.min(1 + Math.floor(combo / 20) * 0.25, 2.0)
}

export function calculateScoreForCorrect(combo: number): number {
  const multiplier = calculateMultiplier(combo)
  return Math.round(1 * multiplier)
}

export const CHALLENGE_PENALTY = 5
export const CHALLENGE_DURATION_SEC = 60
