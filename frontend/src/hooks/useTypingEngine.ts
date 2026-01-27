import { useState, useCallback, useRef, useEffect } from 'react'
import type { TypingStats, PracticeSettings } from '../types/practice'

interface UseTypingEngineProps {
  targetText: string
  settings: PracticeSettings
  onComplete?: (stats: TypingStats, reason?: string) => void
}

interface UseTypingEngineReturn {
  userInput: string
  stats: TypingStats
  isStarted: boolean
  isFinished: boolean
  remainingTime: number | null
  handleInput: (value: string) => void
  reset: () => void
  inputRef: React.RefObject<HTMLInputElement>
}

export function useTypingEngine({
  targetText,
  settings,
  onComplete
}: UseTypingEngineProps): UseTypingEngineReturn {
  const inputRef = useRef<HTMLInputElement>(null)
  
  const [userInput, setUserInput] = useState('')
  const [isStarted, setIsStarted] = useState(false)
  const [isFinished, setIsFinished] = useState(false)
  const [startTime, setStartTime] = useState<number | null>(null)
  const [remainingTime, setRemainingTime] = useState<number | null>(
    settings.mode === 'time_attack' ? settings.timeLimitSec ?? 60 : null
  )
  
  const [stats, setStats] = useState<TypingStats>({
    wpm: 0,
    accuracy: 100,
    time: 0,
    correctChars: 0,
    totalChars: 0,
    errors: 0
  })

  // 통계 계산
  const calculateStats = useCallback((value: string, elapsed: number): TypingStats => {
    let correct = 0
    let errors = 0
    
    for (let i = 0; i < value.length; i++) {
      if (value[i] === targetText[i]) {
        correct++
      } else {
        errors++
      }
    }
    
    const accuracy = value.length > 0 ? Math.round((correct / value.length) * 100) : 100
    const minutes = elapsed / 60
    const wordsTyped = value.trim().split(/\s+/).filter(w => w).length
    const wpm = minutes > 0 ? Math.round(wordsTyped / minutes) : 0
    
    return {
      wpm,
      accuracy,
      time: elapsed,
      correctChars: correct,
      totalChars: value.length,
      errors
    }
  }, [targetText])

  // 완료 처리
  const finishPractice = useCallback((reason?: string) => {
    if (isFinished) return
    
    setIsFinished(true)
    const endTime = Date.now()
    const totalTime = startTime ? (endTime - startTime) / 1000 : 0
    const finalStats = calculateStats(userInput, totalTime)
    
    setStats(finalStats)
    onComplete?.(finalStats, reason)
  }, [isFinished, startTime, userInput, calculateStats, onComplete])

  // 타이머 (타임어택/실시간 통계)
  useEffect(() => {
    let interval: number | undefined

    if (isStarted && !isFinished && startTime) {
      interval = window.setInterval(() => {
        const elapsed = (Date.now() - startTime) / 1000
        
        // 타임어택: 남은 시간 계산
        if (settings.mode === 'time_attack' && settings.timeLimitSec) {
          const remaining = settings.timeLimitSec - elapsed
          setRemainingTime(Math.max(0, remaining))
          
          if (remaining <= 0) {
            finishPractice('time_up')
            return
          }
        }
        
        // 실시간 통계 업데이트
        const currentStats = calculateStats(userInput, elapsed)
        setStats(currentStats)
      }, 100)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [isStarted, isFinished, startTime, userInput, settings, calculateStats, finishPractice])

  // 입력 처리
  const handleInput = useCallback((value: string) => {
    if (isFinished) return
    
    // 첫 입력 시 시작
    if (!isStarted && value.length > 0) {
      setIsStarted(true)
      setStartTime(Date.now())
    }
    
    setUserInput(value)
    
    // 통계 계산
    const elapsed = startTime ? (Date.now() - startTime) / 1000 : 0
    const currentStats = calculateStats(value, elapsed)
    setStats(currentStats)
    
    // 정확도 챌린지: 오타 제한 체크
    if (settings.mode === 'accuracy_challenge') {
      if (settings.maxErrors && currentStats.errors >= settings.maxErrors) {
        finishPractice('max_errors')
        return
      }
      if (settings.minAccuracy && currentStats.accuracy < settings.minAccuracy && value.length > 10) {
        finishPractice('min_accuracy')
        return
      }
    }
    
    // 완료 체크
    // 단어 모드: 단어 길이를 채운 후 다음 입력이 들어오면 자동 완료
    if (settings.mode === 'word' && value.length > targetText.length) {
      finishPractice('completed')
      return
    }
    
    // 문장/드릴 모드: 정확히 일치해야 완료 (단어 모드 제외)
    if (settings.mode !== 'word' && value === targetText) {
      finishPractice('completed')
    }
  }, [isFinished, isStarted, startTime, targetText, settings, calculateStats, finishPractice])

  // 리셋
  const reset = useCallback(() => {
    setUserInput('')
    setIsStarted(false)
    setIsFinished(false)
    setStartTime(null)
    setRemainingTime(settings.mode === 'time_attack' ? settings.timeLimitSec ?? 60 : null)
    setStats({
      wpm: 0,
      accuracy: 100,
      time: 0,
      correctChars: 0,
      totalChars: 0,
      errors: 0
    })
  }, [settings])

  return {
    userInput,
    stats,
    isStarted,
    isFinished,
    remainingTime,
    handleInput,
    reset,
    inputRef
  }
}
