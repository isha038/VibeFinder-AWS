import firebase_admin
from firebase_admin import credentials, firestore
from embedding import get_embedding
import json
import os
from dotenv import load_dotenv
load_dotenv()



FIREBASE_KEY = 'path/to/serviceAccountKey.json'

cred = credentials.Certificate(FIREBASE_KEY)
firebase_admin.initialize_app(cred)
db = firestore.client()

batch = db.batch()
collection = db.collection('artists')

with open('artist_tags_5000.json') as f:
    artist_tags = json.load(f)

ARTISTS = list(artist_tags.items())
BATCH_SIZE = 500

import re

def sanitize_id(name):
    # Replace forward/back slashes with underscores
    safe = name.replace('/', '_').replace('\\', '_')
    # Optionally remove other illegal characters via regex
    safe = re.sub(r'[^A-Za-z0-9_\- ]', '', safe)
    
    return safe

for i in range(0, len(ARTISTS), BATCH_SIZE):
    batch = db.batch()
    for artist, tags in ARTISTS[i:i+BATCH_SIZE]:
        emb = get_embedding(tags)
        if not emb:
            continue
        doc_id  = sanitize_id(artist)
        if not doc_id:
            print(f"Skipping invalid document ID for artist: {artist!r}")
            continue
        doc_ref = collection.document(doc_id)
        batch.set(doc_ref, {
            'artist_name': artist,    # keep original name in a field
            'tags':         tags,
            'embedding':    emb
        })
    batch.commit()
    print(f"Committed batch {i//BATCH_SIZE + 1}")