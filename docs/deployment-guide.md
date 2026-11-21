# Deployment Guide

Honest framing: this app deploys to two free services — a backend on Render and a
static frontend on Cloudflare Pages. Both require you (not an AI agent) to create
accounts and authorize GitHub access, since that's an interactive OAuth step. This
guide gets you from "working locally" to "live URL" with as few steps as possible.

## Free-tier facts (verified November 2026, re-check before relying on them long-term)

**Render** (backend, [render.com](https://render.com)):
- 750 free instance-hours/month, no credit card required.
- Free web services **sleep after 15 minutes of no traffic**; the next request wakes
  them (a few seconds' cold start). Fine for a demo or viva; not for 24/7 production.
- Free tier has **no persistent disk** — the SQLite file resets on redeploy, and
  possibly on sleep/wake. This project's demo soil profiles reseed on demand
  (`POST /api/soil/demo/{key}`), so that's an acceptable limitation for a demo.
  If you need durable storage, attach Render's free Postgres (expires after 30
  days on the free tier) and change `DATABASE_URL` — the backend's DB layer
  already works with either via that one environment variable.

**Cloudflare Pages** (frontend, [pages.cloudflare.com](https://pages.cloudflare.com)):
- Genuinely free static hosting: unmetered bandwidth, 500 builds/month, 20,000
  files/site, 20-minute build timeout. No server-side functions needed for this
  app (it's a pure Vite SPA talking to the Render API), so nothing here bills at
  Workers rates.

## Step 1 — push this repo to GitHub

You need a GitHub account and the repo pushed there (both Render and Cloudflare
Pages deploy by connecting to a GitHub repo).

```bash
# from the repo root
gh auth login          # interactive — follow the browser prompt
gh repo create pocket-soil-lab --private --source=. --remote=origin --push
```

(No `gh` CLI, or prefer the web UI? Create an empty repo at github.com/new, then
`git remote add origin <url> && git push -u origin master`.)

## Step 2 — deploy the backend to Render

1. Go to [dashboard.render.com](https://dashboard.render.com) → sign up (GitHub login
   is the fastest path) → **New +** → **Blueprint**.
2. Point it at your GitHub repo. Render reads `render.yaml` at the repo root and
   provisions the `pocket-soil-lab-api` web service automatically (root dir
   `backend/`, build/start commands already set).
3. It'll ask for the `CORS_ORIGINS` env var (marked `sync: false` in the blueprint
   so it isn't guessed) — leave it as `http://localhost:5173` for now; you'll update
   it in Step 4 once the frontend URL exists.
4. Deploy. Note the resulting URL (something like `https://pocket-soil-lab-api.onrender.com`).
5. Confirm it's alive: `curl https://<your-url>.onrender.com/health` should return
   `{"status":"ok","version":"0.1.0"}` (allow a few seconds for the cold start).

## Step 3 — deploy the frontend to Cloudflare Pages

1. Go to [dash.cloudflare.com](https://dash.cloudflare.com) → **Workers & Pages** →
   **Create** → **Pages** → **Connect to Git** → select your repo.
2. Build settings:
   - Root directory: `frontend`
   - Build command: `npm run build`
   - Build output directory: `dist`
3. Add an environment variable: `VITE_API_BASE_URL` = the Render URL from Step 2
   (e.g. `https://pocket-soil-lab-api.onrender.com`).
4. Deploy. Note the resulting URL (something like `https://pocket-soil-lab.pages.dev`).

## Step 4 — close the loop: update backend CORS

Back in Render, update the `CORS_ORIGINS` env var to your Cloudflare Pages URL from
Step 3 (e.g. `https://pocket-soil-lab.pages.dev`), save, and let it redeploy. Without
this step the frontend loads but every API call fails with a CORS error — the same
failure mode you'd see testing locally against the wrong port.

## Verifying it worked

Open the Cloudflare Pages URL on your phone. The Home page's "Backend connection"
card should say "Connected" within a few seconds (longer if Render's free instance
had gone to sleep). From there, try: Weather (GPS or search a city) → Soil Analysis
(load a demo sample) → Crop Advisor (get recommendations) — the same flow verified
locally in this project's `STATUS.md`.

## What this guide does NOT cover

- A custom domain (both services support it on the free tier if you own one).
- The free Postgres option, since the SQLite-resets-on-redeploy tradeoff is
  explicitly acceptable for this project's demo-data use case.
- CI/CD beyond each platform's own "push to deploy" (good enough for a student
  project; add GitHub Actions later if you want gated deploys).
