// 가상 키보드 타입 정의

export type FingerName =
  | 'left-pinky' | 'left-ring' | 'left-middle' | 'left-index'
  | 'right-index' | 'right-middle' | 'right-ring' | 'right-pinky'
  | 'thumb'

export interface KeyInfo {
  code: string         // KeyboardEvent.code (예: 'KeyA', 'Space')
  label: string        // 영문 표시 (예: 'A', 'Space')
  labelKo?: string     // 한글 표시 (예: 'ㅁ')
  labelShift?: string  // Shift 영문 (예: '!')
  labelShiftKo?: string // Shift 한글 (예: 'ㅃ')
  finger: FingerName
  width?: number       // 기본 1, Space는 6 등
}

export type KeyboardRow = KeyInfo[]

export interface KeyboardLayout {
  rows: KeyboardRow[]
}

export interface KeyboardSettings {
  showKeyboard: boolean
  showHandGuide: boolean
  showPressedKeys: boolean
}

// 키스트로크 정보 (한글 IME용)
export interface Keystroke {
  code: string        // 물리 키 code
  shift: boolean      // Shift 필요 여부
}
