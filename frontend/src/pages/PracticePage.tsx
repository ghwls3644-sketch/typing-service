import { useState, useEffect, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import './PracticePage.css'

// 샘플 문장 데이터
const sampleTexts = {
    korean: [
        '하늘 아래 첫 동네에 봄이 찾아왔다.',
        '빠른 갈색 여우가 게으른 개를 뛰어넘는다.',
        '오늘도 좋은 하루가 되기를 바랍니다.',
        '타자 연습은 꾸준히 하면 실력이 늘어납니다.',
        '컴퓨터 자판을 익히면 업무 효율이 올라갑니다.',
        '매일 조금씩 연습하면 어느새 달인이 됩니다.',
        '키보드를 보지 않고 치는 것이 목표입니다.',
        '정확하게 치는 것이 빠르게 치는 것보다 중요합니다.',
    ],
    english: [
        'The quick brown fox jumps over the lazy dog.',
        'Practice makes perfect in everything we do.',
        'Typing skills improve with consistent practice.',
        'Hello world, this is a typing practice app.',
        'Learning to type fast requires patience and dedication.',
        'Keep your fingers on the home row keys.',
        'Speed will come naturally with accuracy first.',
        'Every expert was once a beginner at typing.',
    ]
}

interface TypingStats {
    wpm: number
    accuracy: number
    time: number
    correctChars: number
    totalChars: number
    errors: number
}

function PracticePage() {
    const navigate = useNavigate()
    const inputRef = useRef<HTMLInputElement>(null)

    const [language, setLanguage] = useState<'korean' | 'english'>('korean')
    const [currentText, setCurrentText] = useState('')
    const [userInput, setUserInput] = useState('')
    const [isStarted, setIsStarted] = useState(false)
    const [isFinished, setIsFinished] = useState(false)
    const [startTime, setStartTime] = useState<number | null>(null)
    const [stats, setStats] = useState<TypingStats>({
        wpm: 0,
        accuracy: 100,
        time: 0,
        correctChars: 0,
        totalChars: 0,
        errors: 0
    })

    // 새 문장 선택
    const selectNewText = useCallback(() => {
        const texts = sampleTexts[language]
        const randomIndex = Math.floor(Math.random() * texts.length)
        setCurrentText(texts[randomIndex])
    }, [language])

    // 초기화
    useEffect(() => {
        selectNewText()
    }, [selectNewText])

    // 언어 변경 시 리셋
    useEffect(() => {
        resetPractice()
        selectNewText()
    }, [language])

    // 타이머 및 WPM 계산
    useEffect(() => {
        let interval: number | undefined

        if (isStarted && !isFinished && startTime) {
            interval = window.setInterval(() => {
                const elapsed = (Date.now() - startTime) / 1000 / 60 // 분 단위
                const wordsTyped = userInput.trim().split(/\s+/).filter(w => w).length
                const wpm = elapsed > 0 ? Math.round(wordsTyped / elapsed) : 0

                setStats(prev => ({ ...prev, wpm, time: (Date.now() - startTime) / 1000 }))
            }, 100)
        }

        return () => {
            if (interval) clearInterval(interval)
        }
    }, [isStarted, isFinished, startTime, userInput])

    // 입력 처리
    const handleInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value

        // 첫 입력 시 시작
        if (!isStarted && value.length > 0) {
            setIsStarted(true)
            setStartTime(Date.now())
        }

        setUserInput(value)

        // 정확도 계산
        let correct = 0
        let errors = 0
        for (let i = 0; i < value.length; i++) {
            if (value[i] === currentText[i]) {
                correct++
            } else {
                errors++
            }
        }

        const accuracy = value.length > 0 ? Math.round((correct / value.length) * 100) : 100
        setStats(prev => ({
            ...prev,
            accuracy,
            correctChars: correct,
            totalChars: value.length,
            errors
        }))

        // 완료 체크
        if (value === currentText) {
            finishPractice()
        }
    }

    // 연습 완료
    const finishPractice = () => {
        setIsFinished(true)
        const endTime = Date.now()
        const totalTime = startTime ? (endTime - startTime) / 1000 : 0
        const minutes = totalTime / 60
        const wordsTyped = currentText.trim().split(/\s+/).length
        const finalWpm = minutes > 0 ? Math.round(wordsTyped / minutes) : 0

        const finalStats = {
            ...stats,
            wpm: finalWpm,
            time: totalTime
        }
        setStats(finalStats)

        // 결과 페이지로 이동
        setTimeout(() => {
            navigate('/result', {
                state: {
                    stats: finalStats,
                    text: currentText,
                    language
                }
            })
        }, 500)
    }

    // 리셋
    const resetPractice = () => {
        setUserInput('')
        setIsStarted(false)
        setIsFinished(false)
        setStartTime(null)
        setStats({
            wpm: 0,
            accuracy: 100,
            time: 0,
            correctChars: 0,
            totalChars: 0,
            errors: 0
        })
    }

    // 다음 문장
    const nextSentence = () => {
        resetPractice()
        selectNewText()
        inputRef.current?.focus()
    }

    // 문자 렌더링 (색상 표시)
    const renderText = () => {
        return currentText.split('').map((char, index) => {
            let className = 'char'
            if (index < userInput.length) {
                className += userInput[index] === char ? ' correct' : ' incorrect'
            } else if (index === userInput.length) {
                className += ' current'
            }
            return (
                <span key={index} className={className}>
                    {char}
                </span>
            )
        })
    }

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60)
        const secs = Math.floor(seconds % 60)
        return `${mins}:${secs.toString().padStart(2, '0')}`
    }

    return (
        <div className="practice-page container">
            {/* 헤더 영역 */}
            <div className="practice-header">
                <h1>타자 연습</h1>
                <div className="language-toggle">
                    <button
                        className={`toggle-btn ${language === 'korean' ? 'active' : ''}`}
                        onClick={() => setLanguage('korean')}
                    >
                        🇰🇷 한글
                    </button>
                    <button
                        className={`toggle-btn ${language === 'english' ? 'active' : ''}`}
                        onClick={() => setLanguage('english')}
                    >
                        🇺🇸 영어
                    </button>
                </div>
            </div>

            {/* 통계 영역 */}
            <div className="stats-bar">
                <div className="stat-item">
                    <span className="stat-label">WPM</span>
                    <span className="stat-value">{stats.wpm}</span>
                </div>
                <div className="stat-item">
                    <span className="stat-label">정확도</span>
                    <span className="stat-value">{stats.accuracy}%</span>
                </div>
                <div className="stat-item">
                    <span className="stat-label">시간</span>
                    <span className="stat-value">{formatTime(stats.time)}</span>
                </div>
                <div className="stat-item">
                    <span className="stat-label">오류</span>
                    <span className="stat-value error">{stats.errors}</span>
                </div>
            </div>

            {/* 타이핑 영역 */}
            <div className="typing-area" onClick={() => inputRef.current?.focus()}>
                <div className="text-display">
                    {renderText()}
                </div>
                <input
                    ref={inputRef}
                    type="text"
                    className="typing-input"
                    value={userInput}
                    onChange={handleInput}
                    disabled={isFinished}
                    placeholder={isStarted ? '' : '여기를 클릭하고 타이핑을 시작하세요'}
                    autoFocus
                    autoComplete="off"
                    autoCapitalize="off"
                    spellCheck="false"
                />
            </div>

            {/* 진행률 바 */}
            <div className="progress-bar">
                <div
                    className="progress-fill"
                    style={{ width: `${(userInput.length / currentText.length) * 100}%` }}
                />
            </div>

            {/* 액션 버튼 */}
            <div className="practice-actions">
                <button className="btn btn-secondary" onClick={resetPractice}>
                    🔄 다시 시작
                </button>
                <button className="btn btn-primary" onClick={nextSentence}>
                    ➡️ 다음 문장
                </button>
            </div>

            {/* 도움말 */}
            <div className="help-text">
                <p>💡 정확하게 입력하면 글자가 <span className="text-success">초록색</span>으로,
                    틀리면 <span className="text-error">빨간색</span>으로 표시됩니다.</p>
            </div>
        </div>
    )
}

export default PracticePage
