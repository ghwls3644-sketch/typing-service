/**
 * Typing Service API Functions
 */
import api from './api'

// Types
export interface TextPack {
    id: number
    title: string
    language: 'ko' | 'en'
    difficulty: number
    item_count: number
}

export interface TextItem {
    id: number
    content: string
    length: number
    order: number
}

export interface TextPackDetail extends TextPack {
    items: TextItem[]
    source: string
    description: string
}

export interface SessionCreateData {
    mode: string
    language: string
    text_content: string
    duration_ms: number
    input_length: number
    correct_length: number
    error_count: number
    accuracy: number
    wpm: number
    cpm?: number
    metadata?: Record<string, unknown>
    guest_session_id?: string
}

export interface SessionResponse {
    id: number
    mode: string
    language: string
    text_content: string
    wpm: string
    accuracy: string
    duration_ms: number
    started_at: string
}

// Text Pack APIs
export async function fetchTextPacks(language?: string, difficulty?: number): Promise<TextPack[]> {
    const params: Record<string, string> = {}
    if (language) params.language = language
    if (difficulty) params.difficulty = String(difficulty)
    return api.get<TextPack[]>('/texts/packs/', params)
}

export async function fetchTextPackDetail(packId: number): Promise<TextPackDetail> {
    return api.get<TextPackDetail>(`/texts/packs/${packId}/`)
}

export async function fetchRandomPack(language?: string, difficulty?: number): Promise<TextPackDetail> {
    const params: Record<string, string> = {}
    if (language) params.language = language
    if (difficulty) params.difficulty = String(difficulty)
    return api.get<TextPackDetail>('/texts/packs/random/', params)
}

// Text Item APIs
export async function fetchTextItems(packId?: number, language?: string): Promise<TextItem[]> {
    const params: Record<string, string> = {}
    if (packId) params.pack = String(packId)
    if (language) params.language = language
    return api.get<TextItem[]>('/texts/items/', params)
}

// Session APIs
export async function saveSession(data: SessionCreateData): Promise<SessionResponse> {
    return api.post<SessionResponse>('/sessions/', data)
}

export async function fetchSessionHistory(
    language?: string,
    mode?: string,
    guestSessionId?: string
): Promise<SessionResponse[]> {
    const params: Record<string, string> = {}
    if (language) params.language = language
    if (mode) params.mode = mode
    if (guestSessionId) params.guest_session_id = guestSessionId
    return api.get<SessionResponse[]>('/sessions/', params)
}

export async function fetchRecentSessions(guestSessionId?: string): Promise<SessionResponse[]> {
    const params: Record<string, string> = {}
    if (guestSessionId) params.guest_session_id = guestSessionId
    return api.get<SessionResponse[]>('/sessions/recent/', params)
}

// Guest Session ID
const GUEST_SESSION_KEY = 'typing_guest_session_id'

export function getGuestSessionId(): string {
    let id = localStorage.getItem(GUEST_SESSION_KEY)
    if (!id) {
        id = `guest_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`
        localStorage.setItem(GUEST_SESSION_KEY, id)
    }
    return id
}

// === 로컬 백업 시스템 ===
const PENDING_SESSIONS_KEY = 'typing_pending_sessions'

interface PendingSession extends SessionCreateData {
    savedAt: number
}

/**
 * 실패한 세션을 로컬에 저장
 */
export function savePendingSession(data: SessionCreateData): void {
    try {
        const pending: PendingSession[] = JSON.parse(localStorage.getItem(PENDING_SESSIONS_KEY) || '[]')
        pending.push({ ...data, savedAt: Date.now() })
        // 최대 20개 유지 (오래된 것 제거)
        const trimmed = pending.slice(-20)
        localStorage.setItem(PENDING_SESSIONS_KEY, JSON.stringify(trimmed))
    } catch (e) {
        console.error('로컬 저장 실패:', e)
    }
}

/**
 * 대기 중인 세션 목록 조회
 */
export function getPendingSessions(): PendingSession[] {
    try {
        return JSON.parse(localStorage.getItem(PENDING_SESSIONS_KEY) || '[]')
    } catch {
        return []
    }
}

/**
 * 대기 중인 세션 동기화 시도
 */
export async function syncPendingSessions(): Promise<{ synced: number; failed: number }> {
    const pending = getPendingSessions()
    if (pending.length === 0) return { synced: 0, failed: 0 }

    let synced = 0
    const stillPending: PendingSession[] = []

    for (const session of pending) {
        try {
            // eslint-disable-next-line @typescript-eslint/no-unused-vars
            const { savedAt, ...data } = session
            await saveSession(data)
            synced++
        } catch {
            stillPending.push(session)
        }
    }

    localStorage.setItem(PENDING_SESSIONS_KEY, JSON.stringify(stillPending))
    return { synced, failed: stillPending.length }
}

/**
 * 세션 저장 (실패 시 로컬 백업)
 */
export async function saveSessionWithBackup(data: SessionCreateData): Promise<SessionResponse | null> {
    try {
        const response = await saveSession(data)
        return response
    } catch (e) {
        console.warn('세션 저장 실패, 로컬에 백업:', e)
        savePendingSession(data)
        return null
    }
}
