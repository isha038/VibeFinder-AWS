// index.js
import admin from 'firebase-admin'

if (!admin.apps.length) {
  admin.initializeApp({
    credential: admin.credential.cert({
      projectId:   process.env.FIREBASE_PROJECT_ID,
      clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
      // Replace literal "\n" with real newlines in your secret
      privateKey:  process.env.FIREBASE_PRIVATE_KEY.replace(/\\n/g, '\n'),
    }),
  })
}
const db = admin.firestore()


export const handler = async function(event) {
  try {
    // 1) Extract & validate query param
    const artist = event.queryStringParameters?.artist
    if (!artist) {
      return {
        statusCode: 400,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ error: 'artist query required' }),
      }
    }

    // 2) Sanitize to match DynamoDB/Firestore doc IDs
    const docId = artist.replace(/\//g, '_')

    // 3) Fetch from Firestore
    const docSnap = await db.collection('artists').doc(docId).get()
    if (!docSnap.exists) {
      return {
        statusCode: 404,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ error: `Artist "${artist}" not found in database.` }),
      }
    }

    const data = docSnap.data()
    const similar = data.similar_artists
    if (!Array.isArray(similar)) {
      return {
        statusCode: 500,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ error: `No recommendations precomputed for "${artist}".` }),
      }
    }

    // 4) Success
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        // Enable CORS if your frontend is on a different origin:
        'Access-Control-Allow-Origin': '*',
      },
      body: JSON.stringify({ similar }),
    }
  } catch (err) {
    console.error(err)
    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: 'Internal server error' }),
    }
  }
}

