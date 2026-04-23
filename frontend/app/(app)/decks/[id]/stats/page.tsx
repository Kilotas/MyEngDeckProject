'use client'

import { useEffect, useState, use } from 'react'
import { useRouter } from 'next/navigation'
import { getDeckStats, getDecks, type DeckStats, type Deck } from '@/lib/api'
import { isAuthenticated } from '@/lib/auth'
import Link from 'next/link'

function StatCard({ label, value, sub }: { label: string; value: number | string; sub?: string }) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900 px-5 py-4 flex flex-col gap-1">
      <span className="text-2xl font-semibold">{value}</span>
      <span className="text-sm text-zinc-400">{label}</span>
      {sub && <span className="text-xs text-zinc-600">{sub}</span>}
    </div>
  )
}

export default function StatsPage(props: PageProps<'/decks/[id]/stats'>) {
  const { id } = use(props.params)
  const router = useRouter()
  const [stats, setStats] = useState<DeckStats | null>(null)
  const [deck, setDeck] = useState<Deck | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!isAuthenticated()) { router.replace('/login'); return }

    Promise.all([getDeckStats(id), getDecks()])
      .then(([s, decks]) => {
        setStats(s)
        setDeck(decks.find(d => d.id === id) ?? null)
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [id, router])

  if (loading) return <p className="text-zinc-500 text-sm">Loading…</p>
  if (error) return <p className="text-red-400 text-sm">{error}</p>
  if (!stats) return null

  const progressPct = stats.total_cards > 0
    ? Math.round((stats.reviewed_cards / stats.total_cards) * 100)
    : 0

  const learnedPct = stats.total_cards > 0
    ? Math.round((stats.learned_cards / stats.total_cards) * 100)
    : 0

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <Link href="/decks" className="text-sm text-zinc-500 hover:text-zinc-300 transition-colors">
          ← Колоды
        </Link>
        <Link
          href={`/decks/${id}/study`}
          className="text-sm px-4 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 transition-colors"
        >
          Учить
        </Link>
      </div>

      <div>
        <h1 className="text-xl font-semibold">{deck?.name ?? 'Статистика'}</h1>
        <p className="text-zinc-500 text-sm mt-0.5">Прогресс изучения</p>
      </div>

      {/* Прогресс-бар */}
      <div className="flex flex-col gap-2">
        <div className="flex justify-between text-xs text-zinc-500">
          <span>Изучено</span>
          <span>{progressPct}%</span>
        </div>
        <div className="h-2 rounded-full bg-zinc-800 overflow-hidden">
          <div
            className="h-full rounded-full bg-emerald-500 transition-all"
            style={{ width: `${progressPct}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-zinc-500">
          <span>Освоено</span>
          <span>{learnedPct}%</span>
        </div>
        <div className="h-1 rounded-full bg-zinc-800 overflow-hidden">
          <div
            className="h-full rounded-full bg-blue-500 transition-all"
            style={{ width: `${learnedPct}%` }}
          />
        </div>
      </div>

      {/* Карточки со статистикой */}
      <div className="grid grid-cols-2 gap-3">
        <StatCard label="Всего карточек" value={stats.total_cards} />
        <StatCard label="К повторению" value={stats.due_cards} sub="сегодня" />
        <StatCard label="Новые" value={stats.new_cards} sub="не начаты" />
        <StatCard label="В процессе" value={stats.reviewed_cards} sub="хотя бы раз" />
        <StatCard label="Освоено" value={stats.learned_cards} sub="≥ 5 повторений" />
        <StatCard
          label="Средний интервал"
          value={stats.avg_interval > 0 ? `${stats.avg_interval} д` : '—'}
          sub="между повторениями"
        />
      </div>
    </div>
  )
}
