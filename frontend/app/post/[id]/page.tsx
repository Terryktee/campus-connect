import Link from 'next/link'
import { Header, Footer } from '@/components/campus-app'
import { ApiError, getCategories, getInstitutions, getPost } from '@/lib/api'

export const dynamic = 'force-dynamic'

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  try {
    const [post, categories, institutions] = await Promise.all([getPost(id), getCategories(), getInstitutions()])
    const category = categories.find(item => item.id === post.category)?.name || 'Community'
    const institution = institutions.find(item => item.id === post.institution)?.name
    return <><Header/><main className="page"><article className="container narrow"><span className="category-pill">{category}</span><h1>{post.title}</h1><p className="large-copy">{post.content}</p><div className="post-meta"><span className="avatar">{(post.submitter_name || 'C').charAt(0)}</span>{post.submitter_name || 'CampusConnect community'}{institution && <span>{institution}</span>}<span>{new Date(post.created_at).toLocaleDateString()}</span></div>{post.link_url && <p><a className="text-link" href={post.link_url} rel="noreferrer">View the original link →</a></p>}<Link href="/" className="text-link">← Back to the noticeboard</Link></article></main><Footer/></>
  } catch (error) {
    const message = error instanceof ApiError ? error.message : 'We could not load this post.'
    return <><Header/><main className="page"><div className="container narrow"><h1>Post unavailable</h1><p className="large-copy">{message}</p><Link href="/" className="button primary">Back to explore</Link></div></main><Footer/></>
  }
}
