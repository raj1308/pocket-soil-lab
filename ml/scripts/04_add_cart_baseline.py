#!/usr/bin/env python3
"""Add a plain CART (DecisionTreeRegressor) baseline to the existing evaluation.

Why a separate script instead of editing 03_train_evaluate.py and rerunning:
the full script takes ~15 minutes (RF/ExtraTrees/HistGB + 4-way leave-one-out).
This reuses the *exact* same data load, train/test split (same RANDOM_SEED, so
an identical split) and chosen preprocessing (snv_sg1, already decided), and
only trains the one additional cheap model -- then appends its row to the
already-saved metadata.json and report.md rather than regenerating them.

Why this baseline matters here specifically: the course's own "CART and RF"
material teaches Random Forest as an ensemble-of-trees improvement over a
single CART tree, with CART's higher-variance, lower-accuracy behavior as the
explicit motivation. This baseline makes that comparison visible with this
project's own real numbers rather than just citing the lecture.
"""
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipelines"))
from preprocessing import build_preprocessor  # noqa: E402

PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"
ARTIFACTS_DIR = Path(__file__).resolve().parents[1] / "artifacts"
EVAL_DIR = Path(__file__).resolve().parents[1] / "evaluation"
TARGET_COL = "oc_usda.c729_w.pct"
GROUP_COL = "dataset.code_ascii_txt"
RANDOM_SEED = 42
MODEL_VERSION = "soc-visnir-rf-v1"


def main():
    import pandas as pd

    df = pd.read_csv(PROCESSED_DIR / "ossl_oc_subset_v1.csv.gz", compression="gzip")
    wavelength_cols = [c for c in df.columns if c.startswith("scan_visnir.") and c.endswith("_ref")]
    wavelength_cols.sort(key=lambda c: int(c.split(".")[1].split("_")[0]))
    X = df[wavelength_cols].to_numpy(dtype=np.float64)
    y = df[TARGET_COL].to_numpy(dtype=np.float64)
    groups = df[GROUP_COL].to_numpy()

    X_train, X_test, y_train, y_test, _, _ = train_test_split(
        X, y, groups, test_size=0.2, random_state=RANDOM_SEED, stratify=groups
    )
    y_train_log = np.log1p(y_train)

    pre = build_preprocessor("snv_sg1")
    pipe = Pipeline([("pre", pre), ("model", DecisionTreeRegressor(random_state=RANDOM_SEED))])
    pipe.fit(X_train, y_train_log)

    pred_log = pipe.predict(X_test)
    pred_real = np.clip(np.expm1(pred_log), 0, None)
    metrics = {
        "mae": mean_absolute_error(y_test, pred_real),
        "rmse": float(np.sqrt(mean_squared_error(y_test, pred_real))),
        "r2": r2_score(y_test, pred_real),
        "oob_r2_log_target": None,
    }
    print(f"decision_tree (CART)   MAE={metrics['mae']:.3f}  RMSE={metrics['rmse']:.3f}  R²={metrics['r2']:.3f}")

    metadata_path = ARTIFACTS_DIR / f"{MODEL_VERSION}.metadata.json"
    metadata = json.loads(metadata_path.read_text())
    # Insert right after dummy_mean so the comparison table reads baseline -> CART -> ensembles.
    new_comparison = {}
    for k, v in metadata["model_comparison"].items():
        new_comparison[k] = v
        if k == "dummy_mean":
            new_comparison["decision_tree_cart"] = metrics
    metadata["model_comparison"] = new_comparison
    metadata_path.write_text(json.dumps(metadata, indent=2, default=str))
    print(f"Updated {metadata_path}")

    report_path = EVAL_DIR / f"{MODEL_VERSION}_report.md"
    report = report_path.read_text()
    old_row_marker = "| dummy_mean |"
    cart_row = (
        f"| dummy_mean | {metadata['model_comparison']['dummy_mean']['mae']:.3f} | "
        f"{metadata['model_comparison']['dummy_mean']['rmse']:.3f} | "
        f"{metadata['model_comparison']['dummy_mean']['r2']:.3f} | — |\n"
        f"| decision_tree_cart | {metrics['mae']:.3f} | {metrics['rmse']:.3f} | {metrics['r2']:.3f} | — |"
    )
    idx = report.find(old_row_marker)
    line_end = report.find("\n", idx)
    report = report[:idx] + cart_row + report[line_end:]
    report_path.write_text(report)
    print(f"Updated {report_path}")


if __name__ == "__main__":
    main()
