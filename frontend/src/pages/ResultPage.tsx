import { useLocation, Link, useNavigate } from 'react-router-dom'
import { useEffect, useMemo, useState, useRef } from 'react'
import type { PracticeMode } from '../types/practice'
import { saveSession, getGuestSessionId, type SessionCreateData } from '../lib/typingApi'
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

interface LocationState {
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

function ResultPage() {
    const location = useLocation()
    const navigate = useNavigate()
    const state = location.state as LocationState | null
    
    const { stats, text, userInput, language, mode, metadata } = state || {
        stats: null,
        text: '',
        userInput: '',
        language: 'korean' as const,
        mode: 'sentence' as PracticeMode,
        metadata: undefined
    }

    // 결과 없이 접근 시 리다이렉트
    useEffect(() => {
        if (!stats) {
            navigate('/practice')
        }
    }, [stats, navigate])
    
    // 세션 저장 상태
    const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')
    const saveAttempted = useRef(false)
    
    // 결과 저장 (마운트 시 한 번만)
    useEffect(() => {
        if (!stats || saveAttempted.current) return
        saveAttempted.current = true
        
        const saveResult = async () => {
            setSaveStatus('saving')
            try {
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
                    cpm: Math.round(stats.correctChars / (stats.time / 60)),
                    metadata: metadata,
                    guest_session_id: getGuestSessionId()
                }
                await saveSession(sessionData)
                setSaveStatus('saved')
                console.log('Session saved successfully')
            } catch (err) {
                console.warn('Failed to save session:', err)
                setSaveStatus('error')
            }
        }
        
        saveResult()
    }, [stats, text, language, metadata])

    // 오타 분석 (Top 5)
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
        
        // Top 5로 정렬
        return Array.from(errorMap.entries())
            .map(([key, value]) => ({
                char: key.split('→')[1] || '?',
                expected: value.expected,
                count: value.count
            }))
            .sort((a, b) => b.count - a.count)
            .slice(0, 5)
    }, [text, userInput])

    if (!stats) {
        return null
    }

    // 등급 계산
    const getGrade = (wpm: number, accuracy: number): { grade: string; label: string; color: string } => {
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

    // 모드 이름
    const getModeName = (m?: PracticeMode) => {
        const names: Record<PracticeMode, string> = {
            sentence: '문장 연습',
            word: '단어 연습',
            time_attack: '타임어택',
            accuracy_challenge: '정확도 챌린지',
            kor_drill: '한글 드릴',
            weakness_drill: '약점 훈련'
        }
        return m ? names[m] : '연습'
    }

    // 피드백 메시지
    const getFeedback = () => {
        // 종료 이유에 따른 피드백
        const failReason = metadata?.result_extra?.fail_reason
        if (failReason === 'time_up') {
            return '⏰ 시간이 종료되었습니다! 다음에는 더 빠르게 도전해보세요.'
        }
        if (failReason === 'max_errors') {
            return '❌ 오타 제한에 도달했습니다. 정확도를 높여보세요!'
        }
        
        if (stats.wpm >= 80 && stats.accuracy >= 95) {
            return '🏆 놀라운 실력입니다! 타자 마스터시네요!'
        }
        if (stats.wpm >= 60 && stats.accuracy >= 90) {
            return '👏 훌륭합니다! 꾸준히 연습하면 더 좋아질 거예요.'
        }
        if (stats.accuracy >= 95) {
            return '🎯 정확도가 뛰어나요! 속도를 조금씩 올려보세요.'
        }
        if (stats.wpm >= 50) {
            return '⚡ 속도가 빠르네요! 정확도를 신경 쓰면 완벽해질 거예요.'
        }
        return '💪 좋은 시작이에요! 꾸준한 연습이 실력을 만듭니다.'
    }

    return (
        <div className="result-page container">
            {/* 결과 카드 */}
            <div className="result-card">
                {/* 저장 상태 표시 */}
                <div className={`save-status ${saveStatus}`}>
                    {saveStatus === 'saving' && '💾 저장 중...'}
                    {saveStatus === 'saved' && '✅ 기록 저장됨'}
                    {saveStatus === 'error' && '⚠️ 저장 실패 (오프라인 모드)'}
                </div>
                <h1 className="result-title">연습 결과</h1>
                
                {/* 모드 표시 */}
                {mode && (
                    <div className="mode-tag">
                        {getModeName(mode)} · {language === 'korean' ? '🇰🇷 한글' : '🇺🇸 영어'}
                    </div>
                )}

                {/* 등급 표시 */}
                <div className="grade-section">
                    <div className="grade-circle" style={{ borderColor: color }}>
                        <span className="grade-letter" style={{ color }}>{grade}</span>
                    </div>
                    <span className="grade-label" style={{ color }}>{label}</span>
                </div>

                {/* 피드백 */}
                <p className="feedback">{getFeedback()}</p>

                {/* 상세 통계 */}
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

                {/* 오타 분석 */}
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

                {/* 연습 문장 */}
                <div className="practiced-text">
                    <h3>연습한 문장</h3>
                    <p>"{text}"</p>
                </div>

                {/* 액션 버튼 */}
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
