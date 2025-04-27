import firebase_admin
from firebase_admin import credentials, firestore
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

cred = credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

artists_col = db.collection('artists')

# 2. Fetch all artist docs and their embeddings
docs = list(artists_col.stream())
artist_ids   = [doc.id for doc in docs]
embeddings   = [doc.to_dict().get('embedding') for doc in docs]

# convert to numpy array
emb_matrix = np.array(embeddings)  # shape (N, D): N docs, D dimensions(embeddings)
print(f"Loaded {len(artist_ids)} embeddings of dimension {emb_matrix.shape[1]}")

# 3. Compute full cosine‐similarity matrix 
sim_matrix = cosine_similarity(emb_matrix)  # shape (N, N) compare each artist to all artists

# 4. For each artist, pick top 10 similar
top_n = 10
top_similar = {}  
for i, aid in enumerate(artist_ids):
    sims = sim_matrix[i]
    sims[i] = -1  # exclude self
    # get indices of top N
    top_idx = np.argsort(sims)[-top_n:][::-1]
    top_similar[aid] = [artist_ids[j] for j in top_idx]

# 5. Write back to Firestore in batches 
BATCH_SIZE = 400
items = list(top_similar.items())
for batch_start in range(0, len(items), BATCH_SIZE):
    batch = db.batch()
    for aid, sim_list in items[batch_start:batch_start + BATCH_SIZE]:
        doc_ref = artists_col.document(aid)
        batch.update(doc_ref, {'similar_artists': sim_list})
    batch.commit()
    print(f"Committed batch {batch_start//BATCH_SIZE + 1}")

print(" All done! Each artist doc now has a 'similar_artists' field.")
