import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import ArchitectureDetail from './pages/ArchitectureDetail'
import Recommend from './pages/Recommend'

function App() {
  return (
    <BrowserRouter>
      <nav style={{ padding: '12px 24px', background: '#333', color: '#fff' }}>
        <Link to="/" style={{ color: '#fff', marginRight: 16 }}>Dashboard</Link>
        <Link to="/recommend" style={{ color: '#fff' }}>Get Recommendations</Link>
      </nav>
      <main style={{ padding: 24, maxWidth: 1000, margin: '0 auto' }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/architectures/:id" element={<ArchitectureDetail />} />
          <Route path="/recommend" element={<Recommend />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}

export default App
