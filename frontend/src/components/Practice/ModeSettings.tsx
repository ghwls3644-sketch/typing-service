import type { PracticeMode, PracticeSettings } from '../../types/practice'
import './ModeSelector.css'

interface ModeSettingsProps {
  mode: PracticeMode
  settings: PracticeSettings
  onSettingsChange: (settings: Partial<PracticeSettings>) => void
}

function ModeSettings({ mode, settings, onSettingsChange }: ModeSettingsProps) {
  // 언어 설정 (한글 특화 드릴 제외)
  const renderLanguageSettings = () => {
    // 한글 특화 드릴은 한글 전용
    if (mode === 'kor_drill') {
      return (
        <div className="setting-item">
          <span className="setting-label">언어</span>
          <div className="setting-options">
            <button className="setting-btn active" disabled>
              🇰🇷 한글 전용
            </button>
          </div>
        </div>
      )
    }
    
    return (
      <div className="setting-item">
        <span className="setting-label">언어</span>
        <div className="setting-options">
          <button
            className={`setting-btn ${settings.language === 'korean' ? 'active' : ''}`}
            onClick={() => onSettingsChange({ language: 'korean' })}
          >
            🇰🇷 한글
          </button>
          <button
            className={`setting-btn ${settings.language === 'english' ? 'active' : ''}`}
            onClick={() => onSettingsChange({ language: 'english' })}
          >
            🇺🇸 영어
          </button>
        </div>
      </div>
    )
  }

  // 타임어택 설정
  const renderTimeAttackSettings = () => (
    <div className="setting-item">
      <span className="setting-label">제한 시간</span>
      <div className="setting-options">
        {[30, 60, 120].map(sec => (
          <button
            key={sec}
            className={`setting-btn ${settings.timeLimitSec === sec ? 'active' : ''}`}
            onClick={() => onSettingsChange({ timeLimitSec: sec })}
          >
            {sec}초
          </button>
        ))}
      </div>
    </div>
  )

  // 정확도 챌린지 설정
  const renderAccuracySettings = () => (
    <div className="setting-item">
      <span className="setting-label">오타 제한</span>
      <div className="setting-options">
        {[3, 5, 10].map(n => (
          <button
            key={n}
            className={`setting-btn ${settings.maxErrors === n ? 'active' : ''}`}
            onClick={() => onSettingsChange({ maxErrors: n })}
          >
            {n}회
          </button>
        ))}
      </div>
    </div>
  )

  // 문장/단어 수 설정
  const renderItemCountSettings = () => (
    <div className="setting-item">
      <span className="setting-label">{mode === 'word' ? '단어 수' : '문장 수'}</span>
      <div className="setting-options">
        {[5, 10, 20].map(n => (
          <button
            key={n}
            className={`setting-btn ${settings.itemsPerSession === n ? 'active' : ''}`}
            onClick={() => onSettingsChange({ itemsPerSession: n })}
          >
            {n}개
          </button>
        ))}
      </div>
    </div>
  )

  return (
    <div className="mode-settings">
      <h3 className="settings-title">⚙️ 설정</h3>
      <div className="settings-grid">
        {renderLanguageSettings()}
        
        {mode === 'time_attack' && renderTimeAttackSettings()}
        {mode === 'accuracy_challenge' && renderAccuracySettings()}
        {(mode === 'sentence' || mode === 'word' || mode === 'kor_drill') && renderItemCountSettings()}
      </div>
    </div>
  )
}

export default ModeSettings
