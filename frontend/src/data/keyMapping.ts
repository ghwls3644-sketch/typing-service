import type { FingerName, KeyInfo, KeyboardRow } from '../types/keyboard'

// 표준 QWERTY 키보드 레이아웃 (4행 + 스페이스바)
// 각 키: code, 영문 label, 한글 label, 손가락, 너비

const f = (
  code: string,
  label: string,
  finger: FingerName,
  opts?: { ko?: string; shift?: string; shiftKo?: string; width?: number }
): KeyInfo => ({
  code,
  label,
  finger,
  labelKo: opts?.ko,
  labelShift: opts?.shift,
  labelShiftKo: opts?.shiftKo,
  width: opts?.width,
})

// Row 0: 숫자행
const ROW_NUMBER: KeyboardRow = [
  f('Backquote', '`', 'left-pinky', { shift: '~' }),
  f('Digit1', '1', 'left-pinky', { shift: '!' }),
  f('Digit2', '2', 'left-ring', { shift: '@' }),
  f('Digit3', '3', 'left-middle', { shift: '#' }),
  f('Digit4', '4', 'left-index', { shift: '$' }),
  f('Digit5', '5', 'left-index', { shift: '%' }),
  f('Digit6', '6', 'right-index', { shift: '^' }),
  f('Digit7', '7', 'right-index', { shift: '&' }),
  f('Digit8', '8', 'right-middle', { shift: '*' }),
  f('Digit9', '9', 'right-ring', { shift: '(' }),
  f('Digit0', '0', 'right-pinky', { shift: ')' }),
  f('Minus', '-', 'right-pinky', { shift: '_' }),
  f('Equal', '=', 'right-pinky', { shift: '+' }),
  f('Backspace', '⌫', 'right-pinky', { width: 1.5 }),
]

// Row 1: 상단행 (QWERTY)
const ROW_TOP: KeyboardRow = [
  f('Tab', 'Tab', 'left-pinky', { width: 1.5 }),
  f('KeyQ', 'Q', 'left-pinky', { ko: 'ㅂ', shiftKo: 'ㅃ' }),
  f('KeyW', 'W', 'left-ring', { ko: 'ㅈ', shiftKo: 'ㅉ' }),
  f('KeyE', 'E', 'left-middle', { ko: 'ㄷ', shiftKo: 'ㄸ' }),
  f('KeyR', 'R', 'left-index', { ko: 'ㄱ', shiftKo: 'ㄲ' }),
  f('KeyT', 'T', 'left-index', { ko: 'ㅅ', shiftKo: 'ㅆ' }),
  f('KeyY', 'Y', 'right-index', { ko: 'ㅛ' }),
  f('KeyU', 'U', 'right-index', { ko: 'ㅕ' }),
  f('KeyI', 'I', 'right-middle', { ko: 'ㅑ' }),
  f('KeyO', 'O', 'right-ring', { ko: 'ㅐ', shiftKo: 'ㅒ' }),
  f('KeyP', 'P', 'right-pinky', { ko: 'ㅔ', shiftKo: 'ㅖ' }),
  f('BracketLeft', '[', 'right-pinky', { shift: '{' }),
  f('BracketRight', ']', 'right-pinky', { shift: '}' }),
  f('Backslash', '\\', 'right-pinky', { shift: '|' }),
]

// Row 2: 홈행 (ASDF)
const ROW_HOME: KeyboardRow = [
  f('CapsLock', 'Caps', 'left-pinky', { width: 1.75 }),
  f('KeyA', 'A', 'left-pinky', { ko: 'ㅁ' }),
  f('KeyS', 'S', 'left-ring', { ko: 'ㄴ' }),
  f('KeyD', 'D', 'left-middle', { ko: 'ㅇ' }),
  f('KeyF', 'F', 'left-index', { ko: 'ㄹ' }),
  f('KeyG', 'G', 'left-index', { ko: 'ㅎ' }),
  f('KeyH', 'H', 'right-index', { ko: 'ㅗ' }),
  f('KeyJ', 'J', 'right-index', { ko: 'ㅓ' }),
  f('KeyK', 'K', 'right-middle', { ko: 'ㅏ' }),
  f('KeyL', 'L', 'right-ring', { ko: 'ㅣ' }),
  f('Semicolon', ';', 'right-pinky', { shift: ':' }),
  f('Quote', "'", 'right-pinky', { shift: '"' }),
  f('Enter', 'Enter', 'right-pinky', { width: 1.75 }),
]

// Row 3: 하단행 (ZXCV)
const ROW_BOTTOM: KeyboardRow = [
  f('ShiftLeft', 'Shift', 'left-pinky', { width: 2.25 }),
  f('KeyZ', 'Z', 'left-pinky', { ko: 'ㅋ' }),
  f('KeyX', 'X', 'left-ring', { ko: 'ㅌ' }),
  f('KeyC', 'C', 'left-middle', { ko: 'ㅊ' }),
  f('KeyV', 'V', 'left-index', { ko: 'ㅍ' }),
  f('KeyB', 'B', 'left-index', { ko: 'ㅠ' }),
  f('KeyN', 'N', 'right-index', { ko: 'ㅜ' }),
  f('KeyM', 'M', 'right-index', { ko: 'ㅡ' }),
  f('Comma', ',', 'right-middle', { shift: '<' }),
  f('Period', '.', 'right-ring', { shift: '>' }),
  f('Slash', '/', 'right-pinky', { shift: '?' }),
  f('ShiftRight', 'Shift', 'right-pinky', { width: 2.25 }),
]

// Row 4: 스페이스바 행
const ROW_SPACE: KeyboardRow = [
  f('Space', 'Space', 'thumb', { width: 8 }),
]

export const KEYBOARD_ROWS: KeyboardRow[] = [
  ROW_NUMBER,
  ROW_TOP,
  ROW_HOME,
  ROW_BOTTOM,
  ROW_SPACE,
]

// === 한글 두벌식 자모 → 물리 키 매핑 ===

// 자모 → { code, shift } 매핑
export const JAMO_TO_KEY: Record<string, { code: string; shift: boolean }> = {
  // 초성/종성 자음
  'ㄱ': { code: 'KeyR', shift: false },
  'ㄲ': { code: 'KeyR', shift: true },
  'ㄴ': { code: 'KeyS', shift: false },
  'ㄷ': { code: 'KeyE', shift: false },
  'ㄸ': { code: 'KeyE', shift: true },
  'ㄹ': { code: 'KeyF', shift: false },
  'ㅁ': { code: 'KeyA', shift: false },
  'ㅂ': { code: 'KeyQ', shift: false },
  'ㅃ': { code: 'KeyQ', shift: true },
  'ㅅ': { code: 'KeyT', shift: false },
  'ㅆ': { code: 'KeyT', shift: true },
  'ㅇ': { code: 'KeyD', shift: false },
  'ㅈ': { code: 'KeyW', shift: false },
  'ㅉ': { code: 'KeyW', shift: true },
  'ㅊ': { code: 'KeyC', shift: false },
  'ㅋ': { code: 'KeyZ', shift: false },
  'ㅌ': { code: 'KeyX', shift: false },
  'ㅍ': { code: 'KeyV', shift: false },
  'ㅎ': { code: 'KeyG', shift: false },

  // 모음
  'ㅏ': { code: 'KeyK', shift: false },
  'ㅐ': { code: 'KeyO', shift: false },
  'ㅑ': { code: 'KeyI', shift: false },
  'ㅒ': { code: 'KeyO', shift: true },
  'ㅓ': { code: 'KeyJ', shift: false },
  'ㅔ': { code: 'KeyP', shift: false },
  'ㅕ': { code: 'KeyU', shift: false },
  'ㅖ': { code: 'KeyP', shift: true },
  'ㅗ': { code: 'KeyH', shift: false },
  'ㅛ': { code: 'KeyY', shift: false },
  'ㅜ': { code: 'KeyN', shift: false },
  'ㅠ': { code: 'KeyB', shift: false },
  'ㅡ': { code: 'KeyM', shift: false },
  'ㅣ': { code: 'KeyL', shift: false },
}

// 영문 문자 → 물리 키 code 매핑
export const CHAR_TO_KEY: Record<string, { code: string; shift: boolean }> = {
  'a': { code: 'KeyA', shift: false }, 'A': { code: 'KeyA', shift: true },
  'b': { code: 'KeyB', shift: false }, 'B': { code: 'KeyB', shift: true },
  'c': { code: 'KeyC', shift: false }, 'C': { code: 'KeyC', shift: true },
  'd': { code: 'KeyD', shift: false }, 'D': { code: 'KeyD', shift: true },
  'e': { code: 'KeyE', shift: false }, 'E': { code: 'KeyE', shift: true },
  'f': { code: 'KeyF', shift: false }, 'F': { code: 'KeyF', shift: true },
  'g': { code: 'KeyG', shift: false }, 'G': { code: 'KeyG', shift: true },
  'h': { code: 'KeyH', shift: false }, 'H': { code: 'KeyH', shift: true },
  'i': { code: 'KeyI', shift: false }, 'I': { code: 'KeyI', shift: true },
  'j': { code: 'KeyJ', shift: false }, 'J': { code: 'KeyJ', shift: true },
  'k': { code: 'KeyK', shift: false }, 'K': { code: 'KeyK', shift: true },
  'l': { code: 'KeyL', shift: false }, 'L': { code: 'KeyL', shift: true },
  'm': { code: 'KeyM', shift: false }, 'M': { code: 'KeyM', shift: true },
  'n': { code: 'KeyN', shift: false }, 'N': { code: 'KeyN', shift: true },
  'o': { code: 'KeyO', shift: false }, 'O': { code: 'KeyO', shift: true },
  'p': { code: 'KeyP', shift: false }, 'P': { code: 'KeyP', shift: true },
  'q': { code: 'KeyQ', shift: false }, 'Q': { code: 'KeyQ', shift: true },
  'r': { code: 'KeyR', shift: false }, 'R': { code: 'KeyR', shift: true },
  's': { code: 'KeyS', shift: false }, 'S': { code: 'KeyS', shift: true },
  't': { code: 'KeyT', shift: false }, 'T': { code: 'KeyT', shift: true },
  'u': { code: 'KeyU', shift: false }, 'U': { code: 'KeyU', shift: true },
  'v': { code: 'KeyV', shift: false }, 'V': { code: 'KeyV', shift: true },
  'w': { code: 'KeyW', shift: false }, 'W': { code: 'KeyW', shift: true },
  'x': { code: 'KeyX', shift: false }, 'X': { code: 'KeyX', shift: true },
  'y': { code: 'KeyY', shift: false }, 'Y': { code: 'KeyY', shift: true },
  'z': { code: 'KeyZ', shift: false }, 'Z': { code: 'KeyZ', shift: true },
  ' ': { code: 'Space', shift: false },
  '1': { code: 'Digit1', shift: false }, '!': { code: 'Digit1', shift: true },
  '2': { code: 'Digit2', shift: false }, '@': { code: 'Digit2', shift: true },
  '3': { code: 'Digit3', shift: false }, '#': { code: 'Digit3', shift: true },
  '4': { code: 'Digit4', shift: false }, '$': { code: 'Digit4', shift: true },
  '5': { code: 'Digit5', shift: false }, '%': { code: 'Digit5', shift: true },
  '6': { code: 'Digit6', shift: false }, '^': { code: 'Digit6', shift: true },
  '7': { code: 'Digit7', shift: false }, '&': { code: 'Digit7', shift: true },
  '8': { code: 'Digit8', shift: false }, '*': { code: 'Digit8', shift: true },
  '9': { code: 'Digit9', shift: false }, '(': { code: 'Digit9', shift: true },
  '0': { code: 'Digit0', shift: false }, ')': { code: 'Digit0', shift: true },
  '-': { code: 'Minus', shift: false }, '_': { code: 'Minus', shift: true },
  '=': { code: 'Equal', shift: false }, '+': { code: 'Equal', shift: true },
  '[': { code: 'BracketLeft', shift: false }, '{': { code: 'BracketLeft', shift: true },
  ']': { code: 'BracketRight', shift: false }, '}': { code: 'BracketRight', shift: true },
  '\\': { code: 'Backslash', shift: false }, '|': { code: 'Backslash', shift: true },
  ';': { code: 'Semicolon', shift: false }, ':': { code: 'Semicolon', shift: true },
  "'": { code: 'Quote', shift: false }, '"': { code: 'Quote', shift: true },
  ',': { code: 'Comma', shift: false }, '<': { code: 'Comma', shift: true },
  '.': { code: 'Period', shift: false }, '>': { code: 'Period', shift: true },
  '/': { code: 'Slash', shift: false }, '?': { code: 'Slash', shift: true },
  '`': { code: 'Backquote', shift: false }, '~': { code: 'Backquote', shift: true },
}

// code로 KeyInfo 빠르게 찾기
const _keyByCode = new Map<string, KeyInfo>()
for (const row of KEYBOARD_ROWS) {
  for (const key of row) {
    _keyByCode.set(key.code, key)
  }
}

export function getKeyByCode(code: string): KeyInfo | undefined {
  return _keyByCode.get(code)
}
