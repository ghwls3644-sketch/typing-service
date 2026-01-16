import { useState, useEffect } from 'react'
import './LeaderboardPage.css'

interface LeaderEntry {
    rank: number
    username: string
    avgWpm: number
    avgAccuracy: number
    sessionCount: number
    isMe?: boolean
}

// Mock data for demo
const getMockLeaderboard = (): LeaderEntry[] => {
    return [
        { rank: 1, username: '타자왕', avgWpm: 145, avgAccuracy: 98.5, sessionCount: 234 },
        { rank: 2, username: '스피드러너', avgWpm: 138, avgAccuracy: 97.2, sessionCount: 189 },
        { rank: 3, username: '키보드마스터', avgWpm: 132, avgAccuracy: 96.8, sessionCount: 156 },
        { rank: 4, username: '빠른손', avgWpm: 128, avgAccuracy: 95.4, sessionCount: 201 },
        { rank: 5, username: '연습왕', avgWpm: 125, avgAccuracy: 94.9, sessionCount: 312 },
        { rank: 6, username: '타자초보탈출', avgWpm: 118, avgAccuracy: 93.2, sessionCount: 87 },
        { rank: 7, username: '게스트', avgWpm: 95, avgAccuracy: 91.5, sessionCount: 12, isMe: true },
        { rank: 8, username: '타자신', avgWpm: 142, avgAccuracy: 99.1, sessionCount: 45 },
        { rank: 9, username: '손가락달인', avgWpm: 110, avgAccuracy: 92.3, sessionCount: 78 },
        { rank: 10, username: '연습중', avgWpm: 85, avgAccuracy: 88.7, sessionCount: 34 },
    ].sort((a, b) => b.avgWpm - a.avgWpm).map((e, i) => ({ ...e, rank: i + 1 }))
}

function LeaderboardPage() {
    const [period, setPeriod] = useState<'weekly' | 'monthly' | 'all'>('weekly')
    const [language, setLanguage] = useState<'all' | 'ko' | 'en'>('all')
    const [leaderboard, setLeaderboard] = useState<LeaderEntry[]>([])
    const [myRank, setMyRank] = useState<LeaderEntry | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        // Simulate API call
        setLoading(true)
        setTimeout(() => {
            const data = getMockLeaderboard()
            setLeaderboard(data)
            setMyRank(data.find(e => e.isMe) || null)
            setLoading(false)
        }, 500)
    }, [period, language])

    const getRankIcon = (rank: number) => {
        switch (rank) {
            case 1: return '🥇'
            case 2: return '🥈'
            case 3: return '🥉'
            default: return `#${rank}`
        }
    }

    const getRankClass = (rank: number) => {
        if (rank <= 3) return `rank-${rank}`
        return ''
    }

    return (
        <div className="leaderboard-page container">
            <header className="leaderboard-header">
                <h1 className="page-title">
                    🏆 <span className="text-gradient">랭킹</span>
                </h1>
                <p className="page-description">
                    다른 타자 연습생들과 실력을 비교해보세요!
                </p>
            </header>

            {/* 필터 */}
            <div className="leaderboard-filters">
                <div className="filter-group">
                    <label>기간</label>
                    <div className="filter-buttons">
                        <button
                            className={`filter-btn ${period === 'weekly' ? 'active' : ''}`}
                            onClick={() => setPeriod('weekly')}
                        >
                            주간
                        </button>
                        <button
                            className={`filter-btn ${period === 'monthly' ? 'active' : ''}`}
                            onClick={() => setPeriod('monthly')}
                        >
                            월간
                        </button>
                        <button
                            className={`filter-btn ${period === 'all' ? 'active' : ''}`}
                            onClick={() => setPeriod('all')}
                        >
                            전체
                        </button>
                    </div>
                </div>
                <div className="filter-group">
                    <label>언어</label>
                    <div className="filter-buttons">
                        <button
                            className={`filter-btn ${language === 'all' ? 'active' : ''}`}
                            onClick={() => setLanguage('all')}
                        >
                            전체
                        </button>
                        <button
                            className={`filter-btn ${language === 'ko' ? 'active' : ''}`}
                            onClick={() => setLanguage('ko')}
                        >
                            🇰🇷 한글
                        </button>
                        <button
                            className={`filter-btn ${language === 'en' ? 'active' : ''}`}
                            onClick={() => setLanguage('en')}
                        >
                            🇺🇸 영어
                        </button>
                    </div>
                </div>
            </div>

            {/* 내 순위 */}
            {myRank && (
                <div className="my-rank-card">
                    <div className="my-rank-badge">내 순위</div>
                    <div className="my-rank-info">
                        <span className="my-rank-number">#{myRank.rank}</span>
                        <span className="my-rank-wpm">{myRank.avgWpm} WPM</span>
                        <span className="my-rank-accuracy">{myRank.avgAccuracy}%</span>
                    </div>
                </div>
            )}

            {/* 랭킹 테이블 */}
            <div className="leaderboard-table">
                {loading ? (
                    <div className="loading">
                        <div className="loading-spinner"></div>
                        <span>랭킹 로딩 중...</span>
                    </div>
                ) : (
                    <table>
                        <thead>
                            <tr>
                                <th>순위</th>
                                <th>사용자</th>
                                <th>평균 WPM</th>
                                <th>정확도</th>
                                <th>세션 수</th>
                            </tr>
                        </thead>
                        <tbody>
                            {leaderboard.map((entry) => (
                                <tr
                                    key={entry.rank}
                                    className={`${getRankClass(entry.rank)} ${entry.isMe ? 'is-me' : ''}`}
                                >
                                    <td className="rank-cell">
                                        <span className="rank-icon">{getRankIcon(entry.rank)}</span>
                                    </td>
                                    <td className="username-cell">
                                        {entry.username}
                                        {entry.isMe && <span className="me-badge">나</span>}
                                    </td>
                                    <td className="wpm-cell">{entry.avgWpm}</td>
                                    <td className="accuracy-cell">{entry.avgAccuracy}%</td>
                                    <td className="sessions-cell">{entry.sessionCount}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {/* 안내 */}
            <div className="leaderboard-info">
                <div className="info-card">
                    <span className="info-icon">💡</span>
                    <p>랭킹은 평균 WPM 기준으로 정렬됩니다. 더 많이 연습하면 순위가 올라갑니다!</p>
                </div>
            </div>
        </div>
    )
}

export default LeaderboardPage
