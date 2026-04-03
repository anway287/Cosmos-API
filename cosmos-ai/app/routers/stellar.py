from fastapi import APIRouter
from app.models.schemas import StellarInput, StellarAnalysisResponse, StellarMetrics
from app.services import astronomy as astro
from app.services.narratives import stellar_narrative, stellar_fun_fact

router = APIRouter(prefix="/api/stellar", tags=["Stellar Analysis"])


@router.post("/analyze", response_model=StellarAnalysisResponse)
def analyze_star(body: StellarInput):
    spectral_class, color = astro.classify_spectral_type(body.temperature_k)
    radius = astro.stellar_radius(body.luminosity_solar, body.temperature_k)
    gravity = astro.surface_gravity(body.mass_solar, radius)
    abs_mag = astro.absolute_magnitude(body.luminosity_solar)
    ms_lifetime = astro.main_sequence_lifetime_gyr(body.mass_solar, body.luminosity_solar)
    stage = astro.evolution_stage(body.mass_solar, body.luminosity_solar, body.temperature_k)
    hr_pos = astro.hr_region(body.temperature_k, body.luminosity_solar)

    metrics = StellarMetrics(
        spectral_class=spectral_class,
        radius_solar=round(radius, 4),
        surface_gravity=round(gravity, 2),
        absolute_magnitude=round(abs_mag, 2),
        color=color,
        main_sequence_lifetime_gyr=round(ms_lifetime, 3),
        current_stage=stage.current,
        next_stage=stage.next,
        time_remaining_gyr=round(stage.time_remaining_gyr, 3) if stage.time_remaining_gyr else None,
    )

    metrics_dict = metrics.model_dump()
    metrics_dict["luminosity_solar"] = body.luminosity_solar
    metrics_dict["temperature_k"] = body.temperature_k

    return StellarAnalysisResponse(
        metrics=metrics,
        narrative=stellar_narrative(metrics_dict, body.name),
        hr_position=hr_pos,
        fun_fact=stellar_fun_fact(spectral_class),
    )
