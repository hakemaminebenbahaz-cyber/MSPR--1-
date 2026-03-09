import { useEffect, useState } from 'react'
import { checkHealth } from '../api'
import type { Page } from '../App'
import { useTheme } from '../context/ThemeContext'

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
  const { dark, toggle } = useTheme()

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
      background: 'var(--bg-nav)',
      borderBottom: 'var(--nav-border)',
      boxShadow: 'var(--shadow)',
      transition: 'background 0.2s',
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
          <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-1)', letterSpacing: '-0.3px' }}>
            ObRail Europe
          </div>
          <div style={{ fontSize: '10px', color: 'var(--text-4)', letterSpacing: '0.5px', marginTop: '-1px' }}>
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
            color: page === tab.id ? '#6366f1' : 'var(--text-3)',
            background: page === tab.id ? (dark ? '#312e81' : '#f5f3ff') : 'transparent',
            border: 'none', borderRadius: '8px',
            cursor: 'pointer', transition: 'all 0.15s',
          }}
          onMouseEnter={e => { if (page !== tab.id) e.currentTarget.style.background = dark ? '#1e293b' : '#f8fafc' }}
          onMouseLeave={e => { if (page !== tab.id) e.currentTarget.style.background = 'transparent' }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Right side */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
        <span style={{
          width: '8px', height: '8px', borderRadius: '50%', display: 'inline-block',
          background: healthy === null ? 'var(--text-4)' : healthy ? '#22c55e' : '#ef4444',
          boxShadow: healthy ? '0 0 6px rgba(34,197,94,0.5)' : 'none',
        }} />
        <span style={{ fontSize: '12px', color: 'var(--text-4)' }}>
          {healthy === null ? 'Vérification…' : healthy ? 'API en ligne' : 'API hors ligne'}
        </span>

        <div style={{ width: '1px', height: '16px', background: 'var(--border)', margin: '0 4px' }} />

        {/* Dark mode toggle */}
        <button onClick={toggle} title={dark ? 'Mode clair' : 'Mode sombre'} style={{
          width: '34px', height: '34px', borderRadius: '8px', border: '1px solid var(--border)',
          background: 'var(--bg-input)', cursor: 'pointer', display: 'flex',
          alignItems: 'center', justifyContent: 'center', fontSize: '16px',
          transition: 'all 0.15s',
        }}>
          {dark ? '☀️' : '🌙'}
        </button>

        <div style={{ width: '1px', height: '16px', background: 'var(--border)', margin: '0 4px' }} />
        <a href="http://localhost:8001/docs" target="_blank" rel="noreferrer"
          style={{ fontSize: '12px', color: '#6366f1', textDecoration: 'none', fontWeight: 500 }}>
          Docs →
        </a>
      </div>
    </nav>
  )
}
