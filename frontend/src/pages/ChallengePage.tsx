import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import './ChallengePage.css'

interface Challenge {
    id: number
    title: string
    description: string
    challenge_type: string
    challenge_type_display: string
    difficulty: number
    difficulty_display: string
    target_wpm?: number
    target_accuracy?: number
    target_sessions?: number
    target_time_minutes?: number
    reward_points: number
    participants_count: number
    completed_count: number
}

interface MyProgress {
    current_wpm?: number
    current_accuracy?: number
    current_sessions: number
    status: string
    progress_wpm?: number
    progress_accuracy?: number
    progress_sessions?: number
}

// Mock data for demo
const getMockChallenge = (): Challenge => ({
    id: 1,
    title: '스피드 러너',
    description: '오늘의 도전! 평균 WPM 80 이상을 달성하고 5회 이상 연습하세요.',
    challenge_type: 'speed',
    challenge_type_display: '속도 챌린지',
    difficulty: 2,
    difficulty_display: '보통',
    target_wpm: 80,
    target_sessions: 5,
    reward_points: 150,
    participants_count: 234,
    completed_count: 89,
})

function ChallengePage() {
    const [challenge, setChallenge] = useState<Challenge | null>(null)
    const [myProgress, setMyProgress] = useState<MyProgress | null>(null)
    const [isJoined, setIsJoined] = useState(false)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        // Load today's challenge
        setTimeout(() => {
            setChallenge(getMockChallenge())
            setLoading(false)
        }, 500)
    }, [])

    const handleJoin = () => {
        setIsJoined(true)
        setMyProgress({
            current_wpm: 0,
            current_accuracy: 0,
            current_sessions: 0,
            status: 'in_progress',
            progress_wpm: 0,
            progress_accuracy: 100,
            progress_sessions: 0,
        })
    }

    const getDifficultyColor = (difficulty: number) => {
        switch (difficulty) {
            case 1: return 'var(--color-success)'
            case 2: return 'var(--color-primary)'
            case 3: return 'var(--color-warning, #f59e0b)'
            case 4: return 'var(--color-error)'
            default: return 'var(--text-secondary)'
        }
    }

    const getDifficultyIcon = (difficulty: number) => {
        switch (difficulty) {
            case 1: return '⭐'
            case 2: return '⭐⭐'
            case 3: return '⭐⭐⭐'
            case 4: return '⭐⭐⭐⭐'
            default: return ''
        }
    }

    const getChallengeTypeIcon = (type: string) => {
        switch (type) {
            case 'speed': return '⚡'
            case 'accuracy': return '🎯'
            case 'endurance': return '🔥'
            case 'special': return '🌟'
            default: return '🏆'
        }
    }

    if (loading) {
        return (
            <div className="challenge-page container">
                <div className="loading">
                    <div className="loading-spinner"></div>
                    <span>오늘의 챌린지 로딩 중...</span>
                </div>
            </div>
        )
    }

    if (!challenge) {
        return (
            <div className="challenge-page container">
                <div className="no-challenge">
                    <span className="no-challenge-icon">😴</span>
                    <h2>오늘의 챌린지가 없습니다</h2>
                    <p>내일 다시 확인해주세요!</p>
                </div>
            </div>
        )
    }

    return (
        <div className="challenge-page container">
            <header className="challenge-header">
                <div className="challenge-date">
                    {new Date().toLocaleDateString('ko-KR', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        weekday: 'long'
                    })}
                </div>
                <h1 className="page-title">
                    {getChallengeTypeIcon(challenge.challenge_type)} 오늘의 챌린지
                </h1>
            </header>

            {/* 챌린지 카드 */}
            <div className="challenge-card">
                <div className="challenge-badge">
                    <span
                        className="difficulty-badge"
                        style={{ background: getDifficultyColor(challenge.difficulty) }}
                    >
                        {getDifficultyIcon(challenge.difficulty)} {challenge.difficulty_display}
                    </span>
                    <span className="type-badge">{challenge.challenge_type_display}</span>
                </div>

                <h2 className="challenge-title">{challenge.title}</h2>
                <p className="challenge-description">{challenge.description}</p>

                {/* 목표 */}
                <div className="challenge-targets">
                    <h3>🎯 목표</h3>
                    <div className="targets-grid">
                        {challenge.target_wpm && (
                            <div className="target-item">
                                <span className="target-value">{challenge.target_wpm}</span>
                                <span className="target-label">WPM 이상</span>
                            </div>
                        )}
                        {challenge.target_accuracy && (
                            <div className="target-item">
                                <span className="target-value">{challenge.target_accuracy}%</span>
                                <span className="target-label">정확도 이상</span>
                            </div>
                        )}
                        {challenge.target_sessions && (
                            <div className="target-item">
                                <span className="target-value">{challenge.target_sessions}회</span>
                                <span className="target-label">세션 완료</span>
                            </div>
                        )}
                        {challenge.target_time_minutes && (
                            <div className="target-item">
                                <span className="target-value">{challenge.target_time_minutes}분</span>
                                <span className="target-label">연습 시간</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* 보상 */}
                <div className="challenge-reward">
                    <span className="reward-icon">🎁</span>
                    <span className="reward-text">완료 시 {challenge.reward_points} 포인트</span>
                </div>

                {/* 참가 현황 */}
                <div className="challenge-stats">
                    <div className="stat">
                        <span className="stat-value">{challenge.participants_count}</span>
                        <span className="stat-label">참가자</span>
                    </div>
                    <div className="stat">
                        <span className="stat-value">{challenge.completed_count}</span>
                        <span className="stat-label">완료</span>
                    </div>
                    <div className="stat">
                        <span className="stat-value">
                            {Math.round((challenge.completed_count / challenge.participants_count) * 100) || 0}%
                        </span>
                        <span className="stat-label">완료율</span>
                    </div>
                </div>
            </div>

            {/* 내 진행 상황 */}
            {isJoined && myProgress && (
                <div className="my-progress-card">
                    <h3>📊 내 진행 상황</h3>
                    <div className="progress-items">
                        {challenge.target_wpm && (
                            <div className="progress-item">
                                <div className="progress-header">
                                    <span>WPM</span>
                                    <span>{myProgress.current_wpm || 0} / {challenge.target_wpm}</span>
                                </div>
                                <div className="progress-bar">
                                    <div
                                        className="progress-fill"
                                        style={{ width: `${myProgress.progress_wpm || 0}%` }}
                                    ></div>
                                </div>
                            </div>
                        )}
                        {challenge.target_sessions && (
                            <div className="progress-item">
                                <div className="progress-header">
                                    <span>세션</span>
                                    <span>{myProgress.current_sessions} / {challenge.target_sessions}</span>
                                </div>
                                <div className="progress-bar">
                                    <div
                                        className="progress-fill"
                                        style={{ width: `${myProgress.progress_sessions || 0}%` }}
                                    ></div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* 액션 버튼 */}
            <div className="challenge-actions">
                {!isJoined ? (
                    <button className="btn btn-primary btn-lg" onClick={handleJoin}>
                        🚀 챌린지 참가
                    </button>
                ) : (
                    <Link to="/practice" className="btn btn-primary btn-lg">
                        ⌨️ 연습 시작하기
                    </Link>
                )}
            </div>

            {/* 안내 */}
            <div className="challenge-info">
                <div className="info-card">
                    <span className="info-icon">💡</span>
                    <p>챌린지에 참가하고 연습을 시작하면 자동으로 진행 상황이 업데이트됩니다!</p>
                </div>
            </div>
        </div>
    )
}

export default ChallengePage
