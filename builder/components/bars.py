"""
Modulo Componente: 14 - Mana Bar & 16 - Castbar
================================================
Gestisce le barre centrali sincronizzate a 278px di larghezza:
1. 14 - Mana Bar (278x14px a y = -20):
   - Barra percentuale del mana con cambio colore dinamico in rosso se mana <= 20%.
   - Testo centrale: % mana con due decimali (%1.percentpower%%).
2. 16 - Castbar (278x20px a y = +8):
   - Barra di lancio nativa WeakAuras (texture Blizzard, colore azzurro [0.0, 0.77, 1.0]).
   - Mostra il nome dell'incantesimo a sinistra (%n) e il tempo rimanente a destra (%p).
   - Icona della spell attiva a sinistra (icon: True, icon_side: LEFT, iconSource: -1).
"""
from builder.core.helpers import make_subtext
from builder.core.constants import TEXTURE_STATUSBAR


def build_bars_auras() -> list[dict]:
    """
    Costruisce e restituisce le 2 barre principali dell'HUD:
    - 14 - Mana Bar (Aurabar)
    - 16 - Castbar (Aurabar)
    """
    return [
        # =====================================================================
        # 14 - MANA BAR
        # =====================================================================
        {
            "id": "14 - Mana Bar",
            "uid": "FMHUD_MANABAR",
            "parent": "Class Mage (TTW Fire)",
            "regionType": "aurabar",
            "internalVersion": 52,
            "width": 278,
            "height": 14,
            "xOffset": 0,
            "yOffset": -20,
            "barColor": [0.09, 0.55, 1.0, 1.0],
            "backgroundColor": [0.1, 0.1, 0.1, 0.8],
            "texture": TEXTURE_STATUSBAR,
            "displayText_format_1.percentpower_format": "Number",
            "displayText_format_1.percentpower_decimal_precision": 2,
            "triggers": {
                1: {
                    "trigger": {
                        "type": "unit",
                        "event": "Power",
                        "unit": "player",
                        "powertype": 0,
                        "use_powertype": True,
                        "use_unit": True,
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
            "conditions": [
                {
                    "check": {
                        "trigger": 1,
                        "op": "<=",
                        "variable": "percentpower",
                        "value": "20",
                    },
                    "changes": [
                        {
                            "property": "barColor",
                            "value": [1.0, 0.15, 0.15, 1.0],
                        }
                    ]
                }
            ],
            "subRegions": [
                make_subtext(
                    "%1.percentpower%%",
                    justify="CENTER",
                    anchor_point="CENTER",
                    font_size=10,
                    extra_props={
                        "text_selfPoint": "CENTER",
                        "text_text_format_1.percentpower_format": "Number",
                        "text_text_format_1.percentpower_decimal_precision": 2,
                    }
                ),
            ],
        },

        # =====================================================================
        # 16 - CASTBAR
        # =====================================================================
        {
            "id": "16 - Castbar",
            "uid": "FMHUD_CASTBAR",
            "parent": "Class Mage (TTW Fire)",
            "regionType": "aurabar",
            "internalVersion": 52,
            "width": 278,
            "height": 20,
            "xOffset": 0,
            "yOffset": 8,
            "barColor": [0.0, 0.77, 1.0, 1.0],
            "backgroundColor": [0.15, 0.15, 0.15, 0.8],
            "texture": "Blizzard",
            "icon": True,
            "icon_side": "LEFT",
            "iconSource": -1,
            "icon_color": [1, 1, 1, 1],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "unit",
                        "event": "Cast",
                        "unit": "player",
                        "use_unit": True,
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                make_subtext(
                    "%n",
                    justify="LEFT",
                    anchor_point="INNER_LEFT",
                    font_size=11,
                    x_offset=6,
                    extra_props={
                        "text_selfPoint": "AUTO",
                    }
                ),
                make_subtext(
                    "%p",
                    justify="RIGHT",
                    anchor_point="INNER_RIGHT",
                    font_size=11,
                    x_offset=-6,
                    extra_props={
                        "text_selfPoint": "AUTO",
                        "text_text_format_p_format": "timed",
                        "text_text_format_p_time_precision": 1,
                    }
                ),
            ],
        },
    ]
