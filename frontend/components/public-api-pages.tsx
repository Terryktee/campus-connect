'use client'

import Link from 'next/link'
import { useEffect, useMemo, useState } from 'react'
import { Header, Footer } from '@/components/campus-app'
import {
  ApiError, ApiPost, getCategories, getChannel, getChannels, getInstitutions, getPosts,
  type ApiCategory, type ApiChannel, type ApiInstitution,
} from '@/lib/api'

function State({ message, retry }: { message: string; retry?: () => void }) {
  return <div className="container narrow" role="status"><p className="large-copy">{message}</p>{retry && <button className="button primary" onClick={retry}>Try again</button>}</div>
}

function postView(post: ApiPost, categories: ApiCategory[], institutions: ApiInstitution[], channels: ApiChannel[]) {
  return {
    ...post,
    categoryName: categories.find(item => item.id === post.category)?.name || 'Community',
    institutionName: institutions.find(item => item.id === post.institution)?.name || '',
    channelName: channels.find(item => item.id === post.channel)?.name || '',
  }
}

export function ApiHome() {
  const [posts, setPosts] = useState<ApiPost[]>([])
  const [categories, setCategories] = useState<ApiCategory[]>([])
  const [institutions, setInstitutions] = useState<ApiInstitution[]>([])
  const [channels, setChannels] = useState<ApiChannel[]>([])
  const [active, setActive] = useState('all')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true); setError('')
    Promise.all([getPosts(), getCategories(), getInstitutions(), getChannels()])
      .then(([postData, categoryData, institutionData, channelData]) => {
        setPosts(postData); setCategories(categoryData); setInstitutions(institutionData); setChannels(channelData)
      })
      .catch((reason: unknown) => setError(reason instanceof ApiError ? reason.message : 'We could not load the noticeboard.'))
      .finally(() => setLoading(false))
  }
  useEffect(load, [])

  const visible = useMemo(() => posts
    .filter(post => active === 'all' || post.category === Number(active))
    .map(post => postView(post, categories, institutions, channels)), [posts, categories, institutions, channels, active])

  return <><Header/><main><section className="hero"><div className="container hero-grid"><div><span className="eyebrow">THE STUDENT NOTICEBOARD</span><h1>What&apos;s happening<br/><i>on campus?</i></h1><p className="hero-copy">University news, opportunities, and tech for Zimbabwean students. Find your people, share what matters and make campus life a little easier.</p><div className="hero-actions"><Link href="/submit" className="button primary">Submit a Post <span>→</span></Link><Link href="/orientation" className="button ghost">New here? Start here</Link></div></div></div></section><section className="container feed-section"><div className="section-heading"><div><span className="eyebrow">FROM THE COMMUNITY</span><h2>Fresh on the noticeboard</h2></div><Link href="/channels" className="text-link">Explore channels →</Link></div>{loading ? <State message="Loading the latest posts…"/> : error ? <State message={error} retry={load}/> : <><div className="category-row"><button className={active === 'all' ? 'category active' : 'category'} onClick={() => setActive('all')}>All posts</button>{categories.map(category => <button className={active === String(category.id) ? 'category active' : 'category'} key={category.id} onClick={() => setActive(String(category.id))}>{category.name}</button>)}</div>{visible.length ? <div className="post-grid">{visible.map((post, index) => <article className={index === 0 && active === 'all' ? 'post-card featured' : 'post-card'} key={post.id}><div className="post-top"><span className="category-pill">{post.categoryName}</span><span className="post-time">{new Date(post.created_at).toLocaleDateString()}</span></div><Link href={`/post/${post.id}`}><h3>{post.title}</h3></Link><p>{post.content}</p><div className="post-meta"><span className="avatar">{(post.submitter_name || 'C').charAt(0)}</span><span>{post.channelName || post.institutionName || post.submitter_name || 'CampusConnect'}</span><span className="meta-spacer"/></div></article>)}</div> : <State message="No approved posts match this category yet."/>}</>}</section></main><Footer/></>
}

export function ApiChannels() {
  const [channels, setChannels] = useState<ApiChannel[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  useEffect(() => { getChannels().then(setChannels).catch((reason: unknown) => setError(reason instanceof ApiError ? reason.message : 'We could not load channels.')).finally(() => setLoading(false)) }, [])
  return <><Header/><main className="page"><div className="container page-intro"><span className="eyebrow">FIND YOUR PEOPLE</span><h1>Campus channels</h1><p>Join focused communities with their own description, conversations and opportunities.</p></div>{loading ? <State message="Loading channels…"/> : error ? <State message={error}/> : channels.length ? <div className="container channel-grid">{channels.map(channel => <div className="channel-card green" key={channel.id}><Link href={`/c/${channel.slug}`} className="channel-badge">{channel.name.slice(0, 3).toUpperCase()}</Link><div><Link href={`/c/${channel.slug}`}><h3>{channel.name}</h3></Link><p>{channel.bio}</p><span>{channel.follower_count} followers</span></div></div>)}</div> : <State message="No active channels are available yet."/>}</main><Footer/></>
}

export function ApiInstitutions({ children }: { children: (institutions: ApiInstitution[]) => React.ReactNode }) {
  const [items, setItems] = useState<ApiInstitution[]>([])
  useEffect(() => { getInstitutions().then(setItems).catch(() => setItems([])) }, [])
  return <>{children(items)}</>
}
