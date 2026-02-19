import { useState, useEffect } from 'react'
import { getGuestSessionId, fetchLeaderboardLatest, fetchLeaderboardMe } from '../lib/typingApi'
import type { LeaderboardEntry } from '../lib/typingApi'
import './LeaderboardPage.css'

function LeaderboardPage() {
    const [entries, setEntries] = useState<LeaderboardEntry[]>([])
    const [myRank, setMyRank] = useState<number | null>(null)
    const [totalEntries, setTotalEntries] = useState(0)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [language, setLanguage] = useState<'ko' | 'en'>('ko')

    useEffect(() => {
        const controller = new AbortController()
        loadLeaderboard(controller.signal)
        return () => { controller.abort() }
    }, [language])

    const loadLeaderboard = async (signal?: AbortSignal) => {
        setLoading(true)
        setError(null)
        const guestId = getGuestSessionId()

        const [snapshot, me] = await Promise.allSettled([
            fetchLeaderboardLatest(language),
            fetchLeaderboardMe(guestId, language),
        ])

        if (signal?.aborted) return

        if (snapshot.status === 'fulfilled') {
            setEntries(snapshot.value.entries || [])
            setTotalEntries(snapshot.value.total_entries || 0)
        } else {
            setError('랭킹 데이터를 불러올 수 없습니다.')
        }

        if (me.status === 'fulfilled') {
            setMyRank(me.value.rank)
        }

        setLoading(false)
    }

    const getRankEmoji = (rank: number) => {
        if (rank === 1) return '🥇'
        if (rank === 2) return '🥈'
        if (rank === 3) return '🥉'
        return `#${rank}`
    }

    const getRankClass = (rank: number) => {
        if (rank === 1) return 'rank-gold'
        if (rank === 2) return 'rank-silver'
        if (rank === 3) return 'rank-bronze'
        return ''
    }

    return (
        <div className="leaderboard-page container">
            <header className="leaderboard-header">
                <h1 className="leaderboard-title">🏆 주간 랭킹</h1>
                <div className="language-tabs">
                    <button
                        className={`tab-btn ${language === 'ko' ? 'active' : ''}`}
                        onClick={() => setLanguage('ko')}
                    >
                        🇰🇷 한글
                    </button>
                    <button
                        className={`tab-btn ${language === 'en' ? 'active' : ''}`}
                        onClick={() => setLanguage('en')}
                    >
                        🇺🇸 영어
                    </button>
                </div>
            </header>

            {/* 내 순위 카드 */}
            {myRank && (
                <div className="my-rank-card">
                    <span className="my-rank-label">내 순위</span>
                    <span className="my-rank-value">{getRankEmoji(myRank)}</span>
                    <span className="my-rank-total">/ {totalEntries}명</span>
                </div>
            )}

            {/* 로딩 */}
            {loading && (
                <div className="leaderboard-loading">
                    <div className="loading-spinner" />
                    <p>랭킹 로딩중...</p>
                </div>
            )}

            {/* 에러 */}
            {error && !loading && (
                <div className="leaderboard-empty">
                    <div className="empty-icon">⚠️</div>
                    <p>{error}</p>
                    <button className="btn btn-primary" onClick={() => loadLeaderboard()}>
                        다시 시도
                    </button>
                </div>
            )}

            {/* 데이터 없음 */}
            {!loading && !error && entries.length === 0 && (
                <div className="leaderboard-empty">
                    <div className="empty-icon">📋</div>
                    <h2>아직 랭킹 데이터가 없습니다</h2>
                    <p>이번 주 연습을 시작하면 다음 주간 랭킹에 반영됩니다!</p>
                </div>
            )}

            {/* 랭킹 테이블 */}
            {!loading && !error && entries.length > 0 && (
                <div className="leaderboard-table-wrapper">
                    <table className="leaderboard-table">
                        <thead>
                            <tr>
                                <th className="col-rank">순위</th>
                                <th className="col-name">이름</th>
                                <th className="col-wpm">평균 WPM</th>
                                <th className="col-accuracy">정확도</th>
                                <th className="col-sessions">세션</th>
                            </tr>
                        </thead>
                        <tbody>
                            {entries.map((entry) => (
                                <tr
                                    key={entry.rank}
                                    className={`${getRankClass(entry.rank)} ${entry.rank === myRank ? 'is-me' : ''}`}
                                >
                                    <td className="col-rank">
                                        <span className="rank-badge">
                                            {getRankEmoji(entry.rank)}
                                        </span>
                                    </td>
                                    <td className="col-name">{entry.name}</td>
                                    <td className="col-wpm">
                                        <strong>{parseFloat(entry.avg_wpm).toFixed(1)}</strong>
                                    </td>
                                    <td className="col-accuracy">
                                        {parseFloat(entry.avg_accuracy).toFixed(1)}%
                                    </td>
                                    <td className="col-sessions">{entry.total_sessions}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    <div className="leaderboard-footer">
                        총 {totalEntries}명 참가
                    </div>
                </div>
            )}
        </div>
    )
}

export default LeaderboardPage
