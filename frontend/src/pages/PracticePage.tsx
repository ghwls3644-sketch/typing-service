import { useState, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import ModeSelector from '../components/Practice/ModeSelector'
import ModeSettings from '../components/Practice/ModeSettings'
import { useTypingEngine } from '../hooks/useTypingEngine'
import { DEFAULT_SETTINGS, type PracticeMode, type PracticeSettings, type TypingStats } from '../types/practice'
import { fetchPracticeItems } from '../lib/typingApi'
import './PracticePage.css'

// Fallback 데이터 (컴포넌트 외부 - 서버 연결 실패 시 사용)
const FALLBACK_DATA: Record<string, Record<string, string[]>> = {
  word: {
    korean: ['안녕', '반갑습니다', '타자연습', '키보드', '모니터', '컴퓨터', '프로그래밍', '개발자', '코딩', '알고리즘'],
    english: ['hello', 'world', 'keyboard', 'typing', 'practice', 'computer', 'programming', 'developer', 'coding', 'algorithm']
  },
  short: {
    korean: ['빠른 타자는 연습에서 나온다.', '정확한 타자가 빠른 타자보다 낫다.', '오늘도 열심히 연습하자!', '타자 연습은 꾸준함이 중요하다.', '손가락이 기억하는 타자를 목표로.'],
    english: ['The quick brown fox jumps over the lazy dog.', 'Practice makes perfect.', 'Typing is an essential skill.', 'Keep calm and type on.', 'Every expert was once a beginner.']
  }
}

type Phase = 'select' | 'practice'

function PracticePage() {
  const navigate = useNavigate()
  const inputRef = useRef<HTMLInputElement>(null)
  
  // 단계: select(모드 선택) -> practice(연습 중)
  const [phase, setPhase] = useState<Phase>('select')
  const [settings, setSettings] = useState<PracticeSettings>(DEFAULT_SETTINGS)
  
  // 아이템 큐 시스템
  const [itemQueue, setItemQueue] = useState<string[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [currentText, setCurrentText] = useState('')
  
  // 전체 세션 통계 (누적)
  const [sessionStats, setSessionStats] = useState<TypingStats>({
    wpm: 0, accuracy: 100, time: 0, correctChars: 0, totalChars: 0, errors: 0
  })
  const [allInputs, setAllInputs] = useState<string>('')
  
  // 서버 데이터 상태
  const [isLoading, setIsLoading] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)

  // 현재 아이템 완료 -> 다음으로 이동
  const handleItemComplete = useCallback((stats: TypingStats) => {
    // 누적 통계 업데이트
    setSessionStats(prev => ({
      wpm: Math.round((prev.wpm * currentIndex + stats.wpm) / (currentIndex + 1)),
      accuracy: Math.round((prev.accuracy * currentIndex + stats.accuracy) / (currentIndex + 1)),
      time: prev.time + stats.time,
      correctChars: prev.correctChars + stats.correctChars,
      totalChars: prev.totalChars + stats.totalChars,
      errors: prev.errors + stats.errors
    }))
    setAllInputs(prev => prev + (prev ? ' ' : '') + userInput)
    
    const nextIndex = currentIndex + 1
    
    // 모든 아이템 완료
    if (nextIndex >= itemQueue.length) {
      setTimeout(() => {
        const finalStats = {
          wpm: Math.round((sessionStats.wpm * currentIndex + stats.wpm) / (currentIndex + 1)),
          accuracy: Math.round((sessionStats.accuracy * currentIndex + stats.accuracy) / (currentIndex + 1)),
          time: sessionStats.time + stats.time,
          correctChars: sessionStats.correctChars + stats.correctChars,
          totalChars: sessionStats.totalChars + stats.totalChars,
          errors: sessionStats.errors + stats.errors
        }
        navigate('/result', {
          state: {
            stats: finalStats,
            text: itemQueue.join(settings.mode === 'word' ? ' ' : '\n'),
            userInput: allInputs + (allInputs ? ' ' : '') + userInput,
            language: settings.language,
            mode: settings.mode,
            settings
          }
        })
      }, 300)
      return
    }
    
    // 다음 아이템으로 이동
    setCurrentIndex(nextIndex)
    setCurrentText(itemQueue[nextIndex])
    reset()
    setTimeout(() => {
      if (inputRef.current) {
        inputRef.current.value = ''
        inputRef.current.focus()
      }
    }, 50)
  }, [currentIndex, itemQueue, navigate, settings, sessionStats, allInputs])

  // 타자 엔진 훅
  const {
    userInput,
    stats,
    isStarted,
    isFinished,
    handleInput,
    reset
  } = useTypingEngine({
    targetText: currentText,
    settings,
    onComplete: handleItemComplete
  })

  // Fallback 데이터 가져오기
  const getFallbackItems = () => {
    const mode = settings.mode === 'word' ? 'word' : 'short'
    const lang = settings.language === 'korean' ? 'korean' : 'english'
    const items = [...(FALLBACK_DATA[mode]?.[lang] || [])]
    console.log('[Fallback] mode:', mode, 'lang:', lang, 'items:', items.length)
    // 셔플
    return items.sort(() => Math.random() - 0.5).slice(0, settings.itemsPerSession || 10)
  }

  // 아이템으로 연습 시작
  const beginPractice = (items: string[], warningMessage?: string) => {
    if (warningMessage) {
      setServerError(warningMessage)
    } else {
      setServerError(null)
    }
    setItemQueue(items)
    setCurrentIndex(0)
    setCurrentText(items[0])
    setSessionStats({ wpm: 0, accuracy: 100, time: 0, correctChars: 0, totalChars: 0, errors: 0 })
    setAllInputs('')
    setPhase('practice')
    setIsLoading(false)
    reset()
    setTimeout(() => inputRef.current?.focus(), 100)
  }

  // 연습 시작 (서버에서 데이터 로드, 실패 시 fallback)
  const startPractice = async () => {
    setIsLoading(true)
    setServerError(null)
    
    // 먼저 fallback 데이터 준비
    const fallbackItems = getFallbackItems()
    
    try {
      const language = settings.language === 'korean' ? 'ko' : 'en'
      const response = await fetchPracticeItems(
        settings.mode,
        language,
        settings.difficulty,
        settings.itemsPerSession || 10
      )
      
      // 서버 응답이 있고 아이템이 있으면 사용
      if (response.items && response.items.length > 0) {
        beginPractice(response.items)
        return
      }
    } catch (err) {
      console.warn('서버 연결 실패, fallback 사용:', err)
    }
    
    // 서버 응답 없거나 실패 시 fallback 사용
    if (fallbackItems.length > 0) {
      beginPractice(fallbackItems, '기본 문장으로 연습합니다.')
    } else {
      setServerError('연습 데이터를 불러올 수 없습니다.')
      setIsLoading(false)
    }
  }

  // 모드 변경
  const handleModeChange = (mode: PracticeMode) => {
    setSettings(prev => ({ ...prev, mode }))
  }

  // 설정 변경
  const handleSettingsChange = (updates: Partial<PracticeSettings>) => {
    setSettings(prev => ({ ...prev, ...updates }))
  }

  // 다시 시작
  const handleRestart = () => {
    reset()
    inputRef.current?.focus()
  }

  // 다음 아이템으로 스킵
  const handleSkip = () => {
    const nextIndex = currentIndex + 1
    if (nextIndex < itemQueue.length) {
      setCurrentIndex(nextIndex)
      setCurrentText(itemQueue[nextIndex])
      reset()
      inputRef.current?.focus()
    } else {
      handleItemComplete(stats)
    }
  }

  // 모드 선택으로 돌아가기
  const handleBackToSelect = () => {
    setPhase('select')
    reset()
  }

  // 문자 렌더링
  const renderText = () => {
    return currentText.split('').map((char, index) => {
      let className = 'char'
      if (index < userInput.length) {
        className += userInput[index] === char ? ' correct' : ' incorrect'
      } else if (index === userInput.length) {
        className += ' current'
      }
      return (
        <span key={index} className={className}>
          {char}
        </span>
      )
    })
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  // 모드 이름 가져오기
  const getModeName = () => {
    return settings.mode === 'word' ? '단어 연습' : '짧은 글 연습'
  }

  // 난이도 이름 가져오기
  const getDifficultyName = () => {
    const names = { 1: '초급', 2: '중급', 3: '고급' }
    return names[settings.difficulty]
  }

  // 모드 선택 화면
  if (phase === 'select') {
    return (
      <div className="practice-page container">
        {/* 서버 상태 표시 */}
        {isLoading && (
          <div className="server-status loading">📡 서버 데이터 로딩 중...</div>
        )}
        {serverError && (
          <div className="server-status error">⚠️ {serverError}</div>
        )}
        
        <ModeSelector 
          selectedMode={settings.mode}
          onSelectMode={handleModeChange}
          onStartPractice={startPractice}
        />
        <ModeSettings
          mode={settings.mode}
          settings={settings}
          onSettingsChange={handleSettingsChange}
        />
      </div>
    )
  }

  // 연습 화면
  return (
    <div className="practice-page container">
      {/* 헤더 영역 */}
      <div className="practice-header">
        <button className="btn btn-ghost btn-back" onClick={handleBackToSelect}>
          ← 모드 선택
        </button>
        <h1>{getModeName()}</h1>
        <div className="mode-badge-header">
          {settings.language === 'korean' ? '🇰🇷 한글' : '🇺🇸 영어'} | {getDifficultyName()}
        </div>
      </div>

      {/* 진행 상황 */}
      <div className="progress-info">
        <span className="progress-current">{currentIndex + 1}</span>
        <span className="progress-separator">/</span>
        <span className="progress-total">{itemQueue.length}</span>
        <span className="progress-label">{settings.mode === 'word' ? '단어' : '문장'}</span>
      </div>

      {/* 통계 영역 */}
      <div className="stats-bar">
        <div className="stat-item">
          <span className="stat-label">WPM</span>
          <span className="stat-value">{stats.wpm}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">정확도</span>
          <span className="stat-value">{stats.accuracy}%</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">시간</span>
          <span className="stat-value">{formatTime(stats.time)}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">오류</span>
          <span className="stat-value">{stats.errors}</span>
        </div>
      </div>

      {/* 타이핑 영역 */}
      <div className="typing-area" onClick={() => inputRef.current?.focus()}>
        <div className="text-display">
          {renderText()}
        </div>
        <input
          ref={inputRef}
          type="text"
          className="typing-input"
          value={userInput}
          onChange={(e) => handleInput(e.target.value)}
          disabled={isFinished}
          placeholder={isStarted ? '' : '여기를 클릭하고 타이핑을 시작하세요'}
          autoFocus
          autoComplete="off"
          autoCapitalize="off"
          spellCheck="false"
        />
      </div>

      {/* 진행률 바 */}
      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${(userInput.length / currentText.length) * 100}%` }}
        />
      </div>

      {/* 액션 버튼 */}
      <div className="practice-actions">
        <button className="btn btn-secondary" onClick={handleRestart}>
          🔄 다시 시작
        </button>
        <button className="btn btn-primary" onClick={handleSkip}>
          ➡️ 다음 {settings.mode === 'word' ? '단어' : '문장'}
        </button>
      </div>

      {/* 도움말 */}
      <div className="help-text">
        <p>💡 정확하게 입력하면 글자가 <span className="text-success">초록색</span>으로,
          틀리면 <span className="text-error">빨간색</span>으로 표시됩니다.</p>
      </div>
    </div>
  )
}

export default PracticePage
