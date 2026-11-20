# Feature & Phase Checklist

Only check an item once it is implemented AND verified running (not just coded). This file is the source of truth for "what's actually done" — update it at the end of every work session.

## Phase 0 — Feasibility & Planning
- [ ] Lecture slides / syllabus / evaluation criteria reviewed (**waiting on upload**)
- [ ] Traceability table (lecture concept → feature) completed
- [ ] Dataset feasibility confirmed (candidate: OSSL — not yet inspected)
- [x] Initial architecture decided (provisional — may change after slides review)
- [x] Repo skeleton created

## Phase 1 — Application Skeleton
- [ ] React + Vite + TS + Tailwind frontend scaffolded
- [ ] FastAPI backend scaffolded with /health
- [ ] SQLite DB + models initialized
- [ ] 5-tab navigation shell (Home, Soil Analysis, Crop Advisor, Weather, Reports)
- [ ] Frontend ↔ backend integration verified end-to-end locally

## Phase 2 — Weather Integration
- [ ] Location selection (GPS / manual / search)
- [ ] Real Open-Meteo forecast call verified with actual response
- [ ] Weather dashboard + graphs
- [ ] Error/timeout/offline handling

## Phase 3 — Soil Data Workflow
- [ ] Manual entry form + validation
- [ ] Demo sample profiles (labeled "not a real-time measurement")
- [ ] Persistence to DB with provenance fields

## Phase 4 — Crop Recommendation Engine
- [ ] Crop knowledge base (8–12 crops, sourced ranges)
- [ ] Rule-based weighted suitability scoring
- [ ] Explanation output per crop

## Phase 5 — Soil ML Model
- [ ] Dataset downloaded/inspected (real inspection, not assumed)
- [ ] Preprocessing pipeline (train-only fitting, no leakage)
- [ ] Baseline vs PLS vs RF vs ExtraTrees vs HistGB compared
- [ ] Held-out test evaluation (MAE/RMSE/R²) documented
- [ ] Model + pipeline serialized, exposed via backend endpoint

## Phase 6 — Fertilizer Calculations
- [ ] Unit conversion + dosage functions (tested)
- [ ] "Insufficient validated data" guardrail wired in
- [ ] Cost comparison (sourced prices, dated)

## Phase 7 — Camera Observation
- [ ] Capture/upload/crop UI
- [ ] RGB/HSV/histogram analysis
- [ ] Explicit limitations statement shown (no fake NPK/pH)

## Phase 8 — Reports & History
- [ ] Saved reports + comparison
- [ ] PDF export

## Phase 9 — PWA & Deployment
- [ ] Manifest, service worker, installability
- [ ] Offline fallback
- [ ] Hosting chosen and verified (free tier)

## Phase 10 — Testing & Presentation
- [ ] pytest suite for backend/ML/fertilizer logic
- [ ] Manual mobile test checklist run on real device
- [ ] Academic report + presentation + viva prep drafted

---
**Known provisional decisions (may change once lecture materials are reviewed):**
- Target region: India; initial crop set: rice, wheat, maize, potato, mustard, groundnut, chickpea, pigeon pea, green gram, soybean (per master prompt default — not yet cross-checked against any syllabus-mandated region/crop list).
- ML dataset: OSSL assumed likely candidate — not yet actually downloaded/inspected. No dataset facts (sample counts, wavelength ranges, licence) should be treated as confirmed until Phase 5 does real inspection.
