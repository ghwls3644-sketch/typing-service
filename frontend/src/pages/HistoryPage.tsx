import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import './HistoryPage.css'

interface HistoryItem {
    id: string
    date: string
    wpm: number
    accuracy: number
    time: number
    language: 'korean' | 'english'
    text: string
}

function HistoryPage() {
    const [history, setHistory] = useState<HistoryItem[]>([])
    const [filter, setFilter] = useState<'all' | 'korean' | 'english'>('all')

    // 로컬 스토리지에서 히스토리 불러오기 (현재는 샘플 데이터)
    useEffect(() => {
        // TODO: 실제 API 연동 후 대체
        const sampleHistory: HistoryItem[] = [
            {
                id: '1',
                date: '2026-01-09 21:00',
                wpm: 75,
                accuracy: 96,
                time: 45.2,
                language: 'korean',
                text: '하늘 아래 첫 동네에 봄이 찾아왔다.'
            },
            {
                id: '2',
                date: '2026-01-09 20:30',
                wpm: 82,
                accuracy: 94,
                time: 38.5,
                language: 'english',
                text: 'The quick brown fox jumps over the lazy dog.'
            },
            {
                id: '3',
                date: '2026-01-09 20:00',
                wpm: 68,
                accuracy: 98,
                time: 52.1,
                language: 'korean',
                text: '타자 연습은 꾸준히 하면 실력이 늘어납니다.'
            },
            {
                id: '4',
                date: '2026-01-08 19:30',
                wpm: 71,
                accuracy: 92,
                time: 48.3,
                language: 'english',
                text: 'Practice makes perfect in everything we do.'
            },
            {
                id: '5',
                date: '2026-01-08 19:00',
                wpm: 65,
                accuracy: 97,
                time: 55.0,
                language: 'korean',
                text: '정확하게 치는 것이 빠르게 치는 것보다 중요합니다.'
            }
        ]
        setHistory(sampleHistory)
    }, [])

    const filteredHistory = history.filter(item => {
        if (filter === 'all') return true
        return item.language === filter
    })

    // 평균 통계 계산
    const avgStats = filteredHistory.length > 0 ? {
        wpm: Math.round(filteredHistory.reduce((sum, item) => sum + item.wpm, 0) / filteredHistory.length),
        accuracy: Math.round(filteredHistory.reduce((sum, item) => sum + item.accuracy, 0) / filteredHistory.length),
        totalPractice: filteredHistory.length
    } : { wpm: 0, accuracy: 0, totalPractice: 0 }

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60)
        const secs = Math.floor(seconds % 60)
        return `${mins}:${secs.toString().padStart(2, '0')}`
    }

    return (
        <div className="history-page container">
            <div className="history-header">
                <h1>연습 기록</h1>
                <Link to="/practice" className="btn btn-primary">
                    ⌨️ 연습하기
                </Link>
            </div>

            {/* 종합 통계 */}
            <div className="summary-stats">
                <div className="summary-card">
                    <div className="summary-icon">📊</div>
                    <div className="summary-info">
                        <span className="summary-value">{avgStats.totalPractice}</span>
                        <span className="summary-label">총 연습 횟수</span>
                    </div>
                </div>
                <div className="summary-card">
                    <div className="summary-icon">⌨️</div>
                    <div className="summary-info">
                        <span className="summary-value">{avgStats.wpm}</span>
                        <span className="summary-label">평균 WPM</span>
                    </div>
                </div>
                <div className="summary-card">
                    <div className="summary-icon">🎯</div>
                    <div className="summary-info">
                        <span className="summary-value">{avgStats.accuracy}%</span>
                        <span className="summary-label">평균 정확도</span>
                    </div>
                </div>
            </div>

            {/* 필터 */}
            <div className="filter-bar">
                <button
                    className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
                    onClick={() => setFilter('all')}
                >
                    전체
                </button>
                <button
                    className={`filter-btn ${filter === 'korean' ? 'active' : ''}`}
                    onClick={() => setFilter('korean')}
                >
                    🇰🇷 한글
                </button>
                <button
                    className={`filter-btn ${filter === 'english' ? 'active' : ''}`}
                    onClick={() => setFilter('english')}
                >
                    🇺🇸 영어
                </button>
            </div>

            {/* 기록 목록 */}
            <div className="history-list">
                {filteredHistory.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-icon">📝</div>
                        <h3>기록이 없습니다</h3>
                        <p>타자 연습을 시작하고 기록을 쌓아보세요!</p>
                        <Link to="/practice" className="btn btn-primary">
                            연습 시작하기
                        </Link>
                    </div>
                ) : (
                    filteredHistory.map((item) => (
                        <div key={item.id} className="history-item">
                            <div className="history-item-header">
                                <span className="history-date">{item.date}</span>
                                <span className="history-language">
                                    {item.language === 'korean' ? '🇰🇷' : '🇺🇸'}
                                </span>
                            </div>
                            <div className="history-item-stats">
                                <div className="history-stat">
                                    <span className="history-stat-value">{item.wpm}</span>
                                    <span className="history-stat-label">WPM</span>
                                </div>
                                <div className="history-stat">
                                    <span className="history-stat-value">{item.accuracy}%</span>
                                    <span className="history-stat-label">정확도</span>
                                </div>
                                <div className="history-stat">
                                    <span className="history-stat-value">{formatTime(item.time)}</span>
                                    <span className="history-stat-label">시간</span>
                                </div>
                            </div>
                            <p className="history-text">"{item.text}"</p>
                        </div>
                    ))
                )}
            </div>
        </div>
    )
}

export default HistoryPage
