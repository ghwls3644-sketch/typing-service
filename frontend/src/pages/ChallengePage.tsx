import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useChallengeEngine } from '../hooks/useChallengeEngine'
import { saveChallengeResult, getChallengeBest } from '../lib/challengeStorage'
import type { ChallengeStats, ChallengeBest } from '../types/challenge'
import { CHALLENGE_DURATION_SEC } from '../types/challenge'
import { fetchPracticeItems } from '../lib/typingApi'
import './ChallengePage.css'

// Fallback 단어들 (서버 로딩 실패 시)
const FALLBACK_WORDS = [
  '안녕', '반갑습니다', '타자연습', '키보드', '모니터', '컴퓨터', '프로그래밍',
  '개발자', '코딩', '알고리즘', '데이터', '인터넷', '소프트웨어', '하드웨어',
  '네트워크', '서버', '클라이언트', '데이터베이스', '프론트엔드', '백엔드'
]

function ChallengePage() {
  const navigate = useNavigate()
  const inputRef = useRef<HTMLInputElement>(null)
  
  // 콘텐츠 로딩 상태
  const [items, setItems] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  
  // 최고기록
  const [best, setBest] = useState<ChallengeBest | null>(null)
  
  // 챌린지 엔진
  const handleComplete = useCallback((stats: ChallengeStats) => {
    // 결과 저장
    saveChallengeResult(stats, CHALLENGE_DURATION_SEC * 1000)
    
    // 결과 페이지로 이동
    navigate('/result', {
      state: {
        resultType: 'challenge',
        stats,
        durationMs: CHALLENGE_DURATION_SEC * 1000
      }
    })
  }, [navigate])
  
  const {
    phase,
    currentText,
    userInput,
    stats,
    remainingTime,
    isError,
    charStatuses,
    start,
    handleInput,
    handleCompositionEnd,
    reset
  } = useChallengeEngine({
    items,
    onComplete: handleComplete
  })
  
  // 콘텐츠 로딩
  useEffect(() => {
    const loadItems = async () => {
      setIsLoading(true)
      setLoadError(null)
      
      try {
        // 서버에서 단어 로딩 (난이도 2, 한글, 200개)
        const response = await fetchPracticeItems('word', 'ko', 2, 200)
        
        if (response.items.length > 0) {
          // 셔플
          const shuffled = [...response.items].sort(() => Math.random() - 0.5)
          setItems(shuffled)
        } else {
          // Fallback
          setItems([...FALLBACK_WORDS].sort(() => Math.random() - 0.5))
        }
      } catch (err) {
        console.warn('게임 콘텐츠 로딩 실패, fallback 사용:', err)
        setItems([...FALLBACK_WORDS].sort(() => Math.random() - 0.5))
        setLoadError('서버 연결 실패 - 기본 단어로 진행합니다')
      } finally {
        setIsLoading(false)
      }
    }
    
    loadItems()
    
    // 최고기록 로딩
    setBest(getChallengeBest())
  }, [])
  
  // Start 클릭 핸들러
  const handleStart = () => {
    start()
    setTimeout(() => {
      inputRef.current?.focus()
    }, 50)
  }
  
  // 다시하기
  const handleRetry = () => {
    reset()
    setBest(getChallengeBest()) // 최고기록 갱신
  }
  
  // 텍스트 렌더링 (각 글자별 상태 표시)
  const renderText = () => {
    return (
      <>
        {currentText.split('').map((char, i) => {
          let className = 'text-rest'
          
          if (i < userInput.length) {
            // 사용자가 입력한 글자
            const status = charStatuses[i]
            if (status === 'correct') {
              className = 'text-correct'
            } else if (status === 'incorrect') {
              className = 'text-incorrect'
            } else {
              className = 'text-pending'  // 조합 중
            }
          } else if (i === userInput.length) {
            // 현재 입력해야 할 글자
            className = 'text-current'
          }
          
          return (
            <span key={i} className={className}>{char}</span>
          )
        })}
      </>
    )
  }
  
  // 시간 포맷
  const formatTime = (seconds: number) => {
    const s = Math.ceil(seconds)
    return `${s}초`
  }
  
  // 로딩 중
  if (isLoading) {
    return (
      <div className="challenge-page container">
        <div className="loading">
          <div className="loading-spinner"></div>
          <span>게임 준비 중...</span>
        </div>
      </div>
    )
  }
  
  // Ready 화면
  if (phase === 'ready') {
    return (
      <div className="challenge-page container">
        <div className="challenge-ready">
          <div className="challenge-icon">🔥</div>
          <h1 className="challenge-title">60초 챌린지</h1>
          <p className="challenge-rule">
            60초 동안 최대한 정확하게 타이핑하세요!<br/>
            콤보를 쌓으면 점수가 올라갑니다.
          </p>
          
          {loadError && (
            <div className="load-error">{loadError}</div>
          )}
          
          {best && (
            <div className="best-record">
              <span className="best-label">🏆 최고기록</span>
              <span className="best-score">{best.bestScore}점</span>
              <span className="best-combo">최대 {best.bestMaxCombo}콤보</span>
            </div>
          )}
          
          <button className="btn btn-primary btn-lg start-btn" onClick={handleStart}>
            🚀 시작하기
          </button>
          
          <div className="challenge-tips">
            <h4>💡 팁</h4>
            <ul>
              <li>정확하게 입력하면 콤보가 쌓입니다</li>
              <li>20콤보마다 점수 배율이 올라갑니다 (최대 2배)</li>
              <li>오타 시 -5점, 콤보 초기화</li>
            </ul>
          </div>
        </div>
      </div>
    )
  }
  
  // Running 화면
  return (
    <div className={`challenge-page container ${isError ? 'error-shake' : ''}`}>
      {/* HUD */}
      <div className="challenge-hud">
        <div className="hud-item hud-time">
          <span className="hud-label">⏱️ 남은 시간</span>
          <span className={`hud-value ${remainingTime <= 10 ? 'warning' : ''}`}>
            {formatTime(remainingTime)}
          </span>
        </div>
        <div className="hud-item hud-score">
          <span className="hud-label">🏆 점수</span>
          <span className="hud-value">{stats.score}</span>
        </div>
        <div className="hud-item hud-combo">
          <span className="hud-label">🔥 콤보</span>
          <span className={`hud-value ${stats.combo >= 20 ? 'combo-high' : ''}`}>
            {stats.combo}
          </span>
        </div>
        <div className="hud-item hud-max-combo">
          <span className="hud-label">⭐ 최대콤보</span>
          <span className="hud-value">{stats.maxCombo}</span>
        </div>
      </div>
      
      {/* 텍스트 표시 영역 */}
      <div className="challenge-text-area" onClick={() => inputRef.current?.focus()}>
        <div className={`text-display ${isError ? 'text-error' : ''}`}>
          {renderText()}
        </div>
        <input
          ref={inputRef}
          type="text"
          className="challenge-input"
          value={userInput}
          onChange={(e) => handleInput(e.target.value)}
          onCompositionEnd={handleCompositionEnd}
          autoFocus
          autoComplete="off"
          autoCapitalize="off"
          spellCheck={false}
        />
      </div>
      
      {/* 하단 정보 */}
      <div className="challenge-footer">
        <div className="footer-stat">
          <span className="footer-label">WPM</span>
          <span className="footer-value">{stats.wpm}</span>
        </div>
        <div className="footer-stat">
          <span className="footer-label">정확도</span>
          <span className="footer-value">{stats.accuracy}%</span>
        </div>
        <div className="footer-stat">
          <span className="footer-label">오타</span>
          <span className="footer-value">{stats.errors}</span>
        </div>
      </div>
      
      {/* 그만두기 버튼 */}
      <button className="btn btn-ghost quit-btn" onClick={handleRetry}>
        ❌ 그만두기
      </button>
    </div>
  )
}

export default ChallengePage
