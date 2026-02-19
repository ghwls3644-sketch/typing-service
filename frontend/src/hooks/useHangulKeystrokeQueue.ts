import { useMemo } from 'react'
import { textToKeystrokes, decompose } from '../utils/hangulDecompose'
import type { Keystroke } from '../types/keyboard'

/**
 * 한글 타이핑에서 키스트로크 큐와 소비 위치를 관리하는 훅
 *
 * 전략:
 * - targetText 전체를 키스트로크 배열로 변환 (캐시)
 * - 각 글자별 키스트로크 개수를 미리 계산
 * - userInput의 완성된 글자 수로 소비 위치를 결정
 *
 * 한글 IME 특성:
 * - 조합 중인 글자는 아직 "완성"되지 않음
 * - userInput.length에서 마지막 글자가 조합 중일 수 있음
 * - 간단 근사: 완성된 글자(userInput의 앞부분)의 키스트로크만 소비된 것으로 처리
 */
export function useHangulKeystrokeQueue(
  targetText: string,
  userInput: string,
  enabled: boolean,
): { keystrokeQueue: Keystroke[]; consumedKeystrokes: number } {
  // 키스트로크 큐 (targetText가 바뀔 때만 재계산)
  const keystrokeQueue = useMemo(() => {
    if (!enabled || !targetText) return []
    return textToKeystrokes(targetText)
  }, [targetText, enabled])

  // 글자별 키스트로크 수 누적 합 (targetText가 바뀔 때만 재계산)
  const charKeystrokeCumSum = useMemo(() => {
    if (!enabled || !targetText) return []
    const sums: number[] = []
    let total = 0
    for (const char of targetText) {
      const jamos = decompose(char)
      // decompose가 [char] 반환하면 영문/기호 → 1 키스트로크
      // 한글이면 자모 개수 = 키스트로크 개수
      const code = char.charCodeAt(0)
      if (code >= 0xAC00 && code <= 0xD7A3) {
        total += jamos.length
      } else if (char === ' ' || /[a-zA-Z0-9!@#$%^&*()\-=[\]{}\\|;:'",.<>/?`~_+]/.test(char)) {
        total += 1
      } else {
        // 기타 문자 (특수문자 등)
        total += 1
      }
      sums.push(total)
    }
    return sums
  }, [targetText, enabled])

  // 소비된 키스트로크 계산
  const consumedKeystrokes = useMemo(() => {
    if (!enabled || !userInput || charKeystrokeCumSum.length === 0) return 0

    // 완성된 글자 수 = userInput.length - 1 (마지막이 조합 중일 수 있으므로)
    // 하지만 정확히는: targetText와 비교하여 일치하는 글자까지의 키스트로크
    // 간단 근사: userInput에서 완전히 입력된 글자 수 기반

    const completedChars = userInput.length
    if (completedChars <= 0) return 0
    if (completedChars > charKeystrokeCumSum.length) {
      return charKeystrokeCumSum[charKeystrokeCumSum.length - 1] || 0
    }

    // 완성된 글자 수 - 1 (0-indexed) 까지의 누적 키스트로크
    return charKeystrokeCumSum[completedChars - 1] || 0
  }, [userInput, charKeystrokeCumSum, enabled])

  return { keystrokeQueue, consumedKeystrokes }
}
