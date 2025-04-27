from gensim.models import Word2Vec
import json

with open('artist_tags_5000.json') as f:
    artist_tags = json.load(f)


tag_corpus = list(artist_tags.values())

model = Word2Vec(
    sentences=tag_corpus,
    vector_size=50,
    window=2,
    min_count=1,
    sg=1,
    epochs=100
)


def get_embedding(tags):
    print("Getting embedding for", len(tags), "tags")
    vecs = [model.wv[tag] for tag in tags if tag in model.wv]
    if not vecs:
        return None
    return (sum(vecs) / len(vecs)).tolist()

