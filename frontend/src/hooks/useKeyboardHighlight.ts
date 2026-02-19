import { useMemo } from 'react'
import { CHAR_TO_KEY } from '../data/keyMapping'
import type { Keystroke } from '../types/keyboard'

/**
 * 다음 입력해야 할 키를 계산하는 훅
 * Phase 1: 영문 모드만 지원 (한글은 Phase 2에서 textToKeystrokes 연동)
 */
export function useKeyboardHighlight(
  targetText: string,
  userInput: string,
  language: 'korean' | 'english',
  keystrokeQueue?: Keystroke[],
  consumedKeystrokes?: number,
): string[] {
  return useMemo(() => {
    // 한글 모드: 키스트로크 큐 사용
    if (language === 'korean' && keystrokeQueue && consumedKeystrokes !== undefined) {
      const next = keystrokeQueue[consumedKeystrokes]
      if (!next) return []
      const keys = [next.code]
      if (next.shift) keys.push('ShiftLeft')
      return keys
    }

    // 영문 모드: 다음 문자 → 키 code 변환
    const nextCharIdx = userInput.length
    if (nextCharIdx >= targetText.length) return []

    const nextChar = targetText[nextCharIdx]
    const mapping = CHAR_TO_KEY[nextChar]
    if (!mapping) return []

    const keys = [mapping.code]
    if (mapping.shift) keys.push('ShiftLeft')
    return keys
  }, [targetText, userInput, language, keystrokeQueue, consumedKeystrokes])
}
