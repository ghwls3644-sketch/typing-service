import { Outlet, Link, useLocation } from 'react-router-dom'
import './Layout.css'

function Layout() {
    const location = useLocation()

    const navItems = [
        { path: '/', label: '홈', icon: '🏠' },
        { path: '/practice', label: '연습', icon: '⌨️' },
        { path: '/challenge', label: '챌린지', icon: '⚡' },
        { path: '/leaderboard', label: '랭킹', icon: '🏆' },
        { path: '/history', label: '기록', icon: '📊' },
    ]

    return (
        <div className="layout">
            <header className="header">
                <div className="container header-content">
                    <Link to="/" className="logo">
                        <span className="logo-icon">⌨️</span>
                        <span className="logo-text">타자 연습</span>
                    </Link>
                    <nav className="nav">
                        {navItems.map((item) => (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
                            >
                                <span className="nav-icon">{item.icon}</span>
                                <span className="nav-label">{item.label}</span>
                            </Link>
                        ))}
                    </nav>
                </div>
            </header>
            <main className="main">
                <Outlet />
            </main>
            <footer className="footer">
                <div className="container">
                    <p>&copy; 2026 타자 연습 서비스. All rights reserved.</p>
                </div>
            </footer>
        </div>
    )
}

export default Layout
