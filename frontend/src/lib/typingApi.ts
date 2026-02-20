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

// v4.0 Practice API
export interface PracticeItemsResponse {
    items: string[]
    pack_code: string | null
    total_available: number
    message?: string
}

export async function fetchPracticeItems(
    mode: 'word' | 'short',
    language: 'ko' | 'en',
    difficulty: 1 | 2 | 3,
    count: number = 10
): Promise<PracticeItemsResponse> {
    const params: Record<string, string> = {
        mode,
        language,
        difficulty: String(difficulty),
        count: String(count)
    }
    return api.get<PracticeItemsResponse>('/texts/items/practice_items/', params)
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

// === 대시보드 통계 API ===
export interface DashboardOverview {
    period_days: number
    total_sessions: number
    total_duration_ms: number
    avg_wpm: number
    avg_accuracy: number
    best_wpm: number | null
    best_accuracy: number | null
    current_streak: number
    longest_streak: number
    today: {
        total_sessions: number
        avg_wpm: number
        avg_accuracy: number
        total_duration_ms: number
    }
}

export async function fetchDashboardOverview(guestSessionId?: string): Promise<DashboardOverview> {
    const params: Record<string, string> = {}
    if (guestSessionId) params.guest_session_id = guestSessionId
    return api.get<DashboardOverview>('/stats/client/overview/', params)
}

// === 리더보드 API ===
export interface LeaderboardEntry {
    rank: number
    name: string
    avg_wpm: string
    best_wpm: string
    avg_accuracy: string
    total_sessions: number
    status?: string
}

export interface LeaderboardSnapshot {
    id: number
    period_start: string
    period_end: string
    language: string
    total_entries: number
    entries: LeaderboardEntry[]
}

export interface LeaderboardMeResponse {
    rank: number | null
    entry: LeaderboardEntry | null
    total_entries: number
    around: LeaderboardEntry[]
}

export async function fetchLeaderboardLatest(language?: string): Promise<LeaderboardSnapshot> {
    const params: Record<string, string> = {}
    if (language) params.language = language
    return api.get<LeaderboardSnapshot>('/leaderboard/snapshots/latest/', params)
}

export async function fetchLeaderboardMe(guestSessionId?: string, language?: string): Promise<LeaderboardMeResponse> {
    const params: Record<string, string> = {}
    if (guestSessionId) params.guest_session_id = guestSessionId
    if (language) params.language = language
    return api.get<LeaderboardMeResponse>('/leaderboard/snapshots/me/', params)
}

// === 데일리 챌린지 API ===
export interface DailyChallengeInfo {
    id: number
    date: string
    title: string
    description: string
    difficulty: number
    difficulty_display: string
    target_wpm: number | null
    target_accuracy: string | null
    target_sessions: number
    reward_points: number
    participants_count: number
    completed_count: number
    is_active: boolean
    my_progress?: ChallengeProgress
}

export interface ChallengeProgress {
    id: number
    challenge_title: string
    status: string
    current_wpm: number
    target_wpm: number | null
    progress_wpm: number
    current_accuracy: number
    target_accuracy: number | null
    progress_accuracy: number
    current_sessions: number
    target_sessions: number
    progress_sessions: number
    just_completed?: boolean
}

export async function fetchDailyChallenge(guestSessionId?: string): Promise<DailyChallengeInfo | null> {
    const params: Record<string, string> = {}
    if (guestSessionId) params.guest_session_id = guestSessionId
    try {
        return await api.get<DailyChallengeInfo>('/challenges/daily/today/', params)
    } catch {
        // 챌린지가 없는 날(404)은 정상 상황 → null 반환
        return null
    }
}

export async function joinDailyChallenge(challengeId: number, guestSessionId?: string): Promise<ChallengeProgress> {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const raw: any = await api.post('/challenges/daily/join/', {
        challenge_id: challengeId,
        guest_session_id: guestSessionId,
    })
    // Backend returns ClientChallengeSerializer with nested `challenge` object.
    // Map it to the flat ChallengeProgress type the UI expects.
    const c = raw.challenge || {}
    return {
        id: raw.id,
        challenge_title: c.title || '',
        status: raw.status || 'in_progress',
        current_wpm: raw.current_wpm || 0,
        target_wpm: c.target_wpm ?? null,
        progress_wpm: c.target_wpm ? Math.min((raw.current_wpm || 0) / c.target_wpm * 100, 100) : 0,
        current_accuracy: raw.current_accuracy || 0,
        target_accuracy: c.target_accuracy ?? null,
        progress_accuracy: c.target_accuracy ? Math.min((raw.current_accuracy || 0) / Number(c.target_accuracy) * 100, 100) : 0,
        current_sessions: raw.current_sessions || 0,
        target_sessions: c.target_sessions || 0,
        progress_sessions: c.target_sessions ? Math.min((raw.current_sessions || 0) / c.target_sessions * 100, 100) : 0,
    }
}

export async function submitDailyChallenge(
    challengeId: number,
    wpm: number,
    accuracy: number,
    guestSessionId?: string
): Promise<ChallengeProgress> {
    return api.post<ChallengeProgress>('/challenges/daily/submit/', {
        challenge_id: challengeId,
        wpm,
        accuracy,
        guest_session_id: guestSessionId,
    })
}

export interface DailyChallengeRanking {
    challenge: DailyChallengeInfo
    rankings: LeaderboardEntry[]
    total_participants: number
}

export async function fetchDailyChallengeRanking(): Promise<DailyChallengeRanking> {
    return api.get<DailyChallengeRanking>('/challenges/daily/ranking/')
}

// === Export/Import API ===
export interface ExportData {
    schema_version: number
    exported_at: string
    guest_session_id: string
    total_sessions: number
    sessions: SessionCreateData[]
}

export interface ImportResult {
    imported: number
    skipped: number
    errors: number
    total: number
}

export async function exportSessions(guestSessionId: string): Promise<ExportData> {
    return api.get<ExportData>('/sessions/export/', { guest_session_id: guestSessionId })
}

export async function importSessions(data: ExportData): Promise<ImportResult> {
    return api.post<ImportResult>('/sessions/import/', data)
}

