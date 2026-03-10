"use client"
import { signIn } from "next-auth/react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { useState } from "react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export default function Login() {
  const router = useRouter()
  const [tab, setTab] = useState<"client" | "admin">("client")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [magicStatus, setMagicStatus] = useState("")
  const [adminError, setAdminError] = useState("")

  async function sendMagicLink(e: React.FormEvent) {
    e.preventDefault()
    setMagicStatus("Sending…")
    try {
      const res = await fetch(`${API_URL}/auth/send-magic-link`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim() }),
      })
      setMagicStatus(res.ok ? "Check your email for the sign-in link." : "Something went wrong.")
    } catch {
      setMagicStatus("Network error.")
    }
  }

  async function adminLogin(e: React.FormEvent) {
    e.preventDefault()
    setAdminError("")
    const result = await signIn("credentials", { email, password, redirect: false })
    if (result?.ok) {
      router.push("/admin")
      return
    }
    setAdminError("Invalid email or password.")
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <h1 className="text-2xl font-bold text-center">Sign in</h1>
        <div className="mt-6 flex border-b border-zinc-700">
          <button type="button" onClick={() => setTab("client")} className={"flex-1 py-2 " + (tab === "client" ? "border-b-2 border-amber-500" : "")}>Client</button>
          <button type="button" onClick={() => setTab("admin")} className={"flex-1 py-2 " + (tab === "admin" ? "border-b-2 border-amber-500" : "")}>Admin</button>
        </div>
        {tab === "client" && (
          <form onSubmit={sendMagicLink} className="mt-6 space-y-4">
            <p className="text-zinc-400 text-sm">Enter the email where you receive your report.</p>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="you@company.com" className="w-full rounded-lg bg-zinc-900 border border-zinc-700 px-3 py-2" />
            <button type="submit" className="w-full rounded-lg bg-amber-500 py-2 text-black font-medium">Send sign-in link</button>
            {magicStatus && <p className="text-sm text-zinc-400">{magicStatus}</p>}
          </form>
        )}
        {tab === "admin" && (
          <form onSubmit={adminLogin} className="mt-6 space-y-4">
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="Admin email" className="w-full rounded-lg bg-zinc-900 border border-zinc-700 px-3 py-2" />
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required placeholder="Password" className="w-full rounded-lg bg-zinc-900 border border-zinc-700 px-3 py-2" />
            <button type="submit" className="w-full rounded-lg bg-amber-500 py-2 text-black font-medium">Sign in</button>
            {adminError && <p className="text-sm text-red-400">{adminError}</p>}
          </form>
        )}
        <p className="mt-6 text-center text-sm text-zinc-500"><Link href="/">Back to home</Link></p>
      </div>
    </div>
  )
}
