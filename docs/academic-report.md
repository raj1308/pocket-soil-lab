# Pocket Soil Lab AI
## AI-Powered Soil Health Screening, Weather Intelligence and Crop Recommendation Platform

A student project building on the coursework of AG20103/AG20201 Soil Technology
(Dept. of Agricultural and Food Engineering, IIT Kharagpur; instructor Somsubhra
Chakraborty). Self-directed — not a professor-assigned software deliverable; see
`docs/course-material-digest.md` for the traceability between lecture content and
this project's features.

---

## Abstract

Smallholder farmers in India frequently lack timely, affordable access to soil
testing, weather forecasting, and crop-suitability guidance, and the services that
do exist are fragmented across separate tools. This project builds an integrated,
mobile-first Progressive Web App — Pocket Soil Lab AI — that brings four things
into one place: (1) soil data collection via manual lab-result entry, illustrative
demo profiles, and client-side phone-camera colour observation; (2) real-time
weather forecasting via the Open-Meteo API with conservative, rule-derived farming
advisories; (3) a transparent, weighted rule-based crop suitability engine covering
ten major Indian field crops; and (4) a genuinely trained and evaluated machine
learning model that predicts soil organic carbon from visible/near-infrared
(VisNIR) reflectance spectra, trained on a 12,000-sample subset of the public Open
Soil Spectral Library (OSSL). The best model (HistGradientBoosting regression,
after an empirical preprocessing comparison favoring SNV + first-derivative
spectra) achieved a held-out test R² of 0.934 (MAE 1.465% organic carbon) —
comfortably above the course's own cited published benchmarks for proximal-sensor
soil-property prediction. Critically, a leave-one-source-dataset-out
cross-validation revealed the model's R² ranges from **-0.271** (tested on an
unfamiliar African soil dataset excluded from training) to **0.919** depending on
which source dataset is held out — a finding treated as the single most important
result in this report rather than an inconvenient footnote, and one that
concretely shapes the application's design: no automated fertilizer-dose
calculation in this project ever consumes an ML-predicted nutrient value. The
complete system — soil workflow, weather module, crop and fertilizer engines,
camera observation, reports, and installable PWA — is implemented, tested (39
backend pytest cases, end-to-end Playwright verification against the running
application), and documented as a decision-support and soil-screening tool, not a
certified replacement for laboratory testing.

## 1. Introduction

Soil testing, weather awareness, and crop selection are three of the most
consequential decisions an Indian smallholder farmer makes each season, yet the
information needed to make them well is scattered: a soil sample may need to be
physically carried to a district lab and waited on for days or weeks; weather
forecasts live in a separate app; and crop-suitability knowledge is often
informal, local, and undocumented in any single accessible place. This project
asks a narrower, answerable question: how much of that fragmentation can be
closed by a single, honestly-scoped mobile application, built within a student's
time, budget, and hardware constraints, while still resting on real science
rather than a convincing-looking demo?

## 2. Problem Statement

1. Conventional soil testing requires sample transport, lab queueing, and days-to-
   weeks of turnaround, which is a poor fit for time-sensitive planting decisions.
2. Weather, soil, and crop-requirement information exist in separate tools, forcing
   a farmer to mentally integrate data that a single application could combine.
3. Several existing "AI soil scanner" consumer apps imply that a phone camera can
   measure chemical soil properties (pH, NPK) — a claim this project's own course
   material (spectroscopy fundamentals, diffuse reflectance theory) shows to be
   scientifically unfounded for a standard phone camera; see §9 and §11.
4. Machine-learning soil property prediction from spectroscopy is real and
   published (§4), but deploying it responsibly requires disclosing *where* it
   works and where it does not — a distinction most consumer tools omit entirely.

## 3. Objectives

1. Build a working, installable mobile-first PWA covering soil data collection,
   weather, crop recommendation, fertilizer guidance, and reporting.
2. Train and rigorously evaluate at least one real machine learning model on a
   public soil spectral dataset, with an honest account of where it generalizes
   and where it does not.
3. Ground every non-ML recommendation (crop suitability, fertilizer dose, texture
   classification) in a transparent, inspectable rule rather than a black box.
4. Tie the project's features back to the concepts taught in AG20103/AG20201
   wherever a genuine connection exists, without inventing a connection where one
   does not (see `docs/course-material-digest.md`).
5. Enforce, as a hard design constraint rather than an aspiration, the scientific
   guardrails in the project's own master specification: never present a
   simulated or estimated value as a measurement; never let a camera photograph
   produce a fabricated chemistry value; never compute a fertilizer dose without
   validated nutrient inputs.

## 4. Literature Review

**Soil spectroscopy and VisNIR prediction.** The Open Soil Spectral Library (OSSL)
project (Safanelli et al., 2025, *PLOS ONE*,
[10.1371/journal.pone.0296545](https://doi.org/10.1371/journal.pone.0296545))
aggregates VisNIR and MIR spectra with harmonized wet-chemistry lab measurements
across many national and regional soil surveys (KSSL/USDA, LUCAS/EU, AfSIS,
ICRAF-ISRIC, and others), explicitly to support reproducible machine-learning
research on soil properties — this is the dataset this project trains on (§8).

**Proximal and remote soil sensing.** The course's own "Soil Sensor Part 1/2"
material surveys diffuse reflectance spectroscopy fundamentals (dark/white
referencing, spectral resolution vs. sampling interval), geophysical sensing
(γ-radiometrics, EM induction), and portable XRF (pXRF). Several studies cited in
that material are directly relevant benchmarks for this project's own model
acceptance criteria: pXRF-derived elemental data predicting EC/pH via linear and
multiple regression achieved R² = 0.83–0.90 (strong), while predicting available
phosphorus and exchangeable calcium via regression/Random Forest achieved only
R² = 0.42–0.89 depending on method and soil type (Brazil study cited in-deck) —
a documented example of a soil property that resists proximal-sensor prediction
much more than EC or pH do. Wenjun Ji et al. (2017) and Rouze et al. (2017) mapped
clay, sand, and CaCO₃ from aerial/proximal γ-ray counts.

**CART and Random Forest.** The course's "CART and RF" material (adapted from
Shmueli et al.'s business-analytics text) covers recursive partitioning (Gini/
entropy impurity, cost-complexity pruning, the "1-SE rule"), and Random Forest
(bootstrap aggregation, `mtry = √M` for classification / `M/3` for regression,
out-of-bag validation). It cites two directly relevant applications: Chakraborty
et al. (2019), predicting soil texture class from elemental (Zn/Zr/K/Mn/Pb/Cu/Fe)
data via CART; and Dutta et al. (2019), predicting maize yield variation from
seed rate, labor, farm size, organic manure and fertilizer inputs via CART. This
project's own Random Forest configuration (§7) deliberately mirrors the course's
`mtry = M/3` convention, which differs from scikit-learn's current library
default, and reports an out-of-bag score alongside the held-out test score, as
taught.

**Soil texture classification.** The twelve-class USDA soil textural triangle
used in this project's manual-entry validation (§7) follows the boundary
definitions in the USDA NRCS *Soil Survey Manual* (2017, Handbook No. 18, Ch. 3),
cross-referenced against UC ANR's soil-texture reference material during
implementation.

**Weather-informed agriculture.** This project deliberately does *not* conflate a
short-range weather forecast with growing-season climate. This distinction is
grounded in Jenny's equation of soil formation — soil properties and agronomic
suitability are a function of climate (among other factors) at a climatological
timescale, not a week's forecast — which the course's own mid-semester
examinations test directly (§4, course digest).

## 5. Proposed Methodology

The system follows a layered decision-support design: a mobile PWA client talks to
a FastAPI backend, which in turn (a) queries Open-Meteo for real forecasts, (b)
validates and persists soil measurements with full provenance metadata, (c) runs a
transparent rule-based scoring engine for crop suitability and fertilizer dosing,
and (d) optionally runs a trained ML model for organic-carbon prediction from an
uploaded, grid-validated spectral file. Every soil value carries an explicit
source label (`manually_entered`, `demonstration_data`, `ml_predicted`, etc.), a
measurement method where applicable (e.g. "Olsen's method (NaHCO₃ extraction,
molybdenum-blue colorimetry)"), and, for ML predictions, a model version and a
reliability note — so the UI is never left presenting two different kinds of
number as if they were the same kind of fact.

Four soil input modes were implemented, matching the project's own feature
specification: (1) manual entry of a recent lab result, with server-side
validation (pH range, texture-percentage sum, non-negative nutrients); (2) a
spectral CSV upload, routed to the trained ML model only when its wavelength grid
exactly matches the training grid — a mismatched grid is *rejected*, not
resampled, because resampling a differently-gridded spectrum doesn't manufacture
spectral information the instrument never measured (a direct application of the
course's "spectral resolution vs. sampling interval" lesson); (3) a phone-camera
colour observation, computed entirely client-side via the Canvas API, reporting
only RGB/HSV/brightness/histogram statistics and never a chemistry value; and
(4) five illustrative demo profiles (sandy, clay-rich, loamy, acidic,
organic-carbon-poor), each internally consistent with real soil-science
relationships (e.g. acid soils fixing phosphorus as insoluble Al/Fe phosphates)
and explicitly labeled "Sample dataset — not a real-time soil measurement."

## 6. System Architecture

```
  Mobile/Desktop Browser (PWA)
   React 18 + TypeScript + Vite + Tailwind + React Router + Recharts
   ├─ Home        (backend health, dashboard)
   ├─ Soil        (manual / demo / camera / spectral-upload)
   ├─ Crops       (rule-based recommendation + fertilizer calculator)
   ├─ Weather     (Open-Meteo forecast, charts, advisories)
   └─ Reports     (history, comparison, print-to-PDF)
            │  fetch() over HTTPS/CORS
            ▼
  FastAPI backend (Python)
   ├─ /api/soil/*        manual entry, demo profiles, spectral prediction
   ├─ /api/weather/*     Open-Meteo proxy + 15-min cache + advisories
   ├─ /api/crops/*       rule-based suitability scoring
   ├─ /api/fertilizer/*  dose calculation with the insufficient-data guardrail
   └─ SQLAlchemy ORM → SQLite (dev) / swappable via DATABASE_URL
            │
            ▼
  ml/ — OSSL download + preprocessing + training scripts, evaluation
        report, serialized scikit-learn Pipeline (joblib + JSON metadata)
```

Frontend and backend are deployed separately on free tiers (Cloudflare Pages for
the static PWA; Render for the API), documented in `docs/deployment-guide.md`
with currently-verified (November 2026) free-tier facts rather than assumed ones.

## 7. Dataset Description

**Source.** OSSL v1.2, downloaded directly from its public Google Cloud Storage
mirror (`storage.googleapis.com/soilspec4gg-public/`): VisNIR spectra (182MB
compressed, 135,652 rows × 1,076 wavelength columns on a 350–2500nm grid at 2nm
steps), harmonized lab chemistry (135,418 records), and site metadata (dataset of
origin, coordinates).

**A real data-quality issue found by inspection, not assumed.** Direct per-row
missing-value analysis showed OSSL's combined VisNIR file's row-level NaN
fraction is cleanly bimodal: roughly 52% of rows are ~100% NaN (from projects that
only ran MIR, not VisNIR, scans), with the remainder either essentially complete
(≤1% NaN) or near-complete (1–10% NaN, likely a few points at an instrument's
native-range edge). The modeling pipeline (`ml/scripts/02_build_oc_subset.py`)
filters out the no-scan rows, linearly interpolates the sparse remaining gaps
along the wavelength axis, and only then joins to the organic-carbon label.

**Target and subset.** The target property is soil organic carbon (%),
chosen because it has the most non-null labels in OSSL (132,490 of 135,418), is
the most widely validated VisNIR-predictable soil property in the literature, and
ties directly to this project's Walkley-Black /organic-carbon-status dashboard
field. Of the ~64,180 rows qualifying on both VisNIR completeness and a valid OC
label, a reproducible random subsample of 12,000 (seed=42) was used for training,
split 9,600/2,400 (train/test, stratified by source dataset). The subsample size
is a documented hardware-constrained tradeoff — this development machine has
5.6GB RAM, much of it in use by other running processes — not a scientific
shortcut; the subsample still spans four real, independently-collected source
datasets: LUCAS.SSL (European topsoil survey, 7,542 samples), KSSL.SSL (USDA
Kellogg Soil Survey Laboratory, 3,664), ICRAF.ISRIC (African soils, 677), and
LUCAS.WOODWELL.SSL (117).

## 8. Algorithms

**Preprocessing.** Standard Normal Variate (SNV, per-spectrum row-wise
mean-center and scale) and Savitzky-Golay smoothing/derivatives are implemented
as scikit-learn-compatible transformers (`ml/pipelines/preprocessing.py`). Both
are row-wise operations with no parameters fit from training data, so they are
leak-proof by construction; only the downstream regressors (and, implicitly, any
`StandardScaler` step) are fit on training data alone. Five preprocessing options
(raw, SNV, SG-smooth, SG-1st-derivative, SNV+SG-1st-derivative) were compared via
5-fold cross-validation on the training set only, using a PLS(15) probe model;
SNV+derivative won (CV R² 0.865 vs. 0.815 for raw).

**Models compared** (all on the held-out test set, in real %OC units after
back-transforming a log1p target):

| Model | MAE | RMSE | R² |
|---|---|---|---|
| Dummy (mean baseline) | 5.938 | 13.139 | -0.099 |
| Decision Tree (CART) | 2.235 | 4.845 | 0.851 |
| Partial Least Squares (30 components) | 2.214 | 5.368 | 0.817 |
| Random Forest (`max_features=1/3`, OOB R²=0.907) | 1.588 | 3.465 | 0.924 |
| Extra Trees | 1.525 | 3.324 | 0.930 |
| **HistGradientBoosting (selected)** | **1.465** | **3.224** | **0.934** |

Random Forest's `max_features` was set explicitly to 1/3 rather than left at
scikit-learn's current default, to mirror the course's taught `mtry = M/3` for
regression — a deliberate, documented alignment choice, not an accident of
defaults. Extra Trees and HistGradientBoosting are not covered in the course
material and are disclosed as "beyond the syllabus" additions made for better
performance.

**Rule-based engines.** Crop suitability (`backend/app/services/crop_recommendation.py`)
computes a weighted score (texture 25%, pH 25%, organic carbon 15%,
season/climate 35%) against named, sourced ranges for ten crops
(`crop_catalog.py`); any missing input simply drops its weight and renormalizes
the rest, rather than guessing. Fertilizer dosing
(`backend/app/services/fertilizer.py`) converts a crop's generic N-P₂O₅-K₂O
requirement, adjusted by a Low/Medium/High soil-fertility classification, into
Urea/DAP/MOP masses — crediting DAP's own nitrogen contribution against the
nitrogen requirement before topping up with Urea, so nitrogen is never
double-counted — and refuses to produce a dose at all when available N/P/K
weren't supplied, returning the exact guardrail message the project's own
specification requires.

## 9. Implementation

Stack: React 18 + TypeScript + Vite + Tailwind CSS + React Router + Recharts on
the frontend (installable PWA via `vite-plugin-pwa`, service worker precaching
only the static app shell — API responses are deliberately never cached by the
service worker, so the app's own explicit "cached forecast" labeling is never
silently overridden); FastAPI + Pydantic + SQLAlchemy + scikit-learn on the
backend; SQLite for development with a swap-in `DATABASE_URL` for Postgres.

Eleven backend API route groups were implemented: health/version, soil (manual
entry, demo profiles, sample listing, spectral prediction, model info), weather
(geocoding, forecast), crops (catalog, recommend), and fertilizer (recommend).
Thirty-nine backend pytest cases cover texture classification, crop scoring,
fertilizer arithmetic (unit conversions, DAP-nitrogen-crediting, guardrail
behavior), and ML model loading/validation. Every major feature was additionally
verified against the actually-running application using Playwright
browser automation — not just unit-tested in isolation — which caught and fixed
three real bugs during development: a clipped chart Y-axis, a broken nested-
scikit-learn-Pipeline preprocessing option, and a test-script selector bug.

## 10. Results

The headline ML result is reported in two parts deliberately, because either one
alone would be misleading:

1. **Primary held-out test performance** (same mix of source labs/instruments as
   training): R² = 0.934, MAE = 1.465% organic carbon, RMSE = 3.224% — comfortably
   above the course's own cited "strong" benchmark (R² 0.83–0.90, pXRF→EC/pH) and
   far above its "weak" benchmark (R² 0.42–0.58, pXRF→available-P/Ca).
2. **Leave-one-source-dataset-out generalization check**: retraining the same
   model while excluding each of the four source datasets in turn, then testing
   only on the excluded one:

   | Held out | MAE | RMSE | R² |
   |---|---|---|---|
   | ICRAF.ISRIC (African soils) | 0.915 | 2.560 | **-0.271** |
   | KSSL.SSL | 6.686 | 12.885 | 0.457 |
   | LUCAS.SSL | 1.860 | 3.956 | 0.789 |
   | LUCAS.WOODWELL.SSL | 1.305 | 2.827 | 0.919 |

   The ICRAF.ISRIC result — worse than simply predicting the mean — is the single
   most important number in this report. It demonstrates concretely that a strong
   random-split R² does not imply the model will transfer to an unfamiliar
   region's soil and instrument, and it is the direct justification for this
   project's deployment decision (§11, §13) to never let an ML-predicted value
   feed an automated fertilizer calculation.

Full diagnostic plots (predicted-vs-actual, residual distribution) are in
`ml/evaluation/soc-visnir-rf-v1_diagnostics.png`; the complete evaluation
narrative, including this same generalization finding stated prominently rather
than buried, is in `ml/evaluation/soc-visnir-rf-v1_report.md`.

## 11. Evaluation

Judged against the model-acceptance philosophy this project set for itself (never
deploy a model as decision-ready merely because its headline R² is positive),
HistGradientBoosting's primary-test performance clears the bar for *reporting* an
organic-carbon estimate, labeled `ml_predicted` with its model version and a
reliability note. It does **not** clear the bar for feeding that estimate into an
automated, unreviewed decision (a fertilizer dose) — a bar this project enforces
in code, not just in a disclaimer: the fertilizer module's only nutrient inputs
are manually-entered lab values (§8). The backend additionally refuses, rather
than silently resamples, any uploaded spectrum whose wavelength grid does not
exactly match the training grid, which is the practical, code-level form of the
course's "sampling interval is not the same as information content" lesson.

## 12. Limitations

- The ML model predicts organic carbon only. It has not been trained or validated
  for pH, available N, P, or K — properties the course's own cited literature
  (§4) shows are substantially harder to predict from reflectance or elemental
  proximal-sensor data.
- The 12,000-sample training subset is a reproducible random draw from a larger
  (~64,180-row) qualifying pool, chosen for this development machine's memory
  constraints, not the full OSSL library.
- The leave-one-dataset-out check used only four source datasets; a fifth,
  independently-collected regional dataset was not available to test against.
- Crop suitability ranges and the fertilizer base-requirement table are
  generic, widely-taught teaching figures, explicitly not an official state
  package of practices — the application says so in its own output, not only
  in this report.
- The fertility-class/dose-adjustment heuristic (+25%/unchanged/−25% for
  Low/Medium/High soil-test status) is a standard simplified extension-teaching
  rule, not a precision agronomic model.
- No field validation with real farmers or real soil samples from India was
  performed; demo profiles and the OSSL subset are the only "soil data" this
  project has handled.
- The application has not been deployed to production hosting as of this
  report (see `docs/deployment-guide.md` for the prepared, verified path);
  it has been run and tested locally throughout development.
- OSSL's own per-project data harmonization was used as-is; this project did
  not independently re-verify it against raw instrument files.

## 13. Future Scope

- Train additional targets OSSL supports well (pH, clay/sand/silt fractions),
  each with its own held-out *and* leave-one-dataset-out evaluation before
  being marked deployable, following this project's own acceptance rule.
- Expand training to the full qualifying OSSL pool (or a larger subsample) once
  run on hardware with more available memory.
- Add an out-of-distribution / novelty-detection check (e.g. a simple spectral
  distance-to-training-distribution score) so the UI can flag a specific
  uploaded spectrum as "unlike anything in training" rather than relying only on
  the aggregate leave-one-dataset-out numbers in this report.
- Hindi and Bengali localization (all current UI copy was structured with this
  in mind, per the master specification, but translation itself is not done).
- A real farmer field trial comparing this project's crop/fertilizer suggestions
  against local agricultural-extension guidance.
- Physical sensor integration (a real pXRF or VisNIR probe) as a clearly
  separated hardware extension, once such hardware is available to this
  project — explicitly out of scope until then, per the master specification's
  own instruction not to assume hardware the student does not have.

## 14. Conclusion

Pocket Soil Lab AI demonstrates that a scientifically honest, genuinely working
soil-health and crop-decision-support application is achievable within a
student's time, budget, and hardware constraints — provided the project is
willing to report an inconvenient result (a model that fails on unfamiliar
soils) as prominently as a convenient one, and to encode its own guardrails
(reject, don't resample; refuse, don't guess a fertilizer dose) in the running
code rather than only in prose. The application's real, trained ML model, real
weather integration, transparent rule-based engines, and tested, Playwright-
verified feature set together form a credible decision-support tool consistent
with its own stated limits — not a certified laboratory replacement, and not
presented as one.

## References

1. Safanelli, J.L. et al. (2025). *Open Soil Spectral Library (OSSL): A dataset
   and tools for soil spectroscopy.* PLOS ONE.
   [doi.org/10.1371/journal.pone.0296545](https://doi.org/10.1371/journal.pone.0296545)
2. Open Soil Spectral Library documentation and database access.
   [docs.soilspectroscopy.org](https://docs.soilspectroscopy.org/)
3. USDA Natural Resources Conservation Service (2017). *Soil Survey Manual*,
   Handbook No. 18, Chapter 3 (soil textural classification).
4. Chakraborty, S. et al. (2019). CART-based prediction of soil texture class
   from elemental composition — cited in AG20103/AG20201 "CART and RF" lecture
   material.
5. Dutta, R. et al. (2019). CART-based analysis of maize yield variation — cited
   in AG20103/AG20201 "CART and RF" lecture material.
6. Wenjun Ji et al. (2017); Rouze et al. (2017). γ-radiometric mapping of soil
   clay/sand/CaCO₃ — cited in AG20103/AG20201 "Soil Sensor Part 2" lecture
   material.
7. AG20103/AG20201 Soil Technology course materials (lecture decks, lab manual,
   mid-semester examinations, 2015/2022/2023), Dept. of Agricultural and Food
   Engineering, IIT Kharagpur, instructor Somsubhra Chakraborty — full
   traceability in `docs/course-material-digest.md`.
8. Open-Meteo (open-source weather API). [open-meteo.com](https://open-meteo.com/)
9. This project's own evaluation artifacts: `ml/evaluation/soc-visnir-rf-v1_report.md`,
   `ml/artifacts/soc-visnir-rf-v1.metadata.json`, and `STATUS.md`.
