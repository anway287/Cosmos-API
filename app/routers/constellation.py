from fastapi import APIRouter
from app.models.schemas import ConstellationInput, ConstellationResponse
from app.services import astronomy as astro
from app.services.narratives import (
    constellation_narrative,
    CONST_BEST_MONTH,
    CONST_HEMISPHERE,
)

router = APIRouter(prefix="/api/constellation", tags=["Constellation"])


def _hemisphere(dec: float, name: str) -> str:
    if name in CONST_HEMISPHERE:
        return CONST_HEMISPHERE[name]
    if dec > 25:
        return "Northern"
    if dec < -25:
        return "Southern"
    return "Both hemispheres"


@router.post("/identify", response_model=ConstellationResponse)
def identify_constellation(body: ConstellationInput):
    result = astro.identify_constellation(body.ra_degrees, body.dec_degrees)
    name = result["name"]

    return ConstellationResponse(
        name=name,
        abbreviation=result["abbreviation"],
        genitive=result["genitive"],
        area_sq_deg=result["area_sq_deg"],
        brightest_star=result["brightest_star"],
        mythology=constellation_narrative(name, result["notable_objects"]),
        best_month=CONST_BEST_MONTH.get(name, "Year-round"),
        hemisphere=_hemisphere(body.dec_degrees, name),
        notable_objects=result["notable_objects"],
    )
