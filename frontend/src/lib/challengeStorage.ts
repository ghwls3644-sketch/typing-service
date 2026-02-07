/**
 * 챌린지 로컬 저장 유틸리티
 */
import type { ChallengeSessionLocal, ChallengeBest, ChallengeHistory, ChallengeStats } from '../types/challenge'

const KEYS = {
  BEST: 'typing:challenge_best',
  HISTORY: 'typing:challenge_history'
} as const

const MAX_HISTORY_ITEMS = 10

/**
 * 최고기록 조회
 */
export function getChallengeBest(): ChallengeBest | null {
  try {
    const data = localStorage.getItem(KEYS.BEST)
    return data ? JSON.parse(data) : null
  } catch {
    return null
  }
}

/**
 * 최근 10판 조회
 */
export function getChallengeHistory(): ChallengeSessionLocal[] {
  try {
    const data = localStorage.getItem(KEYS.HISTORY)
    if (!data) return []
    const parsed: ChallengeHistory = JSON.parse(data)
    return parsed.items || []
  } catch {
    return []
  }
}

/**
 * 챌린지 결과 저장 (최고기록 + 최근 10판)
 */
export function saveChallengeResult(stats: ChallengeStats, durationMs: number): void {
  const now = Date.now()
  
  // 세션 데이터 생성
  const session: ChallengeSessionLocal = {
    id: `local-${now}`,
    playedAt: now,
    submode: 'time_attack_combo',
    base: {
      durationMs,
      wpm: stats.wpm,
      accuracy: stats.accuracy,
      errorCount: stats.errors,
      correctChars: stats.correctChars,
      totalInputs: stats.totalInputs
    },
    extra: {
      score: stats.score,
      maxCombo: stats.maxCombo,
      timeLimitSec: 60
    }
  }
  
  // 1. 최고기록 업데이트
  const currentBest = getChallengeBest()
  if (!currentBest || stats.score > currentBest.bestScore) {
    const newBest: ChallengeBest = {
      bestScore: stats.score,
      bestMaxCombo: stats.maxCombo,
      bestWpm: stats.wpm,
      updatedAt: now
    }
    localStorage.setItem(KEYS.BEST, JSON.stringify(newBest))
  }
  
  // 2. 히스토리 업데이트 (최신순, 최대 10개)
  const history = getChallengeHistory()
  history.unshift(session)
  const trimmed = history.slice(0, MAX_HISTORY_ITEMS)
  
  const historyData: ChallengeHistory = {
    version: 1,
    items: trimmed
  }
  localStorage.setItem(KEYS.HISTORY, JSON.stringify(historyData))
}

/**
 * 챌린지 데이터 초기화 (테스트용)
 */
export function clearChallengeData(): void {
  localStorage.removeItem(KEYS.BEST)
  localStorage.removeItem(KEYS.HISTORY)
}
