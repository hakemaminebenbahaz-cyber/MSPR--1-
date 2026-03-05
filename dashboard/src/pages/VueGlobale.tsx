import { useEffect, useState } from 'react'
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, LabelList,
} from 'recharts'
import { fetchApi } from '../api'
import MetricCard from '../components/MetricCard'
import Loader from '../components/Loader'

interface StatsGlobales {
  total_operateurs: number
  total_gares: number
  total_dessertes: number
  total_jour: number
  total_nuit: number
}
interface JourNuit {
  type_service: string
  total: number
  co2_moyen: number | null
  duree_moyenne_h: number | null
}
interface TypeLigne {
  type_ligne: string
  total: number
  co2_moyen: number | null
}
interface StatOp {
  operateur: string
  pays_code: string
  total_dessertes: number
  nb_jour: number
  nb_nuit: number
}
interface StatPays {
  pays_code: string
  total_gares: number
  total_dessertes: number
}
interface InterPays {
  liaison: string
  nom_ligne: string
  type_service: string
  gare_depart: string
  gare_arrivee: string
  duree_h: number | null
}

const VIBRANT = ['#6366f1', '#f59e0b', '#22c55e', '#0ea5e9', '#ec4899', '#f97316', '#14b8a6', '#8b5cf6']

const TT: React.CSSProperties = {
  backgroundColor: '#ffffff', border: '1px solid #e2e8f0',
  borderRadius: '10px', color: '#0f172a', fontSize: '12px',
  padding: '10px 14px', boxShadow: '0 4px 20px rgba(0,0,0,0.12)',
}
const CARD: React.CSSProperties = {
  background: '#ffffff', border: '1px solid #e2e8f0',
  borderRadius: '14px', padding: '20px 24px',
  boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
}
function CardTitle({ children }: { children: React.ReactNode }) {
  return <p style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a', marginBottom: '4px' }}>{children}</p>
}
function CardSub({ children }: { children: React.ReactNode }) {
  return <p style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '16px' }}>{children}</p>
}
function legendFmt(v: string) {
  return <span style={{ color: '#64748b', fontSize: '12px' }}>{v}</span>
}

export default function VueGlobale() {
  const [stats,     setStats]     = useState<StatsGlobales | null>(null)
  const [jourNuit,  setJourNuit]  = useState<JourNuit[] | null>(null)
  const [typeLigne, setTypeLigne] = useState<TypeLigne[] | null>(null)
  const [operateurs, setOperateurs] = useState<StatOp[] | null>(null)
  const [pays,      setPays]      = useState<StatPays[] | null>(null)
  const [interPays, setInterPays] = useState<InterPays[] | null>(null)

  useEffect(() => {
    fetchApi<StatsGlobales>('/comparisons/stats-globales').then(setStats)
    fetchApi<JourNuit[]>('/comparisons/jour-vs-nuit').then(setJourNuit)
    fetchApi<TypeLigne[]>('/comparisons/par-type-ligne').then(setTypeLigne)
    fetchApi<StatOp[]>('/comparisons/par-operateur').then(setOperateurs)
    fetchApi<StatPays[]>('/comparisons/par-pays').then(setPays)
    fetchApi<InterPays[]>('/comparisons/inter-pays').then(setInterPays)
  }, [])

  const jourNuitData = jourNuit?.map(d => ({ name: d.type_service, value: d.total }))
  const co2Data      = jourNuit?.map(d => ({ name: d.type_service, co2: d.co2_moyen ?? 0 }))
  const top8ops      = operateurs?.slice(0, 8)

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '14px' }}>

      {/* ── Row 1 : Métriques ── */}
      {stats ? (
        <>
          <div style={{ gridColumn: 'span 3' }}>
            <MetricCard icon="🏭" value={stats.total_operateurs} label="Opérateurs" color="#8b5cf6" colorBg="#f5f3ff" />
          </div>
          <div style={{ gridColumn: 'span 3' }}>
            <MetricCard icon="🏛" value={stats.total_gares} label="Gares en base" color="#6366f1" colorBg="#eef2ff" />
          </div>
          <div style={{ gridColumn: 'span 3' }}>
            <MetricCard icon="☀️" value={stats.total_jour} label="Trains de jour" color="#f59e0b" colorBg="#fffbeb" />
          </div>
          <div style={{ gridColumn: 'span 3' }}>
            <MetricCard icon="🌙" value={stats.total_nuit} label="Trains de nuit" color="#6366f1" colorBg="#eef2ff" />
          </div>
        </>
      ) : (
        <div style={{ gridColumn: 'span 12' }}><Loader /></div>
      )}

      {/* ── Row 2 : Jour/Nuit donut + CO2 ── */}
      <div style={{ gridColumn: 'span 4', ...CARD }}>
        <CardTitle>Répartition Jour / Nuit</CardTitle>
        <CardSub>{stats ? `${stats.total_dessertes} dessertes au total` : '…'}</CardSub>
        {jourNuitData ? (
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={jourNuitData} dataKey="value" nameKey="name"
                cx="50%" cy="50%" innerRadius={55} outerRadius={90} paddingAngle={4}>
                <Cell fill="#f59e0b" stroke="white" strokeWidth={2} />
                <Cell fill="#6366f1" stroke="white" strokeWidth={2} />
              </Pie>
              <Tooltip contentStyle={TT} formatter={(v: number) => [v.toLocaleString('fr-FR'), 'dessertes']} />
              <Legend formatter={legendFmt} iconSize={9} />
            </PieChart>
          </ResponsiveContainer>
        ) : <Loader />}
      </div>

      <div style={{ gridColumn: 'span 4', ...CARD }}>
        <CardTitle>CO₂ moyen (g/km)</CardTitle>
        <CardSub>Émissions moyennes par type de service</CardSub>
        {co2Data ? (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={co2Data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="4 4" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={TT} formatter={(v: number) => [`${v} g/km`, 'CO₂']} />
              <Bar dataKey="co2" radius={[8, 8, 0, 0]}>
                <Cell fill="#f59e0b" />
                <Cell fill="#6366f1" />
                <LabelList dataKey="co2" position="top" style={{ fill: '#94a3b8', fontSize: 11 }} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : <Loader />}
      </div>

      <div style={{ gridColumn: 'span 4', ...CARD }}>
        <CardTitle>Dessertes par type de ligne</CardTitle>
        <CardSub>Répartition Grande vitesse / Intercité / Régional</CardSub>
        {typeLigne ? (
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={typeLigne} dataKey="total" nameKey="type_ligne"
                cx="50%" cy="50%" innerRadius={50} outerRadius={85} paddingAngle={4}>
                {typeLigne.map((_, i) => (
                  <Cell key={i} fill={VIBRANT[i % VIBRANT.length]} stroke="white" strokeWidth={2} />
                ))}
              </Pie>
              <Tooltip contentStyle={TT} formatter={(v: number) => [v, 'dessertes']} />
              <Legend formatter={legendFmt} iconSize={9} />
            </PieChart>
          </ResponsiveContainer>
        ) : <Loader />}
      </div>

      {/* ── Row 3 : Top opérateurs ── */}
      <div style={{ gridColumn: 'span 8', ...CARD }}>
        <CardTitle>Top 8 Opérateurs — Jour vs Nuit</CardTitle>
        <CardSub>Volume de dessertes par opérateur</CardSub>
        {top8ops ? (
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={top8ops} layout="vertical" margin={{ top: 0, right: 60, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="4 4" stroke="#f1f5f9" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis dataKey="operateur" type="category" width={140}
                tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={TT} cursor={{ fill: 'rgba(99,102,241,0.05)' }} />
              <Legend formatter={legendFmt} iconSize={9} />
              <Bar dataKey="nb_jour" name="Jour" stackId="a" fill="#f59e0b" radius={[0, 0, 0, 0]}>
                <LabelList dataKey="nb_jour" position="center" style={{ fill: '#fff', fontSize: 10, fontWeight: 600 }} />
              </Bar>
              <Bar dataKey="nb_nuit" name="Nuit" stackId="a" fill="#6366f1" radius={[0, 6, 6, 0]}>
                <LabelList dataKey="nb_nuit" position="right" style={{ fill: '#94a3b8', fontSize: 10 }} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : <Loader />}
      </div>

      {/* ── Row 3 : Par pays ── */}
      <div style={{ gridColumn: 'span 4', ...CARD }}>
        <CardTitle>Dessertes par pays</CardTitle>
        <CardSub>Répartition géographique des liaisons</CardSub>
        {pays ? (
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={pays} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
              <CartesianGrid strokeDasharray="4 4" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="pays_code" tick={{ fill: '#64748b', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={TT} />
              <Bar dataKey="total_dessertes" name="Dessertes" radius={[6, 6, 0, 0]}>
                {pays.map((_, i) => <Cell key={i} fill={VIBRANT[i % VIBRANT.length]} />)}
                <LabelList dataKey="total_dessertes" position="top" style={{ fill: '#94a3b8', fontSize: 11 }} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : <Loader />}
      </div>

      {/* ── Row 4 : Inter-pays ── */}
      <div style={{ gridColumn: 'span 12', ...CARD }}>
        <CardTitle>Liaisons internationales — {interPays?.length ?? '…'} trajets inter-pays</CardTitle>
        <CardSub>Dessertes ferroviaires traversant les frontières européennes</CardSub>
        {interPays ? (
          <div style={{ overflowX: 'auto', borderRadius: '10px', border: '1px solid #f1f5f9' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
              <thead>
                <tr style={{ background: '#f8fafc' }}>
                  {['Liaison', 'Ligne', 'Type', 'Départ', 'Arrivée', 'Durée'].map(h => (
                    <th key={h} style={{
                      padding: '10px 14px', textAlign: 'left', color: '#94a3b8',
                      fontWeight: 600, textTransform: 'uppercase', fontSize: '10px',
                      letterSpacing: '0.6px', whiteSpace: 'nowrap',
                    }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {interPays.map((r, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid #f8fafc', background: i % 2 !== 0 ? '#fafafa' : '#fff' }}
                    onMouseEnter={e => (e.currentTarget.style.background = '#eef2ff')}
                    onMouseLeave={e => (e.currentTarget.style.background = i % 2 !== 0 ? '#fafafa' : '#fff')}>
                    <td style={{ padding: '9px 14px', whiteSpace: 'nowrap' }}>
                      <span style={{ fontWeight: 600, color: '#6366f1' }}>{r.liaison}</span>
                    </td>
                    <td style={{ padding: '9px 14px', color: '#334155', whiteSpace: 'nowrap' }}>{r.nom_ligne}</td>
                    <td style={{ padding: '9px 14px', whiteSpace: 'nowrap' }}>
                      <span style={{
                        padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 600,
                        background: r.type_service === 'Nuit' ? '#eef2ff' : '#fffbeb',
                        color: r.type_service === 'Nuit' ? '#6366f1' : '#f59e0b',
                      }}>{r.type_service}</span>
                    </td>
                    <td style={{ padding: '9px 14px', color: '#334155', whiteSpace: 'nowrap' }}>{r.gare_depart}</td>
                    <td style={{ padding: '9px 14px', color: '#334155', whiteSpace: 'nowrap' }}>{r.gare_arrivee}</td>
                    <td style={{ padding: '9px 14px', color: '#64748b', whiteSpace: 'nowrap' }}>{r.duree_h ? `${r.duree_h} h` : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <Loader />}
      </div>

    </div>
  )
}
