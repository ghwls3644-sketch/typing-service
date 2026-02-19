import { useState, useEffect, useCallback } from 'react'

/**
 * 물리 키 입력 감지 훅
 * keydown/keyup 이벤트를 통해 현재 눌린 키 Set 관리
 */
export function useKeyPress(enabled: boolean = true): Set<string> {
  const [pressedKeys, setPressedKeys] = useState<Set<string>>(new Set())

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    setPressedKeys(prev => {
      if (prev.has(e.code)) return prev
      const next = new Set(prev)
      next.add(e.code)
      return next
    })
  }, [])

  const handleKeyUp = useCallback((e: KeyboardEvent) => {
    setPressedKeys(prev => {
      if (!prev.has(e.code)) return prev
      const next = new Set(prev)
      next.delete(e.code)
      return next
    })
  }, [])

  // 포커스 잃으면 모두 해제
  const handleBlur = useCallback(() => {
    setPressedKeys(new Set())
  }, [])

  useEffect(() => {
    if (!enabled) {
      setPressedKeys(new Set())
      return
    }

    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('keyup', handleKeyUp)
    window.addEventListener('blur', handleBlur)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('keyup', handleKeyUp)
      window.removeEventListener('blur', handleBlur)
    }
  }, [enabled, handleKeyDown, handleKeyUp, handleBlur])

  return pressedKeys
}
