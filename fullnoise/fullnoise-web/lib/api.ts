const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
export async function apiFetch(path: string, options: RequestInit & { token?: string } = {}) {
  const { token, ...rest } = options
  const headers: HeadersInit = { ...(rest.headers as HeadersInit) }
  if (token) (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`
  return fetch(`${API_URL}${path}`, { ...rest, headers })
}
