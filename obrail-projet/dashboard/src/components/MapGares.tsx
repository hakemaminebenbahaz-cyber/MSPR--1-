import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Tooltip } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { fetchApi } from '../api'

interface Gare {
  id: number
  nom: string
  pays_code: string
  latitude: number | null
  longitude: number | null
}

const PAYS_COLORS: Record<string, string> = {
  FR: '#6366f1', DE: '#f59e0b', BE: '#22c55e', NL: '#0ea5e9',
  ES: '#ec4899', IT: '#f97316', AT: '#14b8a6', CH: '#8b5cf6',
  GB: '#ef4444', PL: '#84cc16', CZ: '#06b6d4', HU: '#d946ef',
  SK: '#fb923c', SI: '#4ade80', HR: '#38bdf8', RO: '#a78bfa',
  BG: '#fbbf24', SE: '#34d399', FI: '#60a5fa', DK: '#f472b6',
  NO: '#2dd4bf', PT: '#fb7185',
}

function getColor(pays: string) {
  return PAYS_COLORS[pays] ?? '#94a3b8'
}

export default function MapGares() {
  const [gares, setGares] = useState<Gare[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch up to 1000 gares avec coordonnées
    fetchApi<Gare[]>('/gares/map/coords').then(data => {
      if (data) setGares(data)
      setLoading(false)
    })
  }, [])

  const pays = [...new Set(gares.map(g => g.pays_code))].sort()

  return (
    <div>
      {loading ? (
        <div style={{ height: 420, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-4)', fontSize: 14 }}>
          Chargement de la carte…
        </div>
      ) : (
        <>
          <MapContainer
            center={[48.5, 10]}
            zoom={5}
            style={{ height: 420, borderRadius: 10, zIndex: 0 }}
            scrollWheelZoom={true}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {gares.map(g => (
              <CircleMarker
                key={g.id}
                center={[g.latitude!, g.longitude!]}
                radius={4}
                pathOptions={{
                  color: getColor(g.pays_code),
                  fillColor: getColor(g.pays_code),
                  fillOpacity: 0.85,
                  weight: 0,
                }}
              >
                <Tooltip>
                  <span style={{ fontWeight: 600 }}>{g.nom}</span>
                  <br />
                  <span style={{ color: '#64748b', fontSize: 11 }}>{g.pays_code}</span>
                </Tooltip>
              </CircleMarker>
            ))}
          </MapContainer>

          {/* Légende pays */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px 16px', marginTop: 12 }}>
            {pays.map(p => (
              <span key={p} style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11, color: 'var(--text-3)' }}>
                <span style={{ width: 10, height: 10, borderRadius: '50%', background: getColor(p), display: 'inline-block' }} />
                {p}
              </span>
            ))}
          </div>

          <p style={{ fontSize: 11, color: 'var(--text-4)', marginTop: 8, textAlign: 'right' }}>
            {gares.length} gares avec coordonnées GPS
          </p>
        </>
      )}
    </div>
  )
}
