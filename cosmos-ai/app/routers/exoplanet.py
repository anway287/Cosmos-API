from fastapi import APIRouter
from app.models.schemas import ExoplanetInput, ExoplanetResponse, HabitabilityZone
from app.services import astronomy as astro
from app.services.narratives import exoplanet_summary

router = APIRouter(prefix="/api/exoplanet", tags=["Exoplanet Habitability"])


@router.post("/habitability", response_model=ExoplanetResponse)
def score_habitability(body: ExoplanetInput):
    hz_inner, hz_outer = astro.habitable_zone(body.stellar_luminosity_solar)
    eq_temp = astro.equilibrium_temperature(body.stellar_luminosity_solar, body.orbital_distance_au)
    esi = astro.earth_similarity_index(body.planet_radius_earth, body.planet_mass_earth, eq_temp)
    score, label, factors = astro.habitability_score(
        body.orbital_distance_au,
        body.planet_radius_earth,
        body.planet_mass_earth,
        body.stellar_luminosity_solar,
        body.stellar_temperature_k,
        body.has_atmosphere,
    )
    in_zone = hz_inner <= body.orbital_distance_au <= hz_outer

    summary = exoplanet_summary(
        body.planet_name, score, label, eq_temp, esi, in_zone, factors,
        body.planet_radius_earth, body.planet_mass_earth, body.stellar_temperature_k,
    )

    return ExoplanetResponse(
        habitability_score=score,
        habitability_class=label,
        equilibrium_temperature_k=round(eq_temp, 1),
        habitable_zone=HabitabilityZone(
            inner_au=round(hz_inner, 3),
            outer_au=round(hz_outer, 3),
            in_zone=in_zone,
        ),
        earth_similarity_index=esi,
        summary=summary,
        key_factors=factors,
    )
