import { useEffect, useState } from 'react'
import { fetchApi } from '../api'
import Loader from '../components/Loader'

const TABLES = ['Gares', 'Lignes Train', 'Opérateurs', 'Trajets', 'Horaires'] as const
type TableName = (typeof TABLES)[number]

const ENDPOINT: Record<TableName, (l: number) => string> = {
  'Gares':        l => `/gares?limit=${l}`,
  'Lignes Train': l => `/lignes-train?limit=${l}`,
  'Opérateurs':   l => `/operateurs?limit=${l}`,
  'Trajets':      l => `/trajets?limit=${l}`,
  'Horaires':     l => `/horaires?limit=${l}`,
}

const TAB_COLORS: Record<TableName, string> = {
  'Gares':        '#6366f1',
  'Lignes Train': '#0ea5e9',
  'Opérateurs':   '#22c55e',
  'Trajets':      '#f59e0b',
  'Horaires':     '#ec4899',
}

export default function DonneesBrutes() {
  const [table,   setTable]   = useState<TableName>('Gares')
  const [limit,   setLimit]   = useState(50)
  const [data,    setData]    = useState<Record<string, unknown>[] | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    fetchApi<Record<string, unknown>[]>(ENDPOINT[table](limit)).then(d => {
      setData(d ?? [])
      setLoading(false)
    })
  }, [table, limit])

  const keys = data && data.length > 0 ? Object.keys(data[0]) : []
  const accent = TAB_COLORS[table]

  return (
    <div style={{
      background: '#ffffff', border: '1px solid #e2e8f0',
      borderRadius: '14px', padding: '22px 24px',
      boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
    }}>

      {/* Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px', flexWrap: 'wrap' }}>

        {/* Table tabs */}
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {TABLES.map(t => {
            const active = table === t
            const c = TAB_COLORS[t]
            return (
              <button key={t} onClick={() => setTable(t)} style={{
                padding: '7px 14px', borderRadius: '8px',
                fontSize: '12px', fontWeight: active ? 600 : 400,
                color: active ? '#ffffff' : '#64748b',
                background: active ? c : '#f8fafc',
                border: `1px solid ${active ? c : '#e2e8f0'}`,
                cursor: 'pointer', transition: 'all 0.15s',
                boxShadow: active ? `0 2px 8px ${c}40` : 'none',
              }}>
                {t}
              </button>
            )
          })}
        </div>

        {/* Limit */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginLeft: 'auto' }}>
          <span style={{ fontSize: '12px', color: '#94a3b8' }}>Lignes :</span>
          <input type="range" min={10} max={500} step={10} value={limit}
            onChange={e => setLimit(Number(e.target.value))}
            style={{ width: '100px', accentColor: accent }} />
          <span style={{
            fontSize: '12px', fontWeight: 700,
            color: accent, minWidth: '28px', textAlign: 'right',
            fontVariantNumeric: 'tabular-nums',
          }}>
            {limit}
          </span>
        </div>
      </div>

      {/* Meta */}
      {data && !loading && (
        <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '14px' }}>
          <span style={{
            display: 'inline-block', padding: '3px 10px', borderRadius: '20px',
            background: `${accent}15`, color: accent, fontWeight: 600, fontSize: '11px',
          }}>
            {table}
          </span>
          {' '}— {data.length} entrée{data.length > 1 ? 's' : ''}
        </div>
      )}

      {/* Table */}
      {loading ? (
        <Loader />
      ) : data && keys.length > 0 ? (
        <div style={{
          overflowX: 'auto', overflowY: 'auto',
          maxHeight: '62vh', borderRadius: '10px',
          border: '1px solid #f1f5f9',
        }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
            <thead style={{ position: 'sticky', top: 0, zIndex: 10 }}>
              <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                {keys.map(k => (
                  <th key={k} style={{
                    padding: '10px 14px', textAlign: 'left',
                    color: '#94a3b8', fontWeight: 600,
                    textTransform: 'uppercase', fontSize: '10px', letterSpacing: '0.6px',
                    whiteSpace: 'nowrap',
                  }}>
                    {k}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, i) => (
                <tr key={i}
                  style={{
                    borderBottom: '1px solid #f8fafc',
                    background: i % 2 !== 0 ? '#fafafa' : '#ffffff',
                    transition: 'background 0.1s',
                  }}
                  onMouseEnter={e => (e.currentTarget.style.background = `${accent}08`)}
                  onMouseLeave={e => (e.currentTarget.style.background = i % 2 !== 0 ? '#fafafa' : '#ffffff')}>
                  {keys.map(k => (
                    <td key={k} style={{ padding: '9px 14px', color: '#334155', whiteSpace: 'nowrap' }}>
                      {String(row[k] ?? '—')}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  )
}
