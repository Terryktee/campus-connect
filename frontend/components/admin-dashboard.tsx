'use client'

import Link from 'next/link'
import { FormEvent, useEffect, useState } from 'react'

type AdminProfile = { username: string; role: 'super_admin' | 'moderator' | 'sponsor_viewer'; institution: number | null }
type Post = { id: number; title: string; status: string; is_flagged: boolean; submitter_name: string; category: number; created_at: string }
type Report = { id: number; post: number; reason: string; status: string; created_at: string }
type Channel = { id: number; name: string; status: string; is_verified: boolean }
type Action = { id: number; action: string; admin: number; reason: string; created_at: string }

async function adminFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/admin-proxy/${path.replace(/^\/|\/$/g, '')}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  if (!response.ok) throw new Error('The admin service could not complete that request.')
  return response.json() as Promise<T>
}

function LoginForm() {
  const [error, setError] = useState('')
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    const form = new FormData(event.currentTarget)
    const response = await fetch('/api/admin-auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: form.get('username'), password: form.get('password') }),
    })
    if (!response.ok) {
      setError('That username or password did not match an admin account.')
      return
    }
    window.location.href = '/admin'
  }
  return <main className="page"><div className="container auth-card"><span className="eyebrow">STAFF ONLY</span><h1>Moderation desk</h1><p>Sign in with your CampusConnect admin account.</p><form onSubmit={submit}><label>Username<input name="username" required autoComplete="username" /></label><label>Password<input name="password" type="password" required autoComplete="current-password" /></label>{error && <p className="form-error">{error}</p>}<button className="button primary" type="submit">Log in <span>→</span></button></form></div></main>
}

export function AdminLogin() { return <LoginForm /> }

export function AdminDashboard() {
  const [profile, setProfile] = useState<AdminProfile | null>(null)
  const [tab, setTab] = useState('Pending')
  const [error, setError] = useState('')
  const [items, setItems] = useState<Array<Post | Report | Channel | Action>>([])
  const superAdmin = profile?.role === 'super_admin'

  useEffect(() => { adminFetch<AdminProfile>('/admin/me/').then(setProfile).catch(() => setError('Your session has expired. Please sign in again.')) }, [])
  useEffect(() => {
    if (!profile) return
    const paths: Record<string, string> = { Pending: 'admin/posts/?status=pending', 'Live Posts': 'admin/posts/?status=approved', 'Reported Posts': 'admin/reports/', Channels: 'channels/', 'Audit Log': 'admin/moderation-actions/' }
    if (tab === 'Analytics' || (!superAdmin && tab === 'Audit Log')) return
    adminFetch<{ results?: Array<Post | Report | Channel | Action> } | Array<Post | Report | Channel | Action>>(`/${paths[tab]}`).then(value => setItems(Array.isArray(value) ? value : value.results || [])).catch(() => setError('Could not load this moderation view.'))
  }, [profile, tab, superAdmin])

  async function action(path: string, reasonRequired = false) {
    const reason = reasonRequired ? window.prompt('Enter a reason:')?.trim() : ''
    if (reasonRequired && !reason) return
    await adminFetch(path, { method: 'POST', body: JSON.stringify(reason ? { reason } : {}) })
    setItems(current => current.filter(item => !('id' in item) || String(item.id) !== path.split('/')[2]))
  }
  if (error && !profile) return <main className="page"><div className="container auth-card"><p className="form-error">{error}</p><Link href="/admin/login" className="button primary">Sign in again</Link></div></main>
  if (!profile) return <main className="page"><div className="container narrow"><p>Loading moderation desk…</p></div></main>
  const tabs = ['Pending', 'Live Posts', 'Reported Posts', 'Channels', ...(superAdmin ? ['Audit Log', 'Analytics'] : [])]
  return <main className="page admin-page"><div className="container"><div className="admin-title"><div><span className="eyebrow">STAFF ONLY · {profile.role}</span><h1>Moderation desk</h1></div><button className="button small" onClick={async () => { await fetch('/api/admin-auth/logout', { method: 'POST' }); window.location.href = '/admin/login' }}>Log out</button></div><div className="admin-tabs">{tabs.map(value => <button className={tab === value ? 'active' : ''} onClick={() => setTab(value)} key={value}>{value}</button>)}</div>{error && <p className="form-error">{error}</p>}{tab === 'Analytics' ? <p className="large-copy">Analytics are available to authorised staff through the reporting endpoints.</p> : <div className="admin-table">{items.map(item => <div className="admin-row" key={item.id}><span className="row-number">{item.id}</span><div><b>{'title' in item ? item.title : 'name' in item ? item.name : 'action' in item ? item.action : item.reason}</b><span>{'submitter_name' in item ? item.submitter_name : 'reason' in item ? item.reason : ''}</span></div><span className="status">{'status' in item ? item.status : ''}</span>{'title' in item && <><button className="review-button" onClick={() => action(`admin/posts/${item.id}/approve/`)}>Approve →</button><button className="review-button" onClick={() => action(`admin/posts/${item.id}/reject/`, true)}>Reject →</button></>}{'name' in item && <button className="review-button" onClick={() => action(`admin/channels/${item.id}/verify/`)}>Verify →</button>}</div>)}</div>}</div></main>
}
