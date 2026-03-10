"use client"
import { useSession } from "next-auth/react"
import { useState } from "react"
import { apiFetch } from "@/lib/api"

export default function AskPage() {
  const { data: session } = useSession()
  const apiToken = (session as { apiToken?: string })?.apiToken
  const [message, setMessage] = useState("")
  const [reply, setReply] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function ask() {
    const text = message.trim()
    if (!text || !apiToken) return
    setLoading(true)
    setReply(null)
    try {
      const res = await apiFetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
        token: apiToken,
      })
      const data = await res.json()
      setReply(data.reply ?? "No reply.")
    } catch {
      setReply("Something went wrong. Try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold">Ask a question</h1>
      <p className="mt-2 text-zinc-400">Ask about your latest report. We’ll answer based on your numbers and summary.</p>
      <textarea
        value={message}
        onChange={e => setMessage(e.target.value)}
        placeholder="e.g. Why did costs go up this month?"
        className="mt-4 w-full rounded-lg border border-zinc-700 bg-zinc-900 p-3 text-white placeholder-zinc-500 min-h-[120px]"
        disabled={loading}
      />
      <button onClick={ask} disabled={loading || !message.trim()} className="mt-4 rounded-lg bg-amber-500 px-4 py-2 text-black font-medium disabled:opacity-50">
        {loading ? "Thinking…" : "Ask"}
      </button>
      {reply !== null && (
        <div className="mt-6 rounded-lg bg-zinc-800 p-4">
          <div className="text-zinc-400 text-sm mb-2">Reply</div>
          <p className="whitespace-pre-wrap">{reply}</p>
        </div>
      )}
    </div>
  )
}
