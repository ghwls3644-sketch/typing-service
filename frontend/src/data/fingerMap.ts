import type { FingerName } from '../types/keyboard'

// 손가락별 색상 (키보드 키 배경 힌트 + HandGuide 동일 색상)
export const FINGER_COLORS: Record<FingerName, string> = {
  'left-pinky':  '#e57373',  // 빨강 계열
  'left-ring':   '#ffb74d',  // 주황
  'left-middle': '#fff176',  // 노랑
  'left-index':  '#81c784',  // 초록
  'right-index': '#4fc3f7',  // 하늘
  'right-middle':'#7986cb',  // 남색
  'right-ring':  '#ba68c8',  // 보라
  'right-pinky': '#f06292',  // 분홍
  'thumb':       '#90a4ae',  // 회색
}

// 손가락별 한글 이름
export const FINGER_NAMES_KO: Record<FingerName, string> = {
  'left-pinky':  '왼손 새끼',
  'left-ring':   '왼손 약지',
  'left-middle': '왼손 중지',
  'left-index':  '왼손 검지',
  'right-index': '오른손 검지',
  'right-middle':'오른손 중지',
  'right-ring':  '오른손 약지',
  'right-pinky': '오른손 새끼',
  'thumb':       '엄지',
}
