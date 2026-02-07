import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import './HomePage.css'
import { storage } from '../lib/utils'

// Mock data for demo (replace with API calls when connected)
const getMockStats = () => {
    const savedStats = storage.get('userStats', null)
    if (savedStats) return savedStats
    return {
        currentStreak: 0,
        longestStreak: 0,
        todaySessions: 0,
        todayTime: 0,
        avgWpm: 0,
        avgAccuracy: 0,
        goalProgress: 0,
        goalTarget: 30, // 30분 목표
    }
}

function HomePage() {
    const [stats, setStats] = useState(getMockStats())
    const [isStatsExpanded, setIsStatsExpanded] = useState(() => {
        // localStorage에서 상태 복원
        return storage.get('statsExpanded', false)
    })

    useEffect(() => {
        // Load stats from localStorage or API
        const loadStats = () => {
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

            // Calculate streak
            const streak = calculateStreak(history)

            setStats({
                currentStreak: streak.current,
                longestStreak: streak.longest,
                todaySessions: todaySessions.length,
                todayTime: Math.round(totalTime / 60), // 초 -> 분
                avgWpm: Math.round(avgWpm),
                avgAccuracy: Math.round(avgAccuracy),
                goalProgress: Math.min(Math.round((totalTime / 60 / 30) * 100), 100),
                goalTarget: 30,
            })
        }
        loadStats()
    }, [])

    const calculateStreak = (history: { date: string }[]) => {
        if (history.length === 0) return { current: 0, longest: 0 }

        const dates = [...new Set(history.map(h => new Date(h.date).toDateString()))]
            .sort((a, b) => new Date(b).getTime() - new Date(a).getTime())

        let current = 0
        let longest = 0
        let streak = 0
        const today = new Date()

        for (let i = 0; i < dates.length; i++) {
            const checkDate = new Date(today)
            checkDate.setDate(today.getDate() - i)

            if (dates.includes(checkDate.toDateString())) {
                streak++
                if (i === 0 || i === current) current = streak
            } else if (streak > 0) {
                break
            }
        }

        longest = Math.max(streak, longest)
        return { current, longest }
    }

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
                    className="streak-toggle"
                    onClick={toggleStatsExpanded}
                    aria-expanded={isStatsExpanded}
                >
                    <span className="streak-toggle-icon">
                        🔥 {stats.currentStreak}일 연속
                        {stats.goalProgress > 0 && ` · 목표 ${stats.goalProgress}%`}
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
