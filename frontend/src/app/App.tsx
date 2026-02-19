import { Routes, Route, Link } from 'react-router-dom'
import Layout from '@/components/Layout/Layout'
import HomePage from '@/pages/HomePage'
import PracticePage from '@/pages/PracticePage'
import ResultPage from '@/pages/ResultPage'
import HistoryPage from '@/pages/HistoryPage'
import LeaderboardPage from '@/pages/LeaderboardPage'
import ChallengePage from '@/pages/ChallengePage'

function NotFoundPage() {
    return (
        <div style={{ textAlign: 'center', padding: '4rem 1rem' }}>
            <h1 style={{ fontSize: '3rem', marginBottom: '1rem' }}>404</h1>
            <p style={{ marginBottom: '2rem' }}>페이지를 찾을 수 없습니다.</p>
            <Link to="/">홈으로 돌아가기</Link>
        </div>
    )
}

function App() {
    return (
        <Routes>
            <Route path="/" element={<Layout />}>
                <Route index element={<HomePage />} />
                <Route path="practice" element={<PracticePage />} />
                <Route path="result" element={<ResultPage />} />
                <Route path="history" element={<HistoryPage />} />
                <Route path="leaderboard" element={<LeaderboardPage />} />
                <Route path="challenge" element={<ChallengePage />} />
                <Route path="*" element={<NotFoundPage />} />
            </Route>
        </Routes>
    )
}

export default App


