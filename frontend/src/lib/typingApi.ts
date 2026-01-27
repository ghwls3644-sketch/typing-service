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
