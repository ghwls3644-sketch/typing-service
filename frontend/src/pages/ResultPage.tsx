import { useLocation, Link, useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import './ResultPage.css'

interface ResultStats {
    wpm: number
    accuracy: number
    time: number
    correctChars: number
    totalChars: number
    errors: number
}

function ResultPage() {
    const location = useLocation()
    const navigate = useNavigate()
    const { stats, text, language } = location.state as {
        stats: ResultStats
        text: string
        language: 'korean' | 'english'
    } || { stats: null, text: '', language: 'korean' }

    // 결과 없이 접근 시 리다이렉트
    useEffect(() => {
        if (!stats) {
            navigate('/practice')
        }
    }, [stats, navigate])

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

    // 피드백 메시지
    const getFeedback = () => {
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
                <h1 className="result-title">연습 결과</h1>

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
