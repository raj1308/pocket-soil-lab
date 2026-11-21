"""Illustrative demo soil profiles (Part 5, Mode 4 of the project spec).

These are hand-built, internally-consistent example values for teaching/demo
purposes — not drawn from a specific lab report or published dataset, and
never to be confused with a real measurement. Each is labeled accordingly.
Values are chosen to (a) land cleanly in the named USDA texture class via
`classify_usda_texture`, and (b) respect well-established soil-science
relationships (e.g. acidic soils fixing available P via Al/Fe oxides; organic
carbon and available nitrogen tracking together; clay-rich Indian soils often
testing higher in available K due to illitic clay mineralogy).
"""

DEMO_PROFILES = [
    {
        "key": "sandy",
        "label": "Sandy soil",
        "description": (
            "Low water/nutrient retention, typical of coastal or riverine sandy tracts. "
            "Low organic carbon and low available N/P/K are expected for this texture."
        ),
        "entry": {
            "farm_name": "Demo: Sandy soil",
            "sampling_depth_cm": 15,
            "ph": 6.0,
            "organic_carbon_pct": 0.3,
            "available_nitrogen_kg_ha": 180,
            "available_phosphorus_kg_ha": 8,
            "available_potassium_kg_ha": 90,
            "sand_pct": 90,
            "silt_pct": 5,
            "clay_pct": 5,
            "ec_ds_m": 0.3,
            "moisture_pct": 8,
        },
    },
    {
        "key": "clay_rich",
        "label": "Clay-rich soil",
        "description": (
            "High water retention, slow drainage — typical of black cotton (Vertisol) soils. "
            "Often tests higher in available K due to illitic/smectitic clay mineralogy."
        ),
        "entry": {
            "farm_name": "Demo: Clay-rich soil",
            "sampling_depth_cm": 15,
            "ph": 7.8,
            "organic_carbon_pct": 0.6,
            "available_nitrogen_kg_ha": 220,
            "available_phosphorus_kg_ha": 12,
            "available_potassium_kg_ha": 280,
            "sand_pct": 20,
            "silt_pct": 35,
            "clay_pct": 45,
            "ec_ds_m": 0.5,
            "moisture_pct": 22,
        },
    },
    {
        "key": "loamy",
        "label": "Loamy soil",
        "description": (
            "Balanced sand/silt/clay — generally the most agriculturally versatile texture, "
            "with moderate water retention and nutrient availability."
        ),
        "entry": {
            "farm_name": "Demo: Loamy soil",
            "sampling_depth_cm": 15,
            "ph": 6.8,
            "organic_carbon_pct": 0.75,
            "available_nitrogen_kg_ha": 280,
            "available_phosphorus_kg_ha": 18,
            "available_potassium_kg_ha": 160,
            "sand_pct": 40,
            "silt_pct": 40,
            "clay_pct": 20,
            "ec_ds_m": 0.3,
            "moisture_pct": 18,
        },
    },
    {
        "key": "acidic",
        "label": "Acidic soil",
        "description": (
            "Low pH, typical of high-rainfall lateritic/red soil regions. Available phosphorus "
            "is characteristically very low — acidic soils fix P as insoluble Al/Fe phosphates."
        ),
        "entry": {
            "farm_name": "Demo: Acidic soil",
            "sampling_depth_cm": 15,
            "ph": 4.8,
            "organic_carbon_pct": 0.5,
            "available_nitrogen_kg_ha": 200,
            "available_phosphorus_kg_ha": 5,
            "available_potassium_kg_ha": 100,
            "sand_pct": 50,
            "silt_pct": 25,
            "clay_pct": 25,
            "ec_ds_m": 0.2,
            "moisture_pct": 15,
        },
    },
    {
        "key": "oc_poor",
        "label": "Organic-carbon-poor soil",
        "description": (
            "Degraded/heavily-cropped soil with very low organic carbon. Available nitrogen is "
            "also low, since soil N supply tracks organic matter content closely."
        ),
        "entry": {
            "farm_name": "Demo: Organic-carbon-poor soil",
            "sampling_depth_cm": 15,
            "ph": 7.2,
            "organic_carbon_pct": 0.15,
            "available_nitrogen_kg_ha": 140,
            "available_phosphorus_kg_ha": 10,
            "available_potassium_kg_ha": 120,
            "sand_pct": 55,
            "silt_pct": 30,
            "clay_pct": 15,
            "ec_ds_m": 0.25,
            "moisture_pct": 10,
        },
    },
]

MEASUREMENT_METHODS = {
    "ph": "1:2 soil:water suspension, pH meter",
    "organic_carbon_pct": "Walkley-Black wet oxidation",
    "available_nitrogen_kg_ha": "Alkaline KMnO4 distillation",
    "available_phosphorus_kg_ha": "Olsen's method (NaHCO3 extraction, molybdenum-blue colorimetry)",
    "available_potassium_kg_ha": "Ammonium acetate extraction, flame photometry",
    "sand_pct": "Sieve/hydrometer method",
    "silt_pct": "Sieve/hydrometer method",
    "clay_pct": "Sieve/hydrometer method",
    "ec_ds_m": "1:2 soil:water extract, conductivity meter",
    "moisture_pct": "Oven-dry gravimetric method",
}

MEASUREMENT_UNITS = {
    "ph": "pH",
    "organic_carbon_pct": "%",
    "available_nitrogen_kg_ha": "kg/ha",
    "available_phosphorus_kg_ha": "kg/ha",
    "available_potassium_kg_ha": "kg/ha",
    "sand_pct": "%",
    "silt_pct": "%",
    "clay_pct": "%",
    "ec_ds_m": "dS/m",
    "moisture_pct": "%",
}
