/**
 * 챌린지 게임 엔진 훅
 * 60초 타임어택 + 콤보 점수 시스템
 * 한글 IME 조합을 올바르게 처리
 */
import { useState, useCallback, useRef, useEffect } from 'react'
import type { ChallengeStats, ChallengePhase } from '../types/challenge'
import { calculateScoreForCorrect, CHALLENGE_PENALTY, CHALLENGE_DURATION_SEC } from '../types/challenge'

interface UseChallengeEngineProps {
  items: string[]
  onComplete?: (stats: ChallengeStats) => void
}

interface UseChallengeEngineReturn {
  phase: ChallengePhase
  currentText: string
  currentIndex: number
  userInput: string
  stats: ChallengeStats
  remainingTime: number
  isError: boolean
  charStatuses: ('correct' | 'incorrect' | 'pending')[]  // 각 글자 상태
  start: () => void
  handleInput: (value: string) => void
  handleCompositionEnd: () => void  // 한글 조합 완료 시 호출
  reset: () => void
  moveToNext: (finalInput?: string) => void
}

const INITIAL_STATS: ChallengeStats = {
  score: 0,
  combo: 0,
  maxCombo: 0,
  wpm: 0,
  accuracy: 100,
  correctChars: 0,
  totalInputs: 0,
  errors: 0,
  errorLog: []
}

export function useChallengeEngine({
  items,
  onComplete
}: UseChallengeEngineProps): UseChallengeEngineReturn {
  const [phase, setPhase] = useState<ChallengePhase>('ready')
  const [currentIndex, setCurrentIndex] = useState(0)
  const [userInput, setUserInput] = useState('')
  const [charStatuses, setCharStatuses] = useState<('correct' | 'incorrect' | 'pending')[]>([])
  const [stats, setStats] = useState<ChallengeStats>(INITIAL_STATS)
  const [remainingTime, setRemainingTime] = useState(CHALLENGE_DURATION_SEC)
  const [isError, setIsError] = useState(false)
  
  const startTimeRef = useRef<number | null>(null)
  const timerRef = useRef<number | null>(null)
  const isComposingRef = useRef(false)
  const errorTimeoutRef = useRef<number | null>(null)
  const verifiedLengthRef = useRef(0)  // 검증 완료된 글자 수

  const currentText = items[currentIndex] || ''
  
  // 게임 종료 처리
  const finishGame = useCallback(() => {
    setPhase('finished')
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
  }, [])
  
  // 게임 종료 체크 (Timer Effect)
  useEffect(() => {
    if (phase === 'running' && remainingTime <= 0) {
      finishGame()
    }
  }, [phase, remainingTime, finishGame])

  // 게임 종료 시 onComplete 호출
  useEffect(() => {
    if (phase === 'finished' && onComplete) {
      onComplete(stats)
    }
  }, [phase])

  // 타이머 시작
  const start = useCallback(() => {
    if (phase !== 'ready' || items.length === 0) return
    
    setPhase('running')
    startTimeRef.current = Date.now()
    setRemainingTime(CHALLENGE_DURATION_SEC)
    verifiedLengthRef.current = 0
    setCharStatuses([])
    
    // 기존 타이머 제거
    if (timerRef.current) clearInterval(timerRef.current)

    timerRef.current = window.setInterval(() => {
      const elapsed = (Date.now() - (startTimeRef.current || Date.now())) / 1000
      const remaining = Math.max(0, CHALLENGE_DURATION_SEC - elapsed)
      setRemainingTime(remaining)
      
      // setInterval에서는 state update만 하고, 종료 체크는 useEffect에서 함
    }, 100)
  }, [phase, items.length])
  
  // 다음 텍스트로 이동
  const moveToNext = useCallback((finalInput?: string) => {
    // 오답 기록 (단어 단위)
    if (finalInput) {
      if (finalInput !== items[currentIndex]) {
        setStats(prev => ({
          ...prev,
          errorLog: [
            ...prev.errorLog,
            {
              word: items[currentIndex],
              typed: finalInput
            }
          ]
        }))
      }
    }

    const nextIndex = currentIndex + 1
    if (nextIndex >= items.length) {
      setCurrentIndex(0)
    } else {
      setCurrentIndex(nextIndex)
    }
    setUserInput('')
    setCharStatuses([])
    verifiedLengthRef.current = 0
  }, [currentIndex, items])
  
  // 글자 상태 업데이트 (시각적 피드백용)
  const updateCharStatuses = useCallback((value: string, isComposing: boolean) => {
    const statuses: ('correct' | 'incorrect' | 'pending')[] = []
    const checkLength = isComposing ? value.length - 1 : value.length
    
    for (let i = 0; i < value.length; i++) {
      if (i < checkLength) {
        // 확정된 글자: 정확/오류 판정
        statuses.push(value[i] === currentText[i] ? 'correct' : 'incorrect')
      } else {
        // 조합 중인 글자
        statuses.push('pending')
      }
    }
    
    setCharStatuses(statuses)
  }, [currentText])
  
  // 점수 처리 (확정된 새 글자에 대해)
  const processNewChars = useCallback((value: string, fromIndex: number) => {
    for (let i = fromIndex; i < value.length; i++) {
      const inputChar = value[i]
      const expectedChar = currentText[i]
      
      if (inputChar === expectedChar) {
        // 정답
        setStats(prev => {
          const newCombo = prev.combo + 1
          const scoreGain = calculateScoreForCorrect(prev.combo)
          const newCorrect = prev.correctChars + 1
          const newTotal = prev.totalInputs + 1
          const elapsed = startTimeRef.current ? (Date.now() - startTimeRef.current) / 1000 : 1
          const minutes = elapsed / 60
          
          return {
            ...prev,
            score: prev.score + scoreGain,
            combo: newCombo,
            maxCombo: Math.max(prev.maxCombo, newCombo),
            correctChars: newCorrect,
            totalInputs: newTotal,
            accuracy: Math.round((newCorrect / newTotal) * 100),
            wpm: minutes > 0 ? Math.round((newCorrect / 5) / minutes) : 0
          }
        })
      } else {
        // 오답
        setStats(prev => {
          const newTotal = prev.totalInputs + 1
          const newErrors = prev.errors + 1
          
          return {
            ...prev,
            score: Math.max(0, prev.score - CHALLENGE_PENALTY),
            combo: 0,
            errors: newErrors,
            totalInputs: newTotal,
            accuracy: Math.round((prev.correctChars / newTotal) * 100)
            // errorLog는 단어 완료 시 기록함
          }
        })
        
        // 오타 이펙트 (120ms)
        setIsError(true)
        if (errorTimeoutRef.current) {
          clearTimeout(errorTimeoutRef.current)
        }
        errorTimeoutRef.current = window.setTimeout(() => {
          setIsError(false)
        }, 120)
      }
    }
    
    verifiedLengthRef.current = value.length
  }, [currentText])
  
  // 입력 처리 (매 입력마다 호출)
  const handleInput = useCallback((value: string) => {
    if (phase !== 'running') return
    
    // 변경된 지점 찾기 (공통 접두사 길이 계산)
    let commonLength = 0
    const minLength = Math.min(userInput.length, value.length)
    for (let i = 0; i < minLength; i++) {
      if (userInput[i] === value[i]) {
        commonLength++
      } else {
        break
      }
    }
    
    // 검증된 구간 내에서 변경이 발생했다면, 검증 길이를 축소
    if (commonLength < verifiedLengthRef.current) {
      verifiedLengthRef.current = commonLength
    }

    setUserInput(value)
    updateCharStatuses(value, isComposingRef.current)
    
    // 조합 중이면 점수 처리 보류
    if (isComposingRef.current) {
      return
    }
    
    // 백스페이스 등으로 검증된 길이보다 짧아진 경우 (이미 위에서 verifiedLengthRef 업데이트됨)
    if (value.length <= verifiedLengthRef.current) {
      return
    }
    
    // 새로 확정된 글자들 점수 처리
    if (value.length > verifiedLengthRef.current) {
      processNewChars(value, verifiedLengthRef.current)
    }
    
    // 텍스트 완료 체크
    if (value.length >= currentText.length) {
      moveToNext(value)
    }
  }, [phase, currentText, updateCharStatuses, processNewChars, moveToNext, userInput])
  
  // 한글 조합 완료 시 호출
  const handleCompositionEnd = useCallback(() => {
    isComposingRef.current = false
    
    // 조합이 끝났으므로 마지막 글자까지 확정 처리
    if (userInput.length > verifiedLengthRef.current) {
      processNewChars(userInput, verifiedLengthRef.current)
      updateCharStatuses(userInput, false)
    }
    
    // 텍스트 완료 체크
    if (userInput.length >= currentText.length) {
      moveToNext(userInput)
    }
  }, [userInput, currentText, processNewChars, updateCharStatuses, moveToNext])
  
  // 리셋
  const reset = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
    if (errorTimeoutRef.current) {
      clearTimeout(errorTimeoutRef.current)
      errorTimeoutRef.current = null
    }
    
    setPhase('ready')
    setCurrentIndex(0)
    setUserInput('')
    setCharStatuses([])
    setStats(INITIAL_STATS)
    setRemainingTime(CHALLENGE_DURATION_SEC)
    setIsError(false)
    verifiedLengthRef.current = 0
    startTimeRef.current = null
  }, [])
  
  // 컴포넌트 언마운트 시 정리
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
      if (errorTimeoutRef.current) clearTimeout(errorTimeoutRef.current)
    }
  }, [])
  
  // composition 이벤트 핸들러
  useEffect(() => {
    const handleCompositionStart = () => {
      isComposingRef.current = true
    }
    
    window.addEventListener('compositionstart', handleCompositionStart)
    
    return () => {
      window.removeEventListener('compositionstart', handleCompositionStart)
    }
  }, [])
  
  return {
    phase,
    currentText,
    currentIndex,
    userInput,
    stats,
    remainingTime,
    isError,
    charStatuses,
    start,
    handleInput,
    handleCompositionEnd,
    reset,
    moveToNext
  }
}
