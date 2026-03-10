import type { NextAuthOptions } from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"
import * as jose from "jose"

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      id: "credentials",
      name: "Admin or Client",
      credentials: { email: { label: "Email" }, password: { label: "Password" }, token: { label: "Token" } },
      async authorize(credentials) {
        if (!credentials) return null
        if (credentials.token) {
          try {
            const secret = new TextEncoder().encode(process.env.NEXTAUTH_SECRET)
            const { payload } = await jose.jwtVerify(credentials.token, secret)
            const d = payload as { role?: string; client_id?: string; email?: string }
            if (d.role === "client" && d.client_id) return { id: d.client_id, email: (d.email as string) || "", role: "client", token: credentials.token }
          } catch {
            return null
          }
        }
        if (credentials.email && credentials.password) {
          const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
          const res = await fetch(`${API_URL}/auth/admin-login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: credentials.email, password: credentials.password }),
          })
          if (!res.ok) return null
          const data = await res.json()
          if (data.token) return { id: "admin", email: credentials.email, role: "admin", token: data.token }
        }
        return null
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = (user as { role?: string }).role
        token.client_id = (user as { client_id?: string }).client_id
        token.apiToken = (user as { token?: string }).token
      }
      return token
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as { role?: string }).role = token.role as string
        ;(session.user as { client_id?: string }).client_id = token.client_id as string
        ;(session as { apiToken?: string }).apiToken = token.apiToken as string
      }
      return session
    },
  },
  pages: { signIn: "/login" },
  session: { strategy: "jwt", maxAge: 7 * 24 * 3600 },
  secret: process.env.NEXTAUTH_SECRET,
}
