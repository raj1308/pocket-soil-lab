# Pocket Soil Lab AI

AI-powered soil health screening, weather intelligence and crop recommendation platform for Indian farms. Mobile-first PWA, FastAPI backend, real weather data (Open-Meteo), and a genuinely trained/evaluated soil ML model.

> Status: Phase 0 (planning). See `STATUS.md` for the live feature checklist. Nothing in this repo should be assumed "done" until it is checked off there.

## What this is

A decision-support and soil-screening tool — not a certified replacement for laboratory testing. See `docs/scientific-limitations.md` (to be written in Phase 0/1) for the hard constraints this project follows: no fabricated NPK-from-camera, no fake measurements labeled as real, no fertilizer doses without validated inputs.

## Stack

- **Frontend:** React + TypeScript + Vite + Tailwind CSS + React Router + Recharts, PWA (manifest + service worker)
- **Backend:** FastAPI + Pydantic + Pandas/NumPy/Scikit-learn, SQLite (dev) with a DB layer that can move to PostgreSQL
- **ML:** PLS / Random Forest / Extra Trees / HistGradientBoosting via scikit-learn pipelines on a public soil spectral dataset (candidate: OSSL — to be confirmed in Phase 5 after real dataset inspection)
- **Weather:** Open-Meteo forecast API (real provider, no fabricated forecasts)

## Repo layout

```
frontend/   React PWA
backend/    FastAPI app (app/api, app/schemas, app/services, app/models, app/database, app/core)
ml/         dataset scripts, notebooks, pipelines, trained artifacts, evaluation reports
tests/      pytest + frontend tests
docs/       architecture, dataset methodology, model evaluation, API docs, academic report
sample_data/ transparently-labeled demo soil profiles
```

## Running locally

Not yet runnable end-to-end — see `STATUS.md` for current phase. Setup instructions will be added here as each phase lands (frontend dev server, backend uvicorn command, env vars).

## Scientific ground rules (non-negotiable)

- Every soil value carries: property, value, unit, source (lab-measured / manually-entered / sensor-measured / ML-predicted / regional-estimate / demonstration-data), method, date, uncertainty where available.
- A phone camera never produces a fabricated pH/NPK number — only visual/colour observations with explicit limitations stated.
- Fertilizer doses are only ever computed from validated nutrient inputs; otherwise the app says so explicitly instead of guessing.
- Weather is a real Open-Meteo forecast, cached and timestamped — never presented as a proprietary model or as live when it's stale/cached.
