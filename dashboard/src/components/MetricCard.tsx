import { useEffect, useState } from 'react'

interface Props {
  icon: string
  value: number
  label: string
  color: string      // hex accent (e.g. "#6366f1")
  colorBg: string    // light bg (e.g. "#f5f3ff")
}

function easeOutCubic(t: number) { return 1 - Math.pow(1 - t, 3) }

function useCounter(target: number, duration = 900) {
  const [count, setCount] = useState(0)
  useEffect(() => {
    if (target === 0) return
    const start = Date.now()
    const frame = () => {
      const p = Math.min((Date.now() - start) / duration, 1)
      setCount(Math.floor(easeOutCubic(p) * target))
      if (p < 1) requestAnimationFrame(frame)
      else setCount(target)
    }
    requestAnimationFrame(frame)
  }, [target, duration])
  return count
}

export default function MetricCard({ icon, value, label, color, colorBg }: Props) {
  const count = useCounter(value)

  return (
    <div style={{
      background: '#ffffff',
      border: '1px solid #e2e8f0',
      borderRadius: '14px',
      padding: '24px',
      boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
      transition: 'box-shadow 0.2s, transform 0.2s',
      cursor: 'default',
    }}
    onMouseEnter={e => {
      e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.08)'
      e.currentTarget.style.transform = 'translateY(-2px)'
    }}
    onMouseLeave={e => {
      e.currentTarget.style.boxShadow = '0 1px 4px rgba(0,0,0,0.04)'
      e.currentTarget.style.transform = 'translateY(0)'
    }}
    >
      <div style={{
        width: '40px', height: '40px', borderRadius: '10px',
        background: colorBg, display: 'flex', alignItems: 'center',
        justifyContent: 'center', fontSize: '18px', marginBottom: '16px',
      }}>
        {icon}
      </div>
      <div style={{
        fontSize: '34px', fontWeight: 700, color: '#0f172a',
        letterSpacing: '-1.5px', lineHeight: 1,
        fontVariantNumeric: 'tabular-nums',
      }}>
        {count.toLocaleString('fr-FR')}
      </div>
      <div style={{
        fontSize: '13px', color: '#64748b', marginTop: '8px', fontWeight: 500,
      }}>
        {label}
      </div>
      <div style={{
        marginTop: '10px', height: '3px', borderRadius: '2px',
        background: `linear-gradient(90deg, ${color}, transparent)`,
        opacity: 0.5,
      }} />
    </div>
  )
}
