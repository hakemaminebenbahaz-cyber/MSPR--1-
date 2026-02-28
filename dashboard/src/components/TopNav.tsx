import { useEffect, useState } from 'react'
import { checkHealth } from '../api'
import type { Page } from '../App'

interface Props {
  page: Page
  setPage: (p: Page) => void
}

const TABS: { id: Page; label: string }[] = [
  { id: 'globale',   label: 'Vue Globale'    },
  { id: 'recherche', label: 'Recherche'      },
  { id: 'brutes',    label: 'Données brutes' },
]

export default function TopNav({ page, setPage }: Props) {
  const [healthy, setHealthy] = useState<boolean | null>(null)

  useEffect(() => {
    checkHealth().then(setHealthy)
    const id = setInterval(() => checkHealth().then(setHealthy), 30_000)
    return () => clearInterval(id)
  }, [])

  return (
    <nav style={{
      position: 'sticky', top: 0, zIndex: 50,
      display: 'flex', alignItems: 'center',
      padding: '0 32px', height: '60px',
      background: '#ffffff',
      borderBottom: '1px solid #e2e8f0',
      boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
    }}>

      {/* Brand */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginRight: '40px', flexShrink: 0 }}>
        <div style={{
          width: '32px', height: '32px',
          background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
          borderRadius: '8px',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '16px', boxShadow: '0 2px 8px rgba(99,102,241,0.35)',
        }}>
          🚂
        </div>
        <div>
          <div style={{ fontSize: '14px', fontWeight: 700, color: '#0f172a', letterSpacing: '-0.3px' }}>
            ObRail Europe
          </div>
          <div style={{ fontSize: '10px', color: '#94a3b8', letterSpacing: '0.5px', marginTop: '-1px' }}>
            Observatoire Ferroviaire
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '2px', flex: 1 }}>
        {TABS.map(tab => (
          <button key={tab.id} onClick={() => setPage(tab.id)} style={{
            position: 'relative', padding: '7px 16px',
            fontSize: '13px', fontWeight: page === tab.id ? 600 : 400,
            color: page === tab.id ? '#6366f1' : '#64748b',
            background: page === tab.id ? '#f5f3ff' : 'transparent',
            border: 'none', borderRadius: '8px',
            cursor: 'pointer', transition: 'all 0.15s',
          }}
          onMouseEnter={e => { if (page !== tab.id) e.currentTarget.style.background = '#f8fafc' }}
          onMouseLeave={e => { if (page !== tab.id) e.currentTarget.style.background = 'transparent' }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Status */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
        <span style={{
          width: '8px', height: '8px', borderRadius: '50%', display: 'inline-block',
          background: healthy === null ? '#cbd5e1' : healthy ? '#22c55e' : '#ef4444',
          boxShadow: healthy ? '0 0 6px rgba(34,197,94,0.5)' : 'none',
        }} />
        <span style={{ fontSize: '12px', color: '#94a3b8' }}>
          {healthy === null ? 'Vérification…' : healthy ? 'API en ligne' : 'API hors ligne'}
        </span>
        <div style={{ width: '1px', height: '16px', background: '#e2e8f0', margin: '0 4px' }} />
        <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer"
          style={{ fontSize: '12px', color: '#6366f1', textDecoration: 'none', fontWeight: 500 }}>
          Docs →
        </a>
      </div>
    </nav>
  )
}
