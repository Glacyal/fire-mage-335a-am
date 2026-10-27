"""
Costruttore dell'Albero Gerarchico Completo WeakAuras (Class Mage (TTW Fire))
==========================================================================
Assembla i 7 componenti indipendenti sotto il gruppo master 'Class Mage (TTW Fire)',
applicando le condizioni di caricamento di classe e talento su tutti i nodi foglia.
"""
import copy
from builder.core.constants import FIRE_MAGE_LOAD
from builder.components import (
    build_procs_auras,
    build_buffs_auras,
    build_utility_auras,
    build_bars_auras,
    build_hotstreak_auras,
    build_alerts_auras,
    build_stats_auras,
    build_multi_lb_auras,
)


def build_wa_tree() -> dict:
    """
    Costruisce e restituisce l'albero gerarchico completo delle 43 aure per WeakAuras 4.0.0 (internalVersion 52).
    Assembla modularmente gli 8 componenti:
    1. Procs (Dynamic Group)
    2. Buffs (Molten Armor, Arcane Intellect, Focus Magic)
    3. Utility Row (Trinket 1, Trinket 2, Cloak, Tier 8, Gloves, Mana Gem, Combustion, Mirror Image, Boots)
    4. Bars (Mana Bar, Castbar)
    5. Hot Streak Bar (Background, Segment 1, Proc)
    6. Alerts (Hot Streak Alert)
    7. Stats Panel (Background, Text)
    8. Multi-Target Living Bomb (Dynamic Group, 5 Tracker)
    """
    data = {
        "m": "d",
        "v": 2000,
        "w": "4.0.0",
        "d": {
            "id": "Class Mage (TTW Fire)",
            "uid": "FMHUD_ROOT",
            "regionType": "group",
            "internalVersion": 52,
            "scale": 1.2,
            "xOffset": 0,
            "yOffset": -190,
            "anchorPoint": "CENTER",
            "selfPoint": "CENTER",
            "groupIcon": "Interface\\Icons\\Spell_Fire_FlameBolt",
            "displayIcon": "Interface\\Icons\\Spell_Fire_FlameBolt",
            "icon": "Interface\\Icons\\Spell_Fire_FlameBolt",
            "controlledChildren": [
                "01 - Procs",
                "02 - Molten Armor",
                "03 - Arcane Intellect",
                "04 - Focus Magic",
                "05 - Trinket 1",
                "06 - Trinket 2",
                "06b - Ring",
                "07 - Cloak",
                "08 - Tier 8",
                "09 - Gloves",
                "10 - Mana Gem",
                "11 - Combustion",
                "12 - Mirror Image",
                "13 - Boots",
                "14 - Mana Bar",
                "15 - Hot Streak Bar",
                "16 - Castbar",
                "17 - Alerts",
                "18 - Stats Panel",
                "19 - Multi-Target Living Bomb"
            ],
            "load": copy.deepcopy(FIRE_MAGE_LOAD)
        },
        "c": []
    }

    # Assemblaggio ordinato dei componenti
    data["c"].extend(build_procs_auras())
    data["c"].extend(build_buffs_auras())
    data["c"].extend(build_utility_auras())
    data["c"].extend(build_bars_auras())
    data["c"].extend(build_hotstreak_auras())
    data["c"].extend(build_alerts_auras())
    data["c"].extend(build_stats_auras())
    data["c"].extend(build_multi_lb_auras())

    # Applicazione uniforme delle condizioni di caricamento (Mage + Living Bomb)
    for item in data["c"]:
        item["load"] = copy.deepcopy(FIRE_MAGE_LOAD)

    return data
