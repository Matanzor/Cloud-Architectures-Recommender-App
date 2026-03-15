import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { listArchitectures, triggerScrape } from '../api'

interface ArchItem {
  id: string
  title: string
  source_url: string
  scraped_at: string
  metadata: Record<string, string>
}

export default function Dashboard() {
  const [archs, setArchs] = useState<ArchItem[]>([])
  const [loading, setLoading] = useState(true)
  const [scraping, setScraping] = useState(false)

  async function load() {
    setLoading(true)
    try {
      const data = await listArchitectures()
      setArchs(data.architectures || [])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  async function handleScrape() {
    setScraping(true)
    try {
      await triggerScrape()
      setTimeout(load, 3000)
    } finally {
      setScraping(false)
    }
  }

  return (
    <div>
      <h1>Architectures</h1>
      <button
        onClick={handleScrape}
        disabled={scraping}
        style={{ marginBottom: 16, padding: '8px 16px' }}
      >
        {scraping ? 'Scraping...' : 'Trigger Scrape'}
      </button>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {archs.map((a) => (
            <li
              key={a.id}
              style={{
                padding: 12,
                marginBottom: 8,
                background: '#fff',
                borderRadius: 6,
                border: '1px solid #ddd',
              }}
            >
              <Link to={`/architectures/${a.id}`}>
                <strong>{a.title}</strong>
              </Link>
              <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>
                {new Date(a.scraped_at).toLocaleString()} · {a.metadata?.use_case || '-'}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
