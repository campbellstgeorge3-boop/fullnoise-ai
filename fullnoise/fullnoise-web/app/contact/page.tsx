"use client"
import Link from "next/link"
import { useState } from "react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export default function Contact() {
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [message, setMessage] = useState("")
  const [status, setStatus] = useState<"idle" | "sending" | "ok" | "error">("idle")

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setStatus("sending")
    try {
      const res = await fetch(`${API_URL}/contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, message }),
      })
      if (res.ok) {
        setStatus("ok")
        setName("")
        setEmail("")
        setMessage("")
      } else setStatus("error")
    } catch {
      setStatus("error")
    }
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-zinc-800 px-6 py-4">
        <div className="max-w-4xl mx-auto flex justify-between">
          <Link href="/" className="font-semibold text-xl">FullNoise AI</Link>
          <Link href="/login">Sign in</Link>
        </div>
      </header>
      <main className="max-w-md mx-auto px-6 py-16">
        <h1 className="text-3xl font-bold">Get started</h1>
        <p className="mt-2 text-zinc-400">We’ll set up a short call and send you a quote.</p>
        <form onSubmit={submit} className="mt-8 space-y-4">
          <div>
            <label className="block text-sm text-zinc-400 mb-1">Name</label>
            <input type="text" value={name} onChange={e => setName(e.target.value)} required className="w-full rounded-lg bg-zinc-900 border border-zinc-700 px-3 py-2" placeholder="Your name" />
          </div>
          <div>
            <label className="block text-sm text-zinc-400 mb-1">Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required className="w-full rounded-lg bg-zinc-900 border border-zinc-700 px-3 py-2" placeholder="you@company.com" />
          </div>
          <div>
            <label className="block text-sm text-zinc-400 mb-1">Message</label>
            <textarea value={message} onChange={e => setMessage(e.target.value)} rows={4} className="w-full rounded-lg bg-zinc-900 border border-zinc-700 px-3 py-2" placeholder="What you need" />
          </div>
          <button type="submit" disabled={status === "sending"} className="rounded-lg bg-amber-500 px-4 py-2 text-black font-medium disabled:opacity-50">
            {status === "sending" ? "Sending…" : status === "ok" ? "Sent — we’ll be in touch" : "Send message"}
          </button>
          {status === "error" && <p className="text-red-400 text-sm">Something went wrong. Try again.</p>}
        </form>
      </main>
    </div>
  )
}
