import requests, time
import json
import os
from dotenv import load_dotenv
load_dotenv()

LASTFM_API_KEY = os.getenv('LASTFM_API_KEY')

API_KEY      = LASTFM_API_KEY
BASE_URL     = 'http://ws.audioscrobbler.com/2.0/'
PER_PAGE     = 200
PAGES        = 25     # 25 * 200 = 5,000 artists
API_DELAY    = 0.25   # seconds between API calls

#sanity check
print("Using Last.fm API key:", API_KEY)
resp = requests.get(BASE_URL, params={
    'method': 'chart.gettopartists',
    'api_key': API_KEY,
    'format': 'json',
    'limit': 1,
    'page': 1
})
print("Status:", resp.status_code, "Payload:", resp.json())

#fetch top 5000 artists
def fetch_top_artists(page):
    resp = requests.get(BASE_URL, params={
        'method':  'chart.gettopartists',
        'api_key': API_KEY,
        'format':  'json',
        'limit':   PER_PAGE,
        'page':    page
    })
    data = resp.json().get('artists', {}).get('artist', [])
    return [a['name'] for a in data]

#fetch artist tags
def fetch_artist_tags(artist):
    resp = requests.get(BASE_URL, params={
        'method':  'artist.gettoptags',
        'api_key': API_KEY,
        'artist':  artist,
        'format':  'json'
    })
    tags = []
    try:
        for t in resp.json()['toptags']['tag'][:5]:
            tags.append(t['name'].lower())
    except Exception:
        pass
    return tags

artist_tags = {}
for page in range(1, PAGES + 1):
    names = fetch_top_artists(page)
    print(f"Page {page}/{PAGES}: fetched {len(names)} artists")
    for name in names:
        if name in artist_tags:
            continue
        tags = fetch_artist_tags(name)
        if tags:
            artist_tags[name] = tags
        time.sleep(API_DELAY)
    print(f" → Collected tags for {len(artist_tags)} unique artists so far")
    time.sleep(API_DELAY)

with open('artist_tags_5000.json','w') as f:
    json.dump(artist_tags, f)