
# 🎵 VibeFinder – End-to-End Music Artist Recommender

**VibeFinder** is a serverless, cross-cloud proof-of-concept that:

1. **Fetches** artist tags from Last.fm  
2. **Trains** a Word2Vec embedding model on those tags  
3. **Precomputes** top-10 similar artists for each act  
4. **Stores** everything in Google Firestore  
5. **Exposes** a REST API via AWS Lambda + API Gateway  
6. **Serves** a Next.js (TypeScript) frontend on Vercel  


## 🏗 Architecture

```plaintext
[Python Scripts]        [AWS Lambda]          [Next.js Frontend]
   fetch_artists_tags.py  ──> API Gateway ──> user’s browser
   embedding.py
   firestore.py            Lambda Handler
   precompute_similar.py      ↓
                              Firestore
```

1. **Python**: crawl Last.fm → train embeddings → push to Firestore  
2. **AWS**: Lambda + API Gateway expose `/recommend?artist=`  
3. **Next.js**: calls API and renders top 10 similar artists  



## Prerequisites

- **Node.js** ≥ 18 & **npm**  
- **Python** ≥ 3.7 & **pip**  
- **Google Cloud** project with Firestore 
- **Firebase Admin** service-account JSON  
- **Last.fm API key** (public only)  
- **AWS** account with IAM rights for Lambda & API Gateway  
- **Vercel** account for frontend hosting  



## 📂 Directory Layout

```
FinalProject/
├── DataFetching/            # Python data + ML pipeline
│   ├── fetch_artists_tags.py
│   ├── embedding.py
│   ├── firestore.py
│   ├── precompute_similar.py
│   └── artist_tags_5000.json
├── lambda-deploy/           # AWS Lambda bundle
│   ├── index.js
│   ├── package.json
│   └── node_modules/
├── vibe-finder/             # Next.js (TypeScript) frontend
│   ├── pages/
│   │   └── index.tsx
│   ├── .env.local
│   ├── package.json
│   └── tsconfig.json
├── .env                     # LASTFM_API_KEY
└── .gitignore
```

## 1. Data Pipeline (Python)

### a. Last.fm API Key

1. Go to https://www.last.fm/api → “Get an API account”.  
2. Register app, note your **API key**.  
3. Create a root `.env` in `FinalProject/`:

   ```ini
   LASTFM_API_KEY=YOUR_LASTFM_API_KEY
   ```

### b. Fetch Artist Tags

```bash
pip install requests python-dotenv
```

Run:

```bash
cd DataFetching
python fetch_artists_tags.py
```

### c. Train Embeddings

```bash
pip install gensim numpy
```


### d. Upload to Firestore

```bash
pip install firebase-admin
```


Run:

```bash
python firestore.py
```

### e. Precompute Similarities

```bash
pip install numpy scikit-learn
```

Run:

```bash
python precompute_similar.py
```

---

## 2. Google Firestore Setup

1. In GCP Console → Firestore → Create database.  
2. **IAM → Service Accounts** → Create/edit → grant **Firestore Admin** → download JSON → place in `DataFetching/`.  
3. **Security Rules** to restrict access to your service-account only.
```ini
    rules_version = '2';

service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth == null && request.time < timestamp.date(2099,1,1);
    }
  }
}
```


## 3. AWS Lambda + API Gateway

### a. Bundle & Zip Lambda

Inside `lambda-deploy/`:

```bash
npm init -y
npm install firebase-admin
```


Zip:

```bash
zip -r ../lambda-package.zip .
```

### b. Create Lambda Function

- AWS Console → Lambda → Create function (Author from scratch)  
- Runtime: **Node.js 18.x**  
- Handler: `index.handler`  
- Upload code: **.zip file** → select `lambda-package.zip`

### c. Configure Environment Variables

In Lambda → Configuration → Environment variables, add:

```
FIREBASE_PROJECT_ID=<your-gcp-project>
FIREBASE_CLIENT_EMAIL=<your-service-account-email>
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
```

### d. Create REST API Gateway

- Console → API Gateway → Create API → **REST API** (Regional)  
- **Resource** `/recommend` → **GET** → Integration: Lambda proxy → your function  
- **Method Request**: add Query String Param `artist` (Required)  
- **Enable CORS** (GET, OPTIONS, 4XX/5XX) → Redeploy to stage `prod`  
- Copy **Invoke URL**:  
  ```
  https://<api-id>.execute-api.<region>.amazonaws.com/prod
  ```

---

## 4. Next.js Frontend

### a. Configure API URL

In `vibe-finder/.env.local`:

```ini
NEXT_PUBLIC_API_URL=https://<api-id>.execute-api.<region>.amazonaws.com/prod
```

### b. Run Locally

```bash
cd vibe-finder
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### c. Deploy to Vercel

1. Push `vibe-finder/` to GitHub.  
2. Import repo in Vercel.  
3. Set **Environment Variable** `NEXT_PUBLIC_API_URL` as above.  
4. Deploy.

---

## 5. Testing End-to-End

- **Lambda**: Console “Test” with  
  ```json
  { "queryStringParameters": { "artist": "Coldplay" } }
  ```
- **cURL**:
  ```bash
  curl -i "https://<api-id>.execute-api.<region>.amazonaws.com/prod/recommend?artist=Coldplay"
  ```



## Troubleshooting

- **CORS errors** → re-enable CORS on Method & Gateway Responses → redeploy  
- **404** → ensure Firestore doc ID uses `artist.replace('/', '_')`  
- **Module not found** → zip with `index.js` at root + `node_modules/`  
- **Env vars** → check Lambda console settings, replace `\n` correctly  

