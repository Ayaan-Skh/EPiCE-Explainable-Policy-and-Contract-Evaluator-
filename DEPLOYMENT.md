# EPiCE Deployment

---

## Render (backend) + Vercel (frontend)

Deploy the API on Render and the Next.js app on Vercel. The browser talks to your Render API URL.

### 1. Deploy backend on Render

1. Go to [render.com](https://render.com) and sign in (or use GitHub).
2. **New → Web Service** and connect your repo (or use **Blueprint** if you have `render.yaml`).
3. **If using Blueprint:**  
   - **New → Blueprint**, connect repo, Render will read `render.yaml`.  
   - Skip to step 5.
4. **If configuring manually:**
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory:** leave blank (repo root with `api/`, `src/`, `requirements.txt`).
5. **Environment variables** (Dashboard → Environment):
   - `GROQ_API_KEY` = your Groq API key (secret)
   - `LLM_PROVIDER` = `groq`
   - `LLM_MODEL` = `llama-3.1-8b-instant`
   - `CORS_ORIGINS` = your Vercel app URL, e.g. `https://epice.vercel.app` (no trailing slash; add more comma-separated if you have preview URLs).
6. Deploy. Note the service URL, e.g. `https://epice-api.onrender.com`.

**Important:** On Render free tier the service sleeps after ~15 min idle; the first request after that can take 30–60 s. For production, use a paid plan or another host.

**Note:** Render’s filesystem is ephemeral. Uploaded policy files and the vector store are lost on redeploy or restart. For persistent storage you’d need a Render disk or external storage (e.g. S3).

---

### 2. Deploy frontend on Vercel

1. Go to [vercel.com](https://vercel.com) and sign in (e.g. with GitHub).
2. **Add New → Project** and import your repo.
3. **Configure:**
   - **Root Directory:** `frontend` (so Vercel uses the Next.js app).
   - **Framework Preset:** Next.js (auto-detected).
   - **Build Command:** `npm run build` (default).
   - **Output Directory:** default.
4. **Environment variables:**
   - `NEXT_PUBLIC_API_URL` = your Render API base **including** `/api`, e.g. `https://epice-api.onrender.com/api`
5. Deploy. Vercel will give you a URL like `https://epice-xxx.vercel.app`.

---

### 3. Connect backend and frontend

1. **Backend (Render):**  
   Set `CORS_ORIGINS` to your Vercel URL (and any preview URLs you need):
   - Production: `https://epice-xxx.vercel.app`
   - With previews: `https://epice-xxx.vercel.app,https://epice-*-xxx.vercel.app`
2. **Frontend (Vercel):**  
   Set `NEXT_PUBLIC_API_URL` to `https://your-render-service.onrender.com/api` (with `/api` at the end).
3. Redeploy both if you change env vars (Vercel redeploys on push if connected to Git).

---

### 4. First-time use

1. Open your Vercel app URL (e.g. `https://epice-xxx.vercel.app`).
2. Go to **Upload**, upload a policy document (PDF, DOCX, or TXT).
3. Go to **Query** and run a claim query.

---

### Quick reference

| Where        | What to set |
|-------------|-------------|
| **Render**  | `GROQ_API_KEY`, `LLM_PROVIDER`, `LLM_MODEL`, `CORS_ORIGINS` (your Vercel URL) |
| **Vercel**  | `NEXT_PUBLIC_API_URL` = `https://your-render-app.onrender.com/api` |

---

## Docker (local / single server)

## Prerequisites

- Docker and Docker Compose installed
- `.env` in project root with at least:
  - `GROQ_API_KEY=your_key`
  - `LLM_PROVIDER=groq`
  - `LLM_MODEL=llama-3.1-8b-instant` (or your model)

## Local deployment (same machine)

1. **From project root** (`D:\Projects\EPiCE` or `/path/to/EPiCE`):

   ```bash
   docker compose up --build -d
   ```

2. **First-time setup (upload a policy):**

   - Open http://localhost:3000/upload
   - Upload a policy document (PDF, DOCX, or TXT)
   - Then use http://localhost:3000/query to run queries

3. **URLs:**

   - App: http://localhost:3000
   - API: http://localhost:8000
   - API docs: http://localhost:8000/docs

4. **Logs:**

   ```bash
   docker compose logs -f
   docker compose logs -f api
   docker compose logs -f frontend
   ```

5. **Stop:**

   ```bash
   docker compose down
   ```

## Production / different host

- Set **build-time** API URL for the frontend so the browser can reach the API:
  - In `docker-compose.yml`, set `NEXT_PUBLIC_API_URL` to your public API URL, e.g. `https://api.yourdomain.com/api`.
  - Or build the frontend image with a build arg and use it as `NEXT_PUBLIC_API_URL`.
- Ensure the API is reachable from the browser (CORS allows your frontend origin; add it in `api/main.py` if needed).
- Use HTTPS and secrets (e.g. Docker secrets or a vault) for `GROQ_API_KEY` instead of a plain `.env` if needed.

## Data persistence

- `./data` and `./policy_documents` are bind-mounted; uploads and vector store persist across restarts.
- `./api/logs` holds API logs.

## Troubleshooting

- **Frontend shows "Failed to connect to backend"**  
  Ensure `NEXT_PUBLIC_API_URL` is the URL the **browser** can use (e.g. `http://localhost:8000/api` for local).
- **API 500 on query**  
  Check `.env` has valid `GROQ_API_KEY` and that a policy has been uploaded.
- **Rebuild after code changes:**  
  `docker compose up --build -d`
