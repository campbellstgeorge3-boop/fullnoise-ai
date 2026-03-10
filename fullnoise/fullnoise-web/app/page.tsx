import Link from "next/link"

export default function Home() {
  return (
    <div className="min-h-screen bg-zinc-950 text-white">
      <header className="border-b border-zinc-800 px-6 py-4">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <span className="font-semibold text-xl">FullNoise AI</span>
          <nav className="flex gap-6">
            <Link href="/pricing" className="text-zinc-400 hover:text-white">Pricing</Link>
            <Link href="/contact" className="text-zinc-400 hover:text-white">Contact</Link>
            <Link href="/login" className="rounded-lg bg-amber-500 px-3 py-1.5 text-black font-medium">Sign in</Link>
          </nav>
        </div>
      </header>
      <main className="max-w-3xl mx-auto px-6 py-20">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
          Run your business full noise
        </h1>
        <p className="mt-6 text-xl text-zinc-400">
          Monthly financial reports in your inbox. Reply with a question and get an answer by email. No dashboard to log into unless you want one.
        </p>
        <div className="mt-10 flex flex-wrap gap-4">
          <Link href="/contact" className="rounded-lg bg-amber-500 px-6 py-3 text-black font-medium hover:bg-amber-400">
            Get started
          </Link>
          <Link href="/pricing" className="rounded-lg border border-zinc-600 px-6 py-3 text-zinc-300 hover:border-zinc-500">
            See pricing
          </Link>
        </div>
        <section className="mt-24 grid gap-8 md:grid-cols-3">
          <div>
            <h2 className="font-semibold text-lg">Reports by email</h2>
            <p className="mt-2 text-zinc-400 text-sm">We send a clear monthly summary: revenue, costs, profit, and what it means.</p>
          </div>
          <div>
            <h2 className="font-semibold text-lg">Reply to ask</h2>
            <p className="mt-2 text-zinc-400 text-sm">Reply to the email with any question. You get an answer back in your inbox.</p>
          </div>
          <div>
            <h2 className="font-semibold text-lg">Web portal too</h2>
            <p className="mt-2 text-zinc-400 text-sm">Sign in with a magic link to view your report and ask questions in the browser.</p>
          </div>
        </section>
      </main>
      <footer className="border-t border-zinc-800 mt-24 px-6 py-8">
        <div className="max-w-4xl mx-auto flex justify-between text-sm text-zinc-500">
          <span>FullNoise AI</span>
          <Link href="/contact" className="hover:text-zinc-400">Contact</Link>
        </div>
      </footer>
    </div>
  )
}
