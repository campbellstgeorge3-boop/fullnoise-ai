import { getServerSession } from "next-auth"
import { redirect } from "next/navigation"
import { authOptions } from "@/lib/auth"
import Link from "next/link"

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const session = await getServerSession(authOptions)
  const user = session?.user as { role?: string; client_id?: string } | undefined
  if (!session || user?.role !== "client") redirect("/login")
  return (
    <div className="min-h-screen">
      <header className="border-b border-zinc-800 px-6 py-4 flex justify-between items-center">
        <Link href="/app" className="font-semibold">FullNoise AI</Link>
        <div className="flex gap-4">
          <Link href="/app/report">Report</Link>
          <Link href="/app/ask">Ask</Link>
          <a href="/api/auth/signout" className="text-zinc-400">Sign out</a>
        </div>
      </header>
      <main className="max-w-3xl mx-auto px-6 py-8">{children}</main>
    </div>
  )
}
