#!/usr/bin/env python3
"""Download OSSL (Open Soil Spectral Library) v1.2 raw files.

Source: https://docs.soilspectroscopy.org/db-access.html
Citation: Safanelli et al. 2025, PLOS ONE, https://doi.org/10.1371/journal.pone.0296545
Zenodo archive: https://doi.org/10.5281/zenodo.5759693

Downloads three files (~200MB total compressed) into ml/data/raw/ossl/:
- ossl_visnir_L0_v1.2.csv.gz   VisNIR reflectance spectra, 350-2500nm @ 2nm steps
- ossl_soillab_L1_v1.2.csv.gz  Harmonized wet-chemistry lab measurements
- ossl_soilsite_L0_v1.2.csv.gz Site metadata (dataset/project, lat/lon)

Raw files are left untouched (gzipped) — 02_build_oc_subset.py reads them directly
without needing a separate decompress step.
"""
import gzip
import shutil
import urllib.request
from pathlib import Path

BASE_URL = "https://storage.googleapis.com/soilspec4gg-public/"
FILES = [
    "ossl_visnir_L0_v1.2.csv.gz",
    "ossl_soillab_L1_v1.2.csv.gz",
    "ossl_soilsite_L0_v1.2.csv.gz",
]
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "ossl"


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        dest = RAW_DIR / name
        if dest.exists():
            print(f"Already have {name}, skipping")
            continue
        url = BASE_URL + name
        print(f"Downloading {url} -> {dest}")
        with urllib.request.urlopen(url) as response, open(dest, "wb") as out:
            shutil.copyfileobj(response, out)
        print(f"  {dest.stat().st_size / 1e6:.1f} MB")

    # Verify each gzip is well-formed by reading its header.
    for name in FILES:
        path = RAW_DIR / name
        with gzip.open(path, "rb") as f:
            f.read(1024)
        print(f"Verified {name} is a valid gzip file")


if __name__ == "__main__":
    main()
