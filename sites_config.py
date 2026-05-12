# =============================================================================
#  SITE REGISTRY — Vertu Motors
#  Edit this file to add, remove or update dealerships.
#
#  TO ADD A NEW SITE:
#    Copy one of the entries below, paste it at the bottom of SITES,
#    update the fields and save. That's it — the report picks it up automatically.
#
#  FIELDS:
#    id       - short unique key, no spaces (used internally)
#    name     - full dealership name as it appears in the report
#    address  - optional address shown under the site name
#    arc      - which ARC monitors this site (key from ARC_CENTRES below)
#    active   - set False to exclude from reports without deleting the entry
#
#  TO ADD A NEW ARC: add a new key/label to ARC_CENTRES below.
#  ARC names are internal only — they never appear in the client report.
#
# =============================================================================

ARC_CENTRES = {
    "arc1": "ARC 1",   # Internal label — not shown to client
    "arc2": "ARC 2",   # Replace value with second ARC name when confirmed
}

SITES = [
    {
        "id":      "yeovil_volvo",
        "name":    "Yeovil Volvo (Vertu)",
        "address": "",
        "arc":     "arc1",
        "active":  True,
    },
    {
        "id":      "plymouth_volvo",
        "name":    "Plymouth Volvo (Vertu)",
        "address": "",
        "arc":     "arc1",
        "active":  True,
    },
    {
        "id":      "plymouth_renault",
        "name":    "Plymouth Renault LCV (Vertu)",
        "address": "Ridgeway, PL7 1AJ",
        "arc":     "arc1",
        "active":  True,
    },
    {
        "id":      "yeovil_valet",
        "name":    "Yeovil BMW Valet (Vertu)",
        "address": "",
        "arc":     "arc1",
        "active":  True,
    },
    {
        "id":      "carlisle",
        "name":    "Carlisle Vauxhall (Vertu)",
        "address": "",
        "arc":     "arc1",
        "active":  True,
    },
    {
        "id":      "hereford_audi",
        "name":    "Hereford Audi (Vertu)",
        "address": "",
        "arc":     "arc1",
        "active":  True,
    },
    {
        "id":      "skoda_leicester",
        "name":    "Skoda Leicester (Vertu)",
        "address": "",
        "arc":     "arc1",
        "active":  True,
    },
    {
        "id":      "nottingham_storage",
        "name":    "Nottingham Storage (Vertu)",
        "address": "",
        "arc":     "arc1",
        "active":  True,
    },
    {
        "id":      "ferrari_exeter",
        "name":    "Ferrari Exeter (Vertu)",
        "address": "Sigford Road, EX2 8NL",
        "arc":     "arc1",
        "active":  True,
    },
    {
        "id":      "chesterfield_pdi",
        "name":    "Chesterfield PDI (Vertu)",
        "address": "",
        "arc":     "arc1",
        "active":  True,
    },
    {
        "id":      "exeter_jlr",
        "name":    "Exeter Land Rover (Vertu)",
        "address": "",
        "arc":     "arc1",
        "active":  True,
    },
    {
        "id":      "exeter_volvo",
        "name":    "Exeter Volvo (Vertu)",
        "address": "",
        "arc":     "arc1",
        "active":  True,
    },
    {
        "id":      "chesterfield_jlr",
        "name":    "Chesterfield JLR (Vertu)",
        "address": "",
        "arc":     "arc1",
        "active":  True,
    },

    # ── ADD NEW SITES HERE ────────────────────────────────────────────────────
    # {
    #     "id":      "bristol_bmw",
    #     "name":    "Bristol BMW (Vertu)",
    #     "address": "Cribbs Causeway, BS10 7TU",
    #     "arc":     "arc1",
    #     "active":  True,
    # },
]
