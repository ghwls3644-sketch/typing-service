/**
 * API 클라이언트
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

interface RequestOptions extends RequestInit {
    params?: Record<string, string>
}

class ApiClient {
    private baseUrl: string
    private token: string | null = null

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl
        this.token = localStorage.getItem('access_token')
    }

    setToken(token: string | null) {
        this.token = token
        if (token) {
            localStorage.setItem('access_token', token)
        } else {
            localStorage.removeItem('access_token')
        }
    }

    private getHeaders(): HeadersInit {
        const headers: HeadersInit = {
            'Content-Type': 'application/json',
        }
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`
        }
        return headers
    }

    private buildUrl(endpoint: string, params?: Record<string, string>): string {
        const url = new URL(`${this.baseUrl}${endpoint}`)
        if (params) {
            Object.entries(params).forEach(([key, value]) => {
                url.searchParams.append(key, value)
            })
        }
        return url.toString()
    }

    async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
        const { params, ...fetchOptions } = options
        const url = this.buildUrl(endpoint, params)

        const response = await fetch(url, {
            ...fetchOptions,
            headers: {
                ...this.getHeaders(),
                ...fetchOptions.headers,
            },
        })

        if (!response.ok) {
            const error = await response.json().catch(() => ({}))
            throw new Error(error.detail || `HTTP Error: ${response.status}`)
        }

        return response.json()
    }

    async get<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
        return this.request<T>(endpoint, { method: 'GET', params })
    }

    async post<T>(endpoint: string, data?: unknown): Promise<T> {
        return this.request<T>(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        })
    }

    async patch<T>(endpoint: string, data?: unknown): Promise<T> {
        return this.request<T>(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data),
        })
    }

    async delete<T>(endpoint: string): Promise<T> {
        return this.request<T>(endpoint, { method: 'DELETE' })
    }
}

export const api = new ApiClient(API_BASE_URL)
export default api
