'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { register, login } from '@/lib/api'
import { setTokens } from '@/lib/auth'

export default function RegisterPage() {
  const router = useRouter()
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register(username, email, password)
      const tokens = await login(username, password)
      setTokens(tokens.access_token, tokens.refresh_token)
      router.push('/decks')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-1">Reword</h1>
      <p className="text-zinc-400 text-sm mb-8">Создайте аккаунт</p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm text-zinc-400 mb-1">Логин</label>
          <input
            type="text"
            value={username}
            onChange={e => setUsername(e.target.value)}
            required
            className="w-full rounded-lg bg-zinc-900 border border-zinc-800 px-3 py-2 text-sm focus:outline-none focus:border-zinc-600"
          />
        </div>
        <div>
          <label className="block text-sm text-zinc-400 mb-1">Почта</label>
          <input
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            required
            className="w-full rounded-lg bg-zinc-900 border border-zinc-800 px-3 py-2 text-sm focus:outline-none focus:border-zinc-600"
          />
        </div>
        <div>
          <label className="block text-sm text-zinc-400 mb-1">Пароль</label>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
            minLength={8}
            className="w-full rounded-lg bg-zinc-900 border border-zinc-800 px-3 py-2 text-sm focus:outline-none focus:border-zinc-600"
          />
        </div>

        {error && <p className="text-red-400 text-sm">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-white text-black py-2 text-sm font-medium hover:bg-zinc-200 disabled:opacity-50 transition-colors"
        >
          {loading ? 'Создаём…' : 'Создать аккаунт'}
        </button>
      </form>

      <p className="mt-6 text-sm text-zinc-500 text-center">
        Уже есть аккаунт?{' '}
        <Link href="/login" className="text-zinc-300 hover:text-white">
          Войти
        </Link>
      </p>
    </div>
  )
}
