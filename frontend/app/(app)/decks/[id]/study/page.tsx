'use client'

import { useEffect, useState, use } from 'react'
import { useRouter } from 'next/navigation'
import { getDeckCards, getDueReviews, submitReview, type Card, type Review } from '@/lib/api'
import { isAuthenticated } from '@/lib/auth'

const MINIO_URL = process.env.NEXT_PUBLIC_STORAGE_URL ?? 'http://localhost:9000/reword'

const QUALITY_LABELS: { q: number; label: string; color: string }[] = [
  { q: 1, label: 'Не помню', color: 'bg-red-900 hover:bg-red-800' },
  { q: 3, label: 'Хочу повторить', color: 'bg-yellow-800 hover:bg-yellow-700' },
  { q: 5, label: 'Запомнил', color: 'bg-emerald-700 hover:bg-emerald-600' },
]

type StudyItem = { card: Card; review: Review | null }

export default function StudyPage(props: PageProps<'/decks/[id]/study'>) {
  const { id } = use(props.params)
  const router = useRouter()

  const [queue, setQueue] = useState<StudyItem[]>([])
  const [index, setIndex] = useState(0)
  const [flipped, setFlipped] = useState(false)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [done, setDone] = useState(false)

  useEffect(() => {
    if (!isAuthenticated()) { router.replace('/login'); return }

    Promise.all([getDeckCards(id), getDueReviews()])
      .then(([cards, reviews]) => {
        const reviewMap = new Map(reviews.map(r => [r.card_id, r]))
        const dueCardIds = new Set(reviews.map(r => r.card_id))

        const due: StudyItem[] = cards
          .filter(c => dueCardIds.has(c.id))
          .map(c => ({ card: c, review: reviewMap.get(c.id) ?? null }))

        const fresh: StudyItem[] = cards
          .filter(c => !dueCardIds.has(c.id))
          .map(c => ({ card: c, review: null }))

        const items = [...due, ...fresh]
        if (items.length === 0) setDone(true)
        setQueue(items)
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [id, router])

  function playAudio(audioPath: string) {
    const audio = new Audio(`${MINIO_URL}/${audioPath}`)
    audio.play().catch(console.error)
  }

  function handleFlip() {
    setFlipped(true)
    const card = queue[index]?.card
    if (card?.audio_path) playAudio(card.audio_path)
  }

  async function handleRate(quality: number) {
    if (submitting) return
    setSubmitting(true)
    try {
      await submitReview(queue[index].card.id, quality)
      const next = index + 1
      if (next >= queue.length) {
        setDone(true)
      } else {
        setIndex(next)
        setFlipped(false)
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <p className="text-zinc-500 text-sm">Loading…</p>
  if (error) return <p className="text-red-400 text-sm">{error}</p>

  if (done) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center gap-4">
        <p className="text-4xl">🎉</p>
        <h2 className="text-xl font-semibold">На сегодня всё!</h2>
        <p className="text-zinc-400 text-sm">Возвращайтесь завтра для следующей сессии.</p>
        <button
          onClick={() => router.push('/decks')}
          className="mt-4 px-5 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-sm transition-colors"
        >
          К колодам
        </button>
      </div>
    )
  }

  const item = queue[index]
  if (!item) return null

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between text-sm text-zinc-500">
        <button onClick={() => router.push('/decks')} className="hover:text-zinc-300 transition-colors">
          ← Колоды
        </button>
        <span>{index + 1} / {queue.length}</span>
      </div>

      <div
        onClick={!flipped ? handleFlip : undefined}
        className={`rounded-2xl border border-zinc-800 bg-zinc-900 p-8 min-h-[260px] flex flex-col items-center justify-center gap-4 transition-colors ${!flipped ? 'cursor-pointer hover:border-zinc-700' : ''}`}
      >
        <p className="text-3xl font-semibold tracking-tight">{item.card.word}</p>

        {!flipped && (
          <p className="text-zinc-500 text-sm mt-2">Нажмите чтобы показать</p>
        )}

        {flipped && (
          <>
            <div className="w-12 h-px bg-zinc-700" />
            <p className="text-xl text-zinc-300">{item.card.translation}</p>
            {item.card.audio_path && (
              <button
                onClick={() => playAudio(item.card.audio_path!)}
                className="mt-2 text-zinc-500 hover:text-zinc-300 transition-colors text-sm"
              >
                🔊 Повторить
              </button>
            )}
          </>
        )}
      </div>

      {flipped && (
        <div className="grid grid-cols-3 gap-3">
          {QUALITY_LABELS.map(({ q, label, color }) => (
            <button
              key={q}
              onClick={() => handleRate(q)}
              disabled={submitting}
              className={`rounded-xl py-3 text-sm font-medium ${color} disabled:opacity-50 transition-colors`}
            >
              {label}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
