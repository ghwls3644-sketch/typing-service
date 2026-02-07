import './LeaderboardPage.css'

function LeaderboardPage() {
    return (
        <div className="leaderboard-page container">
            <div className="coming-soon">
                <div className="coming-soon-icon">🏆</div>
                <h1 className="coming-soon-title">랭킹 시스템</h1>
                <div className="coming-soon-badge">준비중</div>
                <p className="coming-soon-description">
                    곧 다른 사용자들과 경쟁할 수 있는<br/>
                    랭킹 시스템이 추가될 예정입니다!
                </p>
                <div className="coming-soon-features">
                    <div className="feature-preview">
                        <span className="feature-icon">🥇</span>
                        <span>주간/월간 랭킹</span>
                    </div>
                    <div className="feature-preview">
                        <span className="feature-icon">📊</span>
                        <span>상세 통계 비교</span>
                    </div>
                    <div className="feature-preview">
                        <span className="feature-icon">🎖️</span>
                        <span>업적 시스템</span>
                    </div>
                </div>
                <a href="/" className="btn btn-primary btn-lg">
                    🏠 홈으로 돌아가기
                </a>
            </div>
        </div>
    )
}

export default LeaderboardPage
