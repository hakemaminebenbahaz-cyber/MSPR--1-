export default function Loader() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '180px' }}>
      <div style={{
        width: '22px', height: '22px', borderRadius: '50%',
        border: '2px solid #e2e8f0',
        borderTopColor: '#6366f1',
        animation: 'spin 0.75s linear infinite',
      }} />
    </div>
  )
}
