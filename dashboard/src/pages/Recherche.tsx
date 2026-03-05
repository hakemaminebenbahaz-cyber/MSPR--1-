import { useState, type FormEvent } from 'react'
import { fetchApi } from '../api'

const CARD: React.CSSProperties = {
  background: '#ffffff', border: '1px solid #e2e8f0',
  borderRadius: '14px', padding: '22px 24px',
  boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
}

const INPUT: React.CSSProperties = {
  flex: 1, minWidth: '140px', padding: '10px 14px',
  borderRadius: '9px', border: '1px solid #e2e8f0',
  background: '#f8fafc', color: '#0f172a', fontSize: '13px', outline: 'none',
}

const SELECT: React.CSSProperties = {
  padding: '10px 14px', borderRadius: '9px',
  border: '1px solid #e2e8f0', background: '#f8fafc',
  color: '#0f172a', fontSize: '13px', outline: 'none',
}

function flatten(row: Record<string, unknown>): Record<string, unknown> {
  const dep = row['gare_depart'] as Record<string, unknown> | null
  const arr = row['gare_arrivee'] as Record<string, unknown> | null
  const op  = row['operateur']   as Record<string, unknown> | null
  const skip = new Set(['gare_depart', 'gare_arrivee', 'operateur', 'id', 'operateur_id', 'gare_depart_id', 'gare_arrivee_id'])
  const r: Record<string, unknown> = {
    'départ':    dep?.nom ?? '—',
    'arrivée':   arr?.nom ?? '—',
    'opérateur': op?.nom  ?? '—',
  }
  for (const [k, v] of Object.entries(row)) {
    if (!skip.has(k)) r[k] = v
  }
  return r
}

function ResultTable({ results, loading, isDessertes = false }: { results: Record<string, unknown>[] | null; loading: boolean; isDessertes?: boolean }) {
  if (loading) return <div style={{ fontSize: '13px', color: '#94a3b8', padding: '12px 0' }}>Chargement…</div>
  if (!results) return null
  if (results.length === 0) return (
    <div style={{ fontSize: '13px', color: '#94a3b8', padding: '12px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
      <span>🔍</span> Aucun résultat trouvé
    </div>
  )

  const flat = isDessertes ? results.map(flatten) : results
  const keys = Object.keys(flat[0])

  return (
    <>
      <div style={{
        display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 500,
        color: '#16a34a', background: '#f0fdf4', border: '1px solid #bbf7d0',
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
                  padding: '10px 14px', textAlign: 'left', color: '#94a3b8',
                  fontWeight: 600, textTransform: 'uppercase', fontSize: '10px',
                  letterSpacing: '0.6px', borderBottom: '1px solid #f1f5f9', whiteSpace: 'nowrap',
                }}>{k.replace(/_/g, ' ')}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {flat.map((row, i) => (
              <tr key={i} style={{ borderBottom: '1px solid #f8fafc' }}
                onMouseEnter={e => (e.currentTarget.style.background = '#f8fafc')}
                onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}>
                {keys.map(k => {
                  const val = row[k]
                  let display = String(val ?? '—')
                  // Affichage enrichi pour certains champs
                  if (k === 'type_service') {
                    return (
                      <td key={k} style={{ padding: '9px 14px', whiteSpace: 'nowrap' }}>
                        <span style={{
                          padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 600,
                          background: val === 'Nuit' ? '#eef2ff' : '#fffbeb',
                          color: val === 'Nuit' ? '#6366f1' : '#f59e0b',
                        }}>{display}</span>
                      </td>
                    )
                  }
                  if (k === 'emissions_co2_gkm') display = val ? `${val} g/km` : '—'
                  if (k === 'duree_h') display = val ? `${val} h` : '—'
                  return (
                    <td key={k} style={{ padding: '9px 14px', color: '#334155', whiteSpace: 'nowrap' }}>
                      {display}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}

export default function Recherche() {
  // ── Dessertes ──
  const [depart,       setDepart]       = useState('')
  const [arrivee,      setArrivee]      = useState('')
  const [typeService,  setTypeService]  = useState('')
  const [typeLigne,    setTypeLigne]    = useState('')
  const [desserteRes,  setDesserteRes]  = useState<Record<string, unknown>[] | null>(null)
  const [desserteLoad, setDesserteLoad] = useState(false)

  // ── Gares ──
  const [gareQ,    setGareQ]    = useState('')
  const [gareRes,  setGareRes]  = useState<Record<string, unknown>[] | null>(null)
  const [gareLoad, setGareLoad] = useState(false)

  // ── Opérateurs ──
  const [opQ,    setOpQ]    = useState('')
  const [opRes,  setOpRes]  = useState<Record<string, unknown>[] | null>(null)
  const [opLoad, setOpLoad] = useState(false)

  async function searchDesserte(e: FormEvent) {
    e.preventDefault()
    if (!depart.trim() && !arrivee.trim() && !typeService && !typeLigne) return
    setDesserteLoad(true)
    const params = new URLSearchParams({ limit: '50' })
    if (depart.trim())   params.append('depart', depart.trim())
    if (arrivee.trim())  params.append('arrivee', arrivee.trim())
    if (typeService)     params.append('type_service', typeService)
    if (typeLigne)       params.append('type_ligne', typeLigne)
    const d = await fetchApi<Record<string, unknown>[]>(`/dessertes/?${params}`)
    setDesserteRes(d ?? [])
    setDesserteLoad(false)
  }

  async function searchGare(e: FormEvent) {
    e.preventDefault(); if (!gareQ.trim()) return
    setGareLoad(true)
    const d = await fetchApi<Record<string, unknown>[]>(`/gares/?nom=${encodeURIComponent(gareQ)}&limit=50`)
    setGareRes(d ?? [])
    setGareLoad(false)
  }

  async function searchOp(e: FormEvent) {
    e.preventDefault(); if (!opQ.trim()) return
    setOpLoad(true)
    const d = await fetchApi<Record<string, unknown>[]>(`/operateurs/`)
    const filtered = (d ?? []).filter(o =>
      String(o.nom).toLowerCase().includes(opQ.toLowerCase())
    )
    setOpRes(filtered)
    setOpLoad(false)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>

      {/* ── Recherche dessertes ── */}
      <div style={CARD}>
        <p style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a', marginBottom: '2px' }}>Recherche de dessertes</p>
        <p style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '14px' }}>
          Rechercher par gare de départ, d'arrivée, type Jour/Nuit ou catégorie de ligne
        </p>
        <form onSubmit={searchDesserte} style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px' }}>
          <input style={INPUT} type="text" value={depart} onChange={e => setDepart(e.target.value)}
            placeholder="Gare de départ… (ex: Lyon)" />
          <input style={INPUT} type="text" value={arrivee} onChange={e => setArrivee(e.target.value)}
            placeholder="Gare d'arrivée… (ex: Paris)" />
          <select style={SELECT} value={typeService} onChange={e => setTypeService(e.target.value)}>
            <option value="">Jour & Nuit</option>
            <option value="Jour">☀️ Jour</option>
            <option value="Nuit">🌙 Nuit</option>
          </select>
          <select style={SELECT} value={typeLigne} onChange={e => setTypeLigne(e.target.value)}>
            <option value="">Tous types</option>
            <option value="Grande vitesse">🚄 Grande vitesse</option>
            <option value="Intercité">🚂 Intercité</option>
            <option value="Train régional">🚃 Régional</option>
            <option value="Train de nuit intern">🌙 Nuit intern.</option>
          </select>
          <button type="submit" disabled={desserteLoad} style={{
            padding: '10px 20px', borderRadius: '9px', border: 'none',
            background: '#f97316', color: '#fff', fontSize: '13px', fontWeight: 600,
            cursor: 'pointer', boxShadow: '0 2px 8px #f9731640',
          }}>
            {desserteLoad ? '…' : 'Rechercher'}
          </button>
        </form>
        <ResultTable results={desserteRes} loading={desserteLoad} isDessertes={true} />
      </div>

      {/* ── Recherche gares ── */}
      <div style={CARD}>
        <p style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a', marginBottom: '2px' }}>Recherche de gares</p>
        <p style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '14px' }}>Rechercher par nom de gare</p>
        <form onSubmit={searchGare} style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
          <input style={INPUT} type="text" value={gareQ} onChange={e => setGareQ(e.target.value)}
            placeholder="Paris, Lyon, München…" />
          <button type="submit" disabled={gareLoad} style={{
            padding: '10px 20px', borderRadius: '9px', border: 'none',
            background: '#6366f1', color: '#fff', fontSize: '13px', fontWeight: 600,
            cursor: 'pointer', boxShadow: '0 2px 8px #6366f140',
          }}>
            {gareLoad ? '…' : 'Rechercher'}
          </button>
        </form>
        <ResultTable results={gareRes} loading={gareLoad} />
      </div>

      {/* ── Recherche opérateurs ── */}
      <div style={CARD}>
        <p style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a', marginBottom: '2px' }}>Recherche d'opérateurs</p>
        <p style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '14px' }}>Rechercher par nom d'opérateur</p>
        <form onSubmit={searchOp} style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
          <input style={INPUT} type="text" value={opQ} onChange={e => setOpQ(e.target.value)}
            placeholder="SNCF, Deutsche Bahn, ÖBB…" />
          <button type="submit" disabled={opLoad} style={{
            padding: '10px 20px', borderRadius: '9px', border: 'none',
            background: '#22c55e', color: '#fff', fontSize: '13px', fontWeight: 600,
            cursor: 'pointer', boxShadow: '0 2px 8px #22c55e40',
          }}>
            {opLoad ? '…' : 'Rechercher'}
          </button>
        </form>
        <ResultTable results={opRes} loading={opLoad} />
      </div>

    </div>
  )
}
