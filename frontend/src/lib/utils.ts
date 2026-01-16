/**
 * 유틸리티 함수
 */

/**
 * UUID 생성 (세션 ID용)
 */
export function generateUUID(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0
        const v = c === 'x' ? r : (r & 0x3 | 0x8)
        return v.toString(16)
    })
}

/**
 * 로컬 스토리지 헬퍼
 */
export const storage = {
    get<T>(key: string, defaultValue: T): T {
        try {
            const item = localStorage.getItem(key)
            return item ? JSON.parse(item) : defaultValue
        } catch {
            return defaultValue
        }
    },

    set<T>(key: string, value: T): void {
        try {
            localStorage.setItem(key, JSON.stringify(value))
        } catch (e) {
            console.error('Storage error:', e)
        }
    },

    remove(key: string): void {
        localStorage.removeItem(key)
    }
}

/**
 * 시간 포맷팅
 */
export function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
}

/**
 * 날짜 포맷팅
 */
export function formatDate(date: Date | string): string {
    const d = typeof date === 'string' ? new Date(date) : date
    return d.toLocaleString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    })
}

/**
 * 디바운스
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
    fn: T,
    delay: number
): (...args: Parameters<T>) => void {
    let timeoutId: ReturnType<typeof setTimeout>
    return (...args: Parameters<T>) => {
        clearTimeout(timeoutId)
        timeoutId = setTimeout(() => fn(...args), delay)
    }
}

/**
 * 세션 ID 가져오기 또는 생성
 */
export function getSessionId(): string {
    let sessionId = storage.get<string>('session_id', '')
    if (!sessionId) {
        sessionId = generateUUID()
        storage.set('session_id', sessionId)
    }
    return sessionId
}
