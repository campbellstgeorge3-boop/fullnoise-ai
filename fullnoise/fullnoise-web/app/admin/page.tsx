import { getServerSession } from "next-auth"
import { redirect } from "next/navigation"
import { authOptions } from "@/lib/auth"
import AdminClient from "./AdminClient"

export default async function Admin() {
  const session = await getServerSession(authOptions)
  const user = session?.user as { role?: string } | undefined
  if (!session || user?.role !== "admin") redirect("/login")
  return (
    <div>
      <h1 className="text-2xl font-bold">Admin — Clients</h1>
      <p className="mt-2 text-zinc-400">Send reports and manage clients.</p>
      <AdminClient clients={[]} />
    </div>
  )
}
