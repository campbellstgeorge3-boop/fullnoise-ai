"use client"
import { useSession } from "next-auth/react"
import { useEffect, useState } from "react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

type Client = { id: string; name: string; email: string; last_report_sent_at: string | null }

export default function AdminClient({ clients: initialClients }: { clients: Client[] }) {
  const { data: session } = useSession()
  const apiToken = (session as { apiToken?: string })?.apiToken
  const [clients, setClients] = useState<Client[]>(initialClients)
  const [sending, setSending] = useState<string | null>(null)

  useEffect(() => {
    if (!apiToken) return
    fetch(`${API_URL}/clients`, { headers: { Authorization: `Bearer ${apiToken}` } })
      .then(r => r.json())
      .then(d => setClients(d.clients || []))
      .catch(() => {})
  }, [apiToken])

  async function sendReport(clientId: string) {
    if (!apiToken) return
    setSending(clientId)
    try {
      const res = await fetch(`${API_URL}/send-report`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiToken}` },
        body: JSON.stringify({ client_id: clientId }),
      })
      const data = await res.json()
      if (data.ok) {
        const updated = await fetch(`${API_URL}/clients`, { headers: { Authorization: `Bearer ${apiToken}` } }).then(r => r.json())
        setClients(updated.clients || clients)
      }
    } finally {
      setSending(null)
    }
  }

  return (
    <div className="mt-8">
      <table className="w-full border border-zinc-700 rounded-lg overflow-hidden">
        <thead className="bg-zinc-800">
          <tr>
            <th className="text-left p-3">Name</th>
            <th className="text-left p-3">Email</th>
            <th className="text-left p-3">Last report sent</th>
            <th className="text-left p-3">Action</th>
          </tr>
        </thead>
        <tbody>
          {clients.map(c => (
            <tr key={c.id} className="border-t border-zinc-700">
              <td className="p-3">{c.name}</td>
              <td className="p-3 text-zinc-400">{c.email}</td>
              <td className="p-3 text-zinc-400">{c.last_report_sent_at ? new Date(c.last_report_sent_at).toLocaleString() : "—"}</td>
              <td className="p-3">
                <button onClick={() => sendReport(c.id)} disabled={!!sending} className="rounded-lg bg-amber-500 px-3 py-1 text-black text-sm font-medium disabled:opacity-50">
                  {sending === c.id ? "Sending…" : "Send report"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {clients.length === 0 && <p className="mt-4 text-zinc-400">No clients yet. Add clients via API or a future admin form.</p>}
    </div>
  )
}
