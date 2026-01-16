import { Routes, Route } from 'react-router-dom'
import Layout from '@/components/Layout/Layout'
import HomePage from '@/pages/HomePage'
import PracticePage from '@/pages/PracticePage'
import ResultPage from '@/pages/ResultPage'
import HistoryPage from '@/pages/HistoryPage'
import LeaderboardPage from '@/pages/LeaderboardPage'
import ChallengePage from '@/pages/ChallengePage'

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
            </Route>
        </Routes>
    )
}

export default App


