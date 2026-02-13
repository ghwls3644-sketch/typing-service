import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { getChallengeBest, getChallengeHistory } from '../lib/challengeStorage'
import { exportSessions, importSessions, getGuestSessionId } from '../lib/typingApi'
import type { ExportData } from '../lib/typingApi'
import type { ChallengeSessionLocal, ChallengeBest } from '../types/challenge'
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

type TabType = 'practice' | 'challenge'

function HistoryPage() {
    const [tab, setTab] = useState<TabType>('practice')
    const [history, setHistory] = useState<HistoryItem[]>([])
    const [filter, setFilter] = useState<'all' | 'korean' | 'english'>('all')
    
    // 챌린지 데이터
    const [challengeBest, setChallengeBest] = useState<ChallengeBest | null>(null)
    const [challengeHistory, setChallengeHistory] = useState<ChallengeSessionLocal[]>([])
    const [exportStatus, setExportStatus] = useState<string | null>(null)
    const [importStatus, setImportStatus] = useState<string | null>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)

    // 내보내기 핸들러
    const handleExport = async () => {
        setExportStatus('내보내는 중...')
        try {
            const guestId = getGuestSessionId()
            const data = await exportSessions(guestId)
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `typing-data-${new Date().toISOString().slice(0, 10)}.json`
            a.click()
            URL.revokeObjectURL(url)
            setExportStatus(`✅ ${data.total_sessions}개 세션 내보내기 완료`)
        } catch {
            setExportStatus('❌ 내보내기 실패')
        }
        setTimeout(() => setExportStatus(null), 3000)
    }

    // 가져오기 핸들러
    const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return
        setImportStatus('가져오는 중...')
        try {
            const text = await file.text()
            const data: ExportData = JSON.parse(text)
            const result = await importSessions(data)
            setImportStatus(`✅ ${result.imported}개 가져옴, ${result.skipped}개 중복`)
        } catch {
            setImportStatus('❌ 가져오기 실패 (파일 형식 확인)')
        }
        if (fileInputRef.current) fileInputRef.current.value = ''
        setTimeout(() => setImportStatus(null), 4000)
    }

    // 연습 히스토리 로드 (샘플 데이터)
    useEffect(() => {
        const sampleHistory: HistoryItem[] = [
            {
                id: '1',
                date: '2026-02-07 14:00',
                wpm: 75,
                accuracy: 96,
                time: 45.2,
                language: 'korean',
                text: '하늘 아래 첫 동네에 봄이 찾아왔다.'
            },
            {
                id: '2',
                date: '2026-02-07 13:30',
                wpm: 82,
                accuracy: 94,
                time: 38.5,
                language: 'english',
                text: 'The quick brown fox jumps over the lazy dog.'
            },
            {
                id: '3',
                date: '2026-02-07 13:00',
                wpm: 68,
                accuracy: 98,
                time: 52.1,
                language: 'korean',
                text: '타자 연습은 꾸준히 하면 실력이 늘어납니다.'
            }
        ]
        setHistory(sampleHistory)
    }, [])

    // 챌린지 데이터 로드
    useEffect(() => {
        setChallengeBest(getChallengeBest())
        setChallengeHistory(getChallengeHistory())
    }, [tab])

    const filteredHistory = history.filter(item => {
        if (filter === 'all') return true
        return item.language === filter
    })

    // 평균 통계
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

    const formatDate = (timestamp: number) => {
        const date = new Date(timestamp)
        return date.toLocaleString('ko-KR', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    return (
        <div className="history-page container">
            <div className="history-header">
                <h1>연습 기록</h1>
                <div className="history-actions">
                    <button className="btn btn-ghost" onClick={handleExport} title="데이터 내보내기">
                        📤 내보내기
                    </button>
                    <button className="btn btn-ghost" onClick={() => fileInputRef.current?.click()} title="데이터 가져오기">
                        📥 가져오기
                    </button>
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept=".json"
                        style={{ display: 'none' }}
                        onChange={handleImport}
                    />
                    <Link to="/practice" className="btn btn-primary">
                        ⌨️ 연습하기
                    </Link>
                </div>
            </div>
            {(exportStatus || importStatus) && (
                <div className="export-import-status">
                    {exportStatus || importStatus}
                </div>
            )}

            {/* 탭 */}
            <div className="history-tabs">
                <button
                    className={`tab-btn ${tab === 'practice' ? 'active' : ''}`}
                    onClick={() => setTab('practice')}
                >
                    📝 연습
                </button>
                <button
                    className={`tab-btn ${tab === 'challenge' ? 'active' : ''}`}
                    onClick={() => setTab('challenge')}
                >
                    🔥 챌린지
                </button>
            </div>

            {/* 연습 탭 */}
            {tab === 'practice' && (
                <>
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
                </>
            )}

            {/* 챌린지 탭 */}
            {tab === 'challenge' && (
                <div className="challenge-history">
                    {/* 최고기록 */}
                    {challengeBest ? (
                        <div className="best-record-card">
                            <div className="best-record-header">
                                <span className="best-icon">🏆</span>
                                <span className="best-title">최고기록</span>
                            </div>
                            <div className="best-stats">
                                <div className="best-stat main">
                                    <span className="best-stat-value">{challengeBest.bestScore}</span>
                                    <span className="best-stat-label">점수</span>
                                </div>
                                <div className="best-stat">
                                    <span className="best-stat-value">{challengeBest.bestMaxCombo}</span>
                                    <span className="best-stat-label">최대 콤보</span>
                                </div>
                                <div className="best-stat">
                                    <span className="best-stat-value">{challengeBest.bestWpm}</span>
                                    <span className="best-stat-label">WPM</span>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="no-best-record">
                            <span>🎮</span>
                            <p>아직 챌린지 기록이 없습니다</p>
                            <Link to="/challenge" className="btn btn-primary">
                                🔥 첫 챌린지 시작하기
                            </Link>
                        </div>
                    )}

                    {/* 최근 기록 */}
                    {challengeHistory.length > 0 && (
                        <>
                            <h3 className="recent-title">최근 기록</h3>
                            <div className="challenge-history-list">
                                {challengeHistory.map((session) => (
                                    <div key={session.id} className="challenge-history-item">
                                        <div className="challenge-history-date">
                                            {formatDate(session.playedAt)}
                                        </div>
                                        <div className="challenge-history-stats">
                                            <span className="ch-score">{session.extra.score}점</span>
                                            <span className="ch-combo">{session.extra.maxCombo}콤보</span>
                                            <span className="ch-wpm">{session.base.wpm} WPM</span>
                                            <span className="ch-accuracy">{session.base.accuracy}%</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </>
                    )}

                    {/* 챌린지 시작 버튼 */}
                    <div className="challenge-cta-bottom">
                        <Link to="/challenge" className="btn btn-warning btn-lg">
                            🔥 60초 챌린지 도전하기
                        </Link>
                    </div>
                </div>
            )}
        </div>
    )
}

export default HistoryPage
