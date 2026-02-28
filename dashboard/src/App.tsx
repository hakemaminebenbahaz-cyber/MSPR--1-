import { useState } from 'react'
import TopNav from './components/TopNav'
import VueGlobale from './pages/VueGlobale'
import Recherche from './pages/Recherche'
import DonneesBrutes from './pages/DonneesBrutes'

export type Page = 'globale' | 'recherche' | 'brutes'

const PAGE_TITLE: Record<Page, string> = {
  globale:   'Vue d\'ensemble',
  recherche: 'Recherche',
  brutes:    'Données brutes',
}
const PAGE_SUB: Record<Page, string> = {
  globale:   'Indicateurs clés et analyses des données ferroviaires européennes',
  recherche: 'Rechercher des gares, lignes et opérateurs dans la base de données',
  brutes:    'Explorer et naviguer dans les tables de données',
}

export default function App() {
  const [page, setPage] = useState<Page>('globale')

  return (
    <div style={{ minHeight: '100vh', background: '#f1f5f9' }}>
      <TopNav page={page} setPage={setPage} />

      <main style={{ maxWidth: '1400px', width: '100%', margin: '0 auto', padding: '32px 32px 48px' }}>

        {/* Page header */}
        <div style={{ marginBottom: '28px' }}>
          <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a', letterSpacing: '-0.5px' }}>
            {PAGE_TITLE[page]}
          </h1>
          <p style={{ fontSize: '14px', color: '#64748b', marginTop: '4px' }}>
            {PAGE_SUB[page]}
          </p>
        </div>

        <div className="page-enter" key={page}>
          {page === 'globale'   && <VueGlobale />}
          {page === 'recherche' && <Recherche />}
          {page === 'brutes'    && <DonneesBrutes />}
        </div>

        <footer style={{
          marginTop: '48px', paddingTop: '20px',
          borderTop: '1px solid #e2e8f0',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        }}>
          <span style={{ fontSize: '12px', color: '#94a3b8' }}>
            © 2025 ObRail Europe — Observatoire ferroviaire européen
          </span>
          <span style={{ fontSize: '12px', color: '#94a3b8' }}>
            Green Deal Européen · TEN-T · Mobilité durable
          </span>
        </footer>
      </main>
    </div>
  )
}
