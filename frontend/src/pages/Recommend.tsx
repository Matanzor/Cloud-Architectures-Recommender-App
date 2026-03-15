import { useState } from 'react'
import { Link } from 'react-router-dom'
import { recommend, RecommendRequest } from '../api'

const OPTIONS = {
  use_case: ['web_application', 'public_api', 'ecommerce', 'real_time_analytics', 'batch_processing', 'event_processing', 'media_delivery', 'internal_tool', 'iot_ingestion', 'ml_inference'],
  scale: ['small', 'medium', 'large'],
  traffic_pattern: ['steady', 'bursty', 'spiky', 'scheduled', 'unpredictable'],
  latency_sensitivity: ['low', 'medium', 'high'],
  processing_style: ['request_response', 'event_driven', 'batch', 'streaming'],
  data_intensity: ['low', 'medium', 'high'],
  availability_requirement: ['standard', 'high', 'critical'],
  ops_preference: ['managed_services', 'balanced', 'self_managed_ok'],
  budget_sensitivity: ['low', 'medium', 'high'],
}

const defaultReq: RecommendRequest = {
  use_case: 'web_application',
  scale: 'medium',
  traffic_pattern: 'steady',
  latency_sensitivity: 'medium',
  processing_style: 'request_response',
  data_intensity: 'medium',
  availability_requirement: 'standard',
  ops_preference: 'managed_services',
  budget_sensitivity: 'medium',
}

interface RecResult {
  architecture: { id: string; title: string; description: string; metadata: Record<string, string> }
  score: number
  explanation: string
}

export default function RecommendPage() {
  const [req, setReq] = useState<RecommendRequest>(defaultReq)
  const [results, setResults] = useState<RecResult[]>([])
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    try {
      const data = await recommend(req)
      setResults(data.recommendations || [])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1>Get Recommendations</h1>
      <form onSubmit={handleSubmit} style={{ marginBottom: 24 }}>
        {Object.entries(OPTIONS).map(([key, opts]) => (
          <div key={key} style={{ marginBottom: 12 }}>
            <label style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>
              {key.replace(/_/g, ' ')}
            </label>
            <select
              value={req[key as keyof RecommendRequest]}
              onChange={(e) => setReq({ ...req, [key]: e.target.value })}
              style={{ padding: 6, minWidth: 200 }}
            >
              {opts.map((o) => (
                <option key={o} value={o}>{o}</option>
              ))}
            </select>
          </div>
        ))}
        <button type="submit" disabled={loading} style={{ padding: '8px 24px' }}>
          {loading ? 'Loading...' : 'Recommend'}
        </button>
      </form>

      {results.length > 0 && (
        <div>
          <h2>Results</h2>
          {results.map((r) => (
            <div
              key={r.architecture.id}
              style={{
                padding: 16,
                marginBottom: 12,
                background: '#fff',
                borderRadius: 6,
                border: '1px solid #ddd',
              }}
            >
              <Link to={`/architectures/${r.architecture.id}`}>
                <strong>{r.architecture.title}</strong>
              </Link>
              <p style={{ margin: '8px 0', fontSize: 14 }}>{r.explanation}</p>
              <span style={{ fontSize: 12, color: '#666' }}>Score: {r.score}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
