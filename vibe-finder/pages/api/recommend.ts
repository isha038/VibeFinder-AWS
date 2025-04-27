// pages/api/recommend.ts
import type { NextApiRequest, NextApiResponse } from 'next'
import db from '../../lib/firebaseAdmin'

type Data =
  | { similar: string[] }
  | { error: string }

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<Data>
) {
  const artist = req.query.artist as string | undefined
  if (!artist) {
    return res.status(400).json({ error: 'artist query required' })
  }

  // sanitize slashes ; replace forward slashes with underscores as done in the pre-processing step
  const docId = artist.replace(/\//g, '_')
  const docSnap = await db.collection('artists').doc(docId).get()

  if (!docSnap.exists) {
    return res
      .status(404)
      .json({ error: `Artist "${artist}" not found in database.` })
  }

  const data = docSnap.data()
  if (!data?.similar_artists || !Array.isArray(data.similar_artists)) {
    return res
      .status(500)
      .json({ error: `No recommendations precomputed for "${artist}".` })
  }

  return res.status(200).json({ similar: data.similar_artists as string[] })
}
