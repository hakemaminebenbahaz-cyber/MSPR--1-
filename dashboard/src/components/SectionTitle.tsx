import type { ReactNode } from 'react'

interface Props {
  children: ReactNode
}

export default function SectionTitle({ children }: Props) {
  return (
    <h2 style={{
      fontSize: '14px',
      fontWeight: 600,
      color: '#e6edf3',
      margin: '0 0 20px 0',
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
    }}>
      {children}
    </h2>
  )
}
