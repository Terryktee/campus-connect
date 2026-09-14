'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { Footer, Header } from '@/components/public-api-pages'
import { getChannels, type ApiChannel } from '@/lib/api'

const eventTypes = ['Workshop', 'Social', 'Career', 'Talk', 'Campus Event']

export default function Page() {
  const [sent, setSent] = useState(false)
  const [channels, setChannels] = useState<ApiChannel[]>([])

  useEffect(() => {
    getChannels().then(setChannels).catch(() => setChannels([]))
  }, [])

  return <><Header /><main className="page"><div className="container form-card narrow"><span className="eyebrow">PUT IT ON THE CALENDAR</span><h1>Add an event</h1><p>Help students find useful things happening nearby.</p>{sent ? <div className="success"><div className="success-mark">✓</div><h2>Event draft submitted.</h2><Link href="/events" className="button primary">View events</Link></div> : <form onSubmit={e => { e.preventDefault(); setSent(true) }}><label>Event title *<input required placeholder="e.g. Build night" /></label><div className="form-two"><label>Date *<input required type="date" /></label><label>Type *<select required>{eventTypes.map(type => <option key={type} value={type}>{type}</option>)}</select></label></div><label>Place or online link *<input required placeholder="Student Centre or https://..." /></label><label>Host channel *<select required defaultValue={channels[0]?.slug ?? ''}>{channels.map(channel => <option key={channel.id} value={channel.slug}>{channel.name}</option>)}</select></label><label>Description *<textarea required rows={5} placeholder="Tell students what to expect..." /></label><button className="button primary">Add event <span>→</span></button></form>}</div></main><Footer /></>
}
