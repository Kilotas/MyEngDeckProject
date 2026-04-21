'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { clearTokens } from '@/lib/auth'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()

  function logout() {
    clearTokens()
    router.push('/login')
  }

  return (
    <div className="min-h-full flex flex-col">
      <header className="border-b border-zinc-800 px-6 py-4 flex items-center justify-between">
        <Link href="/decks" className="font-semibold tracking-tight">
          Reword
        </Link>
        <button
          onClick={logout}
          className="text-sm text-zinc-500 hover:text-zinc-300 transition-colors"
        >
          Выйти
        </button>
      </header>
      <main className="flex-1 px-6 py-8 max-w-2xl mx-auto w-full">{children}</main>
    </div>
  )
}
