const FALLBACK_URL = 'https://hiro-production-1130.up.railway.app'

const raw = (import.meta.env.VITE_API_URL as string | undefined)?.trim()

function normalize(url: string): string {
    let cleaned = url.replace(/\/+$/, '')
    if (!/^https?:\/\//i.test(cleaned)) {
        cleaned = `https://${cleaned}`
    }
    return cleaned
}

export const API_BASE_URL = normalize(raw && raw.length > 0 ? raw : FALLBACK_URL)
