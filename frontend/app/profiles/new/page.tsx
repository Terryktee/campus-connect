'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { Footer, Header } from '@/components/public-api-pages'
import { getInstitutions, type ApiInstitution } from '@/lib/api'

export default function Page() {
  const [sent, setSent] = useState(false)
  const [institutions, setInstitutions] = useState<ApiInstitution[]>([])

  useEffect(() => {
    getInstitutions().then(setInstitutions).catch(() => setInstitutions([]))
  }, [])

  return (
    <>
      <Header />
      <main className="page">
        <div className="container form-card narrow">
          <span className="eyebrow">BE KNOWN FOR SOMETHING</span>
          <h1>Create a profile</h1>
          <p>
            Tell students who you are and what you are learning, building or looking for.
          </p>

          {sent ? (
            <div className="success">
              <div className="success-mark">✓</div>
              <h2>Profile created.</h2>
              <Link href="/profiles" className="button primary">
                View profiles
              </Link>
            </div>
          ) : (
            <form
              onSubmit={(e) => {
                e.preventDefault()
                setSent(true)
              }}
            >
              <label>
                Username *
                <input required placeholder="e.g. nyasha.codes" />
              </label>

              <label>
                Name *
                <input required placeholder="Your name" />
              </label>

              <label>
                Institution *
                <select required defaultValue={institutions[0]?.name ?? ''}>
                  {institutions.map((item) => (
                    <option key={item.id} value={item.name}>
                      {item.name}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Programme *
                <input required placeholder="What are you studying?" />
              </label>

              <label>
                Description *
                <textarea
                  required
                  rows={5}
                  placeholder="What should students know about you?"
                />
              </label>

              <button className="button primary">
                Create profile <span>→</span>
              </button>
            </form>
          )}
        </div>
      </main>
      <Footer />
    </>
  )
}
