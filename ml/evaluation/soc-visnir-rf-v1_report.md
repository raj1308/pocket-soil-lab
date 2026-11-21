# Soil Organic Carbon VisNIR Model — Evaluation Report

Model version: `soc-visnir-rf-v1`  
Trained: 2026-11-21T04:20:07.273500+00:00  
Dataset: OSSL (Open Soil Spectral Library) v1.2, VisNIR + soillab L1 (Safanelli et al. 2025, PLOS ONE, https://doi.org/10.1371/journal.pone.0296545)  
Train/test: 9600 / 2400 samples  
Wavelength range: 350-2500nm @ 2nm steps  
Chosen preprocessing: **snv_sg1** (compared via 5-fold CV, see table below)  
Chosen model: **hist_gradient_boosting**

## Preprocessing comparison (5-fold CV R², log-OC target, PLS(15) probe)

| Preprocessing | CV R² |
|---|---|
| raw | 0.815 |
| snv | 0.840 |
| sg_smooth | 0.815 |
| sg1_deriv | 0.836 |
| snv_sg1 | 0.865 |

## Model comparison (held-out test set, metrics in real %OC units)

| Model | MAE | RMSE | R² | OOB R² (log target) |
|---|---|---|---|---|
| dummy_mean | 5.938 | 13.139 | -0.099 | — |
| pls | 2.214 | 5.368 | 0.817 | — |
| random_forest | 1.588 | 3.465 | 0.924 | 0.907 |
| extra_trees | 1.525 | 3.324 | 0.930 | — |
| hist_gradient_boosting | 1.465 | 3.224 | 0.934 | — |

## Leave-one-dataset-out generalization check

Using the best model (**hist_gradient_boosting**), retrained excluding each source dataset in turn and tested only on the excluded one — this measures transfer to an unfamiliar lab/region's instrument and sample prep, which the primary test metric above does not.

| Held-out dataset | MAE | RMSE | R² |
|---|---|---|---|
| ICRAF.ISRIC | 0.915 | 2.560 | -0.271 |
| KSSL.SSL | 6.686 | 12.885 | 0.457 |
| LUCAS.SSL | 1.860 | 3.956 | 0.789 |
| LUCAS.WOODWELL.SSL | 1.305 | 2.827 | 0.919 |

**Key finding, stated plainly:** the primary held-out test R² (0.934) looks excellent, but it describes performance on soils from the *same mix of labs/instruments* as training. Retrained without ICRAF.ISRIC (African soils) and tested only on it, the model scores **R²=-0.271 — worse than just predicting the mean**. This is the single most important result in this report: a strong random-split R² does not imply the model will work on an unfamiliar region's soil, and this project's backend acts on that finding (see "Deployment decision" below) rather than reporting one optimistic number.

## Deployment decision

Based on the above, this model is deployed with its reliability tied to how well an uploaded spectrum's shape matches the training distribution, not deployed as uniformly trustworthy:
- The backend's `/api/soil/spectra/predict` endpoint validates the uploaded wavelength grid against this model's required grid and **rejects** incompatible spectra outright (wrong range/step/ordering) rather than coercing them.
- Predictions are always returned with source `"ml_predicted"`, this exact model version, and a reliability note pointing back to this report — never presented as equivalent to a lab measurement.
- Given the leave-one-dataset-out spread (-0.27 to +0.92), no automated fertilizer calculation in this project consumes an ML-predicted organic carbon value directly; fertilizer dosing (Phase 6) only ever uses manually-entered lab-test nitrogen/phosphorus/potassium, never a spectral prediction, precisely because of this demonstrated generalization gap.

## Acceptance notes

Compare held-out test R² against this course's own cited published pXRF->soil-property benchmarks (Soil Sensor Part 2 deck): R²=0.42-0.58 for available P/Ca (weak), R²=0.83-0.90 for EC/pH (strong). A model clearing ~0.6+ R² on SOC with real, held-out, cross-lab spectra is a credible result by that bar; R² well below that, or a large gap between the primary test and the leave-one-dataset-out check, means the model should be marked low-reliability and NOT used for automated fertilizer-relevant decisions without further validation.

## Limitations

- This is a ~12,000-sample reproducible random subsample of OSSL's ~64,000 qualifying VisNIR+organic-carbon records, chosen for this machine's memory constraints (documented in `ml/scripts/02_build_oc_subset.py`), not the full library.
- Target distribution is strongly right-skewed (organic/peat soils at the high end); log1p transform was used to stabilize this, but extreme-OC soils remain the hardest cases — see the residual plot.
- Spectra came from multiple instruments/labs pooled into one grid by OSSL's own harmonization; this project did not independently re-verify that harmonization.
- This model predicts organic carbon only. It has NOT been trained or validated for available N, P, or K, which the master project spec explicitly flags as far harder to predict from reflectance spectra alone (see course digest's pXRF P/Ca benchmarks).