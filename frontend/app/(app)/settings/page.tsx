'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getMe, updateMe, type User } from '@/lib/api'
import { isAuthenticated } from '@/lib/auth'

const PRESETS = [5, 10, 20, 30, 50]

export default function SettingsPage() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [limit, setLimit] = useState(20)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isAuthenticated()) { router.replace('/login'); return }
    getMe()
      .then(u => { setUser(u); setLimit(u.daily_new_limit) })
      .finally(() => setLoading(false))
  }, [router])

  async function handleSave() {
    setSaving(true)
    setSaved(false)
    try {
      const updated = await updateMe(limit)
      setUser(updated)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <p className="text-zinc-500 text-sm">Loading…</p>

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="text-xl font-semibold">Настройки</h1>
        {user && <p className="text-zinc-500 text-sm mt-0.5">{user.username} · {user.email}</p>}
      </div>

      <div className="rounded-xl border border-zinc-800 bg-zinc-900 px-5 py-5 flex flex-col gap-4">
        <div>
          <h2 className="font-medium">Новых слов в день</h2>
          <p className="text-zinc-500 text-sm mt-0.5">
            Сколько новых карточек вводить ежедневно в режиме «Учить»
          </p>
        </div>

        <div className="flex items-center gap-3">
          {PRESETS.map(p => (
            <button
              key={p}
              onClick={() => setLimit(p)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                limit === p
                  ? 'bg-zinc-100 text-zinc-900'
                  : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-300'
              }`}
            >
              {p}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <input
            type="range"
            min={1}
            max={100}
            value={limit}
            onChange={e => setLimit(Number(e.target.value))}
            className="flex-1 accent-emerald-500"
          />
          <span className="text-lg font-semibold w-12 text-right">{limit}</span>
        </div>

        <button
          onClick={handleSave}
          disabled={saving}
          className="self-start px-5 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-sm font-medium disabled:opacity-50 transition-colors"
        >
          {saved ? 'Сохранено ✓' : saving ? 'Сохранение…' : 'Сохранить'}
        </button>
      </div>
    </div>
  )
}
