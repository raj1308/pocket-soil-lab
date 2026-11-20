# Feature & Phase Checklist

Only check an item once it is implemented AND verified running (not just coded). This file is the source of truth for "what's actually done" — update it at the end of every work session.

## Phase 0 — Feasibility & Planning
- [x] Lecture slides / syllabus reviewed — `docs/course-material-digest.md` (AG20103/AG20201 Soil Technology, IIT Kharagpur, S. Chakraborty). No formal software-project brief or grading rubric exists in any supplied file — confirmed self-directed, pending final user confirmation.
- [x] Traceability table (lecture concept → feature) drafted — see digest §2
- [ ] Dataset feasibility confirmed (candidate: OSSL — not yet inspected; local course lab files are real but far too small to train on, max 1-2 soil samples)
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

**Decisions locked in from course material review (`docs/course-material-digest.md`):**
- RandomForestRegressor set with `max_features=1/3` explicitly (mirrors the course's taught `mtry=M/3` for regression, not sklearn's current all-features default) + `oob_score=True` reported alongside held-out test R²/RMSE, per the course's CART/RF deck.
- Model comparison includes a plain `DecisionTreeRegressor` (CART) row so the RF/ensemble improvement is visible, per the same deck.
- ExtraTrees/HistGradientBoosting are explicitly flagged in the ML report as "beyond the syllabus" additions, not taught in this course.
- Published pXRF→soil-property R² benchmarks from the course's Soil Sensor Part 2 deck (0.42-0.58 for available-P/Ca, 0.83-0.90 for EC/pH) are cited as the real-world bar a project model should be compared against when deciding whether to mark a target "deployable."
- Manual soil-entry "measurement method" fields use real method names from the course's Soil Chemistry Manual: Olsen's method (NaHCO₃ extraction, molybdenum-blue colorimetry ~720nm) for available P, Walkley-Black for organic carbon, ammonium acetate/flame photometry for available K, alkaline KMnO₄ distillation for available N.
- Weather-vs-climate distinction (7-day forecast ≠ growing-season climate, already mandated by the master spec) is explicitly grounded in Jenny's equation of soil formation (soil = f(climate, organisms, relief, parent material, time)), which the course's own exams test.
- USDA sand/silt/clay mm boundaries from the course's Weathering deck used for texture validation (sum ≈ 100%) and texture-class labeling.
- Real single-sample instrument files from the user's own lab exercise (`/home/raj/Documents/Soil Tech/P Standard.csv`, `FTIR.csv`, `Spectroradiometer.xlsx`, `pXRF.pdf`, `grp 5.pdf`) are planned as genuinely-real "demo sample" profiles (Part 5 Mode 4) with correct provenance (sensor/lab measured, not "demonstration data") — stronger than fabricating synthetic demo profiles. None of these are usable for ML training (too few samples).
