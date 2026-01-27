// 연습 모드 타입 정의

export type PracticeMode = 'sentence' | 'word' | 'time_attack' | 'accuracy_challenge' | 'kor_drill' | 'weakness_drill'

export interface ModeConfig {
  id: PracticeMode
  name: string
  description: string
  icon: string
  available: boolean
}

export interface PracticeSettings {
  mode: PracticeMode
  language: 'korean' | 'english'
  // 문장 연습
  itemsPerSession?: number
  difficulty?: number
  packId?: string
  // 타임어택
  timeLimitSec?: number
  // 정확도 챌린지
  maxErrors?: number
  minAccuracy?: number
  // 단어 연습
  autoNextDelay?: number
}

export interface TypingStats {
  wpm: number
  accuracy: number
  time: number
  correctChars: number
  totalChars: number
  errors: number
}

export interface TypingResult {
  stats: TypingStats
  text: string
  language: 'korean' | 'english'
  mode: PracticeMode
  settings: PracticeSettings
  metadata?: {
    submode: PracticeMode
    settings: Partial<PracticeSettings>
    result_extra?: {
      fail_reason?: string | null
      timeline?: Array<{ t: number; wpm: number; accuracy: number }>
    }
  }
}

// 모드 설정 목록
export const PRACTICE_MODES: ModeConfig[] = [
  {
    id: 'sentence',
    name: '문장 연습',
    description: '문장을 따라 치며 타자 실력을 향상시키세요',
    icon: '📝',
    available: true
  },
  {
    id: 'time_attack',
    name: '타임어택',
    description: '제한 시간 내 최대한 많이 입력하세요',
    icon: '⏱️',
    available: true
  },
  {
    id: 'accuracy_challenge',
    name: '정확도 챌린지',
    description: '오타 없이 정확하게 입력하세요',
    icon: '🎯',
    available: true
  },
  {
    id: 'word',
    name: '단어 연습',
    description: '단어 단위로 빠르게 연습하세요',
    icon: '💬',
    available: true
  },
  {
    id: 'kor_drill',
    name: '한글 특화 드릴',
    description: '받침, 겹받침 등 한글 패턴 훈련',
    icon: '🇰🇷',
    available: true
  },
  {
    id: 'weakness_drill',
    name: '약점 훈련',
    description: '자주 틀리는 패턴을 집중 연습',
    icon: '💪',
    available: false // Phase B
  }
]

// 기본 설정
export const DEFAULT_SETTINGS: PracticeSettings = {
  mode: 'sentence',
  language: 'korean',
  itemsPerSession: 5,
  difficulty: 1,
  timeLimitSec: 60,
  maxErrors: 5,
  minAccuracy: 95,
  autoNextDelay: 300
}
