import { useState, type FormEvent } from 'react'
import { fetchApi } from '../api'

const CARD: React.CSSProperties = {
  background: '#ffffff',
  border: '1px solid #e2e8f0',
  borderRadius: '14px',
  padding: '22px 24px',
  boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
}

interface SearchBlockProps {
  title: string
  sub: string
  placeholder: string
  accentColor: string
  value: string
  onChange: (v: string) => void
  onSubmit: (e: FormEvent) => void
  results: Record<string, unknown>[] | null
  loading: boolean
}

function SearchBlock({ title, sub, placeholder, accentColor, value, onChange, onSubmit, results, loading }: SearchBlockProps) {
  const keys = results && results.length > 0 ? Object.keys(results[0]) : []

  return (
    <div style={CARD}>
      <p style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a', marginBottom: '2px' }}>{title}</p>
      <p style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '14px' }}>{sub}</p>

      <form onSubmit={onSubmit} style={{ display: 'flex', gap: '8px', marginBottom: results !== null ? '16px' : 0 }}>
        <input
          type="text"
          value={value}
          onChange={e => onChange(e.target.value)}
          placeholder={placeholder}
          style={{
            flex: 1, padding: '10px 14px', borderRadius: '9px',
            border: '1px solid #e2e8f0',
            background: '#f8fafc', color: '#0f172a', fontSize: '13px',
            outline: 'none', transition: 'border-color 0.2s, box-shadow 0.2s',
          }}
          onFocus={e => {
            e.currentTarget.style.borderColor = accentColor
            e.currentTarget.style.boxShadow = `0 0 0 3px ${accentColor}20`
          }}
          onBlur={e => {
            e.currentTarget.style.borderColor = '#e2e8f0'
            e.currentTarget.style.boxShadow = 'none'
          }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '10px 20px', borderRadius: '9px',
            border: 'none',
            background: accentColor,
            color: '#ffffff', fontSize: '13px', fontWeight: 600,
            cursor: 'pointer', transition: 'opacity 0.15s, transform 0.15s',
            boxShadow: `0 2px 8px ${accentColor}40`,
          }}
          onMouseEnter={e => e.currentTarget.style.opacity = '0.88'}
          onMouseLeave={e => e.currentTarget.style.opacity = '1'}
        >
          {loading ? '…' : 'Rechercher'}
        </button>
      </form>

      {results !== null && (
        results.length > 0 ? (
          <>
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: '6px',
              fontSize: '12px', fontWeight: 500,
              color: '#16a34a', background: '#f0fdf4',
              border: '1px solid #bbf7d0',
              borderRadius: '6px', padding: '4px 10px', marginBottom: '12px',
            }}>
              ✓ {results.length} résultat{results.length > 1 ? 's' : ''}
            </div>
            <div style={{ overflowX: 'auto', borderRadius: '10px', border: '1px solid #f1f5f9' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                <thead>
                  <tr style={{ background: '#f8fafc' }}>
                    {keys.map(k => (
                      <th key={k} style={{
                        padding: '10px 14px', textAlign: 'left',
                        color: '#94a3b8', fontWeight: 600,
                        textTransform: 'uppercase', fontSize: '10px', letterSpacing: '0.6px',
                        borderBottom: '1px solid #f1f5f9', whiteSpace: 'nowrap',
                      }}>
                        {k}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {results.map((row, i) => (
                    <tr key={i}
                      style={{ borderBottom: '1px solid #f8fafc', transition: 'background 0.1s' }}
                      onMouseEnter={e => (e.currentTarget.style.background = '#f8fafc')}
                      onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}>
                      {keys.map(k => (
                        <td key={k} style={{ padding: '10px 14px', color: '#334155', whiteSpace: 'nowrap' }}>
                          {String(row[k] ?? '—')}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        ) : (
          <div style={{
            fontSize: '13px', color: '#94a3b8', padding: '12px 0',
            display: 'flex', alignItems: 'center', gap: '8px',
          }}>
            <span style={{ fontSize: '16px' }}>🔍</span> Aucun résultat trouvé
          </div>
        )
      )}
    </div>
  )
}

const TYPE_OPTIONS = [
  { value: '', label: 'Tous les types' },
  { value: '2', label: 'Train (2)' },
  { value: '0', label: 'Tram (0)' },
  { value: '1', label: 'Métro (1)' },
  { value: '3', label: 'Bus (3)' },
  { value: '4', label: 'Ferry (4)' },
]

function DesserteBlock({ results, loading }: { results: Record<string, unknown>[] | null, loading: boolean }) {
  const keys = results && results.length > 0 ? Object.keys(results[0]) : []
  return results !== null ? (
    results.length > 0 ? (
      <>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: '6px',
          fontSize: '12px', fontWeight: 500, color: '#16a34a', background: '#f0fdf4',
          border: '1px solid #bbf7d0', borderRadius: '6px', padding: '4px 10px', marginBottom: '12px',
        }}>
          ✓ {results.length} résultat{results.length > 1 ? 's' : ''}
        </div>
        <div style={{ overflowX: 'auto', borderRadius: '10px', border: '1px solid #f1f5f9' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
            <thead>
              <tr style={{ background: '#f8fafc' }}>
                {keys.map(k => (
                  <th key={k} style={{
                    padding: '10px 14px', textAlign: 'left', color: '#94a3b8',
                    fontWeight: 600, textTransform: 'uppercase', fontSize: '10px',
                    letterSpacing: '0.6px', borderBottom: '1px solid #f1f5f9', whiteSpace: 'nowrap',
                  }}>{k}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {results.map((row, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #f8fafc' }}
                  onMouseEnter={e => (e.currentTarget.style.background = '#f8fafc')}
                  onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}>
                  {keys.map(k => (
                    <td key={k} style={{ padding: '10px 14px', color: '#334155', whiteSpace: 'nowrap' }}>
                      {String(row[k] ?? '—')}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </>
    ) : (
      <div style={{ fontSize: '13px', color: '#94a3b8', padding: '12px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ fontSize: '16px' }}>🔍</span> Aucun résultat trouvé
      </div>
    )
  ) : loading ? (
    <div style={{ fontSize: '13px', color: '#94a3b8', padding: '12px 0' }}>Chargement…</div>
  ) : null
}

export default function Recherche() {
  const [gareQ,    setGareQ]    = useState('')
  const [gareRes,  setGareRes]  = useState<Record<string, unknown>[] | null>(null)
  const [gareLoad, setGareLoad] = useState(false)
  const [ligneQ,    setLigneQ]    = useState('')
  const [ligneRes,  setLigneRes]  = useState<Record<string, unknown>[] | null>(null)
  const [ligneLoad, setLigneLoad] = useState(false)
  const [opQ,    setOpQ]    = useState('')
  const [opRes,  setOpRes]  = useState<Record<string, unknown>[] | null>(null)
  const [opLoad, setOpLoad] = useState(false)

  const [depart,        setDepart]        = useState('')
  const [arrivee,       setArrivee]       = useState('')
  const [typeTransport, setTypeTransport] = useState('')
  const [desserteRes,   setDesserteRes]   = useState<Record<string, unknown>[] | null>(null)
  const [desserteLoad,  setDesserteLoad]  = useState(false)

  async function searchGare(e: FormEvent) {
    e.preventDefault(); if (!gareQ.trim()) return
    setGareLoad(true)
    const d = await fetchApi<Record<string, unknown>[]>(`/gares/search/nom?nom=${encodeURIComponent(gareQ)}`)
    setGareRes(d ?? []); setGareLoad(false)
  }
  async function searchLigne(e: FormEvent) {
    e.preventDefault(); if (!ligneQ.trim()) return
    setLigneLoad(true)
    const d = await fetchApi<Record<string, unknown>[]>(`/lignes-train/search/code?code=${encodeURIComponent(ligneQ)}`)
    setLigneRes(d ?? []); setLigneLoad(false)
  }
  async function searchOp(e: FormEvent) {
    e.preventDefault(); if (!opQ.trim()) return
    setOpLoad(true)
    const d = await fetchApi<Record<string, unknown>[]>(`/operateurs/search/nom?nom=${encodeURIComponent(opQ)}`)
    setOpRes(d ?? []); setOpLoad(false)
  }
  async function searchDesserte(e: FormEvent) {
    e.preventDefault()
    if (!depart.trim() && !arrivee.trim() && !typeTransport) return
    setDesserteLoad(true)
    const params = new URLSearchParams()
    if (depart.trim())   params.append('depart', depart.trim())
    if (arrivee.trim())  params.append('arrivee', arrivee.trim())
    if (typeTransport)   params.append('type_transport', typeTransport)
    const d = await fetchApi<Record<string, unknown>[]>(`/trajets/recherche?${params.toString()}`)
    setDesserteRes(d ?? []); setDesserteLoad(false)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>

      {/* ── Recherche dessertes ── */}
      <div style={CARD}>
        <p style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a', marginBottom: '2px' }}>Recherche de dessertes</p>
        <p style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '14px' }}>Rechercher par ville de départ, d'arrivée ou type de transport</p>
        <form onSubmit={searchDesserte} style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: desserteRes !== null ? '16px' : 0 }}>
          <input type="text" value={depart} onChange={e => setDepart(e.target.value)}
            placeholder="Ville de départ…"
            style={{ flex: 1, minWidth: '140px', padding: '10px 14px', borderRadius: '9px', border: '1px solid #e2e8f0', background: '#f8fafc', color: '#0f172a', fontSize: '13px', outline: 'none' }} />
          <input type="text" value={arrivee} onChange={e => setArrivee(e.target.value)}
            placeholder="Ville d'arrivée…"
            style={{ flex: 1, minWidth: '140px', padding: '10px 14px', borderRadius: '9px', border: '1px solid #e2e8f0', background: '#f8fafc', color: '#0f172a', fontSize: '13px', outline: 'none' }} />
          <select value={typeTransport} onChange={e => setTypeTransport(e.target.value)}
            style={{ padding: '10px 14px', borderRadius: '9px', border: '1px solid #e2e8f0', background: '#f8fafc', color: '#0f172a', fontSize: '13px', outline: 'none' }}>
            {TYPE_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
          <button type="submit" disabled={desserteLoad}
            style={{ padding: '10px 20px', borderRadius: '9px', border: 'none', background: '#f97316', color: '#fff', fontSize: '13px', fontWeight: 600, cursor: 'pointer' }}>
            {desserteLoad ? '…' : 'Rechercher'}
          </button>
        </form>
        <DesserteBlock results={desserteRes} loading={desserteLoad} />
      </div>

      <SearchBlock title="Gare" sub="Rechercher par nom de gare" placeholder="Paris, Lyon, Marseille…"
        accentColor="#6366f1" value={gareQ} onChange={setGareQ} onSubmit={searchGare} results={gareRes} loading={gareLoad} />
      <SearchBlock title="Ligne de train" sub="Rechercher par code de ligne" placeholder="C30, TGV, TER…"
        accentColor="#0ea5e9" value={ligneQ} onChange={setLigneQ} onSubmit={searchLigne} results={ligneRes} loading={ligneLoad} />
      <SearchBlock title="Opérateur" sub="Rechercher par nom d'opérateur" placeholder="SNCF, ÖBB, Trenitalia…"
        accentColor="#22c55e" value={opQ} onChange={setOpQ} onSubmit={searchOp} results={opRes} loading={opLoad} />
    </div>
  )
}
