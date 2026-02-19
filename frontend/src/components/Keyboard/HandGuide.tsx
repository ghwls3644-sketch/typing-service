import type { FingerName } from '../../types/keyboard'
import { FINGER_COLORS } from '../../data/fingerMap'
import './HandGuide.css'

interface HandGuideProps {
  activeFingers: FingerName[]
}

// 손가락 SVG path (좌측 손 기준, 우측은 mirror)
// 간단한 손 실루엣 - 각 손가락을 개별 path로

interface FingerPath {
  finger: FingerName
  d: string  // SVG path
}

const LEFT_HAND_FINGERS: FingerPath[] = [
  { finger: 'left-pinky', d: 'M18,58 L18,30 Q18,24 22,24 Q26,24 26,30 L26,58' },
  { finger: 'left-ring', d: 'M30,58 L30,22 Q30,16 34,16 Q38,16 38,22 L38,58' },
  { finger: 'left-middle', d: 'M42,58 L42,18 Q42,12 46,12 Q50,12 50,18 L50,58' },
  { finger: 'left-index', d: 'M54,58 L54,22 Q54,16 58,16 Q62,16 62,22 L62,58' },
  { finger: 'thumb', d: 'M64,58 L68,48 Q72,42 76,46 Q78,50 74,56 L66,62' },
]

const RIGHT_HAND_FINGERS: FingerPath[] = [
  { finger: 'thumb', d: 'M16,58 L12,48 Q8,42 4,46 Q2,50 6,56 L14,62' },
  { finger: 'right-index', d: 'M18,58 L18,22 Q18,16 22,16 Q26,16 26,22 L26,58' },
  { finger: 'right-middle', d: 'M30,58 L30,18 Q30,12 34,12 Q38,12 38,18 L38,58' },
  { finger: 'right-ring', d: 'M42,58 L42,22 Q42,16 46,16 Q50,16 50,22 L50,58' },
  { finger: 'right-pinky', d: 'M54,58 L54,30 Q54,24 58,24 Q62,24 62,30 L62,58' },
]

function HandSvg({ fingers, activeFingers, label }: {
  fingers: FingerPath[]
  activeFingers: Set<FingerName>
  label: string
}) {
  return (
    <div className="hand-container">
      <svg viewBox="0 0 80 70" className="hand-svg">
        {/* 손바닥 */}
        <rect x="14" y="52" width="52" height="16" rx="8" fill="var(--bg-tertiary)" stroke="var(--text-muted)" strokeWidth="1" opacity="0.6" />

        {/* 손가락 */}
        {fingers.map(({ finger, d }) => {
          const isActive = activeFingers.has(finger)
          return (
            <path
              key={finger}
              d={d}
              fill={isActive ? FINGER_COLORS[finger] : 'var(--bg-tertiary)'}
              stroke={isActive ? FINGER_COLORS[finger] : 'var(--text-muted)'}
              strokeWidth={isActive ? 2 : 1}
              opacity={isActive ? 1 : 0.4}
              className={`hand-finger ${isActive ? 'hand-finger--active' : ''}`}
            />
          )
        })}
      </svg>
      <span className="hand-label">{label}</span>
    </div>
  )
}

function HandGuide({ activeFingers }: HandGuideProps) {
  const activeSet = new Set(activeFingers)

  return (
    <div className="hand-guide">
      <HandSvg fingers={LEFT_HAND_FINGERS} activeFingers={activeSet} label="L" />
      <HandSvg fingers={RIGHT_HAND_FINGERS} activeFingers={activeSet} label="R" />
    </div>
  )
}

export default HandGuide
