import { useState } from 'react'
import TopNav from './components/TopNav'
import VueGlobale from './pages/VueGlobale'
import Recherche from './pages/Recherche'
import DonneesBrutes from './pages/DonneesBrutes'
import { ThemeProvider } from './context/ThemeContext'

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
    <ThemeProvider>
      <div style={{ minHeight: '100vh', background: 'var(--bg-page)', transition: 'background 0.2s' }}>
        <TopNav page={page} setPage={setPage} />

        <main style={{ maxWidth: '1400px', width: '100%', margin: '0 auto', padding: '32px 32px 48px' }}>

          {/* Page header */}
          <div style={{ marginBottom: '28px' }}>
            <h1 style={{ fontSize: '24px', fontWeight: 700, color: 'var(--text-1)', letterSpacing: '-0.5px' }}>
              {PAGE_TITLE[page]}
            </h1>
            <p style={{ fontSize: '14px', color: 'var(--text-3)', marginTop: '4px' }}>
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
            borderTop: '1px solid var(--border)',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          }}>
            <span style={{ fontSize: '12px', color: 'var(--text-4)' }}>
              © 2025 ObRail Europe — Observatoire ferroviaire européen
            </span>
            <span style={{ fontSize: '12px', color: 'var(--text-4)' }}>
              Green Deal Européen · TEN-T · Mobilité durable
            </span>
          </footer>
        </main>
      </div>
    </ThemeProvider>
  )
}
