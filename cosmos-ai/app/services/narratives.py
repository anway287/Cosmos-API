"""
Template-driven astronomy narratives.
All text is generated from real calculated values — no API keys needed.
"""
import math

# ── Stellar narratives ────────────────────────────────────────────────────────

_FUSION_CYCLE = {
    "O": "the CNO cycle dominates overwhelmingly, burning through hydrogen in mere millions of years",
    "B": "the CNO cycle dominates, with blazing luminosity that will exhaust its fuel in tens of millions of years",
    "A": "a mix of the proton-proton chain and CNO cycle sustains its white brilliance",
    "F": "primarily the proton-proton chain, with CNO becoming increasingly important",
    "G": "the proton-proton chain — the same slow, steady reaction powering our own Sun",
    "K": "the proton-proton chain in a slow, miserly burn that can last tens of billions of years",
    "M": "the proton-proton chain at a glacial pace — these stars outlive everything in the universe",
}

_COLOR_DESC = {
    "O": "blazing blue-violet",
    "B": "brilliant blue-white",
    "A": "pure white",
    "F": "warm yellow-white",
    "G": "golden yellow",
    "K": "deep orange",
    "M": "dim crimson red",
}

_END_FATE = {
    "white dwarf": "It will shed its outer layers as a beautiful planetary nebula, leaving behind a white dwarf — a crystallising ember the size of Earth that will glow for trillions of years.",
    "neutron star": "At end of life it will detonate in a core-collapse supernova, the brightest event in its galaxy, leaving a neutron star — city-sized, but more massive than the Sun.",
    "black hole": "When its iron core collapses, nothing can stop it. A black hole will form — a point of infinite density wrapped in an event horizon from which not even light escapes.",
    "brown dwarf": "It never ignited sustained hydrogen fusion. It will simply cool and fade over trillions of years, a failed star slowly dimming into darkness.",
    "red giant": "In its twilight, it will balloon into a red giant, engulfing inner planets, before gently expelling a planetary nebula and retiring as a white dwarf.",
    "supernova": "This massive star is destined for a violent supernova explosion, forging heavy elements — gold, uranium, iron — and scattering them across the galaxy.",
}

_FUN_FACTS = {
    "O": "O-type stars are so rare that fewer than 0.00003% of all stars are this type, yet they produce most of the galaxy's UV radiation.",
    "B": "The blue-white glow of B stars comes from helium being ionised at their surface — too hot for most atoms to hold their electrons.",
    "A": "Vega, the star used to calibrate telescope brightness for decades, is an A-type star spinning so fast it bulges at its equator.",
    "F": "F-type stars like Procyon are in the 'sweet spot' for stellar lifetimes — long enough for complex life, bright enough to warm their worlds well.",
    "G": "Our G2-type Sun has so far consumed about half its hydrogen — it has roughly 5 billion years remaining on the main sequence.",
    "K": "K-type orange dwarfs may be the best stars for life: more stable than G stars, longer-lived, and with a habitable zone less threatened by flares.",
    "M": "The most common stars in the Milky Way — about 70% of all stars are M dwarfs — yet not a single one is visible to the naked eye from Earth.",
}

_HR_COMPARE = {
    "main sequence": "It sits on the hydrogen-burning Main Sequence of the Hertzsprung-Russell diagram — the stable, middle-aged phase of a star's life.",
    "giant": "It has left the main sequence and ascended the Giant Branch, its core now contracting while its outer envelope swells enormously.",
    "supergiant": "It blazes in the top of the HR diagram — a Supergiant — among the most luminous and short-lived objects in the galaxy.",
    "white dwarf": "It occupies the lower-left of the HR diagram as a White Dwarf: hot but tiny, the cooling remnant of a once-active star.",
    "brown dwarf": "It sits below the main sequence as a Brown Dwarf — not quite a star, not quite a planet, radiating heat from gravitational contraction.",
}


def stellar_narrative(metrics: dict, name) -> str:
    sc = metrics["spectral_class"]
    letter = sc[0].upper() if sc else "G"
    stage_lower = metrics["current_stage"].lower()
    lum = metrics.get("luminosity_solar", 1.0)
    temp = metrics.get("temperature_k", 5778)
    radius = metrics["radius_solar"]
    ms_life = metrics["main_sequence_lifetime_gyr"]
    next_s = metrics["next_stage"].lower()
    remaining = metrics.get("time_remaining_gyr")

    star_name = name or "this star"
    color = _COLOR_DESC.get(letter, "yellow")
    fusion = _FUSION_CYCLE.get(letter, _FUSION_CYCLE["G"])

    # HR diagram region
    if "giant" in stage_lower and "super" in stage_lower:
        hr_label = "supergiant"
    elif "giant" in stage_lower:
        hr_label = "giant"
    elif "white dwarf" in stage_lower:
        hr_label = "white dwarf"
    elif "brown" in stage_lower:
        hr_label = "brown dwarf"
    else:
        hr_label = "main sequence"
    hr_phrase = _HR_COMPARE.get(hr_label, _HR_COMPARE["main sequence"])

    # Size comparison
    if radius < 0.3:
        size_phrase = f"At just {radius:.2f} R☉, it is a tiny fraction of the Sun's size"
    elif radius < 0.9:
        size_phrase = f"Slightly smaller than the Sun at {radius:.2f} R☉"
    elif radius < 1.1:
        size_phrase = f"Nearly identical in size to the Sun at {radius:.2f} R☉"
    elif radius < 5:
        size_phrase = f"About {radius:.1f} times larger than the Sun"
    elif radius < 100:
        size_phrase = f"A giant at {radius:.0f} solar radii — if placed at the Sun's position, it would engulf the inner planets"
    else:
        size_phrase = f"A colossus spanning {radius:.0f} solar radii — large enough to swallow the entire inner Solar System"

    # Luminosity comparison
    if lum < 0.01:
        lum_phrase = f"a thousand times dimmer than the Sun ({lum:.4f} L☉)"
    elif lum < 0.1:
        lum_phrase = f"much fainter than the Sun ({lum:.3f} L☉)"
    elif lum < 2:
        lum_phrase = f"similar in brightness to the Sun ({lum:.2f} L☉)"
    elif lum < 100:
        lum_phrase = f"{lum:.1f} times more luminous than the Sun"
    else:
        lum_phrase = f"an extraordinary {lum:,.0f} times more luminous than the Sun"

    # Fate
    fate = ""
    if "white dwarf" in next_s:
        fate = _END_FATE["white dwarf"]
    elif "black hole" in next_s:
        fate = _END_FATE["black hole"]
    elif "neutron" in next_s:
        fate = _END_FATE["neutron star"]
    elif "supernova" in next_s:
        fate = _END_FATE["supernova"]
    else:
        fate = _END_FATE["red giant"]

    # Remaining time sentence
    if remaining:
        if remaining > 1:
            time_phrase = f"With roughly {remaining:.1f} billion years remaining in this phase,"
        else:
            time_phrase = f"With only {remaining*1000:.0f} million years remaining,"
    else:
        time_phrase = "Already past its productive hydrogen-burning phase,"

    narrative = (
        f"{star_name.capitalize()} shines as a {color} {sc}-type star, {lum_phrase}. "
        f"{size_phrase}, with a searing surface of {temp:,.0f} K. "
        f"{hr_phrase} "
        f"Its energy comes from {fusion}. "
        f"The total main-sequence lifetime for a star of this mass and luminosity is {ms_life:.2f} Gyr. "
        f"{time_phrase} its evolutionary path leads toward: {metrics['next_stage']}. "
        f"{fate}"
    )
    return narrative


def stellar_fun_fact(spectral_class: str) -> str:
    letter = spectral_class[0].upper() if spectral_class else "G"
    return _FUN_FACTS.get(letter, _FUN_FACTS["G"])


# ── Constellation narratives ──────────────────────────────────────────────────

CONST_MYTHS: dict[str, str] = {
    "Orion": "In Greek myth, Orion was the greatest hunter who ever lived, companion of Artemis and son of Poseidon. He boasted he would kill every beast on Earth, so Gaia sent a scorpion to sting him — which is why Orion and Scorpius are never in the sky at the same time.",
    "Andromeda": "Princess Andromeda was chained to a rock as a sacrifice to the sea monster Cetus, punishment for her mother Cassiopeia's vanity. Perseus, returning on Pegasus with the severed head of Medusa, slew the monster and claimed her hand in marriage.",
    "Cassiopeia": "Queen Cassiopeia of Ethiopia boasted her daughter was more beautiful than the sea nymphs, enraging Poseidon. As punishment she was placed in the sky where she endlessly circles the pole, sometimes hanging upside down — her eternal humiliation.",
    "Scorpius": "Orion and Scorpius are forever separated in the sky — the scorpion that slew the hunter. As one rises in the east, the other sets in the west, the two enemies never meeting across the vault of heaven.",
    "Sagittarius": "The centaur Chiron, wisest of his kind and tutor of heroes, points his arrow toward the heart of the Milky Way — toward the very centre of our galaxy, where a supermassive black hole of 4 million solar masses lurks.",
    "Leo": "The Nemean Lion, first labour of Hercules. Its hide was impervious to weapons — Hercules strangled it with his bare hands. Zeus placed it among the stars to commemorate the hero's triumph.",
    "Virgo": "Demeter, goddess of the harvest, mourning the abduction of her daughter Persephone to the underworld. When she mourns, winter comes. When Persephone returns, spring follows. The bright star Spica represents a sheaf of wheat in her hand.",
    "Lyra": "Orpheus, the greatest musician ever born, whose lyre could charm animals, trees, and rivers. When his wife Eurydice died, his music was so moving that Hades permitted him to lead her from the underworld — but he looked back, and lost her forever.",
    "Cygnus": "Zeus disguised himself as a swan to court Leda, queen of Sparta. Their union produced two divine eggs — from one hatched the twins Castor and Pollux, from the other, Helen of Troy, whose face launched a thousand ships.",
    "Perseus": "The hero Perseus who slew the Gorgon Medusa and rescued Andromeda. He wears Medusa's severed head at his belt — represented by the 'Demon Star' Algol, which dims every 2.87 days as a companion star eclipses it, just as the eyes of Medusa still pulse with eerie power.",
    "Ursa Major": "Zeus transformed his lover Callisto into a bear to hide her from Hera's jealousy. Her son Arcas nearly hunted her before Zeus intervened, sweeping them both into the sky by their tails — explaining why bear tails are so implausibly long in the stars.",
    "Taurus": "Zeus transformed into a magnificent white bull to abduct Europa, princess of Phoenicia. The Pleiades cluster represents the seven daughters of Atlas, pursued by Orion across the sky for seven years until Zeus took mercy and placed them among the stars.",
    "Aquarius": "Ganymede, a beautiful Trojan youth, was abducted by Zeus in the form of an eagle to serve as cup-bearer to the gods. He eternally pours the water of immortality from a great urn across the sky.",
    "Gemini": "The twin brothers Castor and Pollux — one mortal, one divine. When Castor died, Pollux was so grief-stricken that Zeus allowed them to share immortality, spending alternate days in Olympus and in the underworld, forever together.",
    "Hercules": "The greatest hero of antiquity, Heracles was plagued by Hera throughout his life. The constellation shows him kneeling — performing one of his famous Twelve Labours, wielding his club against monsters that threatened the gods and men alike.",
}

CONST_BEST_MONTH: dict[str, str] = {
    "Andromeda": "November", "Aquarius": "October", "Aquila": "September",
    "Aries": "December", "Auriga": "February", "Bootes": "June",
    "Cancer": "March", "Canis Major": "February", "Canis Minor": "March",
    "Capricornus": "September", "Cassiopeia": "November", "Centaurus": "May",
    "Cetus": "December", "Corona Borealis": "July", "Corvus": "May",
    "Cygnus": "September", "Draco": "July", "Eridanus": "December",
    "Gemini": "February", "Hercules": "July", "Hydra": "April",
    "Leo": "April", "Leo Minor": "April", "Lepus": "February",
    "Libra": "June", "Lupus": "June", "Lyra": "August",
    "Monoceros": "February", "Ophiuchus": "July", "Orion": "January",
    "Pegasus": "October", "Perseus": "December", "Pisces": "November",
    "Piscis Austrinus": "October", "Sagittarius": "August", "Scorpius": "July",
    "Serpens": "July", "Taurus": "January", "Triangulum": "December",
    "Ursa Major": "April", "Ursa Minor": "June", "Virgo": "May",
    "Vulpecula": "September", "Columba": "February", "Fornax": "December",
}

CONST_HEMISPHERE: dict[str, str] = {
    "Centaurus": "Southern", "Lupus": "Southern", "Corvus": "Southern",
    "Hydra": "Both", "Virgo": "Both", "Leo": "Both",
    "Orion": "Both", "Canis Major": "Both", "Gemini": "Northern",
    "Ursa Major": "Northern", "Ursa Minor": "Northern", "Cassiopeia": "Northern",
    "Perseus": "Northern", "Auriga": "Northern", "Cygnus": "Northern",
    "Lyra": "Northern", "Hercules": "Northern", "Draco": "Northern",
    "Sagittarius": "Both", "Scorpius": "Both", "Aquila": "Both",
    "Taurus": "Both", "Aries": "Both", "Pisces": "Both",
    "Andromeda": "Northern", "Pegasus": "Northern", "Bootes": "Northern",
}

_DEFAULT_MYTH = (
    "Ancient sky-watchers across cultures traced their stories into these stars — "
    "connecting dots of light into heroes, animals, and gods that gave meaning to the night sky "
    "long before telescopes revealed the true nature of the cosmos."
)


def constellation_narrative(name: str, notable: list[str]) -> str:
    myth = CONST_MYTHS.get(name, _DEFAULT_MYTH)
    if notable:
        top = notable[0]
        objects_note = (
            f" Look for {top} within this region — "
            "binoculars reveal fuzzy patches that resolve into millions of stars through a telescope."
            if "cluster" in top.lower() or "nebula" in top.lower()
            else f" The standout target here is {top}, a rewarding sight in any telescope."
        )
    else:
        objects_note = " This region of sky is best appreciated with a wide-field view under dark skies."
    return myth + objects_note


# ── Exoplanet summaries ───────────────────────────────────────────────────────

def exoplanet_summary(
    planet_name: str,
    score: float,
    label: str,
    eq_temp: float,
    esi: float,
    in_zone: bool,
    factors: list[str],
    radius: float,
    mass: float,
    stellar_temp: float,
) -> str:
    # Surface conditions
    if eq_temp < 180:
        temp_desc = "bitterly cold, well below the freezing point of CO₂"
    elif eq_temp < 273:
        temp_desc = "cold — liquid water could exist only with a strong greenhouse effect"
    elif eq_temp < 320:
        temp_desc = "temperate, potentially compatible with liquid water on the surface"
    elif eq_temp < 400:
        temp_desc = "warm to hot — a runaway greenhouse effect is a real risk"
    else:
        temp_desc = "extremely hot, likely above the boiling point of water"

    # Size description
    if radius < 0.8:
        size_desc = "smaller than Earth, likely with thin or no atmosphere"
    elif radius < 1.25:
        size_desc = "Earth-sized — a strong candidate for a rocky surface"
    elif radius < 2.0:
        size_desc = "a super-Earth, possibly rocky with a thick atmosphere"
    elif radius < 4.0:
        size_desc = "a mini-Neptune, probably dominated by gas or deep ocean"
    else:
        size_desc = "a gas giant — a rocky surface is unlikely"

    # Star suitability
    if 4500 <= stellar_temp <= 7000:
        star_desc = "Its host star is a stable G or K dwarf — an encouraging sign for long-term habitability."
    elif stellar_temp < 4500:
        star_desc = "Its host is an M or K dwarf — long-lived but prone to intense UV flares that can strip atmospheres."
    else:
        star_desc = "Its host is a hot, short-lived star — the window for life to develop may be very narrow."

    zone_phrase = (
        "It sits within the classical habitable zone where liquid water could theoretically exist on the surface."
        if in_zone else
        "It falls outside the traditional habitable zone — liquid surface water seems unlikely without exotic conditions."
    )

    conclusion = {
        "Potentially Habitable":  f"{planet_name} is one of the more promising worlds we know of. With a habitability score of {score:.0f}/100 and ESI of {esi:.3f}, it warrants high-priority follow-up with next-generation telescopes like the ELT or a future flagship mission.",
        "Marginally Habitable":   f"{planet_name} is a borderline case. Some conditions favour habitability, others don't. A score of {score:.0f}/100 means it shouldn't be dismissed — edge cases sometimes surprise us.",
        "Unlikely Habitable":     f"{planet_name} scores {score:.0f}/100. Life as we know it would struggle here, though extremophile-like organisms cannot be entirely ruled out in subsurface environments.",
        "Uninhabitable":          f"With a score of {score:.0f}/100, {planet_name} is almost certainly hostile to any form of life we can conceive of with current understanding.",
    }.get(label, f"Score: {score:.0f}/100.")

    return (
        f"{planet_name} is {size_desc}, with an equilibrium temperature that is {temp_desc} ({eq_temp:.0f} K). "
        f"{zone_phrase} "
        f"{star_desc} "
        f"{conclusion}"
    )
