"""Crop suitability reference data for the rule-based recommendation engine.

Ranges are illustrative agronomic guidance compiled for a classroom decision-
support demo, informed by widely-taught general ranges for major Indian field
crops (texture preference, pH tolerance, growing-season temperature and
rainfall, duration, water need). They are NOT a substitute for a state
agricultural department's official package of practices, and the engine says
so in its output. Treat this file as the single place to tune/extend the
crop list — weights and ranges are deliberately kept in plain, readable data
rather than hidden in code, per the master spec's "configurable weights"
requirement.
"""

CROPS = [
    {
        "key": "rice",
        "name": "Rice (paddy)",
        "season": "kharif",
        "duration_days": (100, 150),
        "water_need": "high",
        "texture_pref": ["clay", "silty clay", "clay loam", "silty clay loam"],
        "texture_tolerant": ["loam", "silt loam"],
        "ph_range": (5.5, 7.5),
        "temp_range_c": (20, 35),
        "min_rainfall_mm_season": 1000,
        "requires_irrigation_if_dry": True,
    },
    {
        "key": "wheat",
        "name": "Wheat",
        "season": "rabi",
        "duration_days": (110, 140),
        "water_need": "medium",
        "texture_pref": ["loam", "clay loam", "silt loam"],
        "texture_tolerant": ["sandy loam", "silty clay loam"],
        "ph_range": (6.0, 7.5),
        "temp_range_c": (10, 25),
        "min_rainfall_mm_season": 300,
        "requires_irrigation_if_dry": True,
    },
    {
        "key": "maize",
        "name": "Maize",
        "season": "kharif_or_rabi",
        "duration_days": (90, 120),
        "water_need": "medium",
        "texture_pref": ["loam", "sandy loam", "clay loam"],
        "texture_tolerant": ["silt loam", "sandy clay loam"],
        "ph_range": (5.5, 7.5),
        "temp_range_c": (18, 32),
        "min_rainfall_mm_season": 500,
        "requires_irrigation_if_dry": True,
    },
    {
        "key": "potato",
        "name": "Potato",
        "season": "rabi",
        "duration_days": (75, 110),
        "water_need": "medium",
        "texture_pref": ["sandy loam", "loam"],
        "texture_tolerant": ["loamy sand", "silt loam"],
        "ph_range": (5.0, 6.5),
        "temp_range_c": (15, 24),
        "min_rainfall_mm_season": 400,
        "requires_irrigation_if_dry": True,
    },
    {
        "key": "mustard",
        "name": "Mustard",
        "season": "rabi",
        "duration_days": (90, 120),
        "water_need": "low",
        "texture_pref": ["loam", "sandy loam", "clay loam"],
        "texture_tolerant": ["silt loam", "sandy clay loam"],
        "ph_range": (6.0, 7.5),
        "temp_range_c": (10, 25),
        "min_rainfall_mm_season": 250,
        "requires_irrigation_if_dry": False,
    },
    {
        "key": "groundnut",
        "name": "Groundnut",
        "season": "kharif",
        "duration_days": (100, 130),
        "water_need": "medium",
        "texture_pref": ["sandy loam", "loamy sand"],
        "texture_tolerant": ["loam"],
        "ph_range": (6.0, 7.0),
        "temp_range_c": (22, 32),
        "min_rainfall_mm_season": 500,
        "requires_irrigation_if_dry": False,
    },
    {
        "key": "chickpea",
        "name": "Chickpea (gram)",
        "season": "rabi",
        "duration_days": (90, 120),
        "water_need": "low",
        "texture_pref": ["loam", "clay loam", "sandy loam"],
        "texture_tolerant": ["silty clay loam"],
        "ph_range": (6.0, 7.5),
        "temp_range_c": (10, 28),
        "min_rainfall_mm_season": 200,
        "requires_irrigation_if_dry": False,
    },
    {
        "key": "pigeon_pea",
        "name": "Pigeon pea (arhar/tur)",
        "season": "kharif",
        "duration_days": (150, 200),
        "water_need": "low",
        "texture_pref": ["loam", "sandy loam", "clay loam"],
        "texture_tolerant": ["sandy clay loam"],
        "ph_range": (5.5, 7.5),
        "temp_range_c": (20, 32),
        "min_rainfall_mm_season": 400,
        "requires_irrigation_if_dry": False,
    },
    {
        "key": "green_gram",
        "name": "Green gram (moong)",
        "season": "kharif_or_summer",
        "duration_days": (60, 90),
        "water_need": "low",
        "texture_pref": ["sandy loam", "loam"],
        "texture_tolerant": ["loamy sand", "clay loam"],
        "ph_range": (6.0, 7.5),
        "temp_range_c": (22, 35),
        "min_rainfall_mm_season": 300,
        "requires_irrigation_if_dry": False,
    },
    {
        "key": "soybean",
        "name": "Soybean",
        "season": "kharif",
        "duration_days": (90, 120),
        "water_need": "medium",
        "texture_pref": ["loam", "clay loam"],
        "texture_tolerant": ["silty clay loam", "sandy loam"],
        "ph_range": (6.0, 7.5),
        "temp_range_c": (20, 30),
        "min_rainfall_mm_season": 500,
        "requires_irrigation_if_dry": False,
    },
]

# Configurable weights — kept separate from the scoring code so they can be
# tuned and their sensitivity tested without touching engine logic.
SCORING_WEIGHTS = {
    "texture": 0.25,
    "ph": 0.25,
    "organic_carbon": 0.15,
    "season_climate": 0.35,
}
