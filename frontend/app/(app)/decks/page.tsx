'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { getDecks, type Deck } from '@/lib/api'
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

export default function DecksPage() {
  const router = useRouter()
  const [decks, setDecks] = useState<Deck[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace('/login')
      return
    }
    getDecks()
      .then(setDecks)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
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
          {decks.map(deck => (
            <Link
              key={deck.id}
              href={`/decks/${deck.id}/study`}
              className="block rounded-xl border border-zinc-800 bg-zinc-900 px-5 py-4 hover:border-zinc-700 transition-colors"
            >
              <div className="flex items-center justify-between">
                <span className="font-medium">{deck.name}</span>
                <span
                  className={`text-xs font-medium px-2 py-0.5 rounded-full ${LEVEL_COLOR[deck.level]}`}
                >
                  {LEVEL_LABEL[deck.level]}
                </span>
              </div>
              <p className="text-zinc-500 text-sm mt-1">Нажмите чтобы учить</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
