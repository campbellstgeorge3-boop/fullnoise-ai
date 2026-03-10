"use client"
import { useSearchParams } from "next/navigation"
import { useEffect, useState } from "react"
import { signIn } from "next-auth/react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export default function Verify() {
  const searchParams = useSearchParams()
  const token = searchParams.get("token")
  const [status, setStatus] = useState<"loading" | "ok" | "error">("loading")

  useEffect(() => {
    if (!token) {
      setStatus("error")
      return
    }
    fetch(`${API_URL}/auth/verify?token=${encodeURIComponent(token)}`)
      .then(r => r.json())
      .then(data => {
        if (data.token) {
          signIn("credentials", { token: data.token, redirect: true, callbackUrl: "/app" })
        } else setStatus("error")
      })
      .catch(() => setStatus("error"))
  }, [token])

  if (status === "loading") return <div className="min-h-screen flex items-center justify-center">Signing you in…</div>
  if (status === "error") return <div className="min-h-screen flex items-center justify-center">Invalid or expired link. <a href="/login" className="text-amber-400 ml-2">Try again</a></div>
  return null
}
