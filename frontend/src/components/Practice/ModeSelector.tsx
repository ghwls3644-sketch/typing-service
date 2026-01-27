import { PRACTICE_MODES, type PracticeMode, type ModeConfig } from '../../types/practice'
import './ModeSelector.css'

interface ModeSelectorProps {
  selectedMode: PracticeMode
  onSelectMode: (mode: PracticeMode) => void
  onStartPractice: () => void
}

function ModeSelector({ selectedMode, onSelectMode, onStartPractice }: ModeSelectorProps) {
  return (
    <div className="mode-selector">
      <h2 className="mode-selector-title">연습 모드 선택</h2>
      <p className="mode-selector-subtitle">원하는 연습 방식을 선택하세요</p>
      
      <div className="mode-grid">
        {PRACTICE_MODES.map((mode: ModeConfig) => (
          <button
            key={mode.id}
            className={`mode-card ${selectedMode === mode.id ? 'selected' : ''} ${!mode.available ? 'disabled' : ''}`}
            onClick={() => mode.available && onSelectMode(mode.id)}
            disabled={!mode.available}
          >
            <span className="mode-icon">{mode.icon}</span>
            <span className="mode-name">{mode.name}</span>
            <span className="mode-desc">{mode.description}</span>
            {!mode.available && <span className="mode-badge">준비중</span>}
          </button>
        ))}
      </div>
      
      <button className="btn btn-primary btn-start" onClick={onStartPractice}>
        🚀 연습 시작하기
      </button>
    </div>
  )
}

export default ModeSelector
