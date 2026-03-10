import Link from "next/link"

export default function Pricing() {
  return (
    <div className="min-h-screen bg-zinc-950 text-white">
      <header className="border-b border-zinc-800 px-6 py-4">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <Link href="/" className="font-semibold text-xl">FullNoise AI</Link>
          <nav className="flex gap-6">
            <Link href="/pricing" className="text-amber-500">Pricing</Link>
            <Link href="/contact" className="text-zinc-400 hover:text-white">Contact</Link>
            <Link href="/login" className="rounded-lg bg-amber-500 px-3 py-1.5 text-black font-medium">Sign in</Link>
          </nav>
        </div>
      </header>
      <main className="max-w-2xl mx-auto px-6 py-16">
        <h1 className="text-3xl font-bold">Pricing</h1>
        <p className="mt-2 text-zinc-400">Simple plans for business owners who want reports that answer back.</p>
        <div className="mt-12 rounded-xl border border-zinc-800 bg-zinc-900/50 p-8">
          <h2 className="text-xl font-semibold">Starter</h2>
          <p className="mt-2 text-zinc-400">Monthly report by email. Reply with questions and get answers in your inbox. Web portal access included.</p>
          <p className="mt-6 text-3xl font-bold">Contact us</p>
          <p className="mt-1 text-zinc-400 text-sm">We’ll set up a short call and send you a quote.</p>
          <Link href="/contact" className="mt-6 inline-block rounded-lg bg-amber-500 px-6 py-2.5 text-black font-medium">
            Get started
          </Link>
        </div>
        <p className="mt-8 text-zinc-500 text-sm">
          <Link href="/" className="hover:text-zinc-400">← Back to home</Link>
        </p>
      </main>
    </div>
  )
}
