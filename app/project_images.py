"""
project_images.py — Curated image configuration for the Projects section
-------------------------------------------------------------------------
Each project is keyed by its `order` number (integer, matches MongoDB field).

IMAGE TYPES:
  "food_fallback"    – High-quality representative food/concept image.
                       Used when no verified business photo is available.
  "exact_business"   – Verified photo of the actual business (add manually
                       when you have the owner's real photo).

IMAGE SOURCE:
  All fallback images use stable Unsplash CDN photo IDs.
  Format: https://images.unsplash.com/photo-<id>?w=600&q=80&fit=crop&auto=format

  Attribution: Photos from Unsplash (unsplash.com) – free to use under the
  Unsplash License. Photographer credit shown on image hover via title attribute.

REVERSIBILITY:
  Set IMAGE_SELECTION_ENABLED=false in .env to disable ALL image selection
  and immediately fall back to the grey placeholder for every project.

ADDING A REAL BUSINESS PHOTO:
  1. Upload the image to app/static/images/projects/  (e.g. noodle_house.jpg)
  2. Change image_type to "exact_business"
  3. Change image_url to "/static/images/projects/noodle_house.jpg"
  4. Change image_source to "Owner provided"
"""

# ---------------------------------------------------------------------------
# Curated per-project image data  (keyed by project `order` number)
# ---------------------------------------------------------------------------
PROJECT_IMAGES = {

    # ── 1. Noodle House — Mayajaal Cinemas, ECR, Uthandi ──────────────────
    # Cinema-dining noodle outlet  → high-energy Asian noodle dish
    1: {
        "image_url":    "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=600&q=80&fit=crop&auto=format",
        "image_alt":    "Steaming noodle dish — Noodle House, Mayajaal",
        "image_credit": "Photo by Engin Akyurt on Unsplash",
        "image_type":   "food_fallback",
        "image_source": "Unsplash",
        "original_image": None,
    },

    # ── 2. The Padington Club — Nandanam ──────────────────────────────────
    # Hospitality / beverage-focused club  → premium cocktail bar interior
    2: {
        "image_url":    "https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=600&q=80&fit=crop&auto=format",
        "image_alt":    "Premium cocktail bar interior — The Padington Club, Nandanam",
        "image_credit": "Photo by Ambitious Creative Co. on Unsplash",
        "image_type":   "food_fallback",
        "image_source": "Unsplash",
        "original_image": None,
    },

    # ── 3. Episode 23 Bistro — Anna Nagar ─────────────────────────────────
    # Bistro concept with menu engineering  → modern bistro fine dining
    3: {
        "image_url":    "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&q=80&fit=crop&auto=format",
        "image_alt":    "Modern bistro dining interior — Episode 23 Bistro, Anna Nagar",
        "image_credit": "Photo by Shawnanggg on Unsplash",
        "image_type":   "food_fallback",
        "image_source": "Unsplash",
        "original_image": None,
    },

    # ── 4. Fika Café — Adyar (Pre-Opening) ────────────────────────────────
    # Café planning → specialty coffee & café ambience
    4: {
        "image_url":    "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=600&q=80&fit=crop&auto=format",
        "image_alt":    "Cosy café with specialty coffee — Fika Café, Adyar",
        "image_credit": "Photo by Nathan Dumlao on Unsplash",
        "image_type":   "food_fallback",
        "image_source": "Unsplash",
        "original_image": None,
    },

    # ── 5. Sola Resto Bar — Pondicherry ───────────────────────────────────
    # Restaurant & bar  → vibrant resto-bar / craft cocktails
    5: {
        "image_url":    "https://images.unsplash.com/photo-1470337458703-46ad1756a187?w=600&q=80&fit=crop&auto=format",
        "image_alt":    "Vibrant restaurant bar — Sola Resto Bar, Pondicherry",
        "image_credit": "Photo by Patrick Fore on Unsplash",
        "image_type":   "food_fallback",
        "image_source": "Unsplash",
        "original_image": None,
    },

    # ── 6. Mantra Restaurant — Kuala Lumpur, Malaysia ─────────────────────
    # International Indian restaurant  → Indian spice / fine-dining spread
    6: {
        "image_url":    "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=600&q=80&fit=crop&auto=format",
        "image_alt":    "Indian fine-dining spread — Mantra Restaurant, Kuala Lumpur",
        "image_credit": "Photo by Raman on Unsplash",
        "image_type":   "food_fallback",
        "image_source": "Unsplash",
        "original_image": None,
    },

    # ── 7. Sam's Kitchen Catering — Ipoh, Malaysia ────────────────────────
    # High-volume catering service  → professional catering buffet setup
    7: {
        "image_url":    "https://images.unsplash.com/photo-1555244162-803834f70033?w=600&q=80&fit=crop&auto=format",
        "image_alt":    "Professional catering buffet — Sam's Kitchen, Ipoh",
        "image_credit": "Photo by Brooke Lark on Unsplash",
        "image_type":   "food_fallback",
        "image_source": "Unsplash",
        "original_image": None,
    },

    # ── 8. Radha's Restaurant — Kuala Lumpur, Malaysia ────────────────────
    # Multi-cuisine restaurant  → colourful multi-dish spread
    8: {
        "image_url":    "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=600&q=80&fit=crop&auto=format",
        "image_alt":    "Multi-cuisine dining spread — Radha's Restaurant, Kuala Lumpur",
        "image_credit": "Photo by Jodie Morgan on Unsplash",
        "image_type":   "food_fallback",
        "image_source": "Unsplash",
        "original_image": None,
    },
}

# ---------------------------------------------------------------------------
# CSS gradient fallback (shown if the image URL fails to load)
# Keyed by order number — matches the card's pastel colour palette
# ---------------------------------------------------------------------------
FALLBACK_GRADIENTS = {
    1: "linear-gradient(135deg, #FFE4CC 0%, #FFD0AA 100%)",
    2: "linear-gradient(135deg, #CCE0FF 0%, #AACCFF 100%)",
    3: "linear-gradient(135deg, #E0CCFF 0%, #CCAAFF 100%)",
    4: "linear-gradient(135deg, #CCFFE8 0%, #AAFFD0 100%)",
    5: "linear-gradient(135deg, #FFF0CC 0%, #FFE0AA 100%)",
    6: "linear-gradient(135deg, #CCF0FF 0%, #AADEFF 100%)",
    7: "linear-gradient(135deg, #F0CCFF 0%, #E0AAFF 100%)",
    8: "linear-gradient(135deg, #CCFFDD 0%, #AAFFCC 100%)",
}


def enrich_project(project: dict) -> dict:
    """
    Non-destructively add image fields to a project dict.
    Original fields are NEVER modified.
    Returns a new dict with added image keys.
    """
    order = project.get("order", 0)
    img   = PROJECT_IMAGES.get(order)

    enriched = dict(project)               # shallow copy — originals preserved

    if img:
        enriched["projectImage"]   = img["image_url"]
        enriched["imageAlt"]       = img["image_alt"]
        enriched["imageCredit"]    = img["image_credit"]
        enriched["imageType"]      = img["image_type"]
        enriched["imageSource"]    = img["image_source"]
        enriched["originalImage"]  = img["original_image"]
        enriched["fallbackGradient"] = FALLBACK_GRADIENTS.get(order, "linear-gradient(135deg,#e0e0d8,#d4d4cc)")
    else:
        enriched["projectImage"]     = None
        enriched["imageType"]        = "original"
        enriched["fallbackGradient"] = FALLBACK_GRADIENTS.get(order, "linear-gradient(135deg,#e0e0d8,#d4d4cc)")

    return enriched
