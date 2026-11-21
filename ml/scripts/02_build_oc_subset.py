#!/usr/bin/env python3
"""Build a modeling-ready subset of OSSL for soil organic carbon (SOC) prediction.

Target: oc_usda.c729_w.pct (% organic carbon, standard OSSL harmonized column).
Why SOC: it's the most widely validated VisNIR-predictable soil property in the
literature (per the course digest's own pXRF R² benchmarks and the broader
spectroscopy literature), has the most non-null labels in OSSL (132,490 of
135,418 lab records), and ties directly to this project's Walkley-Black /
organic-carbon-status soil health dashboard field.

Data quality note (found by inspection, not assumed): OSSL's combined VisNIR
file includes rows from MIR-only projects, which carry ~100% NaN across every
wavelength column (no VisNIR scan was ever taken for that sample) — about 52%
of all rows. The remaining rows are either essentially complete (<=1% NaN,
~24k rows) or near-complete (1-10% NaN, ~41k rows, likely a few missing points
at an instrument's native range edge). There is no in-between: row-level NaN
fraction is cleanly bimodal. So: rows with >10% NaN are dropped as "no real
scan"; rows with <=10% NaN are kept and their few missing values are filled
by linear interpolation along the wavelength axis (a standard, defensible fix
for sparse instrument-edge gaps, not for fabricating missing spectra).

Why a subsample, not the full ~55k qualifying rows: this machine has 5.6GB
RAM, much of it already used by the running dev servers. This script streams
the 644MB VisNIR file in chunks so peak memory stays bounded by the subset
size, then takes a reproducible random subsample (SUBSET_SIZE, seed=42) from
the pool of qualifying rows — still several thousand real, independently
collected soil samples from many labs/countries, which is what actually gets
saved and used for training.
"""
import gzip
from pathlib import Path

import numpy as np
import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "ossl"
PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"
TARGET_COL = "oc_usda.c729_w.pct"
ID_COL = "id.layer_uuid_txt"
SUBSET_SIZE = 12000
RANDOM_SEED = 42
CHUNK_SIZE = 10000
MAX_ROW_NAN_FRACTION = 0.10


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading soil lab data (organic carbon target)...")
    soillab = pd.read_csv(
        RAW_DIR / "ossl_soillab_L1_v1.2.csv.gz", usecols=[ID_COL, TARGET_COL], compression="gzip"
    )
    before = len(soillab)
    soillab = soillab.dropna(subset=[TARGET_COL])
    soillab = soillab[(soillab[TARGET_COL] >= 0) & (soillab[TARGET_COL] <= 60)]
    print(f"  {before} total lab records -> {len(soillab)} with a plausible OC value (0-60%)")
    valid_oc_ids = set(soillab[ID_COL])

    print("Loading site metadata (dataset grouping, location)...")
    soilsite = pd.read_csv(
        RAW_DIR / "ossl_soilsite_L0_v1.2.csv.gz",
        usecols=[ID_COL, "dataset.code_ascii_txt", "latitude.point_wgs84_dd", "longitude.point_wgs84_dd"],
        compression="gzip",
    )

    print("Streaming VisNIR spectra file once: filtering to rows with a valid OC label "
          f"AND <= {MAX_ROW_NAN_FRACTION:.0%} missing wavelengths...")
    visnir_path = RAW_DIR / "ossl_visnir_L0_v1.2.csv.gz"
    with gzip.open(visnir_path, "rt") as f:
        header = f.readline().strip().split(",")
    wavelength_cols = [c for c in header if c.startswith("scan_visnir.") and c.endswith("_ref")]
    usecols = [ID_COL] + wavelength_cols
    dtype = {c: np.float32 for c in wavelength_cols}

    reader = pd.read_csv(
        visnir_path, usecols=usecols, dtype=dtype, compression="gzip", chunksize=CHUNK_SIZE
    )
    kept_chunks = []
    n_scanned = 0
    for chunk in reader:
        n_scanned += len(chunk)
        chunk = chunk[chunk[ID_COL].isin(valid_oc_ids)]
        if len(chunk) == 0:
            continue
        nan_frac = chunk[wavelength_cols].isna().mean(axis=1)
        chunk = chunk[nan_frac <= MAX_ROW_NAN_FRACTION]
        if len(chunk) > 0:
            kept_chunks.append(chunk)
        print(f"  ...scanned {n_scanned} rows, qualifying so far: "
              f"{sum(len(c) for c in kept_chunks)}")

    pool = pd.concat(kept_chunks, ignore_index=True)
    pool = pool.drop_duplicates(subset=[ID_COL])
    print(f"Qualifying pool: {len(pool)} rows with real, near-complete VisNIR spectra + valid OC label")

    if len(pool) > SUBSET_SIZE:
        pool = pool.sample(n=SUBSET_SIZE, random_state=RANDOM_SEED).reset_index(drop=True)
    print(f"Subsampled to {len(pool)} rows (seed={RANDOM_SEED})")

    print("Interpolating remaining sparse gaps along the wavelength axis...")
    spectra_matrix = pool[wavelength_cols].to_numpy(dtype=np.float32)
    spectra_df = pd.DataFrame(spectra_matrix, columns=wavelength_cols)
    spectra_df = spectra_df.interpolate(axis=1, limit_direction="both")
    remaining_nan_rows = spectra_df.isna().any(axis=1).sum()
    if remaining_nan_rows:
        print(f"  {remaining_nan_rows} rows still had gaps interpolation couldn't fill — dropping them")
        keep_mask = ~spectra_df.isna().any(axis=1)
        pool = pool[keep_mask.values].reset_index(drop=True)
        spectra_df = spectra_df[keep_mask.values].reset_index(drop=True)

    pool[wavelength_cols] = spectra_df.values

    final = pool.merge(
        soillab, on=ID_COL, how="left"
    ).merge(soilsite, on=ID_COL, how="left")
    final = final.drop_duplicates(subset=[ID_COL])
    print(f"Final joined dataset: {len(final)} samples, {len(wavelength_cols)} wavelength columns")

    out_path = PROCESSED_DIR / "ossl_oc_subset_v1.csv.gz"
    final.to_csv(out_path, index=False, compression="gzip")
    print(f"Saved {out_path} ({out_path.stat().st_size / 1e6:.1f} MB)")

    print("\nTarget (organic carbon %) distribution:")
    print(final[TARGET_COL].describe())
    print("\nSamples per source dataset (top 10):")
    print(final["dataset.code_ascii_txt"].value_counts().head(10))


if __name__ == "__main__":
    main()
