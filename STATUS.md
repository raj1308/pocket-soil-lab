# Feature & Phase Checklist

Only check an item once it is implemented AND verified running (not just coded). This file is the source of truth for "what's actually done" — update it at the end of every work session.

## Phase 0 — Feasibility & Planning
- [x] Lecture slides / syllabus reviewed — `docs/course-material-digest.md` (AG20103/AG20201 Soil Technology, IIT Kharagpur, S. Chakraborty). No formal software-project brief or grading rubric exists in any supplied file — confirmed self-directed, pending final user confirmation.
- [x] Traceability table (lecture concept → feature) drafted — see digest §2
- [ ] Dataset feasibility confirmed (candidate: OSSL — not yet inspected; local course lab files are real but far too small to train on, max 1-2 soil samples)
- [x] Initial architecture decided (provisional — may change after slides review)
- [x] Repo skeleton created

## Phase 1 — Application Skeleton
- [x] React + Vite + TS + Tailwind frontend scaffolded (hand-written, not `create-vite`, since the interactive scaffolder couldn't run non-interactively against the pre-existing folder layout)
- [x] FastAPI backend scaffolded with /health and /api/version — verified with `curl`
- [x] SQLite DB + SQLAlchemy session/Base initialized (no models yet — added as each phase needs them)
- [x] 5-tab navigation shell (Home, Soil Analysis, Crop Advisor, Weather, Reports) — other 4 tabs are explicit placeholders naming their phase, not fake content
- [x] Frontend ↔ backend integration verified end-to-end locally — Home page's "Backend connection" card fetches `/health` live; confirmed via `tsc --noEmit`, `vite build`, and curl with `Origin: http://localhost:5173` showing correct CORS headers

**Environment note:** this machine runs Python 3.14 (very new). `pydantic-core` pinned to 2.23.4 doesn't support it at all (hard PyO3 version floor) and `numpy`/`pandas`/`scikit-learn` had no prebuilt wheels yet, so `backend/requirements.txt` uses `>=` floors instead of exact pins, and a Rust toolchain (`rustup default stable`) was configured for `pydantic-core`'s source build. If you ever `pip install` from scratch again expect a slower first install while Rust compiles `pydantic-core`.

**To run it yourself:**
```
# backend (from backend/)
source .venv/bin/activate && uvicorn app.main:app --reload --port 8000

# frontend (from frontend/)
npm run dev
```
Both are currently running in the background from this session (backend :8000, frontend :5173) — visit http://localhost:5173 to see it live.

## Phase 2 — Weather Integration
- [x] Location selection (GPS via browser Geolocation API / manual city search via Open-Meteo geocoding)
- [x] Real Open-Meteo forecast call verified with actual response (current + 7-day daily + 168h hourly, Kharagpur test data)
- [x] Weather dashboard + graphs — current conditions, 7-day list, temperature area chart + rainfall-probability bar chart (Recharts, single-axis each, dataviz-skill-informed: blue/orange sequential hues, no dual-axis, tooltips, recessive gridlines)
- [x] Error/timeout/offline handling — 15-min in-memory backend cache (verified via `is_cached` flag), localStorage frontend fallback cache with a visible "showing cached forecast" banner on backend failure, last-updated timestamp shown
- [x] Conservative rule-based farming advisories (heavy rain, heat stress, waterlogging, fertilizer-timing caution) — thresholds documented in `backend/app/services/weather.py`
- [x] Verified end-to-end in a real headless browser (Playwright): searched "Kharagpur", selected a result, confirmed real temperature/advisories render with zero console errors; caught and fixed a clipped-Y-axis chart bug this way before calling it done

## Phase 3 — Soil Data Workflow
- [x] Manual entry form + validation (pH 0-14 hard range + 3-10 soft warning, texture sum ±5% check, non-negative nutrients) — `backend/app/services/soil.py`
- [x] Demo sample profiles (sandy/clay-rich/loamy/acidic/organic-carbon-poor), each labeled "Sample dataset — not a real-time soil measurement", internally consistent with real soil-science relationships (acid→low available P, low OC→low N, clay→higher K) — `backend/app/services/demo_soil_profiles.py`
- [x] USDA 12-class texture triangle classifier, boundaries sourced from NRCS Soil Survey Manual (2017) Ch.3, verified against known demo values
- [x] Persistence to SQLite with per-measurement provenance (property/value/unit/method/source_type/reliability) — `SoilSample`/`SoilMeasurement` models
- [x] Verified end-to-end with Playwright: demo load → texture classification → measurement table with real method names (Olsen's, Walkley-Black, etc.) all render correctly

## Phase 4 — Crop Recommendation Engine
- [x] Crop knowledge base (10 crops: rice, wheat, maize, potato, mustard, groundnut, chickpea, pigeon pea, green gram, soybean) with texture/pH/temp/rainfall/duration/water-need ranges — `backend/app/services/crop_catalog.py`, weights kept as plain configurable data
- [x] Rule-based weighted suitability scoring (texture/pH/organic-carbon/season-climate components, missing components excluded and weights renormalized rather than guessed) — `backend/app/services/crop_recommendation.py`
- [x] Explanation output per crop: reasons, limiting factors, confidence (high/medium/low based on how many inputs were available), data limitations — confidence kept explicitly separate from the suitability score per the master spec
- [x] 7-day forecast never substituted for season climate — climate inputs are either omitted or explicit user-supplied regional estimates, UI says so directly
- [x] Verified end-to-end with Playwright: soil sample → crop recommendations, zero console errors, scores/reasons/limiting-factors all traceable to the actual inputs

## Phase 5 — Soil ML Model
- [ ] Dataset downloaded/inspected (real inspection, not assumed)
- [ ] Preprocessing pipeline (train-only fitting, no leakage)
- [ ] Baseline vs PLS vs RF vs ExtraTrees vs HistGB compared
- [ ] Held-out test evaluation (MAE/RMSE/R²) documented
- [ ] Model + pipeline serialized, exposed via backend endpoint

## Phase 6 — Fertilizer Calculations
- [x] Unit conversion + dosage functions (tested) — `backend/app/services/fertilizer.py`: ha↔acres, N-P2O5-K2O → Urea/DAP/MOP with correct DAP-nitrogen-credit (no double counting), 31 pytest cases covering fertilizer+soil+crop modules, all passing (`backend/tests/`)
- [x] "Insufficient validated data" guardrail wired in — exact master-spec message returned (and shown in UI) whenever N/P/K aren't all present; verified via test and live UI
- [x] Cost comparison — only computed when user supplies all 3 prices, otherwise explicitly omitted with an assumption note; prices are user-entered, never fabricated
- [x] Generic crop N-P2O5-K2O requirements + Low/Medium/High fertility-based adjustment, clearly labeled as a simplified teaching heuristic, not an official state package of practices
- [x] Verified end-to-end with Playwright (clay-rich demo sample → crop pick → fertilizer dose), zero console errors

## Phase 7 — Camera Observation
- [x] Capture/upload UI (`capture="environment"` for direct mobile camera access, falls back to file picker on desktop) — third tab on Soil Analysis
- [x] RGB/HSV/16-bin-per-channel histogram analysis, computed entirely client-side via Canvas `getImageData` (no image ever leaves the device, no backend image-processing dependency risk)
- [x] Explicit limitations statement always shown first ("a phone photo cannot measure pH, nitrogen, phosphorus or potassium") + brightness-based under/overexposure warnings; output strictly limited to colour/visual statistics, source labeled "image-derived visual observation"
- [x] Verified end-to-end with Playwright (real uploaded image → real computed RGB/HSV/histogram), zero console errors

## Phase 8 — Reports & History
- [x] Saved reports list (all persisted soil samples, demo and manual) + sample-to-sample comparison (select up to 2, renders side-by-side on wider screens)
- [x] PDF export via the browser's native print-to-PDF (`window.print()` + a print stylesheet that hides nav/chrome) — a genuinely real, working "save as PDF" with no extra server dependency, labeled accurately as "Print / Save as PDF" rather than implying an automatic download
- [x] Verified with Playwright: comparison view renders both samples' full measurement tables correctly, zero console errors

## Phase 9 — PWA & Deployment
- [x] Manifest (hand-written `public/manifest.json`), hand-drawn SVG icon rendered to PNG (192/512/apple-touch) via `rsvg-convert`
- [x] Service worker via `vite-plugin-pwa` (generateSW) — precaches app shell only, deliberately never caches `/api/*` responses (the app already has its own visibly-labeled offline cache for weather/soil data; a silent SW cache would undermine that labeling)
- [x] Offline fallback page (`public/offline.html`)
- [x] Verified with Playwright against a real production preview build: service worker reaches `active` state, manifest linked correctly, icons/sw.js/manifest all serve 200
- [ ] Hosting chosen and verified (free tier) — not yet deployed anywhere; still local-only

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
