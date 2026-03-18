import { useEffect, useState } from 'react'
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, LabelList,
} from 'recharts'
import { fetchApi } from '../api'
import MetricCard from '../components/MetricCard'
import Loader from '../components/Loader'
import MapGares from '../components/MapGares'

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
interface ContextePays {
  pays_code: string
  nos_gares: number
  nos_dessertes: number
  notre_distance_km: number
  reseau_total_km: number | null
  electrifie_km: number | null
  taux_electrification_pct: number | null
  grande_vitesse_km: number | null
  taux_couverture_pct: number | null
}
interface QualiteChamp {
  table: string
  champ: string
  label: string
  total: number
  remplis: number
  manquants: number
  taux_completude: number
}

const VIBRANT = ['#6366f1', '#f59e0b', '#22c55e', '#0ea5e9', '#ec4899', '#f97316', '#14b8a6', '#8b5cf6']

const TT: React.CSSProperties = {
  backgroundColor: 'var(--bg-card)', border: '1px solid var(--border)',
  borderRadius: '10px', color: 'var(--text-1)', fontSize: '12px',
  padding: '10px 14px', boxShadow: '0 4px 20px rgba(0,0,0,0.18)',
}
const CARD: React.CSSProperties = {
  background: 'var(--bg-card)', border: '1px solid var(--border)',
  borderRadius: '14px', padding: '20px 24px',
  boxShadow: 'var(--shadow)',
}
function CardTitle({ children }: { children: React.ReactNode }) {
  return <p style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-1)', marginBottom: '4px' }}>{children}</p>
}
function CardSub({ children }: { children: React.ReactNode }) {
  return <p style={{ fontSize: '12px', color: 'var(--text-4)', marginBottom: '16px' }}>{children}</p>
}
function legendFmt(v: string) {
  return <span style={{ color: 'var(--text-3)', fontSize: '12px' }}>{v}</span>
}

export default function VueGlobale() {
  const [stats,     setStats]     = useState<StatsGlobales | null>(null)
  const [jourNuit,  setJourNuit]  = useState<JourNuit[] | null>(null)
  const [typeLigne, setTypeLigne] = useState<TypeLigne[] | null>(null)
  const [operateurs, setOperateurs] = useState<StatOp[] | null>(null)
  const [pays,      setPays]      = useState<StatPays[] | null>(null)
  const [interPays, setInterPays] = useState<InterPays[] | null>(null)
  const [qualite,   setQualite]   = useState<QualiteChamp[] | null>(null)
  const [contexte,  setContexte]  = useState<ContextePays[] | null>(null)

  useEffect(() => {
    fetchApi<StatsGlobales>('/comparisons/stats-globales').then(setStats)
    fetchApi<JourNuit[]>('/comparisons/jour-vs-nuit').then(setJourNuit)
    fetchApi<TypeLigne[]>('/comparisons/par-type-ligne').then(setTypeLigne)
    fetchApi<StatOp[]>('/comparisons/par-operateur').then(setOperateurs)
    fetchApi<StatPays[]>('/comparisons/par-pays').then(setPays)
    fetchApi<InterPays[]>('/comparisons/inter-pays').then(setInterPays)
    fetchApi<QualiteChamp[]>('/comparisons/qualite-donnees').then(setQualite)
    fetchApi<ContextePays[]>('/comparisons/contexte-pays').then(setContexte)
  }, [])

  const jourNuitData = jourNuit?.map(d => ({ name: d.type_service, value: d.total }))
  const co2Data      = jourNuit?.map(d => ({ name: d.type_service, co2: d.co2_moyen ?? 0 }))
  const top8ops      = operateurs?.slice(0, 8)

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '14px' }} role="main" aria-label="Tableau de bord ObRail Europe">

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
      <div style={{ gridColumn: 'span 4', ...CARD }} role="region" aria-label="Répartition Jour / Nuit">
        <CardTitle>Répartition Jour / Nuit</CardTitle>
        <CardSub>{stats ? `${stats.total_dessertes} dessertes au total` : '…'}</CardSub>
        {jourNuitData ? (
          <ResponsiveContainer width="100%" height={220} aria-label="Graphique répartition Jour / Nuit">
            <PieChart>
              <Pie data={jourNuitData} dataKey="value" nameKey="name"
                cx="50%" cy="50%" innerRadius={55} outerRadius={90} paddingAngle={4}>
                {jourNuitData.map((entry, i) => (
                  <Cell key={i} fill={entry.name === 'Jour' ? '#f59e0b' : '#6366f1'} stroke="white" strokeWidth={2} />
                ))}
              </Pie>
              <Tooltip contentStyle={TT} formatter={(v: number) => [v.toLocaleString('fr-FR'), 'dessertes']} />
              <Legend formatter={legendFmt} iconSize={9} />
            </PieChart>
          </ResponsiveContainer>
        ) : <Loader />}
      </div>

      <div style={{ gridColumn: 'span 4', ...CARD }} role="region" aria-label="CO2 moyen par type de service">
        <CardTitle>CO₂ moyen (g/km)</CardTitle>
        <CardSub>Émissions moyennes par type de service</CardSub>
        {co2Data ? (
          <ResponsiveContainer width="100%" height={220} aria-label="Graphique CO2 moyen Jour et Nuit">
            <BarChart data={co2Data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="4 4" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={TT} formatter={(v: number) => [`${v} g/km`, 'CO₂']} />
              <Bar dataKey="co2" radius={[8, 8, 0, 0]}>
                {co2Data.map((entry, i) => (
                  <Cell key={i} fill={entry.name === 'Jour' ? '#f59e0b' : '#6366f1'} />
                ))}
                <LabelList dataKey="co2" position="top" style={{ fill: '#94a3b8', fontSize: 11 }} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : <Loader />}
      </div>

      <div style={{ gridColumn: 'span 4', ...CARD }} role="region" aria-label="Dessertes par type de ligne">
        <CardTitle>Dessertes par type de ligne</CardTitle>
        <CardSub>Répartition Grande vitesse / Intercité / Régional</CardSub>
        {typeLigne ? (
          <ResponsiveContainer width="100%" height={220} aria-label="Graphique dessertes par type de ligne">
            <PieChart>
              <Pie data={typeLigne} dataKey="total" nameKey="type_ligne"
                cx="50%" cy="50%" innerRadius={50} outerRadius={85} paddingAngle={4}>
                {typeLigne.map((entry) => {
                  const TYPE_COLORS: Record<string, string> = {
                    'Grande vitesse': '#f59e0b',
                    'Intercité': '#6366f1',
                    'Train régional': '#0ea5e9',
                    'Train régional express': '#22c55e',
                    'Train de nuit': '#8b5cf6',
                    'Train de nuit interne': '#8b5cf6',
                  }
                  return <Cell key={entry.type_ligne} fill={TYPE_COLORS[entry.type_ligne] ?? '#94a3b8'} stroke="white" strokeWidth={2} />
                })}
              </Pie>
              <Tooltip contentStyle={TT} formatter={(v: number) => [v, 'dessertes']} />
              <Legend formatter={legendFmt} iconSize={9} />
            </PieChart>
          </ResponsiveContainer>
        ) : <Loader />}
      </div>

      {/* ── Row 3 : Top opérateurs ── */}
      <div style={{ gridColumn: 'span 8', ...CARD }} role="region" aria-label="Top 8 opérateurs Jour vs Nuit">
        <CardTitle>Top 8 Opérateurs — Jour vs Nuit</CardTitle>
        <CardSub>Volume de dessertes par opérateur</CardSub>
        {top8ops ? (
          <ResponsiveContainer width="100%" height={280} aria-label="Graphique top 8 opérateurs">
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
      <div style={{ gridColumn: 'span 4', ...CARD }} role="region" aria-label="Dessertes par pays">
        <CardTitle>Dessertes par pays</CardTitle>
        <CardSub>Répartition géographique des liaisons</CardSub>
        {pays ? (
          <ResponsiveContainer width="100%" height={280} aria-label="Graphique dessertes par pays">
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

      {/* ── Row 4 : Contexte ferroviaire européen (données Wikipedia scrapées) ── */}
      <div style={{ gridColumn: 'span 12', ...CARD }}>
        <CardTitle>Contexte ferroviaire européen</CardTitle>
        <CardSub>Nos données GTFS croisées avec les statistiques Wikipedia — réseau total, grande vitesse, taux de couverture</CardSub>
        {contexte ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
            {contexte.map(c => {
              const flag: Record<string, string> = { FR: '🇫🇷', BE: '🇧🇪', DE: '🇩🇪', AT: '🇦🇹' }
              const nom:  Record<string, string> = { FR: 'France', BE: 'Belgique', DE: 'Allemagne', AT: 'Autriche' }
              return (
                <div key={c.pays_code} style={{ background: 'var(--bg-page)', borderRadius: '12px', padding: '16px', border: '1px solid var(--border)' }}>
                  <p style={{ fontSize: '18px', marginBottom: '4px' }}>{flag[c.pays_code]} <span style={{ fontWeight: 700, color: 'var(--text-1)' }}>{nom[c.pays_code]}</span></p>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                      <span style={{ color: 'var(--text-3)' }}>Réseau total</span>
                      <span style={{ fontWeight: 600, color: 'var(--text-1)' }}>{c.reseau_total_km?.toLocaleString('fr-FR') ?? '—'} km</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                      <span style={{ color: 'var(--text-3)' }}>Grande vitesse</span>
                      <span style={{ fontWeight: 600, color: '#f59e0b' }}>{c.grande_vitesse_km?.toLocaleString('fr-FR') ?? '—'} km</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                      <span style={{ color: 'var(--text-3)' }}>Électrification</span>
                      <span style={{ fontWeight: 600, color: '#22c55e' }}>{c.taux_electrification_pct ?? '—'}%</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                      <span style={{ color: 'var(--text-3)' }}>Nos dessertes</span>
                      <span style={{ fontWeight: 600, color: '#6366f1' }}>{c.nos_dessertes.toLocaleString('fr-FR')}</span>
                    </div>
                    <div style={{ marginTop: '4px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', marginBottom: '4px' }}>
                        <span style={{ color: 'var(--text-4)' }}>Couverture réseau</span>
                        <span style={{ fontWeight: 700, color: c.taux_couverture_pct && c.taux_couverture_pct >= 5 ? '#22c55e' : '#f59e0b' }}>
                          {c.taux_couverture_pct ?? '—'}%
                        </span>
                      </div>
                      <div style={{ background: 'var(--border)', borderRadius: '4px', height: '6px', overflow: 'hidden' }}>
                        <div style={{
                          width: `${Math.min(c.taux_couverture_pct ?? 0, 100)}%`,
                          height: '100%', borderRadius: '4px',
                          background: 'linear-gradient(90deg, #6366f1, #8b5cf6)',
                          transition: 'width 0.6s ease',
                        }} />
                      </div>
                    </div>
                  </div>
                  <p style={{ fontSize: '10px', color: 'var(--text-4)', marginTop: '10px' }}>Source : Wikipedia (scraping)</p>
                </div>
              )
            })}
          </div>
        ) : <Loader />}
      </div>

      {/* ── Row 5 : Qualité des données ── */}
      <div style={{ gridColumn: 'span 12', ...CARD }}>
        <CardTitle>Qualité des données — Taux de complétude</CardTitle>
        <CardSub>Champs remplis vs manquants par table</CardSub>
        {qualite ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '32px' }}>
            {(['operateurs', 'gares', 'dessertes'] as const).map(table => {
              const champs = qualite.filter(q => q.table === table)
              const labels: Record<string, string> = { operateurs: 'Opérateurs', gares: 'Gares', dessertes: 'Dessertes' }
              const totals: Record<string, string> = { operateurs: `${champs[0]?.total} lignes`, gares: `${champs[0]?.total} lignes`, dessertes: `${champs[0]?.total} lignes` }
              return (
                <div key={table}>
                  <p style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-1)', marginBottom: '2px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{labels[table]}</p>
                  <p style={{ fontSize: '11px', color: 'var(--text-4)', marginBottom: '14px' }}>{totals[table]}</p>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {champs.map(q => (
                      <div key={q.champ} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{ width: '120px', fontSize: '12px', color: 'var(--text-2)', flexShrink: 0 }}>{q.label}</span>
                        <div style={{ flex: 1, background: 'var(--border)', borderRadius: '6px', height: '8px', overflow: 'hidden' }}
                          role="progressbar" aria-valuenow={q.taux_completude} aria-valuemin={0} aria-valuemax={100}
                          aria-label={`${q.label} : ${q.taux_completude}% de complétude`}>
                          <div style={{
                            width: `${q.taux_completude}%`, height: '100%', borderRadius: '6px',
                            background: q.taux_completude >= 95 ? '#22c55e' : q.taux_completude >= 80 ? '#f59e0b' : '#ef4444',
                            transition: 'width 0.6s ease',
                          }} />
                        </div>
                        <span style={{ width: '44px', fontSize: '12px', fontWeight: 600, textAlign: 'right', flexShrink: 0, color: q.taux_completude >= 95 ? '#22c55e' : q.taux_completude >= 80 ? '#f59e0b' : '#ef4444' }}>
                          {q.taux_completude}%
                        </span>
                        <span style={{ width: '76px', fontSize: '11px', color: 'var(--text-4)', flexShrink: 0 }}>
                          {q.manquants > 0 ? `${q.manquants} manquants` : 'complet'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        ) : <Loader />}
      </div>

      {/* ── Row 5 : Carte des gares ── */}
      <div style={{ gridColumn: 'span 12', ...CARD }}>
        <CardTitle>Carte des gares européennes</CardTitle>
        <CardSub>Toutes les gares avec coordonnées GPS — survolez un point pour le nom</CardSub>
        <MapGares />
      </div>

      {/* ── Row 6 : Inter-pays ── */}
      <div style={{ gridColumn: 'span 12', ...CARD }}>
        <CardTitle>Liaisons internationales — {interPays?.length ?? '…'} trajets inter-pays</CardTitle>
        <CardSub>Dessertes ferroviaires traversant les frontières européennes</CardSub>
        {interPays ? (
          <div style={{ overflowX: 'auto', borderRadius: '10px', border: '1px solid #f1f5f9' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }} aria-label="Liaisons internationales ferroviaires">
              <thead>
                <tr style={{ background: 'var(--bg-thead)' }}>
                  {['Liaison', 'Ligne', 'Type', 'Départ', 'Arrivée', 'Durée'].map(h => (
                    <th key={h} scope="col" style={{
                      padding: '10px 14px', textAlign: 'left', color: 'var(--text-4)',
                      fontWeight: 600, textTransform: 'uppercase', fontSize: '10px',
                      letterSpacing: '0.6px', whiteSpace: 'nowrap',
                    }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {interPays.map((r, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid var(--border-lt)', background: i % 2 !== 0 ? 'var(--bg-row-alt)' : 'var(--bg-card)' }}
                    onMouseEnter={e => (e.currentTarget.style.background = '#eef2ff22')}
                    onMouseLeave={e => (e.currentTarget.style.background = i % 2 !== 0 ? 'var(--bg-row-alt)' : 'var(--bg-card)')}>
                    <td style={{ padding: '9px 14px', whiteSpace: 'nowrap' }}>
                      <span style={{ fontWeight: 600, color: '#6366f1' }}>{r.liaison}</span>
                    </td>
                    <td style={{ padding: '9px 14px', color: 'var(--text-2)', whiteSpace: 'nowrap' }}>{r.nom_ligne}</td>
                    <td style={{ padding: '9px 14px', whiteSpace: 'nowrap' }}>
                      <span style={{
                        padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 600,
                        background: r.type_service === 'Nuit' ? '#eef2ff' : '#fffbeb',
                        color: r.type_service === 'Nuit' ? '#6366f1' : '#f59e0b',
                      }}>{r.type_service}</span>
                    </td>
                    <td style={{ padding: '9px 14px', color: 'var(--text-2)', whiteSpace: 'nowrap' }}>{r.gare_depart}</td>
                    <td style={{ padding: '9px 14px', color: 'var(--text-2)', whiteSpace: 'nowrap' }}>{r.gare_arrivee}</td>
                    <td style={{ padding: '9px 14px', color: 'var(--text-3)', whiteSpace: 'nowrap' }}>{r.duree_h ? `${r.duree_h} h` : '—'}</td>
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
