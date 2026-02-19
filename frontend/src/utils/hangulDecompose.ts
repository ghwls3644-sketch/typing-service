import { JAMO_TO_KEY, CHAR_TO_KEY } from '../data/keyMapping'
import type { Keystroke } from '../types/keyboard'

/**
 * 한글 유니코드 음절 분해 유틸리티
 *
 * 한글 음절(가~힣) = 0xAC00 + (초성 × 21 + 중성) × 28 + 종성
 * - 초성: 19개 (ㄱ~ㅎ)
 * - 중성: 21개 (ㅏ~ㅣ)
 * - 종성: 28개 (없음 + ㄱ~ㅎ)
 */

const HANGUL_START = 0xAC00
const HANGUL_END = 0xD7A3

// 초성 19개
const CHOSEONG = [
  'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ',
  'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
]

// 중성 21개
const JUNGSEONG = [
  'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ',
  'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ',
  'ㅣ'
]

// 종성 28개 (첫 번째는 종성 없음)
const JONGSEONG = [
  '', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ',
  'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ',
  'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
]

// 복합 중성 분해
const COMPOUND_JUNGSEONG: Record<string, string[]> = {
  'ㅘ': ['ㅗ', 'ㅏ'],
  'ㅙ': ['ㅗ', 'ㅐ'],
  'ㅚ': ['ㅗ', 'ㅣ'],
  'ㅝ': ['ㅜ', 'ㅓ'],
  'ㅞ': ['ㅜ', 'ㅔ'],
  'ㅟ': ['ㅜ', 'ㅣ'],
  'ㅢ': ['ㅡ', 'ㅣ'],
}

// 복합 종성 분해
const COMPOUND_JONGSEONG: Record<string, string[]> = {
  'ㄳ': ['ㄱ', 'ㅅ'],
  'ㄵ': ['ㄴ', 'ㅈ'],
  'ㄶ': ['ㄴ', 'ㅎ'],
  'ㄺ': ['ㄹ', 'ㄱ'],
  'ㄻ': ['ㄹ', 'ㅁ'],
  'ㄼ': ['ㄹ', 'ㅂ'],
  'ㄽ': ['ㄹ', 'ㅅ'],
  'ㄾ': ['ㄹ', 'ㅌ'],
  'ㄿ': ['ㄹ', 'ㅍ'],
  'ㅀ': ['ㄹ', 'ㅎ'],
  'ㅄ': ['ㅂ', 'ㅅ'],
}

function isHangulSyllable(code: number): boolean {
  return code >= HANGUL_START && code <= HANGUL_END
}

/**
 * 한글 음절 하나를 자모 배열로 분해
 */
export function decompose(char: string): string[] {
  const code = char.charCodeAt(0)

  if (!isHangulSyllable(code)) {
    return [char]
  }

  const offset = code - HANGUL_START
  const choIdx = Math.floor(offset / (21 * 28))
  const jungIdx = Math.floor((offset % (21 * 28)) / 28)
  const jongIdx = offset % 28

  const result: string[] = []

  // 초성
  result.push(CHOSEONG[choIdx])

  // 중성 (복합이면 분해)
  const jung = JUNGSEONG[jungIdx]
  if (COMPOUND_JUNGSEONG[jung]) {
    result.push(...COMPOUND_JUNGSEONG[jung])
  } else {
    result.push(jung)
  }

  // 종성 (있으면, 복합이면 분해)
  if (jongIdx > 0) {
    const jong = JONGSEONG[jongIdx]
    if (COMPOUND_JONGSEONG[jong]) {
      result.push(...COMPOUND_JONGSEONG[jong])
    } else {
      result.push(jong)
    }
  }

  return result
}

/**
 * 자모를 물리 키스트로크로 변환
 */
function jamoToKeystroke(jamo: string): Keystroke | null {
  const mapping = JAMO_TO_KEY[jamo]
  if (mapping) {
    return { code: mapping.code, shift: mapping.shift }
  }
  return null
}

/**
 * 텍스트 전체를 물리 키스트로크 배열로 변환
 * 한글 음절은 분해 후 자모→키 변환
 * 영문/기호/공백은 직접 CHAR_TO_KEY로 변환
 */
export function textToKeystrokes(text: string): Keystroke[] {
  const keystrokes: Keystroke[] = []

  for (const char of text) {
    const code = char.charCodeAt(0)

    if (isHangulSyllable(code)) {
      // 한글 음절 → 자모 분해 → 키스트로크
      const jamos = decompose(char)
      for (const jamo of jamos) {
        const ks = jamoToKeystroke(jamo)
        if (ks) keystrokes.push(ks)
      }
    } else {
      // 영문/기호/공백 → 직접 매핑
      const mapping = CHAR_TO_KEY[char]
      if (mapping) {
        keystrokes.push({ code: mapping.code, shift: mapping.shift })
      }
    }
  }

  return keystrokes
}
