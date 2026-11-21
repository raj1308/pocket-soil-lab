# Pocket Soil Lab AI

AI-powered soil health screening, weather intelligence and crop recommendation platform for Indian farms. Mobile-first PWA, FastAPI backend, real weather data (Open-Meteo), and a genuinely trained/evaluated soil ML model.

> Status: Phases 0–9 complete and verified (manual testing + 39 backend pytest cases + Playwright end-to-end checks against the running app). See `STATUS.md` for the full, continuously-updated checklist — nothing there is checked off without having actually run.

## What this is

A decision-support and soil-screening tool — not a certified replacement for laboratory testing. Hard constraints this project follows: no fabricated NPK-from-camera, no fake measurements labeled as real, no fertilizer doses without validated inputs, no ML prediction feeding an automated dose calculation. See `docs/academic-report.md` §12 for the full, honest limitations list.

## Stack

- **Frontend:** React + TypeScript + Vite + Tailwind CSS + React Router + Recharts, installable PWA (manifest + service worker)
- **Backend:** FastAPI + Pydantic + Pandas/NumPy/Scikit-learn, SQLite (dev) with a DB layer that swaps to PostgreSQL via `DATABASE_URL`
- **ML:** OSSL (Open Soil Spectral Library) VisNIR spectra → soil organic carbon. HistGradientBoosting selected after comparing Dummy/CART/PLS/RandomForest/ExtraTrees/HistGB; held-out test R²=0.934 — see `ml/evaluation/soc-visnir-rf-v1_report.md` for the full comparison and an equally-prominent leave-one-dataset-out generalization finding (R² from -0.27 to 0.92 depending on excluded source)
- **Weather:** Open-Meteo forecast API (real provider, no fabricated forecasts)

## Repo layout

```
frontend/   React PWA (components, pages, services, hooks, types, utils)
backend/    FastAPI app (app/api, app/schemas, app/services, app/models, app/database, app/core) + pytest suite
ml/         OSSL download/preprocessing/training scripts, pipelines, trained artifacts, evaluation report
docs/       course-material digest, academic report, deployment guide
```

## Running locally

Backend (FastAPI, port 8000):
```
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend (Vite dev server, port 5173):
```
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173 — the Home page's "Backend connection" card confirms the frontend can reach the backend's `/health` endpoint.

**Note on Python 3.14:** if you're on a very new Python, `pydantic-core` needs a Rust toolchain to build from source (no prebuilt wheel yet for brand-new interpreter versions) — run `rustup default stable` once if `pip install` fails with a Cargo/PyO3 error.

**Running the backend tests:** `cd backend && source .venv/bin/activate && pytest -q` (39 cases covering soil validation, crop scoring, fertilizer arithmetic, and ML model loading).

**Retraining the ML model from scratch:** see `ml/scripts/01_download_ossl.py` through `04_add_cart_baseline.py`, run in order. `ml/artifacts/` and `ml/data/processed/` are committed so this isn't required to run the app — the trained model is already there.

## Documentation

- `STATUS.md` — live, per-phase feature checklist (what's actually verified working)
- `docs/course-material-digest.md` — traceability from AG20103/AG20201 lecture content to this project's features
- `docs/academic-report.md` — full academic report (abstract through references)
- `docs/deployment-guide.md` — step-by-step deployment to Render (backend) + Cloudflare Pages (frontend), with verified free-tier facts
- `ml/evaluation/soc-visnir-rf-v1_report.md` — the ML model's full evaluation, including the leave-one-dataset-out generalization finding

## Deployment

Prepared and documented in `docs/deployment-guide.md`, but **not yet live** — pushing to GitHub and connecting Render/Cloudflare Pages requires an interactive account login only you can do. The guide gets you from a working local checkout to a live URL in four steps.

## Scientific ground rules (non-negotiable)

- Every soil value carries: property, value, unit, source (lab-measured / manually-entered / sensor-measured / ML-predicted / regional-estimate / demonstration-data), method, date, uncertainty where available.
- A phone camera never produces a fabricated pH/NPK number — only visual/colour observations with explicit limitations stated.
- Fertilizer doses are only ever computed from validated nutrient inputs; otherwise the app says so explicitly instead of guessing. No ML-predicted value feeds a fertilizer calculation, ever — see the ML evaluation report for why.
- Weather is a real Open-Meteo forecast, cached and timestamped — never presented as a proprietary model or as live when it's stale/cached.
- An uploaded spectrum whose wavelength grid doesn't match the trained model's grid is rejected, never resampled/coerced.
