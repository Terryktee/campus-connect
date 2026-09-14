'use client'

import Link from 'next/link'
import { useState } from 'react'
import { Footer, Header } from '@/components/public-api-pages'

export default function Page() {
  const [sent, setSent] = useState(false)

  return <><Header /><main className="page"><div className="container form-card narrow"><span className="eyebrow">MAKE ROOM FOR A NEW COMMUNITY</span><h1>Add a channel</h1><p>Channels are focused communities with their own description and feed.</p>{sent ? <div className="success"><div className="success-mark">✓</div><h2>Channel draft submitted.</h2><Link href="/channels" className="button primary">View channels</Link></div> : <form onSubmit={e => { e.preventDefault(); setSent(true) }}><label>Channel name *<input required placeholder="e.g. Women in STEM Zimbabwe" /></label><label>Short code *<input required maxLength={6} placeholder="e.g. WSTEM" /></label><label>What is this channel about? *<textarea required rows={5} placeholder="What will students find here?" /></label><button className="button primary">Submit channel <span>→</span></button></form>}</div></main><Footer /></>
}
