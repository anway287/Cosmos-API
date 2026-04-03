from pydantic import BaseModel, Field
from typing import Optional


# ── Stellar Analysis ──────────────────────────────────────────────────────────

class StellarInput(BaseModel):
    temperature_k: float = Field(..., gt=0, description="Surface temperature in Kelvin")
    luminosity_solar: float = Field(..., gt=0, description="Luminosity relative to the Sun (L☉ = 1.0)")
    mass_solar: float = Field(..., gt=0, description="Mass relative to the Sun (M☉ = 1.0)")
    name: Optional[str] = Field(None, description="Optional star name")

class StellarMetrics(BaseModel):
    spectral_class: str
    radius_solar: float
    surface_gravity: float
    absolute_magnitude: float
    color: str
    main_sequence_lifetime_gyr: float
    current_stage: str
    next_stage: str
    time_remaining_gyr: Optional[float]

class StellarAnalysisResponse(BaseModel):
    metrics: StellarMetrics
    narrative: str
    hr_position: dict[str, str]
    fun_fact: str


# ── Constellation ─────────────────────────────────────────────────────────────

class ConstellationInput(BaseModel):
    ra_degrees: float = Field(..., ge=0, lt=360, description="Right Ascension in decimal degrees (0–360)")
    dec_degrees: float = Field(..., ge=-90, le=90, description="Declination in decimal degrees")

class ConstellationResponse(BaseModel):
    name: str
    abbreviation: str
    genitive: str
    area_sq_deg: float
    brightest_star: str
    mythology: str
    best_month: str
    hemisphere: str
    notable_objects: list[str]


# ── Exoplanet Habitability ────────────────────────────────────────────────────

class ExoplanetInput(BaseModel):
    planet_name: str
    orbital_distance_au: float = Field(..., gt=0)
    planet_radius_earth: float = Field(..., gt=0)
    planet_mass_earth: float = Field(..., gt=0)
    stellar_luminosity_solar: float = Field(..., gt=0)
    stellar_temperature_k: float = Field(..., gt=0)
    has_atmosphere: bool = True

class HabitabilityZone(BaseModel):
    inner_au: float
    outer_au: float
    in_zone: bool

class ExoplanetResponse(BaseModel):
    habitability_score: float
    habitability_class: str
    equilibrium_temperature_k: float
    habitable_zone: HabitabilityZone
    earth_similarity_index: float
    summary: str
    key_factors: list[str]
