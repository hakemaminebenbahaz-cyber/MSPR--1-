import { useEffect, useState } from 'react'
import { fetchApi } from '../api'
import Loader from '../components/Loader'

const TABLES = ['Opérateurs', 'Gares', 'Dessertes'] as const
type TableName = (typeof TABLES)[number]

const ENDPOINT: Record<TableName, (l: number) => string> = {
  'Opérateurs': l => `/operateurs/?limit=${l}`,
  'Gares':      l => `/gares/?limit=${l}`,
  'Dessertes':  l => `/dessertes/?limit=${l}`,
}

const TAB_COLORS: Record<TableName, string> = {
  'Opérateurs': '#22c55e',
  'Gares':      '#6366f1',
  'Dessertes':  '#f97316',
}

// Champs à exclure (objets imbriqués)
const EXCLUDE_KEYS: Record<TableName, string[]> = {
  'Opérateurs': [],
  'Gares':      [],
  'Dessertes':  ['operateur', 'gare_depart', 'gare_arrivee'],
}

// Champs à afficher en badge
const BADGE_FIELD: Record<string, Record<string, string>> = {
  type_service: { Jour: '#f59e0b', Nuit: '#6366f1' },
  pays_code:    { FR: '#0ea5e9', DE: '#ec4899', AT: '#22c55e', BE: '#8b5cf6', CH: '#f97316', EU: '#94a3b8' },
}

export default function DonneesBrutes() {
  const [table,   setTable]   = useState<TableName>('Dessertes')
  const [limit,   setLimit]   = useState(50)
  const [data,    setData]    = useState<Record<string, unknown>[] | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    setData(null)
    fetchApi<Record<string, unknown>[]>(ENDPOINT[table](limit)).then(d => {
      setData(d ?? [])
      setLoading(false)
    })
  }, [table, limit])

  const exclude = EXCLUDE_KEYS[table]
  const keys = data && data.length > 0
    ? Object.keys(data[0]).filter(k => !exclude.includes(k))
    : []
  const accent = TAB_COLORS[table]

  return (
    <div style={{
      background: 'var(--bg-card)', border: '1px solid var(--border)',
      borderRadius: '14px', padding: '22px 24px',
      boxShadow: 'var(--shadow)',
    }}>

      {/* Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', gap: '6px' }}>
          {TABLES.map(t => {
            const active = table === t
            const c = TAB_COLORS[t]
            return (
              <button key={t} onClick={() => setTable(t)} style={{
                padding: '7px 16px', borderRadius: '8px', fontSize: '12px',
                fontWeight: active ? 600 : 400,
                color: active ? '#ffffff' : 'var(--text-3)',
                background: active ? c : 'var(--bg-input)',
                border: `1px solid ${active ? c : 'var(--border)'}`,
                cursor: 'pointer', transition: 'all 0.15s',
                boxShadow: active ? `0 2px 8px ${c}40` : 'none',
              }}>
                {t}
              </button>
            )
          })}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginLeft: 'auto' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-4)' }}>Lignes :</span>
          <input type="range" min={10} max={200} step={10} value={limit}
            onChange={e => setLimit(Number(e.target.value))}
            style={{ width: '100px', accentColor: accent }} />
          <span style={{
            fontSize: '12px', fontWeight: 700, color: accent,
            minWidth: '32px', textAlign: 'right', fontVariantNumeric: 'tabular-nums',
          }}>
            {limit}
          </span>
        </div>
      </div>

      {/* Meta */}
      {data && !loading && (
        <div style={{ fontSize: '12px', color: 'var(--text-4)', marginBottom: '14px' }}>
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
          border: '1px solid var(--border-lt)',
        }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
            <thead style={{ position: 'sticky', top: 0, zIndex: 10 }}>
              <tr style={{ background: 'var(--bg-thead)', borderBottom: '1px solid var(--border)' }}>
                {keys.map(k => (
                  <th key={k} style={{
                    padding: '10px 14px', textAlign: 'left',
                    color: 'var(--text-4)', fontWeight: 600,
                    textTransform: 'uppercase', fontSize: '10px',
                    letterSpacing: '0.6px', whiteSpace: 'nowrap',
                  }}>
                    {k.replace(/_/g, ' ')}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, i) => (
                <tr key={i}
                  style={{
                    borderBottom: '1px solid var(--border-lt)',
                    background: i % 2 !== 0 ? 'var(--bg-row-alt)' : 'var(--bg-card)',
                    transition: 'background 0.1s',
                  }}
                  onMouseEnter={e => (e.currentTarget.style.background = `${accent}08`)}
                  onMouseLeave={e => (e.currentTarget.style.background = i % 2 !== 0 ? 'var(--bg-row-alt)' : 'var(--bg-card)')}>
                  {keys.map(k => {
                    const val = row[k]
                    // Badge coloré
                    if (BADGE_FIELD[k]) {
                      const color = BADGE_FIELD[k][String(val)] ?? '#94a3b8'
                      return (
                        <td key={k} style={{ padding: '9px 14px', whiteSpace: 'nowrap' }}>
                          <span style={{
                            padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 600,
                            background: `${color}18`, color,
                          }}>
                            {String(val ?? '—')}
                          </span>
                        </td>
                      )
                    }
                    // Formatage spécial
                    let display = String(val ?? '—')
                    if (k === 'emissions_co2_gkm' && val) display = `${val} g/km`
                    if (k === 'duree_h' && val) display = `${val} h`
                    return (
                      <td key={k} style={{ padding: '9px 14px', color: 'var(--text-2)', whiteSpace: 'nowrap' }}>
                        {display}
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  )
}
