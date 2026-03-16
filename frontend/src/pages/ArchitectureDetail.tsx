import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getArchitecture } from '../api'

interface Resource {
  resource_type: string
  resource_name: string
  count: number
}

interface Arch {
  id: string
  title: string
  source_url: string
  description: string
  scraped_at: string
  resources: Resource[]
  metadata: Record<string, string>
  parsed_with?: string
}

export default function ArchitectureDetail() {
  const { id } = useParams<{ id: string }>()
  const [arch, setArch] = useState<Arch | null>(null)

  useEffect(() => {
    if (!id) return
    getArchitecture(id).then(setArch)
  }, [id])

  if (!arch) return <p>Loading...</p>

  return (
    <div>
      <Link to="/" style={{ marginBottom: 16, display: 'block' }}>← Back</Link>
      <h1>{arch.title}</h1>
      {arch.parsed_with && (
        <p style={{ fontSize: 12, color: '#666', marginTop: -8 }}>Parsed with: {arch.parsed_with}</p>
      )}
      <p style={{ color: '#666' }}>
        <a href={arch.source_url} target="_blank" rel="noreferrer">{arch.source_url}</a>
      </p>
      <p>{new Date(arch.scraped_at).toLocaleString()}</p>
      <p>{arch.description}</p>
      <h3>Resources</h3>
      <ul>
        {arch.resources?.map((r, i) => (
          <li key={i}>{r.resource_type} – {r.resource_name} (x{r.count})</li>
        ))}
      </ul>
      <h3>Metadata</h3>
      <dl style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '4px 24px' }}>
        {arch.metadata && Object.entries(arch.metadata).map(([k, v]) => (
          <React.Fragment key={k}>
            <dt style={{ fontWeight: 600 }}>{k}</dt>
            <dd>{v}</dd>
          </React.Fragment>
        ))}
      </dl>
    </div>
  )
}
