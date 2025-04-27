// pages/index.tsx
import { useState, FormEvent } from 'react'

export default function Home() {
  const [artist, setArtist]     = useState<string>('')
  const [results, setResults]   = useState<string[]>([])
  const [error, setError]       = useState<string | null>(null)
  const [loading, setLoading]   = useState<boolean>(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!artist.trim()) return

    setLoading(true)
    setError(null)
    setResults([])

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/recommend?artist=${encodeURIComponent(artist)}`)
      const json = await res.json()
      if (!res.ok) {
        throw new Error(json.error || 'Unknown error')
      }
      setResults(json.similar)
    }
    catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } 
      else {
        setError('An unexpected error occurred.');
        console.error('Caught an unknown error:', err);
       }
    } 
     finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 600, margin: '2rem auto', fontFamily: 'sans-serif' }}>
      <h1 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>
        🎵VibeFinder - Discover Artists Who Share Your VIBE
      </h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Enter artist name"
          value={artist}
          onChange={e => setArtist(e.target.value)}
          disabled={loading}
          style={{
            width: '100%',
            padding: '.5rem',
            fontSize: '1rem',
            marginBottom: '.5rem'
          }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: '.5rem',
            fontSize: '1rem',
            backgroundColor: '#0070f3',
            color: 'white',
            border: 'none',
            cursor: 'pointer'
          }}
        >
          {loading ? 'Searching…' : 'Search'}
        </button>
      </form>

      {error && (
        <p style={{ color: 'red', marginTop: '1rem' }}>{error}</p>
      )}

      {results.length > 0 && (
        <div style={{ marginTop: '2rem' }}>
          <h2 style={{ marginBottom: '.5rem' }}>
            Similar Artists to <strong>{artist}</strong>
          </h2>
          <ul>
            {results.map((a, i) => (
              <li key={i}>{a}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
