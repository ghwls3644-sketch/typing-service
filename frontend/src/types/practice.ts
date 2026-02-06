// 연습 모드 타입 정의 (v4.0 스펙)

// 2개 모드만 지원 (v4.0)
export type PracticeMode = 'word' | 'short'

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
  difficulty: 1 | 2 | 3  // v4.0: 3단계만
  itemsPerSession?: number
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

// 모드 설정 목록 (v4.0: 2개만)
export const PRACTICE_MODES: ModeConfig[] = [
  {
    id: 'word',
    name: '단어 연습',
    description: '단어 단위로 타자 실력을 향상시키세요',
    icon: '💬',
    available: true
  },
  {
    id: 'short',
    name: '짧은 글 연습',
    description: '속담을 따라 치며 문장 타이핑을 연습하세요',
    icon: '📝',
    available: true
  }
]

// 난이도 설정
export const DIFFICULTY_LEVELS = [
  { value: 1, name: '초급', description: '짧고 쉬운 텍스트' },
  { value: 2, name: '중급', description: '중간 길이 텍스트' },
  { value: 3, name: '고급', description: '긴 텍스트' }
] as const

// 기본 설정
export const DEFAULT_SETTINGS: PracticeSettings = {
  mode: 'word',
  language: 'korean',
  difficulty: 1,
  itemsPerSession: 10
}
