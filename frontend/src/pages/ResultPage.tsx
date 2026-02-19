import { useLocation, Link, useNavigate } from 'react-router-dom'
import { useEffect, useMemo, useState, useRef } from 'react'
import type { PracticeMode } from '../types/practice'
import type { ChallengeStats } from '../types/challenge'
import { saveSessionWithBackup, getGuestSessionId, syncPendingSessions, type SessionCreateData } from '../lib/typingApi'
import { getChallengeBest } from '../lib/challengeStorage'
import { storage } from '../lib/utils'
import './ResultPage.css'

interface ResultStats {
    wpm: number
    accuracy: number
    time: number
    correctChars: number
    totalChars: number
    errors: number
}

interface ErrorAnalysis {
    char: string
    expected: string
    count: number
}

// 연습 결과 state
interface PracticeLocationState {
    resultType?: 'practice'
    stats: ResultStats
    text: string
    userInput?: string
    language: 'korean' | 'english'
    mode?: PracticeMode
    metadata?: {
        submode: PracticeMode
        result_extra?: {
            fail_reason?: string | null
        }
    }
}

// 챌린지 결과 state
interface ChallengeLocationState {
    resultType: 'challenge'
    stats: ChallengeStats
    durationMs: number
    isBlindMode?: boolean
}

type LocationState = PracticeLocationState | ChallengeLocationState

function ResultPage() {
    const location = useLocation()
    const navigate = useNavigate()
    const state = location.state as LocationState | null
    
    // 결과 타입 판별
    const isChallenge = state?.resultType === 'challenge'
    
    // 결과 없이 접근 시 리다이렉트
    useEffect(() => {
        if (!state || !state.stats) {
            navigate('/practice')
        }
    }, [state, navigate])
    
    // 챌린지 결과 화면
    if (isChallenge && state) {
        return <ChallengeResult state={state as ChallengeLocationState} />
    }
    
    // 연습 결과 화면
    if (state && !isChallenge) {
        return <PracticeResult state={state as PracticeLocationState} />
    }
    
    return null
}

// ===== 챌린지 결과 컴포넌트 =====
function ChallengeResult({ state }: { state: ChallengeLocationState }) {
    const { stats, durationMs, isBlindMode } = state
    const best = getChallengeBest()
    const isNewRecord = best && stats.score === best.bestScore && Date.now() - best.updatedAt < 5000
    const historySaved = useRef(false)

    // 챌린지 결과를 typingHistory에 저장 (홈페이지 대시보드용)
    useEffect(() => {
        if (!stats || historySaved.current) return
        historySaved.current = true
        const history = storage.get<{ date: string; time: number; wpm: number; accuracy: number }[]>('typingHistory', [])
        history.push({
            date: new Date().toISOString(),
            time: durationMs / 1000,
            wpm: stats.wpm,
            accuracy: stats.accuracy,
        })
        storage.set('typingHistory', history)
    }, [stats, durationMs])
    
    // 오답 로그 (중복 제거 및 카운팅)
    const errorAnalysis = useMemo(() => {
        if (!stats.errorLog || stats.errorLog.length === 0) return []
        
        // ErrorLogEntry is now { word: string, typed: string }
        const errorMap = new Map<string, { word: string; typed: string; count: number }>()
        
        stats.errorLog.forEach(log => {
            const key = `${log.word}:${log.typed}`
            const existing = errorMap.get(key)
            if (existing) {
                existing.count++
            } else {
                errorMap.set(key, { ...log, count: 1 })
            }
        })
        
        return Array.from(errorMap.values()).sort((a, b) => b.count - a.count)
    }, [stats.errorLog])

    // 글자별 비교 렌더링
    const renderDiff = (word: string, typed: string) => {
        return typed.split('').map((char, i) => {
            const exactChar = word[i]
            const isCorrect = char === exactChar
            return (
                <span key={i} className={isCorrect ? 'diff-correct' : 'diff-incorrect'}>
                    {char}
                </span>
            )
        })
    }

    return (
        <div className="result-page container">
            <div className="result-card challenge-result">
                <div className="result-badges">
                  <div className="result-badge">🔥 60초 챌린지</div>
                  {isBlindMode && <div className="result-badge blind-badge">🕶️ 블라인드 모드</div>}
                </div>
                
                {isNewRecord && (
                    <div className="new-record-banner">
                        🎉 새로운 최고기록!
                    </div>
                )}
                
                <h1 className="result-title challenge-title">챌린지 완료!</h1>
                
                {/* 점수 강조 */}
                <div className="score-section">
                    <span className="score-label">최종 점수</span>
                    <span className="score-value">{stats.score}</span>
                </div>
                
                {/* 주요 통계 */}
                <div className="challenge-stats-grid">
                    <div className="challenge-stat">
                        <span className="stat-icon">⭐</span>
                        <span className="stat-value">{stats.maxCombo}</span>
                        <span className="stat-label">최대 콤보</span>
                    </div>
                    <div className="challenge-stat">
                        <span className="stat-icon">⌨️</span>
                        <span className="stat-value">{stats.wpm}</span>
                        <span className="stat-label">WPM</span>
                    </div>
                    <div className="challenge-stat">
                        <span className="stat-icon">🎯</span>
                        <span className="stat-value">{stats.accuracy}%</span>
                        <span className="stat-label">정확도</span>
                    </div>
                    <div className="challenge-stat">
                        <span className="stat-icon">❌</span>
                        <span className="stat-value">{stats.errors}</span>
                        <span className="stat-label">오타</span>
                    </div>
                </div>
                
                {/* 오답 노트 (개선된 UI) */}
                {errorAnalysis.length > 0 && (
                    <div className="error-analysis challenge-errors">
                        <h3>
                            🔍 오답 노트
                            {isBlindMode && <span className="blind-note-badge">🕶️ 블라인드 모드 리뷰</span>}
                        </h3>
                        <div className="error-list-stacked">
                            {errorAnalysis.map((error, index) => (
                                <div key={index} className="error-card">
                                    <div className="error-word-original">{error.word}</div>
                                    <div className="error-arrow-down">↓</div>
                                    <div className="error-word-typed">
                                        {renderDiff(error.word, error.typed)}
                                    </div>
                                    {error.count > 1 && (
                                        <div className="error-frequency-badge">{error.count}회 반복</div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
                
                {/* 액션 버튼 */}
                <div className="result-actions">
                    <Link to="/challenge" className="btn btn-primary btn-lg">
                        🔄 다시 도전하기
                    </Link>
                    <Link to="/history" className="btn btn-secondary btn-lg">
                        📊 기록 보기
                    </Link>
                    <Link to="/" className="btn btn-secondary btn-lg">
                        🏠 홈으로
                    </Link>
                </div>
            </div>
        </div>
    )
}

// ===== 연습 결과 컴포넌트 =====
function PracticeResult({ state }: { state: PracticeLocationState }) {
    const { stats, text, userInput, language, mode, metadata } = state
    
    // 세션 저장 상태
    const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')
    const saveAttempted = useRef(false)
    
    // 결과 저장
    useEffect(() => {
        if (!stats || saveAttempted.current) return
        saveAttempted.current = true
        
        syncPendingSessions().catch(() => {})
        
        const saveResult = async () => {
            setSaveStatus('saving')
            const sessionData: SessionCreateData = {
                mode: 'practice',
                language: language === 'korean' ? 'ko' : 'en',
                text_content: text,
                duration_ms: Math.round(stats.time * 1000),
                input_length: stats.totalChars,
                correct_length: stats.correctChars,
                error_count: stats.errors,
                accuracy: stats.accuracy,
                wpm: stats.wpm,
                cpm: stats.time > 0 ? Math.round(stats.correctChars / (stats.time / 60)) : 0,
                metadata: metadata,
                guest_session_id: getGuestSessionId()
            }
            const result = await saveSessionWithBackup(sessionData)
            setSaveStatus(result ? 'saved' : 'error')
        }
        
        saveResult()

        // typingHistory에도 저장 (홈페이지 대시보드용)
        const history = storage.get<{ date: string; time: number; wpm: number; accuracy: number }[]>('typingHistory', [])
        history.push({
            date: new Date().toISOString(),
            time: stats.time,
            wpm: stats.wpm,
            accuracy: stats.accuracy,
        })
        storage.set('typingHistory', history)
    }, [stats, text, language, metadata])

    // 오타 분석
    const errorAnalysis = useMemo((): ErrorAnalysis[] => {
        if (!text || !userInput) return []
        
        const errorMap = new Map<string, { expected: string; count: number }>()
        
        for (let i = 0; i < Math.min(text.length, userInput.length); i++) {
            if (text[i] !== userInput[i]) {
                const key = `${text[i]}→${userInput[i]}`
                const existing = errorMap.get(key)
                if (existing) {
                    existing.count++
                } else {
                    errorMap.set(key, { expected: text[i], count: 1 })
                }
            }
        }
        
        return Array.from(errorMap.entries())
            .map(([key, value]) => ({
                char: key.split('→')[1] || '?',
                expected: value.expected,
                count: value.count
            }))
            .sort((a, b) => b.count - a.count)
            .slice(0, 5)
    }, [text, userInput])

    if (!stats) return null

    // 등급 계산
    const getGrade = (wpm: number, accuracy: number) => {
        const score = (wpm * 0.6) + (accuracy * 0.4)
        if (score >= 90) return { grade: 'S', label: '마스터', color: '#ffd700' }
        if (score >= 80) return { grade: 'A', label: '전문가', color: '#48bb78' }
        if (score >= 70) return { grade: 'B', label: '숙련자', color: '#667eea' }
        if (score >= 60) return { grade: 'C', label: '중급자', color: '#ed8936' }
        if (score >= 50) return { grade: 'D', label: '초급자', color: '#a0aec0' }
        return { grade: 'F', label: '연습 필요', color: '#f56565' }
    }

    const { grade, label, color } = getGrade(stats.wpm, stats.accuracy)

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60)
        const secs = Math.floor(seconds % 60)
        const ms = Math.floor((seconds % 1) * 10)
        return `${mins}:${secs.toString().padStart(2, '0')}.${ms}`
    }

    const getModeName = (m?: PracticeMode) => {
        const names: Record<string, string> = {
            word: '단어 연습',
            short: '짧은 글 연습',
            sentence: '문장 연습',
            time_attack: '타임어택',
            accuracy_challenge: '정확도 챌린지',
            kor_drill: '한글 드릴',
            weakness_drill: '약점 훈련'
        }
        return m ? (names[m] || '연습') : '연습'
    }

    const getFeedback = () => {
        const failReason = metadata?.result_extra?.fail_reason
        if (failReason === 'time_up') return '⏰ 시간이 종료되었습니다!'
        if (failReason === 'max_errors') return '❌ 오타 제한에 도달했습니다.'
        
        if (stats.wpm >= 80 && stats.accuracy >= 95) return '🏆 놀라운 실력입니다!'
        if (stats.wpm >= 60 && stats.accuracy >= 90) return '👏 훌륭합니다!'
        if (stats.accuracy >= 95) return '🎯 정확도가 뛰어나요!'
        if (stats.wpm >= 50) return '⚡ 속도가 빠르네요!'
        return '💪 좋은 시작이에요!'
    }

    return (
        <div className="result-page container">
            <div className="result-card">
                <div className={`save-status ${saveStatus}`}>
                    {saveStatus === 'saving' && '💾 저장 중...'}
                    {saveStatus === 'saved' && '✅ 기록 저장됨'}
                    {saveStatus === 'error' && '⚠️ 저장 실패 (오프라인 모드)'}
                </div>
                <h1 className="result-title">연습 결과</h1>
                
                {mode && (
                    <div className="mode-tag">
                        {getModeName(mode)} · {language === 'korean' ? '🇰🇷 한글' : '🇺🇸 영어'}
                    </div>
                )}

                <div className="grade-section">
                    <div className="grade-circle" style={{ borderColor: color }}>
                        <span className="grade-letter" style={{ color }}>{grade}</span>
                    </div>
                    <span className="grade-label" style={{ color }}>{label}</span>
                </div>

                <p className="feedback">{getFeedback()}</p>

                <div className="stats-grid">
                    <div className="stat-card main">
                        <div className="stat-icon">⌨️</div>
                        <div className="stat-info">
                            <span className="stat-value">{stats.wpm}</span>
                            <span className="stat-label">WPM</span>
                        </div>
                    </div>
                    <div className="stat-card main">
                        <div className="stat-icon">🎯</div>
                        <div className="stat-info">
                            <span className="stat-value">{stats.accuracy}%</span>
                            <span className="stat-label">정확도</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon">⏱️</div>
                        <div className="stat-info">
                            <span className="stat-value">{formatTime(stats.time)}</span>
                            <span className="stat-label">소요 시간</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon">✅</div>
                        <div className="stat-info">
                            <span className="stat-value">{stats.correctChars}</span>
                            <span className="stat-label">정확한 글자</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon">❌</div>
                        <div className="stat-info">
                            <span className="stat-value">{stats.errors}</span>
                            <span className="stat-label">오류</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon">{language === 'korean' ? '🇰🇷' : '🇺🇸'}</div>
                        <div className="stat-info">
                            <span className="stat-value">{language === 'korean' ? '한글' : '영어'}</span>
                            <span className="stat-label">언어</span>
                        </div>
                    </div>
                </div>

                {errorAnalysis.length > 0 && (
                    <div className="error-analysis">
                        <h3>🔍 오타 분석 Top {errorAnalysis.length}</h3>
                        <div className="error-list">
                            {errorAnalysis.map((error, index) => (
                                <div key={index} className="error-item">
                                    <span className="error-expected">{error.expected}</span>
                                    <span className="error-arrow">→</span>
                                    <span className="error-typed">{error.char === ' ' ? '␣' : error.char}</span>
                                    <span className="error-count">{error.count}회</span>
                                </div>
                            ))}
                        </div>
                        <Link to="/practice" state={{ mode: 'weakness_drill', focusErrors: errorAnalysis }} className="btn btn-warning btn-sm">
                            💪 약점 훈련 시작
                        </Link>
                    </div>
                )}

                <div className="practiced-text">
                    <h3>연습한 문장</h3>
                    <p>"{text}"</p>
                </div>

                {/* 챌린지 CTA - 연습 결과에서만 표시 */}
                <div className="challenge-cta">
                    <Link to="/challenge" className="btn btn-warning btn-lg">
                        🔥 60초 챌린지 해보기
                    </Link>
                </div>

                <div className="result-actions">
                    <Link to="/practice" className="btn btn-primary btn-lg">
                        🔄 다시 연습하기
                    </Link>
                    <Link to="/history" className="btn btn-secondary btn-lg">
                        📊 기록 보기
                    </Link>
                    <Link to="/" className="btn btn-secondary btn-lg">
                        🏠 홈으로
                    </Link>
                </div>
            </div>
        </div>
    )
}

export default ResultPage
