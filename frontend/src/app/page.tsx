export default function Home() {
  return (
    <main style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      background: '#0a0a0a',
      color: '#ededed',
    }}>
      <h1 style={{ fontSize: '3rem', fontWeight: 700, marginBottom: '0.5rem' }}>Forr</h1>
      <p style={{ fontSize: '1.2rem', color: '#888' }}>Project scaffolded successfully.</p>
      <p style={{ fontSize: '0.9rem', color: '#555', marginTop: '2rem' }}>
        Frontend: Next.js &middot; Backend: FastAPI &middot; Database: Postgres
      </p>
    </main>
  );
}
