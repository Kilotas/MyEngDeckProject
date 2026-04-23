'use client'

import { useEffect, useState, use, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { getLearnCards, getReviewCards, submitReview, type Card } from '@/lib/api'
import { isAuthenticated } from '@/lib/auth'
import Link from 'next/link'

const MINIO_URL = process.env.NEXT_PUBLIC_STORAGE_URL ?? 'http://localhost:9000/reword'

const QUALITY_LABELS: { q: number; label: string; color: string }[] = [
  { q: 1, label: 'Не помню', color: 'bg-red-900 hover:bg-red-800' },
  { q: 3, label: 'Хочу повторить', color: 'bg-yellow-800 hover:bg-yellow-700' },
  { q: 5, label: 'Запомнил', color: 'bg-emerald-700 hover:bg-emerald-600' },
]

type Mode = 'learn' | 'review'

function StudyContent({ id }: { id: string }) {
  const searchParams = useSearchParams()
  const mode = (searchParams.get('mode') ?? 'learn') as Mode
  const router = useRouter()

  const [cards, setCards] = useState<Card[]>([])
  const [index, setIndex] = useState(0)
  const [flipped, setFlipped] = useState(false)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [done, setDone] = useState(false)

  useEffect(() => {
    if (!isAuthenticated()) { router.replace('/login'); return }

    const fetcher = mode === 'review' ? getReviewCards(id) : getLearnCards(id)
    fetcher
      .then(cs => {
        if (cs.length === 0) setDone(true)
        setCards(cs)
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [id, mode, router])

  function playAudio(audioPath: string) {
    const audio = new Audio(`${MINIO_URL}/${audioPath}`)
    audio.play().catch(console.error)
  }

  function handleFlip() {
    setFlipped(true)
    const card = cards[index]
    if (card?.audio_path) playAudio(card.audio_path)
  }

  async function handleRate(quality: number) {
    if (submitting) return
    setSubmitting(true)
    try {
      await submitReview(cards[index].id, quality)
      const next = index + 1
      if (next >= cards.length) {
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

  const modeLabel = mode === 'review' ? 'Повторение' : 'Учить'

  if (loading) return <p className="text-zinc-500 text-sm">Loading…</p>
  if (error) return <p className="text-red-400 text-sm">{error}</p>

  if (done) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center gap-4">
        <p className="text-4xl">🎉</p>
        <h2 className="text-xl font-semibold">
          {mode === 'review' ? 'Все повторения сделаны!' : 'Новые слова на сегодня изучены!'}
        </h2>
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

  const card = cards[index]
  if (!card) return null

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between text-sm text-zinc-500">
        <Link href="/decks" className="hover:text-zinc-300 transition-colors">
          ← Колоды
        </Link>
        <div className="flex items-center gap-3">
          <span className={`text-xs px-2 py-0.5 rounded-full ${
            mode === 'review' ? 'bg-blue-900/50 text-blue-300' : 'bg-emerald-900/50 text-emerald-300'
          }`}>
            {modeLabel}
          </span>
          <span>{index + 1} / {cards.length}</span>
        </div>
      </div>

      <div
        onClick={!flipped ? handleFlip : undefined}
        className={`rounded-2xl border border-zinc-800 bg-zinc-900 p-8 min-h-[260px] flex flex-col items-center justify-center gap-4 transition-colors ${
          !flipped ? 'cursor-pointer hover:border-zinc-700' : ''
        }`}
      >
        <p className="text-3xl font-semibold tracking-tight">{card.word}</p>

        {!flipped && (
          <p className="text-zinc-500 text-sm mt-2">Нажмите чтобы показать</p>
        )}

        {flipped && (
          <>
            <div className="w-12 h-px bg-zinc-700" />
            <p className="text-xl text-zinc-300">{card.translation}</p>
            {card.audio_path && (
              <button
                onClick={() => playAudio(card.audio_path!)}
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

export default function StudyPage(props: PageProps<'/decks/[id]/study'>) {
  const { id } = use(props.params)
  return (
    <Suspense fallback={<p className="text-zinc-500 text-sm">Loading…</p>}>
      <StudyContent id={id} />
    </Suspense>
  )
}
