"""
Pure astronomy calculations — no AI involved.
All physics is grounded in real astrophysics formulae.
"""
import math
from dataclasses import dataclass
from typing import Optional

# Solar constants
T_SUN = 5778.0      # K
L_SUN = 1.0         # relative
M_SUN = 1.0         # relative
R_SUN = 1.0         # relative
G_SUN = 274.0       # m/s² surface gravity
BC_SUN = -0.07      # bolometric correction
M_BOL_SUN = 4.74    # absolute bolometric magnitude


# ── Spectral Classification ───────────────────────────────────────────────────

SPECTRAL_BOUNDARIES = [
    ("O", 30000, float("inf"), "#9bb0ff", "blue-violet"),
    ("B", 10000, 30000,        "#aabfff", "blue-white"),
    ("A", 7500,  10000,        "#cad7ff", "white"),
    ("F", 6000,  7500,         "#f8f7ff", "yellow-white"),
    ("G", 5200,  6000,         "#fff4ea", "yellow"),
    ("K", 3700,  5200,         "#ffd2a1", "orange"),
    ("M", 2400,  3700,         "#ffcc6f", "red"),
    ("L", 1300,  2400,         "#ff6633", "dark red"),
    ("T", 700,   1300,         "#880000", "methane brown dwarf"),
]

SPECTRAL_ELEMENTS: dict[str, list[str]] = {
    "O": ["He II", "He I", "H I (weak)", "C III", "N III", "O III"],
    "B": ["He I", "H I", "Mg II", "Si II/III", "C II"],
    "A": ["H I (strong)", "Ca II (weak)", "Mg II", "Fe I"],
    "F": ["H I", "Ca II", "Fe I", "Ca I", "Cr I"],
    "G": ["Ca II (strong)", "H I", "Fe I", "Ca I", "Mg I", "Na I"],
    "K": ["Ca II", "Ca I", "Fe I", "TiO (weak)", "Molecular bands"],
    "M": ["TiO (strong)", "Ca I", "Fe I", "VO", "CaOH", "H₂O"],
    "L": ["FeH", "CrH", "H₂O", "CO", "Dust"],
    "T": ["CH₄ (strong)", "H₂O", "H₂", "NH₃"],
}


def classify_spectral_type(temperature_k: float) -> tuple[str, str]:
    """Return (spectral_letter, color_description)."""
    for letter, t_min, t_max, _, color in SPECTRAL_BOUNDARIES:
        if t_min <= temperature_k < t_max:
            # Subtype 0-9
            fraction = (temperature_k - t_min) / (t_max - t_min)
            subtype = int(9 * (1 - fraction))
            return f"{letter}{subtype}V", color
    return "T9V", "ultra-cool brown dwarf"


def get_spectral_elements(spectral_class: str) -> list[str]:
    letter = spectral_class[0].upper() if spectral_class else "G"
    return SPECTRAL_ELEMENTS.get(letter, SPECTRAL_ELEMENTS["G"])


# ── Stellar Physics ───────────────────────────────────────────────────────────

def stellar_radius(luminosity_solar: float, temperature_k: float) -> float:
    """Stefan-Boltzmann: L = 4πR²σT⁴ → R = R☉ √(L/L☉) (T☉/T)²"""
    return math.sqrt(luminosity_solar) * (T_SUN / temperature_k) ** 2


def surface_gravity(mass_solar: float, radius_solar: float) -> float:
    """g = GM/R² — result relative to solar (g☉ = 274 m/s²)"""
    return G_SUN * mass_solar / (radius_solar ** 2)


def absolute_magnitude(luminosity_solar: float) -> float:
    """M = M_bol_sun − 2.5 log₁₀(L/L☉)"""
    return M_BOL_SUN - 2.5 * math.log10(max(luminosity_solar, 1e-10))


def main_sequence_lifetime_gyr(mass_solar: float, luminosity_solar: float) -> float:
    """τ_ms = (M/L) × τ☉  where τ☉ ≈ 10 Gyr."""
    return (mass_solar / max(luminosity_solar, 1e-10)) * 10.0


def color_index_bv(temperature_k: float) -> float:
    """Ballesteros (2012) approximation: B-V from temperature."""
    return 4600 * (1 / (0.92 * temperature_k + 1.7) + 1 / (0.92 * temperature_k + 0.62))


# ── Stellar Evolution Stage ────────────────────────────────────────────────────

@dataclass
class EvolutionStage:
    current: str
    next: str
    time_remaining_gyr: Optional[float]


def evolution_stage(
    mass_solar: float, luminosity_solar: float, temperature_k: float
) -> EvolutionStage:
    """Estimate current stage on the Hertzsprung-Russell diagram."""
    ms_lifetime = main_sequence_lifetime_gyr(mass_solar, luminosity_solar)

    # HR region classification
    log_l = math.log10(max(luminosity_solar, 1e-10))
    log_t = math.log10(max(temperature_k, 1))

    # White dwarf
    if luminosity_solar < 0.01 and temperature_k > 8000:
        return EvolutionStage("White Dwarf", "Black Dwarf (> 10¹⁴ yr)", None)

    # Brown dwarf
    if mass_solar < 0.08:
        return EvolutionStage("Brown Dwarf", "Cooling (> 10¹² yr)", None)

    # Giant branch (high luminosity, cool)
    if luminosity_solar > 100 and temperature_k < 7000:
        if mass_solar < 8:
            return EvolutionStage(
                "Red Giant / AGB",
                "Planetary Nebula → White Dwarf",
                ms_lifetime * 0.05,
            )
        return EvolutionStage(
            "Red Supergiant",
            "Core-Collapse Supernova → Neutron Star / Black Hole",
            ms_lifetime * 0.01,
        )

    # Hot giant / supergiant
    if luminosity_solar > 1000 and temperature_k > 20000:
        return EvolutionStage(
            "Blue Supergiant",
            "Luminous Blue Variable → Wolf-Rayet → Supernova",
            ms_lifetime * 0.05,
        )

    # Main sequence
    time_remaining = ms_lifetime * 0.7  # rough midpoint assumption
    if mass_solar > 8:
        return EvolutionStage(
            "Main Sequence (O/B massive)",
            "Red Supergiant → Supernova",
            time_remaining,
        )
    if mass_solar > 1.5:
        return EvolutionStage(
            "Main Sequence (A/F/G intermediate)",
            "Red Giant → Planetary Nebula → White Dwarf",
            time_remaining,
        )
    return EvolutionStage(
        "Main Sequence (G/K/M low-mass)",
        "Red Giant → White Dwarf",
        time_remaining,
    )


def hr_region(temperature_k: float, luminosity_solar: float) -> dict[str, str]:
    """Human-readable HR diagram coordinates."""
    if luminosity_solar < 0.01:
        v_label = "Sub-dwarf / White Dwarf"
    elif luminosity_solar < 0.1:
        v_label = "Lower Main Sequence"
    elif luminosity_solar < 10:
        v_label = "Main Sequence"
    elif luminosity_solar < 1000:
        v_label = "Giant Branch"
    else:
        v_label = "Supergiant / Hypergiant"

    if temperature_k < 4000:
        h_label = "Cool / Red"
    elif temperature_k < 7500:
        h_label = "Intermediate / Yellow"
    else:
        h_label = "Hot / Blue-White"

    return {"horizontal": h_label, "vertical": v_label}


# ── Constellation Boundaries (IAU subset — 45 key constellations) ─────────────
# Each entry: (name, abbr, genitive, area_sq_deg, brightest_star,
#              ra_min, ra_max, dec_min, dec_max, notable_objects)

CONSTELLATIONS = [
    ("Andromeda",        "And", "Andromedae",      722.3, "Alpheratz",     0,   30,  21,  53, ["M31 (Andromeda Galaxy)", "NGC 752"]),
    ("Aquarius",         "Aqr", "Aquarii",          979.9, "Sadalsuud",   300,  345, -25,   3, ["Helix Nebula (NGC 7293)", "M2"]),
    ("Aquila",           "Aql", "Aquilae",          652.5, "Altair",      280,  305,  -9,  18, ["NGC 6709"]),
    ("Aries",            "Ari", "Arietis",          441.4, "Hamal",        25,   55,  10,  31, ["NGC 772"]),
    ("Auriga",           "Aur", "Aurigae",          657.1, "Capella",      75,  105,  28,  56, ["M36", "M37", "M38"]),
    ("Bootes",           "Boo", "Bootis",           907.3, "Arcturus",    205,  235,   8,  55, ["NGC 5248"]),
    ("Cancer",           "Cnc", "Cancri",           505.9, "Tarf",        120,  135,   6,  33, ["M44 Beehive Cluster", "M67"]),
    ("Canis Major",      "CMa", "Canis Majoris",    380.1, "Sirius",       96,  110, -33,  -9, ["NGC 2362", "M41"]),
    ("Canis Minor",      "CMi", "Canis Minoris",    183.4, "Procyon",     111,  120,   0,  13, []),
    ("Capricornus",      "Cap", "Capricorni",       413.9, "Deneb Algedi",300,  330, -27,  -8, ["M30"]),
    ("Cassiopeia",       "Cas", "Cassiopeiae",      598.4, "Schedar",       0,   30,  46,  77, ["NGC 457", "NGC 663", "M52", "M103"]),
    ("Centaurus",        "Cen", "Centauri",        1060.4, "Alpha Cen",   180,  220, -65, -25, ["Omega Centauri (NGC 5139)", "NGC 5128"]),
    ("Cetus",            "Cet", "Ceti",            1231.4, "Diphda",       10,   50, -25,  10, ["Mira (ο Cet)", "M77"]),
    ("Corona Borealis",  "CrB", "Coronae Borealis", 178.7, "Alphecca",    225,  240,  26,  39, ["NGC 6085"]),
    ("Corvus",           "Crv", "Corvi",            183.8, "Gienah",      182,  196, -25, -11, []),
    ("Cygnus",           "Cyg", "Cygni",            803.9, "Deneb",       290,  340,  27,  61, ["North America Nebula", "M29", "M39", "NGC 7000"]),
    ("Draco",            "Dra", "Draconis",        1082.9, "Eltanin",     250,  310,  51,  86, ["NGC 6543 Cat's Eye Nebula"]),
    ("Eridanus",         "Eri", "Eridani",         1137.9, "Achernar",     25,   75, -58,   0, ["NGC 1300"]),
    ("Gemini",           "Gem", "Geminorum",        513.8, "Pollux",      100,  120,  10,  35, ["M35", "NGC 2392 Eskimo Nebula"]),
    ("Hercules",         "Her", "Herculis",        1225.1, "Kornephoros", 240,  285,   4,  51, ["M13 Great Hercules Cluster", "M92"]),
    ("Hydra",            "Hya", "Hydrae",           1302.7, "Alphard",    125,  225, -35,   7, ["M48", "M68", "M83", "NGC 3242"]),
    ("Leo",              "Leo", "Leonis",           946.9, "Regulus",     150,  177,  -6,  33, ["M65", "M66", "M95", "M96"]),
    ("Leo Minor",        "LMi", "Leonis Minoris",   231.9, "Praecipua",  150,  172,  22,  41, []),
    ("Lepus",            "Lep", "Leporis",          290.3, "Arneb",        74,   94, -27,  -9, ["M79", "NGC 1981"]),
    ("Libra",            "Lib", "Librae",           538.1, "Zubenelgenubi",220, 245, -30,   5, ["NGC 5897"]),
    ("Lupus",            "Lup", "Lupi",             333.7, "Alpha Lup",  220,  245, -55, -30, []),
    ("Lyra",             "Lyr", "Lyrae",            286.5, "Vega",        277,  295,  25,  48, ["M57 Ring Nebula", "M56"]),
    ("Monoceros",        "Mon", "Monocerotis",      481.6, "Beta Mon",   100,  120, -11,  12, ["Rosette Nebula", "NGC 2244"]),
    ("Ophiuchus",        "Oph", "Ophiuchi",         948.3, "Rasalhague",  240,  275, -30,  14, ["M10", "M12", "M14", "M62"]),
    ("Orion",            "Ori", "Orionis",          594.1, "Rigel",        74,  100,  -9,  22, ["M42 Orion Nebula", "M43", "NGC 1977", "Horsehead Nebula"]),
    ("Pegasus",          "Peg", "Pegasi",           1120.8, "Enif",       330,  360,   3,  35, ["M15", "NGC 7331"]),
    ("Perseus",          "Per", "Persei",           614.9, "Mirfak",       38,   70,  30,  59, ["Double Cluster (NGC 869/884)", "M34", "NGC 1499 California Nebula"]),
    ("Pisces",           "Psc", "Piscium",          889.4, "Eta Psc",    340,  360,  -6,  33, ["M74"]),
    ("Piscis Austrinus", "PsA", "Piscis Austrini",  245.4, "Fomalhaut",  330,  355, -37, -24, []),
    ("Sagittarius",      "Sgr", "Sagittarii",       867.4, "Epsilon Sgr", 270, 310, -45, -12, ["M8 Lagoon", "M17 Omega", "M20 Trifid", "M22", "Galactic Center"]),
    ("Scorpius",         "Sco", "Scorpii",          496.8, "Antares",    240,  270, -45, -10, ["M4", "M6 Butterfly", "M7", "M80"]),
    ("Serpens",          "Ser", "Serpentis",        636.9, "Unukalhai",  230,  280, -16,  26, ["M5", "M16 Eagle Nebula"]),
    ("Taurus",           "Tau", "Tauri",            797.2, "Aldebaran",    50,   90,  -1,  32, ["M1 Crab Nebula", "M45 Pleiades", "Hyades Cluster"]),
    ("Triangulum",       "Tri", "Trianguli",        131.8, "Beta Tri",    25,   45,  25,  37, ["M33 Triangulum Galaxy"]),
    ("Ursa Major",       "UMa", "Ursae Majoris",   1279.7, "Alioth",     140,  200,  28,  73, ["M81 Bode's Galaxy", "M82 Cigar", "M97 Owl Nebula", "M101 Pinwheel"]),
    ("Ursa Minor",       "UMi", "Ursae Minoris",    255.9, "Polaris",    215,  360,  65,  90, ["NGC 6217"]),
    ("Virgo",            "Vir", "Virginis",        1294.4, "Spica",      185,  225, -22,  14, ["M49", "M58", "M84", "M87 (giant elliptical)", "Virgo Cluster"]),
    ("Vulpecula",        "Vul", "Vulpeculae",       268.2, "Anser",      290,  315,  19,  29, ["M27 Dumbbell Nebula"]),
    ("Columba",          "Col", "Columbae",         270.2, "Phact",       80,   95, -43, -27, ["NGC 1851"]),
    ("Fornax",           "For", "Fornacis",         397.5, "Dalim",       25,   55, -40, -22, ["Fornax Cluster", "NGC 1316"]),
]


def identify_constellation(ra_deg: float, dec_deg: float) -> dict:
    """
    Identify the most likely constellation for given RA/Dec.
    Uses a geometric bounding-box approach as a fast first pass.
    """
    candidates = []
    for entry in CONSTELLATIONS:
        name, abbr, genitive, area, brightest, ra_min, ra_max, dec_min, dec_max, notable = entry
        # Handle RA wrap-around (Cassiopeia, Pisces etc.)
        if ra_min <= ra_max:
            ra_ok = ra_min <= ra_deg <= ra_max
        else:
            ra_ok = ra_deg >= ra_min or ra_deg <= ra_max
        dec_ok = dec_min <= dec_deg <= dec_max
        if ra_ok and dec_ok:
            candidates.append(entry)

    if not candidates:
        # Fall back to closest bounding box by midpoint distance
        def dist(entry):
            _, _, _, _, _, ra_min, ra_max, dec_min, dec_max, _ = entry[:-1] + (entry[-1],)
            ra_mid = (ra_min + ra_max) / 2
            dec_mid = (dec_min + dec_max) / 2
            return (ra_deg - ra_mid) ** 2 + (dec_deg - dec_mid) ** 2
        candidates = [min(CONSTELLATIONS, key=dist)]

    # Pick smallest-area match (most precise boundary)
    entry = min(candidates, key=lambda e: e[3])
    name, abbr, genitive, area, brightest, *_, notable = entry
    return {
        "name": name,
        "abbreviation": abbr,
        "genitive": genitive,
        "area_sq_deg": area,
        "brightest_star": brightest,
        "notable_objects": notable,
    }


# ── Exoplanet Habitability ────────────────────────────────────────────────────

def habitable_zone(stellar_luminosity_solar: float) -> tuple[float, float]:
    """
    Conservative habitable zone boundaries (Kopparapu et al. 2013).
    inner: 0.99 × √L  AU (runaway greenhouse)
    outer: 1.70 × √L  AU (maximum greenhouse)
    """
    sqrt_l = math.sqrt(stellar_luminosity_solar)
    return 0.99 * sqrt_l, 1.70 * sqrt_l


def equilibrium_temperature(
    stellar_luminosity_solar: float,
    orbital_distance_au: float,
    albedo: float = 0.3,
) -> float:
    """T_eq = T☉ × (R☉/2d)^0.5 × (1-A)^0.25 — simplified, in K."""
    # Flux at distance d: F = L_sun / (4π d²)  relative to F_earth at 1 AU
    # T_eq = 278.5 × (L/L☉)^0.25 / d^0.5 × (1-A)^0.25  K
    return 278.5 * (stellar_luminosity_solar ** 0.25) / (orbital_distance_au ** 0.5) * ((1 - albedo) ** 0.25)


def earth_similarity_index(
    planet_radius_earth: float,
    planet_mass_earth: float,
    eq_temp_k: float,
) -> float:
    """
    Simplified Earth Similarity Index (ESI) — Schulze-Makuch et al. 2011.
    ESI = ∏ (1 − |xi − xi_earth| / (xi + xi_earth))^wi
    """
    T_EARTH = 288.0
    R_EARTH = 1.0
    M_EARTH = 1.0
    DENSITY_EARTH = 1.0  # normalised

    # Estimated bulk density (very rough): ρ ∝ M/R³
    density = planet_mass_earth / max(planet_radius_earth ** 3, 0.01)

    def esi_factor(v, v_ref, w):
        return (1 - abs(v - v_ref) / (v + v_ref)) ** w

    esi_radius  = esi_factor(planet_radius_earth, R_EARTH, 0.57)
    esi_density = esi_factor(density, DENSITY_EARTH, 1.07)
    esi_temp    = esi_factor(eq_temp_k, T_EARTH, 5.58)

    return round(esi_radius * esi_density * esi_temp, 3)


def habitability_score(
    orbital_distance_au: float,
    planet_radius_earth: float,
    planet_mass_earth: float,
    stellar_luminosity_solar: float,
    stellar_temperature_k: float,
    has_atmosphere: bool,
) -> tuple[float, str, list[str]]:
    """
    Returns (score 0-100, class label, key factors list).
    """
    score = 0.0
    factors = []

    hz_inner, hz_outer = habitable_zone(stellar_luminosity_solar)
    in_hz = hz_inner <= orbital_distance_au <= hz_outer

    # Habitable zone (max 35 pts)
    if in_hz:
        score += 35
        factors.append("Orbit lies within the stellar habitable zone")
    elif orbital_distance_au < hz_inner:
        deficit = min(35, 35 * (hz_inner - orbital_distance_au) / hz_inner)
        score += max(0, 35 - deficit * 2)
        factors.append(f"Too close to star — inside habitable zone (HZ inner: {hz_inner:.2f} AU)")
    else:
        deficit = min(35, 35 * (orbital_distance_au - hz_outer) / hz_outer)
        score += max(0, 35 - deficit * 2)
        factors.append(f"Too far from star — outside habitable zone (HZ outer: {hz_outer:.2f} AU)")

    # Planet size (max 25 pts) — super-Earth window 0.5–1.8 R⊕
    if 0.5 <= planet_radius_earth <= 1.8:
        score += 25
        factors.append("Planetary radius in the super-Earth/Earth-like window")
    elif 1.8 < planet_radius_earth <= 3.5:
        score += 12
        factors.append("Mini-Neptune radius — may retain thick H₂ envelope")
    else:
        score += 3
        factors.append("Planetary radius outside likely rocky-planet range")

    # Mass / gravity (max 15 pts)
    if 0.3 <= planet_mass_earth <= 5.0:
        score += 15
        factors.append("Mass compatible with retaining a thin atmosphere")
    elif 5.0 < planet_mass_earth <= 10.0:
        score += 7
        factors.append("Super-Earth mass — higher gravity, may still be habitable")
    else:
        score += 2

    # Stellar type (max 15 pts)
    if 4500 <= stellar_temperature_k <= 7000:
        score += 15
        factors.append("Host star in stable K/G spectral class — favourable for life")
    elif 3000 <= stellar_temperature_k < 4500:
        score += 8
        factors.append("M-dwarf host — potential tidal locking and flare risk")
    elif stellar_temperature_k > 7000:
        score += 5
        factors.append("Hot host star — elevated UV radiation environment")

    # Atmosphere bonus (10 pts)
    if has_atmosphere:
        score += 10
        factors.append("Atmosphere detected/assumed — greenhouse and UV shielding possible")
    else:
        factors.append("No atmosphere detected — surface liquid water unlikely")

    score = min(100, max(0, score))

    if score >= 75:
        label = "Potentially Habitable"
    elif score >= 50:
        label = "Marginally Habitable"
    elif score >= 25:
        label = "Unlikely Habitable"
    else:
        label = "Uninhabitable"

    return round(score, 1), label, factors


# ── Spectral Decoding ─────────────────────────────────────────────────────────

SPECTRAL_TEMP: dict[str, tuple[float, float]] = {
    "O": (30000, 50000),
    "B": (10000, 30000),
    "A": (7500,  10000),
    "F": (6000,   7500),
    "G": (5200,   6000),
    "K": (3700,   5200),
    "M": (2400,   3700),
    "L": (1300,   2400),
    "T": (700,    1300),
}


def decode_spectral_class(spectral_class: str) -> float:
    """Estimate temperature from spectral class string like 'G2V'."""
    letter = spectral_class[0].upper()
    subtype = 5.0
    for ch in spectral_class[1:]:
        if ch.isdigit():
            subtype = float(ch)
            break
    t_range = SPECTRAL_TEMP.get(letter, (5000, 6000))
    fraction = subtype / 9.0
    return t_range[1] - fraction * (t_range[1] - t_range[0])


def recession_velocity(redshift: float) -> float:
    """v = z × c  (non-relativistic, km/s)"""
    c = 299_792.458  # km/s
    return redshift * c
