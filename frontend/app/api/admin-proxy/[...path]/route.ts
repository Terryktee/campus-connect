import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'

const API_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '')

async function forward(request: Request, path: string[], method: string) {
  const cookieStore = await cookies()
  let access = cookieStore.get('admin_access')?.value
  const refresh = cookieStore.get('admin_refresh')?.value
  const init: RequestInit = {
    method,
    headers: { Accept: 'application/json', ...(method !== 'GET' ? { 'Content-Type': 'application/json' } : {}) },
    body: method === 'GET' || method === 'HEAD' ? undefined : await request.text(),
  }
  const send = (token?: string) => fetch(`${API_URL}/api/${path.join('/')}/${path.length ? '' : ''}`, {
    ...init,
    headers: { ...init.headers, ...(token ? { Authorization: `Bearer ${token}` } : {}) },
  })
  let response = await send(access)

  if (response.status === 401 && refresh) {
    const refreshed = await fetch(`${API_URL}/api/auth/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    })
    if (refreshed.ok) {
      const tokens = await refreshed.json()
      if (typeof tokens.access !== 'string') {
        return NextResponse.json({ detail: 'The admin session could not be refreshed.' }, { status: 401 })
      }
      const refreshedAccess = tokens.access
      access = refreshedAccess
      response = await send(refreshedAccess)
      const result = new NextResponse(response.body, { status: response.status, headers: response.headers })
      result.cookies.set('admin_access', refreshedAccess, {
        httpOnly: true,
        sameSite: 'lax',
        secure: process.env.NODE_ENV === 'production',
        path: '/',
        maxAge: 60 * 15,
      })
      return result
    }
  }
  return new NextResponse(response.body, { status: response.status, headers: response.headers })
}

type Context = { params: Promise<{ path: string[] }> }
export async function GET(request: Request, context: Context) {
  return forward(request, (await context.params).path, 'GET')
}
export async function POST(request: Request, context: Context) {
  return forward(request, (await context.params).path, 'POST')
}
