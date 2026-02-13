import { DIFFICULTY_LEVELS, type PracticeMode, type PracticeSettings } from '../../types/practice'
import './ModeSelector.css'

interface ModeSettingsProps {
  mode: PracticeMode
  settings: PracticeSettings
  onSettingsChange: (settings: Partial<PracticeSettings>) => void
}

function ModeSettings({ mode, settings, onSettingsChange }: ModeSettingsProps) {
  return (
    <div className="mode-settings">
      <h3 className="settings-title">⚙️ 설정</h3>
      <div className="settings-grid">
        {/* 언어 설정 */}
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

        {/* 난이도 설정 (v4.0 신규) */}
        <div className="setting-item">
          <span className="setting-label">난이도</span>
          <div className="setting-options">
            {DIFFICULTY_LEVELS.map(level => (
              <button
                key={level.value}
                className={`setting-btn ${settings.difficulty === level.value ? 'active' : ''}`}
                onClick={() => onSettingsChange({ difficulty: level.value })}
                title={level.description}
              >
                {level.name}
              </button>
            ))}
          </div>
        </div>

        {/* 아이템 수 설정 */}
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

        {/* 특수 모드 설정 */}
        <div className="setting-item">
          <span className="setting-label">특수 모드</span>
          <div className="setting-options">
            <button
              className={`setting-btn ${settings.isBlindMode ? 'active' : ''}`}
              onClick={() => onSettingsChange({ isBlindMode: !settings.isBlindMode })}
              title="입력할 때 원본 텍스트가 숨겨집니다"
            >
              🕶️ 블라인드
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ModeSettings
