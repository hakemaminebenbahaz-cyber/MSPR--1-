import { useEffect, useState } from 'react'
import { checkHealth } from '../api'
import type { Page } from '../App'

interface Props {
  page: Page
  setPage: (p: Page) => void
}

const navItems: { id: Page; label: string; icon: string }[] = [
  { id: 'globale',   label: 'Vue Globale',    icon: '▦' },
  { id: 'recherche', label: 'Recherche',       icon: '⌕' },
  { id: 'brutes',    label: 'Données brutes',  icon: '☰' },
]

export default function Sidebar({ page, setPage }: Props) {
  const [healthy, setHealthy] = useState<boolean | null>(null)

  useEffect(() => {
    checkHealth().then(setHealthy)
    const id = setInterval(() => checkHealth().then(setHealthy), 30_000)
    return () => clearInterval(id)
  }, [])

  return (
    <aside style={{
      width: '220px',
      flexShrink: 0,
      display: 'flex',
      flexDirection: 'column',
      background: '#161b22',
      borderRight: '1px solid #21262d',
      minHeight: '100vh',
      position: 'sticky',
      top: 0,
      height: '100vh',
    }}>

      {/* Logo */}
      <div style={{ padding: '28px 24px 20px', borderBottom: '1px solid #21262d' }}>
        <div style={{ fontSize: '13px', fontWeight: 700, color: '#e6edf3', letterSpacing: '0.5px' }}>
          ObRail Europe
        </div>
        <div style={{ fontSize: '11px', color: '#484f58', marginTop: '3px', letterSpacing: '1.5px', textTransform: 'uppercase' }}>
          Tableau de bord
        </div>
      </div>

      {/* Nav */}
      <nav style={{ padding: '16px 12px', flex: 1 }}>
        <p style={{ fontSize: '10px', color: '#484f58', textTransform: 'uppercase', letterSpacing: '1.5px', padding: '0 10px', marginBottom: '8px' }}>
          Navigation
        </p>
        {navItems.map(item => (
          <button
            key={item.id}
            onClick={() => setPage(item.id)}
            style={{
              width: '100%',
              textAlign: 'left',
              padding: '9px 12px',
              borderRadius: '6px',
              marginBottom: '2px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              fontSize: '13px',
              fontWeight: page === item.id ? 600 : 400,
              color: page === item.id ? '#e6edf3' : '#8b949e',
              background: page === item.id ? '#21262d' : 'transparent',
              border: 'none',
              cursor: 'pointer',
              transition: 'all 0.15s',
            }}
            onMouseEnter={e => {
              if (page !== item.id) e.currentTarget.style.background = '#1c2128'
              if (page !== item.id) e.currentTarget.style.color = '#c9d1d9'
            }}
            onMouseLeave={e => {
              if (page !== item.id) e.currentTarget.style.background = 'transparent'
              if (page !== item.id) e.currentTarget.style.color = '#8b949e'
            }}
          >
            <span style={{ fontSize: '14px', opacity: 0.7 }}>{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>

      {/* Bottom */}
      <div style={{ padding: '16px 24px', borderTop: '1px solid #21262d' }}>
        <div style={{ fontSize: '11px', color: '#484f58', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '1px' }}>
          API Status
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{
            width: '7px', height: '7px', borderRadius: '50%',
            background: healthy === null ? '#484f58' : healthy ? '#3fb950' : '#f85149',
            display: 'inline-block',
            boxShadow: healthy ? '0 0 6px rgba(63,185,80,0.5)' : 'none',
          }} />
          <span style={{ fontSize: '12px', color: '#8b949e' }}>
            {healthy === null ? 'Vérification...' : healthy ? 'Connectée' : 'Hors ligne'}
          </span>
        </div>
        <a
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noreferrer"
          style={{ display: 'block', marginTop: '12px', fontSize: '12px', color: '#58a6ff', textDecoration: 'none' }}
        >
          Documentation →
        </a>
      </div>
    </aside>
  )
}
