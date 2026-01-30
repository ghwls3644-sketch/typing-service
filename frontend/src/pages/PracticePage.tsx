import { useState, useCallback, useRef, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import ModeSelector from '../components/Practice/ModeSelector'
import ModeSettings from '../components/Practice/ModeSettings'
import { useTypingEngine } from '../hooks/useTypingEngine'
import { DEFAULT_SETTINGS, type PracticeMode, type PracticeSettings, type TypingStats } from '../types/practice'
import { fetchTextItems, type TextItem } from '../lib/typingApi'
import './PracticePage.css'

// 약점 훈련용 타입
interface ErrorAnalysisItem {
  char: string
  expected: string
  count: number
}

// 샘플 문장 데이터
const sampleTexts = {
  korean: {
    sentences: [
      '하늘 아래 첫 동네에 봄이 찾아왔다.',
      '빠른 갈색 여우가 게으른 개를 뛰어넘는다.',
      '오늘도 좋은 하루가 되기를 바랍니다.',
      '타자 연습은 꾸준히 하면 실력이 늘어납니다.',
      '컴퓨터 자판을 익히면 업무 효율이 올라갑니다.',
      '매일 조금씩 연습하면 어느새 달인이 됩니다.',
      '키보드를 보지 않고 치는 것이 목표입니다.',
      '정확하게 치는 것이 빠르게 치는 것보다 중요합니다.',
    ],
    words: [
      '안녕', '컴퓨터', '키보드', '마우스', '프로그램', '개발자', '소프트웨어', '하드웨어',
      '인터넷', '네트워크', '데이터', '알고리즘', '변수', '함수', '객체', '클래스',
      '배열', '반복문', '조건문', '라이브러리', '프레임워크', '서버', '클라이언트', '데이터베이스'
    ],
    drills: {
      batchim: [
        '각 간 갈 감 갑 강 같 갔',
        '먹 먼 멀 멈 멉 멍 멋 먼저',
        '작 잔 잘 잠 잡 장 잣 잔디',
        '국 군 굴 굼 굽 궁 궂 국물',
        '독 돈 돌 돔 돕 동 돗 독서',
        '북 분 불 붐 붑 붕 붓 북쪽',
      ],
      doubleConsonant: [
        '닭 삶 값 없 읽 넓 짧 앓',
        '삶은 닭을 먹었다',
        '값이 없는 물건은 넓고 짧다',
        '젊은 시절을 읽다',
        '늙은 나무가 굵다',
        '맑은 하늘 아래 밝게 웃다',
      ],
      spacing: [
        '나는 학교에 간다',
        '오늘 날씨가 좋다',
        '열심히 공부를 한다',
        '맛있는 음식을 먹는다',
        '친구와 함께 놀았다',
        '내일은 더 나을 것이다',
      ],
      similar: [
        '바빠 바빠 빠빠 빠빠',
        '사싸 사싸 싸사 싸사',
        '자짜 자짜 짜자 짜자',
        '다따 다따 따다 따다',
        '가까 가까 까가 까가',
      ]
    }
  },
  english: {
    sentences: [
      'The quick brown fox jumps over the lazy dog.',
      'Practice makes perfect in everything we do.',
      'Typing skills improve with consistent practice.',
      'Hello world, this is a typing practice app.',
      'Learning to type fast requires patience and dedication.',
      'Keep your fingers on the home row keys.',
      'Speed will come naturally with accuracy first.',
      'Every expert was once a beginner at typing.',
    ],
    words: [
      'hello', 'world', 'computer', 'keyboard', 'mouse', 'program', 'developer', 'software',
      'internet', 'network', 'data', 'algorithm', 'variable', 'function', 'object', 'class',
      'array', 'loop', 'condition', 'library', 'framework', 'server', 'client', 'database'
    ]
  }
}

type Phase = 'select' | 'practice'

function PracticePage() {
  const navigate = useNavigate()
  const location = useLocation()
  const inputRef = useRef<HTMLInputElement>(null)
  
  // 단계: select(모드 선택) -> practice(연습 중)
  const [phase, setPhase] = useState<Phase>('select')
  const [settings, setSettings] = useState<PracticeSettings>(DEFAULT_SETTINGS)
  
  // 약점 훈련용 에러 데이터 (ResultPage에서 전달)
  const [focusErrors, setFocusErrors] = useState<ErrorAnalysisItem[]>([])
  
  // location state에서 약점 정보 수신
  useEffect(() => {
    const state = location.state as { mode?: PracticeMode; focusErrors?: ErrorAnalysisItem[] } | null
    if (state?.mode === 'weakness_drill' && state?.focusErrors) {
      setFocusErrors(state.focusErrors)
      setSettings(prev => ({ ...prev, mode: 'weakness_drill' }))
    }
  }, [location.state])
  
  // 아이템 큐 시스템 (문장/단어를 순차적으로 진행)
  const [itemQueue, setItemQueue] = useState<string[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [currentText, setCurrentText] = useState('')
  
  // 전체 세션 통계 (누적)
  const [sessionStats, setSessionStats] = useState<TypingStats>({
    wpm: 0, accuracy: 100, time: 0, correctChars: 0, totalChars: 0, errors: 0
  })
  const [allInputs, setAllInputs] = useState<string>('')
  
  // 서버 데이터 상태
  const [serverItems, setServerItems] = useState<TextItem[]>([])
  const [isLoadingItems, setIsLoadingItems] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)
  
  // 서버에서 텍스트 데이터 로드
  useEffect(() => {
    const loadTextItems = async () => {
      setIsLoadingItems(true)
      setServerError(null)
      try {
        const language = settings.language === 'korean' ? 'ko' : 'en'
        const items = await fetchTextItems(undefined, language)
        setServerItems(items)
      } catch (err) {
        console.warn('Failed to load server texts, using fallback data:', err)
        setServerError('서버 데이터 로드 실패, 기본 데이터를 사용합니다.')
      } finally {
        setIsLoadingItems(false)
      }
    }
    loadTextItems()
  }, [settings.language])

  // 아이템 큐 생성 (서버 데이터 우선, 실패 시 Mock 사용)
  const createItemQueue = useCallback((): string[] => {
    const lang = settings.language
    const mode = settings.mode
    const count = settings.itemsPerSession || 5
    
    // 약점 훈련 모드: 에러 패턴 기반 문장 생성
    if (mode === 'weakness_drill' && focusErrors.length > 0) {
      // 약점 문자들을 포함한 훈련 문장 생성
      const weakChars = focusErrors.map(e => e.expected)
      const allSentences = lang === 'korean' ? sampleTexts.korean.sentences : sampleTexts.english.sentences
      
      // 약점 문자가 포함된 문장 우선 선택
      const prioritized = allSentences.filter(s => 
        weakChars.some(char => s.includes(char))
      )
      
      // 추가 훈련용: 약점 문자 반복 패턴
      const drillPatterns = weakChars.map(char => 
        `${char} ${char} ${char} ${char} ${char}`
      )
      
      const combined = [...drillPatterns, ...prioritized]
      const shuffled = [...combined].sort(() => Math.random() - 0.5)
      return shuffled.slice(0, count)
    }
    
    // 서버 데이터가 있으면 우선 사용 (문장 모드)
    if (serverItems.length > 0 && (mode === 'sentence' || mode === 'time_attack' || mode === 'accuracy_challenge')) {
      const contents = serverItems.map(item => item.content)
      const shuffled = [...contents].sort(() => Math.random() - 0.5)
      return shuffled.slice(0, count)
    }
    
    // 한글 드릴 모드 (Mock 데이터 사용 - 특수 패턴)
    if (mode === 'kor_drill' && lang === 'korean') {
      const drills = sampleTexts.korean.drills
      const allDrills = [
        ...drills.batchim,
        ...drills.doubleConsonant,
        ...drills.spacing,
        ...drills.similar
      ]
      const shuffled = [...allDrills].sort(() => Math.random() - 0.5)
      return shuffled.slice(0, count)
    }
    
    // 단어 모드 - Mock 데이터 사용
    if (mode === 'word') {
      const words = sampleTexts[lang].words
      const shuffled = [...words].sort(() => Math.random() - 0.5)
      return shuffled.slice(0, count)
    }
    
    // Fallback: 문장 모드 (Mock 데이터)
    const sentences = sampleTexts[lang].sentences
    const shuffled = [...sentences].sort(() => Math.random() - 0.5)
    return shuffled.slice(0, count)
  }, [settings, serverItems, focusErrors])

  // 현재 아이템 완료 -> 다음으로 이동
  const handleItemComplete = useCallback((stats: TypingStats, _reason?: string) => {
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
      // 결과 페이지로 이동
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
            settings,
            metadata: {
              submode: settings.mode,
              settings: {
                timeLimitSec: settings.timeLimitSec,
                maxErrors: settings.maxErrors,
                itemsPerSession: settings.itemsPerSession
              },
              result_extra: {
                fail_reason: null
              }
            }
          }
        })
      }, 300)
      return
    }
    
    // 다음 아이템으로 이동
    setCurrentIndex(nextIndex)
    setCurrentText(itemQueue[nextIndex])
    reset()
    // 입력 필드 값을 명시적으로 클리어
    setTimeout(() => {
      if (inputRef.current) {
        inputRef.current.value = ''
        inputRef.current.focus()
      }
    }, 50)
  }, [currentIndex, itemQueue, navigate, settings, sessionStats, allInputs])

  // 타임어택/정확도 챌린지용 완료 핸들러
  const handleTimeBasedComplete = useCallback((stats: TypingStats, reason?: string) => {
    setTimeout(() => {
      navigate('/result', {
        state: {
          stats,
          text: currentText,
          userInput,
          language: settings.language,
          mode: settings.mode,
          settings,
          metadata: {
            submode: settings.mode,
            settings: {
              timeLimitSec: settings.timeLimitSec,
              maxErrors: settings.maxErrors,
              itemsPerSession: settings.itemsPerSession
            },
            result_extra: {
              fail_reason: reason === 'completed' ? null : reason
            }
          }
        }
      })
    }, 500)
  }, [navigate, currentText, settings])

  // 모드에 따른 완료 핸들러 선택
  const onComplete = settings.mode === 'time_attack' || settings.mode === 'accuracy_challenge'
    ? handleTimeBasedComplete
    : handleItemComplete

  // 타자 엔진 훅
  const {
    userInput,
    stats,
    isStarted,
    isFinished,
    remainingTime,
    handleInput,
    reset
  } = useTypingEngine({
    targetText: currentText,
    settings,
    onComplete
  })

  // 연습 시작
  const startPractice = useCallback(() => {
    const queue = createItemQueue()
    setItemQueue(queue)
    setCurrentIndex(0)
    setCurrentText(queue[0] || '')
    setSessionStats({ wpm: 0, accuracy: 100, time: 0, correctChars: 0, totalChars: 0, errors: 0 })
    setAllInputs('')
    setPhase('practice')
    reset()
    setTimeout(() => inputRef.current?.focus(), 100)
  }, [createItemQueue, reset])

  // 모드 변경
  const handleModeChange = (mode: PracticeMode) => {
    // 한글 특화 드릴은 한글만 사용
    if (mode === 'kor_drill') {
      setSettings(prev => ({ ...prev, mode, language: 'korean' }))
    } else {
      setSettings(prev => ({ ...prev, mode }))
    }
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
      // 모든 아이템 완료 시 결과 페이지로
      handleItemComplete(stats, 'completed')
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
    const names: Record<PracticeMode, string> = {
      sentence: '문장 연습',
      word: '단어 연습',
      time_attack: '타임어택',
      accuracy_challenge: '정확도 챌린지',
      kor_drill: '한글 드릴',
      weakness_drill: '약점 훈련'
    }
    return names[settings.mode]
  }

  // 모드 선택 화면
  if (phase === 'select') {
    return (
      <div className="practice-page container">
        {/* 서버 상태 표시 */}
        {isLoadingItems && (
          <div className="server-status loading">📡 서버 데이터 로딩 중...</div>
        )}
        {serverError && (
          <div className="server-status error">⚠️ {serverError}</div>
        )}
        {serverItems.length > 0 && !isLoadingItems && (
          <div className="server-status success">✅ 서버 데이터 연결됨 ({serverItems.length}개 문장)</div>
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
          {settings.language === 'korean' ? '🇰🇷 한글' : '🇺🇸 영어'}
        </div>
      </div>

      {/* 진행 상황 (문장/단어 모드) */}
      {(settings.mode === 'sentence' || settings.mode === 'word' || settings.mode === 'kor_drill') && (
        <div className="progress-info">
          <span className="progress-current">{currentIndex + 1}</span>
          <span className="progress-separator">/</span>
          <span className="progress-total">{itemQueue.length}</span>
          <span className="progress-label">{settings.mode === 'word' ? '단어' : '문장'}</span>
        </div>
      )}

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
        {settings.mode === 'time_attack' && remainingTime !== null ? (
          <div className="stat-item timer">
            <span className="stat-label">남은 시간</span>
            <span className={`stat-value ${remainingTime <= 10 ? 'warning' : ''}`}>
              {formatTime(remainingTime)}
            </span>
          </div>
        ) : (
          <div className="stat-item">
            <span className="stat-label">시간</span>
            <span className="stat-value">{formatTime(stats.time)}</span>
          </div>
        )}
        <div className="stat-item">
          <span className="stat-label">오류</span>
          <span className={`stat-value ${settings.mode === 'accuracy_challenge' ? 'error' : ''}`}>
            {stats.errors}
            {settings.mode === 'accuracy_challenge' && `/${settings.maxErrors}`}
          </span>
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
        {(settings.mode === 'sentence' || settings.mode === 'word' || settings.mode === 'kor_drill') && (
          <button className="btn btn-primary" onClick={handleSkip}>
            ➡️ 다음 {settings.mode === 'word' ? '단어' : '문장'}
          </button>
        )}
      </div>

      {/* 도움말 */}
      <div className="help-text">
        <p>💡 정확하게 입력하면 글자가 <span className="text-success">초록색</span>으로,
          틀리면 <span className="text-error">빨간색</span>으로 표시됩니다.</p>
        {settings.mode === 'time_attack' && (
          <p>⏱️ 제한 시간 내에 최대한 많이 입력하세요!</p>
        )}
        {settings.mode === 'accuracy_challenge' && (
          <p>🎯 오타 {settings.maxErrors}회 초과 시 종료됩니다!</p>
        )}
      </div>
    </div>
  )
}

export default PracticePage
