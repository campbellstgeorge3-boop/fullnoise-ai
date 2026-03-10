import Link from "next/link"
export default function AppHome() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Your report</h1>
      <p className="mt-2 text-zinc-400">View your latest report and ask questions.</p>
      <div className="mt-8 flex gap-4">
        <Link href="/app/report" className="rounded-lg bg-zinc-800 px-4 py-3 hover:bg-zinc-700">Latest report</Link>
        <Link href="/app/ask" className="rounded-lg bg-amber-500 px-4 py-3 text-black font-medium">Ask a question</Link>
      </div>
    </div>
  )
}
