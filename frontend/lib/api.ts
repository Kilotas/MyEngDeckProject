import { getAccessToken, clearTokens } from './auth'

const BASE = (process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8002') + '/api/v1'

export type Deck = {
  id: string
  name: string
  description: string | null
  level: 'beginner' | 'intermediate' | 'advanced'
  is_system: boolean
  owner_id: string | null
  created_at: string
}

export type Card = {
  id: string
  word: string
  translation: string
  example: string | null
  audio_path: string | null
  image_path: string | null
  deck_id: string
  created_at: string
}

export type Review = {
  id: string
  user_id: string
  card_id: string
  easiness_factor: number
  interval: number
  repetitions: number
  last_reviewed_at: string | null
  next_review_at: string
}

export type Tokens = {
  access_token: string
  refresh_token: string
  token_type: string
}

async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getAccessToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(init.headers as Record<string, string>),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE}${path}`, { ...init, headers })

  if (res.status === 401) {
    clearTokens()
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body?.detail ?? `HTTP ${res.status}`)
  }

  return res.json() as Promise<T>
}

export async function login(username: string, password: string): Promise<Tokens> {
  const form = new URLSearchParams({ username, password })
  const res = await fetch(`${BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form.toString(),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body?.detail ?? 'Login failed')
  }
  return res.json()
}

export async function register(username: string, email: string, password: string): Promise<void> {
  await apiFetch('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ username, email, password }),
  })
}

export function getDecks(): Promise<Deck[]> {
  return apiFetch('/decks')
}

export function getDeckCards(deckId: string): Promise<Card[]> {
  return apiFetch(`/decks/${deckId}/cards`)
}

export function getDueReviews(): Promise<Review[]> {
  return apiFetch('/reviews/due')
}

export function submitReview(cardId: string, quality: number): Promise<Review> {
  return apiFetch('/reviews', {
    method: 'POST',
    body: JSON.stringify({ card_id: cardId, quality }),
  })
}

export type DeckStats = {
  total_cards: number
  new_cards: number
  reviewed_cards: number
  due_cards: number
  learned_cards: number
  avg_interval: number
  learn_available: number
}

export type User = {
  id: string
  email: string
  username: string
  is_active: boolean
  daily_new_limit: number
  created_at: string
}

export function getDeckStats(deckId: string): Promise<DeckStats> {
  return apiFetch(`/decks/${deckId}/stats`)
}

export function getLearnCards(deckId: string): Promise<Card[]> {
  return apiFetch(`/decks/${deckId}/learn-cards`)
}

export function getReviewCards(deckId: string): Promise<Card[]> {
  return apiFetch(`/decks/${deckId}/review-cards`)
}

export function getMe(): Promise<User> {
  return apiFetch('/users/me')
}

export function updateMe(daily_new_limit: number): Promise<User> {
  return apiFetch('/users/me', {
    method: 'PATCH',
    body: JSON.stringify({ daily_new_limit }),
  })
}
