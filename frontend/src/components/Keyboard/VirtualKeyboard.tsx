import { KEYBOARD_ROWS } from '../../data/keyMapping'
import { FINGER_COLORS } from '../../data/fingerMap'
import type { KeyInfo } from '../../types/keyboard'
import './VirtualKeyboard.css'

interface VirtualKeyboardProps {
  nextKeys: string[]          // 다음에 눌러야 할 키 code 목록 (Shift 포함 가능)
  pressedKeys: Set<string>    // 현재 물리적으로 눌린 키 Set
  language: 'korean' | 'english'
  showPressedKeys: boolean
  showFingerColors: boolean
}

function VirtualKeyboard({ nextKeys, pressedKeys, language, showPressedKeys, showFingerColors }: VirtualKeyboardProps) {
  const nextKeySet = new Set(nextKeys)

  const getKeyLabel = (key: KeyInfo): string => {
    if (key.width && key.width > 1.2 && key.label !== 'Space') {
      return key.label // 기능키는 그대로
    }
    if (language === 'korean' && key.labelKo) {
      return key.labelKo
    }
    return key.label
  }

  const getSubLabel = (key: KeyInfo): string | null => {
    if (key.width && key.width > 1.2) return null
    if (language === 'korean') {
      // 한글 모드: 영문 label을 서브로
      if (key.labelKo) return key.label
      return key.labelShift || null
    }
    // 영문 모드: shift 문자를 서브로
    return key.labelShift || null
  }

  const getClassNames = (key: KeyInfo): string => {
    const classes = ['key']

    if (nextKeySet.has(key.code)) {
      classes.push('key--highlight')
    }
    if (showPressedKeys && pressedKeys.has(key.code)) {
      classes.push('key--pressed')
    }
    if (key.code === 'Space') {
      classes.push('key--space')
    }
    if (key.width && key.width > 1.2 && key.label !== 'Space') {
      classes.push('key--fn')
    }

    return classes.join(' ')
  }

  const getStyle = (key: KeyInfo): React.CSSProperties => {
    const style: React.CSSProperties = {}
    if (key.width) {
      style.flex = `${key.width}`
    }
    if (showFingerColors && !key.width || (key.width && key.width <= 1.2)) {
      style.borderBottomColor = FINGER_COLORS[key.finger]
    }
    return style
  }

  return (
    <div className="keyboard">
      {KEYBOARD_ROWS.map((row, rowIdx) => (
        <div key={rowIdx} className="keyboard-row">
          {row.map(key => {
            const subLabel = getSubLabel(key)
            return (
              <div
                key={key.code}
                className={getClassNames(key)}
                style={getStyle(key)}
                data-code={key.code}
              >
                {subLabel && <span className="key-sub">{subLabel}</span>}
                <span className="key-main">{getKeyLabel(key)}</span>
              </div>
            )
          })}
        </div>
      ))}
    </div>
  )
}

export default VirtualKeyboard
