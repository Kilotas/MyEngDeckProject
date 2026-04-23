'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { getDecks, getDeckStats, type Deck, type DeckStats } from '@/lib/api'
import { isAuthenticated } from '@/lib/auth'

const LEVEL_LABEL: Record<string, string> = {
  beginner: 'Beginner',
  intermediate: 'Intermediate',
  advanced: 'Advanced',
}

const LEVEL_COLOR: Record<string, string> = {
  beginner: 'text-emerald-400 bg-emerald-400/10',
  intermediate: 'text-yellow-400 bg-yellow-400/10',
  advanced: 'text-red-400 bg-red-400/10',
}

type DeckWithStats = Deck & { stats?: DeckStats }

export default function DecksPage() {
  const router = useRouter()
  const [decks, setDecks] = useState<DeckWithStats[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!isAuthenticated()) { router.replace('/login'); return }

    getDecks()
      .then(async (ds) => {
        setDecks(ds)
        setLoading(false)
        // Загружаем статистику параллельно
        const stats = await Promise.allSettled(ds.map(d => getDeckStats(d.id)))
        setDecks(ds.map((d, i) => ({
          ...d,
          stats: stats[i].status === 'fulfilled' ? stats[i].value : undefined,
        })))
      })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [router])

  if (loading) return <p className="text-zinc-500 text-sm">Loading…</p>
  if (error) return <p className="text-red-400 text-sm">{error}</p>

  return (
    <div>
      <h1 className="text-xl font-semibold mb-6">Ваши колоды</h1>

      {decks.length === 0 ? (
        <p className="text-zinc-500 text-sm">Нет колод. Запустите seed скрипт чтобы загрузить слова.</p>
      ) : (
        <div className="space-y-3">
          {decks.map(deck => {
            const learnCount = deck.stats?.learn_available ?? null
            const reviewCount = deck.stats?.due_cards ?? null

            return (
              <div
                key={deck.id}
                className="rounded-xl border border-zinc-800 bg-zinc-900 px-5 py-4"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{deck.name}</span>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${LEVEL_COLOR[deck.level]}`}>
                    {LEVEL_LABEL[deck.level]}
                  </span>
                </div>

                <div className="flex items-center gap-3 mt-3">
                  <Link
                    href={`/decks/${deck.id}/study?mode=learn`}
                    className={`text-sm px-4 py-1.5 rounded-lg transition-colors ${
                      learnCount === 0
                        ? 'bg-zinc-800 text-zinc-600 pointer-events-none'
                        : 'bg-emerald-800 hover:bg-emerald-700 text-emerald-100'
                    }`}
                  >
                    Учить{learnCount !== null ? ` (${learnCount})` : ''}
                  </Link>

                  <Link
                    href={`/decks/${deck.id}/study?mode=review`}
                    className={`text-sm px-4 py-1.5 rounded-lg transition-colors ${
                      reviewCount === 0
                        ? 'bg-zinc-800 text-zinc-600 pointer-events-none'
                        : 'bg-blue-900 hover:bg-blue-800 text-blue-100'
                    }`}
                  >
                    Повторить{reviewCount !== null ? ` (${reviewCount})` : ''}
                  </Link>

                  <Link
                    href={`/decks/${deck.id}/stats`}
                    className="text-sm text-zinc-500 hover:text-zinc-300 transition-colors ml-auto"
                  >
                    Статистика
                  </Link>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
