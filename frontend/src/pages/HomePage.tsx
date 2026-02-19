import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import './HomePage.css'
import { storage } from '../lib/utils'
import { fetchDashboardOverview, getGuestSessionId, syncPendingSessions, fetchDailyChallenge, joinDailyChallenge } from '../lib/typingApi'
import type { DailyChallengeInfo, ChallengeProgress } from '../lib/typingApi'

function HomePage() {
    const [stats, setStats] = useState({
        currentStreak: 0,
        longestStreak: 0,
        todaySessions: 0,
        todayTime: 0,
        avgWpm: 0,
        avgAccuracy: 0,
        goalProgress: 0,
        goalTarget: 30,
    })
    const [isStatsExpanded, setIsStatsExpanded] = useState(() => {
        return storage.get('statsExpanded', false)
    })
    const [isLoading, setIsLoading] = useState(true)
    const [dailyChallenge, setDailyChallenge] = useState<DailyChallengeInfo | null>(null)
    const [challengeProgress, setChallengeProgress] = useState<ChallengeProgress | null>(null)
    const [isJoining, setIsJoining] = useState(false)

    useEffect(() => {
        const controller = new AbortController()

        // 먼저 대기 중인 세션 동기화(백그라운드)
        syncPendingSessions().catch(() => {})

        // 서버 API에서 대시보드 데이터 로드
        const loadFromServer = async () => {
            try {
                const guestId = getGuestSessionId()
                const overview = await fetchDashboardOverview(guestId)
                if (controller.signal.aborted) return

                const todayDurationMin = Math.round((overview.today?.total_duration_ms || 0) / 60000)

                setStats({
                    currentStreak: overview.current_streak || 0,
                    longestStreak: overview.longest_streak || 0,
                    todaySessions: overview.today?.total_sessions || 0,
                    todayTime: todayDurationMin,
                    avgWpm: Math.round(overview.today?.avg_wpm || 0),
                    avgAccuracy: Math.round(overview.today?.avg_accuracy || 0),
                    goalProgress: Math.min(Math.round((todayDurationMin / 30) * 100), 100),
                    goalTarget: 30,
                })
            } catch {
                if (controller.signal.aborted) return
                // API 실패 시 localStorage 폴백
                loadFromLocal()
            } finally {
                if (!controller.signal.aborted) setIsLoading(false)
            }
        }

        const loadFromLocal = () => {
            const history = storage.get<{ date: string, time: number, wpm: number, accuracy: number }[]>('typingHistory', [])
            const today = new Date().toDateString()
            const todaySessions = history.filter(
                (h: { date: string }) => new Date(h.date).toDateString() === today
            )
            const totalTime = todaySessions.reduce((sum: number, h: { time: number }) => sum + (h.time || 0), 0)
            const avgWpm = todaySessions.length > 0
                ? todaySessions.reduce((sum: number, h: { wpm: number }) => sum + h.wpm, 0) / todaySessions.length
                : 0
            const avgAccuracy = todaySessions.length > 0
                ? todaySessions.reduce((sum: number, h: { accuracy: number }) => sum + h.accuracy, 0) / todaySessions.length
                : 0

            setStats({
                currentStreak: 0,
                longestStreak: 0,
                todaySessions: todaySessions.length,
                todayTime: Math.round(totalTime / 60),
                avgWpm: Math.round(avgWpm),
                avgAccuracy: Math.round(avgAccuracy),
                goalProgress: Math.min(Math.round((totalTime / 60 / 30) * 100), 100),
                goalTarget: 30,
            })
        }

        loadFromServer()

        // 데일리 챌린지 로드
        const loadDailyChallenge = async () => {
            try {
                const guestId = getGuestSessionId()
                const challenge = await fetchDailyChallenge(guestId)
                if (controller.signal.aborted) return
                setDailyChallenge(challenge)
            } catch {
                // 챌린지가 없으면 조용히 무시
            }
        }
        loadDailyChallenge()

        return () => { controller.abort() }
    }, [])



    const toggleStatsExpanded = () => {
        const newValue = !isStatsExpanded
        setIsStatsExpanded(newValue)
        storage.set('statsExpanded', newValue)
    }

    const features = [
        {
            icon: '🇰🇷',
            title: '한글 타자',
            description: '한글 문장으로 타자 연습을 시작하세요'
        },
        {
            icon: '🇺🇸',
            title: '영어 타자',
            description: '영문 문장으로 타자 실력을 향상시키세요'
        },
        {
            icon: '📊',
            title: '실시간 측정',
            description: 'WPM, 정확도, 소요시간을 실시간으로 확인'
        },
        {
            icon: '🏆',
            title: '랭킹 시스템',
            description: '다른 사용자와 경쟁하고 순위를 확인하세요'
        }
    ]

    return (
        <div className="home-page container">
            {/* 히어로 섹션 - 맨 위로 이동 */}
            <section className="hero">
                <div className="hero-content">
                    <h1 className="hero-title">
                        <span className="text-gradient">타자 연습</span>으로
                        <br />
                        키보드 마스터가 되세요
                    </h1>
                    <p className="hero-description">
                        한글과 영어 문장으로 재미있게 타자 연습을 시작하세요.
                        <br />
                        실시간으로 WPM과 정확도를 측정하고 기록을 관리할 수 있습니다.
                    </p>
                    <div className="hero-actions">
                        <Link to="/practice" className="btn btn-primary btn-lg">
                            <span>연습 시작하기</span>
                            <span className="btn-icon">→</span>
                        </Link>
                        <Link to="/challenge" className="btn btn-warning btn-lg">
                            🔥 60초 챌린지
                        </Link>
                    </div>
                </div>
                <div className="hero-visual">
                    <div className="keyboard-animation">
                        <div className="key">ㅎ</div>
                        <div className="key">ㅏ</div>
                        <div className="key">ㄴ</div>
                        <div className="key">ㄱ</div>
                        <div className="key">ㅡ</div>
                        <div className="key">ㄹ</div>
                    </div>
                </div>
            </section>

            {/* 스트릭/목표 섹션 - 접었다 폈다 가능 */}
            <section className="streak-section-wrapper">
                <button
                    className={`streak-toggle ${isLoading ? 'loading' : ''}`}
                    onClick={toggleStatsExpanded}
                    aria-expanded={isStatsExpanded}
                >
                    <span className="streak-toggle-icon">
                        🔥 {isLoading ? '...' : `${stats.currentStreak}일 연속`}
                        {!isLoading && stats.goalProgress > 0 && ` · 목표 ${stats.goalProgress}%`}
                    </span>
                    <span className={`streak-toggle-arrow ${isStatsExpanded ? 'expanded' : ''}`}>
                        ▼
                    </span>
                </button>

                <div className={`streak-section ${isStatsExpanded ? 'expanded' : 'collapsed'}`}>
                    <div className="streak-card">
                        <div className="streak-fire">🔥</div>
                        <div className="streak-info">
                            <div className="streak-number">{stats.currentStreak}</div>
                            <div className="streak-label">일 연속</div>
                        </div>
                        <div className="streak-best">
                            최장: {stats.longestStreak}일
                        </div>
                    </div>

                    <div className="goal-card">
                        <div className="goal-header">
                            <span className="goal-icon">🎯</span>
                            <span className="goal-title">오늘의 목표</span>
                        </div>
                        <div className="goal-progress-bar">
                            <div
                                className="goal-progress-fill"
                                style={{ width: `${stats.goalProgress}%` }}
                            ></div>
                        </div>
                        <div className="goal-stats">
                            <span>{stats.todayTime}분 / {stats.goalTarget}분</span>
                            <span className="goal-percent">{stats.goalProgress}%</span>
                        </div>
                    </div>

                    <div className="today-stats-card">
                        <div className="today-stat">
                            <div className="today-stat-value">{stats.todaySessions}</div>
                            <div className="today-stat-label">오늘 세션</div>
                        </div>
                        <div className="today-stat">
                            <div className="today-stat-value">{stats.avgWpm}</div>
                            <div className="today-stat-label">평균 WPM</div>
                        </div>
                        <div className="today-stat">
                            <div className="today-stat-value">{stats.avgAccuracy}%</div>
                            <div className="today-stat-label">평균 정확도</div>
                        </div>
                    </div>
                </div>
            </section>

            {/* 데일리 챌린지 카드 */}
            {dailyChallenge && (
                <section className="daily-challenge-section">
                    <div className="daily-challenge-card">
                        <div className="dc-header">
                            <span className="dc-badge">🎯 오늘의 챌린지</span>
                            <span className="dc-difficulty">
                                {'⭐'.repeat(dailyChallenge.difficulty)}
                            </span>
                        </div>
                        <h3 className="dc-title">{dailyChallenge.title}</h3>
                        <p className="dc-description">{dailyChallenge.description}</p>
                        
                        <div className="dc-targets">
                            {dailyChallenge.target_wpm && (
                                <span className="dc-target">🎯 {dailyChallenge.target_wpm} WPM</span>
                            )}
                            {dailyChallenge.target_accuracy && (
                                <span className="dc-target">✅ {dailyChallenge.target_accuracy}%</span>
                            )}
                            <span className="dc-target">📝 {dailyChallenge.target_sessions}세션</span>
                        </div>

                        {challengeProgress ? (
                            <div className="dc-progress">
                                <div className="dc-progress-bar">
                                    <div className="dc-progress-fill" style={{ width: `${Math.max(challengeProgress.progress_sessions, challengeProgress.progress_wpm, challengeProgress.progress_accuracy)}%` }} />
                                </div>
                                <span className="dc-progress-text">
                                    {challengeProgress.status === 'completed' ? '✅ 완료!' : `${challengeProgress.current_sessions}/${challengeProgress.target_sessions} 세션`}
                                </span>
                            </div>
                        ) : (
                            <button
                                className="btn btn-warning dc-join-btn"
                                onClick={async () => {
                                    setIsJoining(true)
                                    try {
                                        const guestId = getGuestSessionId()
                                        const progress = await joinDailyChallenge(dailyChallenge.id, guestId)
                                        setChallengeProgress(progress)
                                    } catch { /* silent */ }
                                    setIsJoining(false)
                                }}
                                disabled={isJoining}
                            >
                                {isJoining ? '참가 중...' : '🚀 참가하기'}
                            </button>
                        )}

                        <div className="dc-meta">
                            <span>👥 {dailyChallenge.participants_count}명 참가</span>
                            <span>🏅 +{dailyChallenge.reward_points}P</span>
                        </div>
                    </div>
                </section>
            )}

            {/* 기능 섹션 */}
            <section className="features">
                <h2 className="section-title">주요 기능</h2>
                <div className="features-grid">
                    {features.map((feature, index) => (
                        <div key={index} className="feature-card">
                            <div className="feature-icon">{feature.icon}</div>
                            <h3 className="feature-title">{feature.title}</h3>
                            <p className="feature-description">{feature.description}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* 통계 섹션 */}
            <section className="stats">
                <div className="stat-card">
                    <div className="stat-value">100+</div>
                    <div className="stat-label">연습 문장</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">2</div>
                    <div className="stat-label">지원 언어</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">∞</div>
                    <div className="stat-label">무제한 연습</div>
                </div>
            </section>

            {/* CTA 섹션 */}
            <section className="cta">
                <div className="cta-content">
                    <h2>지금 바로 시작하세요!</h2>
                    <p>무료로 타자 연습을 시작하고 실력을 향상시키세요.</p>
                    <Link to="/practice" className="btn btn-primary btn-lg">
                        연습 시작 →
                    </Link>
                </div>
            </section>
        </div>
    )
}

export default HomePage
