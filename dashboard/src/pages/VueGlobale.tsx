import { useEffect, useState } from 'react'
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, LabelList,
} from 'recharts'
import { fetchApi } from '../api'
import MetricCard from '../components/MetricCard'
import Loader from '../components/Loader'

interface Stats       { total_gares: number; total_lignes: number; total_trajets: number }
interface JourNuit    { periode: string; nombre: number }
interface LigneType   { type_transport: number; nombre_lignes: number }
interface Operateur   { operateur: string; nombre_lignes: number }
interface GarePassage { gare: string; nombre_passages: number }
interface ValeurManq  { champ: string; taux_manquant: number }

const TYPE_LABELS: Record<number, string> = {
  0: 'Tram', 1: 'Métro', 2: 'Train', 3: 'Bus',
  4: 'Ferry', 5: 'Téléph.', 6: 'Gondole', 7: 'Funiculaire',
}

const VIBRANT = [
  '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e',
  '#f97316', '#eab308', '#22c55e', '#14b8a6',
  '#0ea5e9', '#3b82f6',
]

// Palette pour les barres opérateurs (dégradé indigo → violet)
const OP_COLORS = [
  '#6366f1', '#7270f3', '#817ef5', '#918cf7',
  '#a09af8', '#b0a8fa', '#bfb7fc', '#cfc5fd',
]

const TT: React.CSSProperties = {
  backgroundColor: '#ffffff',
  border: '1px solid #e2e8f0',
  borderRadius: '10px',
  color: '#0f172a',
  fontSize: '12px',
  padding: '10px 14px',
  boxShadow: '0 4px 20px rgba(0,0,0,0.12)',
}

const CARD: React.CSSProperties = {
  background: '#ffffff',
  border: '1px solid #e2e8f0',
  borderRadius: '14px',
  padding: '20px 24px',
  boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
}

function CardTitle({ children }: { children: React.ReactNode }) {
  return (
    <p style={{
      fontSize: '13px', fontWeight: 600, color: '#0f172a',
      marginBottom: '4px',
    }}>
      {children}
    </p>
  )
}

function CardSub({ children }: { children: React.ReactNode }) {
  return (
    <p style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '16px' }}>
      {children}
    </p>
  )
}

function legendFmt(v: string) {
  return <span style={{ color: '#64748b', fontSize: '12px' }}>{v}</span>
}

export default function VueGlobale() {
  const [stats,      setStats]      = useState<Stats | null>(null)
  const [jourNuit,   setJourNuit]   = useState<JourNuit[] | null>(null)
  const [lignesType, setLignesType] = useState<LigneType[] | null>(null)
  const [operateurs, setOperateurs] = useState<Operateur[] | null>(null)
  const [gares,      setGares]      = useState<GarePassage[] | null>(null)
  const [manquants,  setManquants]  = useState<ValeurManq[] | null>(null)

  useEffect(() => {
    fetchApi<Stats>('/comparisons/stats').then(setStats)
    fetchApi<JourNuit[]>('/comparisons/repartition-jour-nuit').then(setJourNuit)
    fetchApi<LigneType[]>('/comparisons/lignes-par-type').then(setLignesType)
    fetchApi<Operateur[]>('/comparisons/top-operateurs?limit=10').then(setOperateurs)
    fetchApi<GarePassage[]>('/comparisons/gares-les-plus-desservies?limit=10').then(setGares)
    fetchApi<ValeurManq[]>('/comparisons/valeurs-manquantes').then(setManquants)
  }, [])

  const lignesLabeled = lignesType?.map(d => ({
    name: TYPE_LABELS[d.type_transport] ?? `Type ${d.type_transport}`,
    value: d.nombre_lignes,
  }))

  const allZero = manquants?.every(v => v.taux_manquant === 0)

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '14px' }}>

      {/* ── Row 1 : Métriques ── */}
      {stats ? (
        <>
          <div style={{ gridColumn: 'span 4' }}>
            <MetricCard icon="🏛" value={stats.total_gares}   label="Gares en base"
              color="#6366f1" colorBg="#f5f3ff" />
          </div>
          <div style={{ gridColumn: 'span 4' }}>
            <MetricCard icon="🛤" value={stats.total_lignes}  label="Lignes actives"
              color="#0ea5e9" colorBg="#f0f9ff" />
          </div>
          <div style={{ gridColumn: 'span 4' }}>
            <MetricCard icon="🚆" value={stats.total_trajets} label="Trajets recensés"
              color="#22c55e" colorBg="#f0fdf4" />
          </div>
        </>
      ) : (
        <div style={{ gridColumn: 'span 12' }}><Loader /></div>
      )}

      {/* ── Row 2 : Donuts ── */}
      <div style={{ gridColumn: 'span 5', ...CARD }}>
        <CardTitle>Répartition Jour / Nuit</CardTitle>
        <CardSub>Basée sur l'heure de départ des trajets</CardSub>
        {jourNuit ? (
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={jourNuit} dataKey="nombre" nameKey="periode"
                cx="50%" cy="50%" innerRadius={58} outerRadius={95} paddingAngle={4}>
                <Cell fill="#f59e0b" stroke="white" strokeWidth={2} />
                <Cell fill="#6366f1" stroke="white" strokeWidth={2} />
              </Pie>
              <Tooltip contentStyle={TT} />
              <Legend formatter={legendFmt} iconSize={9} />
            </PieChart>
          </ResponsiveContainer>
        ) : <Loader />}
      </div>

      <div style={{ gridColumn: 'span 7', ...CARD }}>
        <CardTitle>Lignes par type de transport</CardTitle>
        <CardSub>Répartition du réseau selon les catégories GTFS</CardSub>
        {lignesLabeled ? (
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={lignesLabeled} dataKey="value" nameKey="name"
                cx="50%" cy="50%" innerRadius={55} outerRadius={90} paddingAngle={3}>
                {lignesLabeled.map((_, i) => (
                  <Cell key={i} fill={VIBRANT[i % VIBRANT.length]} stroke="white" strokeWidth={2} />
                ))}
              </Pie>
              <Tooltip contentStyle={TT} />
              <Legend formatter={legendFmt} iconSize={9} />
            </PieChart>
          </ResponsiveContainer>
        ) : <Loader />}
      </div>

      {/* ── Row 3 : Top opérateurs ── */}
      <div style={{ gridColumn: 'span 12', ...CARD }}>
        <CardTitle>Top 10 Opérateurs par volume de lignes</CardTitle>
        <CardSub>Classement des opérateurs ferroviaires européens</CardSub>
        {operateurs ? (
          <ResponsiveContainer width="100%" height={310}>
            <BarChart data={operateurs} layout="vertical" margin={{ top: 0, right: 60, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="4 4" stroke="#f1f5f9" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis dataKey="operateur" type="category" width={130}
                tick={{ fill: '#475569', fontSize: 12 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={TT} cursor={{ fill: 'rgba(99,102,241,0.05)' }}
                formatter={(v: number) => [v.toLocaleString('fr-FR'), 'lignes']} />
              <Bar dataKey="nombre_lignes" radius={[0, 6, 6, 0]}>
                {operateurs.map((_, i) => (
                  <Cell key={i} fill={OP_COLORS[i % OP_COLORS.length]} />
                ))}
                <LabelList dataKey="nombre_lignes" position="right"
                  style={{ fill: '#94a3b8', fontSize: 11, fontWeight: 600 }} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : <Loader />}
      </div>

      {/* ── Row 4 : Gares + Qualité ── */}
      <div style={{ gridColumn: 'span 7', ...CARD }}>
        <CardTitle>Top 10 Gares les plus desservies</CardTitle>
        <CardSub>Classement par nombre de passages dans les horaires</CardSub>
        {gares ? (
          <ResponsiveContainer width="100%" height={290}>
            <BarChart data={gares} margin={{ top: 10, right: 16, left: 0, bottom: 64 }}>
              <CartesianGrid strokeDasharray="4 4" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="gare"
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                tick={{ fill: '#64748b', fontSize: 11, angle: -35 } as any}
                tickLine={false} axisLine={false} interval={0} height={68} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={TT} cursor={{ fill: 'rgba(14,165,233,0.05)' }}
                formatter={(v: number) => [v.toLocaleString('fr-FR'), 'passages']} />
              <Bar dataKey="nombre_passages" radius={[6, 6, 0, 0]}>
                {(gares ?? []).map((_, i) => (
                  <Cell key={i} fill={VIBRANT[i % VIBRANT.length]} />
                ))}
                <LabelList dataKey="nombre_passages" position="top"
                  style={{ fill: '#94a3b8', fontSize: 10 }} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : <Loader />}
      </div>

      <div style={{ gridColumn: 'span 5', ...CARD }}>
        <CardTitle>Qualité des données</CardTitle>
        <CardSub>Taux de valeurs manquantes par champ</CardSub>
        {manquants ? (
          <>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={manquants} margin={{ top: 10, right: 16, left: 0, bottom: 80 }}>
                <CartesianGrid strokeDasharray="4 4" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="champ"
                  // eslint-disable-next-line @typescript-eslint/no-explicit-any
                  tick={{ fill: '#64748b', fontSize: 10, angle: -40 } as any}
                  tickLine={false} axisLine={false} interval={0} height={80} />
                <YAxis domain={[0, 100]} tickFormatter={v => `${v}%`}
                  tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={TT} cursor={{ fill: 'rgba(0,0,0,0.03)' }}
                  formatter={(v: number) => [`${v}%`, 'manquant']} />
                <Bar dataKey="taux_manquant" radius={[5, 5, 0, 0]}>
                  {manquants.map((d, i) => (
                    <Cell key={i}
                      fill={d.taux_manquant === 0 ? '#22c55e' : d.taux_manquant < 30 ? '#f59e0b' : '#ef4444'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>

            <div style={{
              marginTop: '12px', padding: '10px 14px', borderRadius: '8px',
              fontSize: '12px', fontWeight: 500,
              background: allZero ? '#f0fdf4' : '#fffbeb',
              border: `1px solid ${allZero ? '#bbf7d0' : '#fde68a'}`,
              color: allZero ? '#16a34a' : '#d97706',
            }}>
              {allZero ? '✓ Données complètes — aucune valeur manquante' : '⚠ Valeurs manquantes détectées'}
            </div>
          </>
        ) : <Loader />}
      </div>

    </div>
  )
}
