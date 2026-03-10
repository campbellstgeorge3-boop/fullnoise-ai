"use client"
import { useSession } from "next-auth/react"
import { useEffect, useState } from "react"
import { apiFetch } from "@/lib/api"

type ReportData = {
  id: string
  month: string
  revenue: number
  costs: number
  profit: number
  jobs: number
  summary: string
  created_at: string
}

export default function ReportPage() {
  const { data: session } = useSession()
  const apiToken = (session as { apiToken?: string })?.apiToken
  const [report, setReport] = useState<ReportData | null | undefined>(undefined)
  const [resending, setResending] = useState(false)

  useEffect(() => {
    if (!apiToken) return
    apiFetch("/report", { token: apiToken })
      .then((r) => r.json())
      .then((d) => setReport(d.report ?? null))
      .catch(() => setReport(null))
  }, [apiToken])

  async function resend() {
    if (!apiToken) return
    setResending(true)
    try {
      await apiFetch("/resend-report", { method: "POST", token: apiToken })
    } finally {
      setResending(false)
    }
  }

  if (report === undefined) return <div className="text-zinc-400">Loading…</div>
  if (report === null) return <div className="text-zinc-400">No report yet. We will send your first one soon.</div>

  return (
    <div>
      <h1 className="text-2xl font-bold">Report — {report.month}</h1>
      <p className="mt-1 text-zinc-400 text-sm">Created {new Date(report.created_at).toLocaleString()}</p>
      <div className="mt-6 grid grid-cols-2 gap-4">
        <div className="rounded-lg bg-zinc-800 p-4">
          <div className="text-zinc-400 text-sm">Revenue</div>
          <div className="text-xl font-semibold">${report.revenue.toLocaleString(undefined, { minimumFractionDigits: 2 })}</div>
        </div>
        <div className="rounded-lg bg-zinc-800 p-4">
          <div className="text-zinc-400 text-sm">Costs</div>
          <div className="text-xl font-semibold">${report.costs.toLocaleString(undefined, { minimumFractionDigits: 2 })}</div>
        </div>
        <div className="rounded-lg bg-zinc-800 p-4">
          <div className="text-zinc-400 text-sm">Profit</div>
          <div className="text-xl font-semibold">${report.profit.toLocaleString(undefined, { minimumFractionDigits: 2 })}</div>
        </div>
        <div className="rounded-lg bg-zinc-800 p-4">
          <div className="text-zinc-400 text-sm">Jobs</div>
          <div className="text-xl font-semibold">{report.jobs}</div>
        </div>
      </div>
      <div className="mt-6 rounded-lg bg-zinc-800 p-4">
        <div className="text-zinc-400 text-sm mb-2">Summary</div>
        <p className="whitespace-pre-wrap">{report.summary}</p>
      </div>
      <button onClick={resend} disabled={resending} className="mt-6 rounded-lg bg-amber-500 px-4 py-2 text-black font-medium disabled:opacity-50">
        {resending ? "Sending…" : "Send my report again by email"}
      </button>
    </div>
  )
}
