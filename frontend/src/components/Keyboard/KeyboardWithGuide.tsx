import VirtualKeyboard from './VirtualKeyboard'
import HandGuide from './HandGuide'
import { getKeyByCode } from '../../data/keyMapping'
import type { FingerName } from '../../types/keyboard'

interface KeyboardWithGuideProps {
  nextKeys: string[]
  pressedKeys: Set<string>
  language: 'korean' | 'english'
  showKeyboard: boolean
  showHandGuide: boolean
  showPressedKeys: boolean
  showFingerColors: boolean
}

function KeyboardWithGuide({
  nextKeys,
  pressedKeys,
  language,
  showKeyboard,
  showHandGuide,
  showPressedKeys,
  showFingerColors,
}: KeyboardWithGuideProps) {
  if (!showKeyboard) return null

  // 다음 키의 손가락 계산 (HandGuide용)
  const activeFingers: FingerName[] = []
  if (showHandGuide && nextKeys.length > 0) {
    for (const code of nextKeys) {
      const keyInfo = getKeyByCode(code)
      if (keyInfo && !activeFingers.includes(keyInfo.finger)) {
        activeFingers.push(keyInfo.finger)
      }
    }
  }

  return (
    <div className="keyboard-guide-wrapper">
      <VirtualKeyboard
        nextKeys={nextKeys}
        pressedKeys={pressedKeys}
        language={language}
        showPressedKeys={showPressedKeys}
        showFingerColors={showFingerColors}
      />
      {showHandGuide && (
        <HandGuide activeFingers={activeFingers} />
      )}
    </div>
  )
}

export default KeyboardWithGuide
