"""
Modulo Componente: 01 - Procs (Dynamic Group)
=============================================
Gestisce la barra orizzontale dinamica superiore dei proc di combattimento (y = 52):
- Crescita orizzontale centrata (space = 6px, icone 34x34px).
- Include i seguenti proc e debuff attivi:
  1. Tier 10 (Pushing the Limit +12% Haste)
  2. Hot Streak (Icona attiva di proc con Pixel Glow)
  3. Clearcasting (Arcane Concentration)
  4. Living Bomb (Debuff sul target attuale con countdown)
  5. Pyroblast (Debuff DoT 12s sul target attuale con countdown)
  6. Ignite (Debuff sul target attuale con countdown)
  7. Scorch (Debuff sul target attuale con countdown)
  8. Molten Fury (Target <= 35% HP con Pixel Glow)
"""
from builder.core.helpers import make_subtext


def build_procs_auras() -> list[dict]:
    """
    Costruisce e restituisce le 9 aure del gruppo dinamico Procs:
    - 01 - Procs (Dynamic Group)
    - Tier 10, Hot Streak, Clearcasting, Living Bomb, Pyroblast, Ignite, Scorch, Molten Fury.
    """
    return [
        {
            "id": "01 - Procs",
            "uid": "FMHUD_PROCS_DG",
            "parent": "Class Mage (TTW Fire)",
            "regionType": "dynamicgroup",
            "internalVersion": 52,
            "grow": "HORIZONTAL",
            "align": "CENTER",
            "space": 6,
            "xOffset": 0,
            "yOffset": 52,
            "controlledChildren": [
                "Tier 10",
                "Hot Streak",
                "Clearcasting",
                "Living Bomb",
                "Pyroblast",
                "Ignite",
                "Scorch",
                "Molten Fury"
            ],
        },
        # Tier 10 (Pushing the Limit +12% Haste buff - Active on proc)
        {
            "id": "Tier 10",
            "uid": "FMHUD_TIER10_PROC",
            "parent": "01 - Procs",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Spell_Fire_ElementalDevastation",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": """function()
    for i = 1, 40 do
        local name, _, _, _, _, _, expirationTime, _, _, _, spellId = UnitBuff("player", i)
        if not name then break end
        if spellId == 70753 or spellId == 70752 or name == "Pushing the Limit" or name == "Oltre il Limite" or string.find(name, "Limit") or string.find(name, "Limite") then
            local rem = expirationTime and expirationTime > 0 and (expirationTime - GetTime()) or 0
            if rem > 0 then
                if rem <= 3 then
                    return string.format("|cFFFF4444%.1fs|r", rem)
                else
                    return string.format("%.0fs", rem)
                end
            end
        end
    end
    return ""
end""",
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "player",
                        "auranames": [
                            "Pushing the Limit",
                            "70753",
                            "70752",
                            "Oltre il Limite"
                        ],
                        "useName": True,
                        "debuffType": "HELPFUL",
                        "matchesShowOn": "showOnActive",
                        "ownOnly": True,
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=11),
                {
                    "type": "subglow",
                    "glow": True,
                    "glowType": "Pixel",
                    "glowLines": 8,
                    "glowFrequency": 0.25,
                    "glowLength": 10,
                    "glowThickness": 2,
                }
            ],
        },
        # Hot Streak (Active on proc)
        {
            "id": "Hot Streak",
            "uid": "FMHUD_HOTSTREAK",
            "parent": "01 - Procs",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Ability_Mage_HotStreak",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": """function()
    for i = 1, 40 do
        local name, _, _, _, _, _, expirationTime, _, _, _, spellId = UnitBuff("player", i)
        if not name then break end
        if spellId == 48108 or name == "Hot Streak" or name == "Buona sorte" or string.find(name, "Hot Streak") or string.find(name, "Buona") then
            local rem = expirationTime and expirationTime > 0 and (expirationTime - GetTime()) or 0
            if rem > 0 then
                if rem <= 3 then
                    return string.format("|cFFFF4444%.1fs|r", rem)
                else
                    return string.format("%.0fs", rem)
                end
            end
        end
    end
    return ""
end""",
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "player",
                        "auranames": [
                            "Hot Streak",
                            "48108",
                            "Buona sorte"
                        ],
                        "useName": True,
                        "debuffType": "HELPFUL",
                        "matchesShowOn": "showOnActive",
                        "ownOnly": True,
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=11),
                {
                    "type": "subglow",
                    "glow": True,
                    "glowType": "Pixel",
                    "glowLines": 8,
                    "glowFrequency": 0.25,
                    "glowLength": 10,
                    "glowThickness": 2,
                }
            ],
        },
        # Clearcasting / Arcane Concentration (Active on proc)
        {
            "id": "Clearcasting",
            "uid": "FMHUD_CLEARCASTING",
            "parent": "01 - Procs",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Spell_Shadow_ManaBurn",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": """function()
    for i = 1, 40 do
        local name, _, _, _, _, _, expirationTime, _, _, _, spellId = UnitBuff("player", i)
        if not name then break end
        if spellId == 12536 or name == "Clearcasting" or name == "Arcane Concentration" or name == "Lancio limpido" or name == "Concentrazione Arcana" or string.find(name, "Clearcasting") or string.find(name, "Limpido") or string.find(name, "Concentrat") then
            local rem = expirationTime and expirationTime > 0 and (expirationTime - GetTime()) or 0
            if rem > 0 then
                if rem <= 4 then
                    return string.format("|cFFFF4444%.1fs|r", rem)
                else
                    return string.format("%.0fs", rem)
                end
            end
        end
    end
    return ""
end""",
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "player",
                        "auranames": [
                            "Clearcasting",
                            "Arcane Concentration",
                            "Lancio limpido",
                            "Concentrazione Arcana",
                            "12536"
                        ],
                        "useName": True,
                        "debuffType": "HELPFUL",
                        "matchesShowOn": "showOnActive",
                        "ownOnly": True,
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=11),
                {
                    "type": "subglow",
                    "glow": True,
                    "glowType": "Pixel",
                    "glowLines": 8,
                    "glowFrequency": 0.25,
                    "glowLength": 10,
                    "glowThickness": 2,
                }
            ],
        },
        # Living Bomb (Target Debuff)
        {
            "id": "Living Bomb",
            "uid": "FMHUD_LIVINGBOMB",
            "parent": "01 - Procs",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Ability_Mage_LivingBomb",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": """function()
    if not UnitExists("target") then return "" end
    for i = 1, 40 do
        local name, _, _, _, _, _, expirationTime, unitCaster, _, _, spellId = UnitDebuff("target", i)
        if not name then break end
        if (unitCaster == "player" or not unitCaster) and (spellId == 55360 or spellId == 55359 or spellId == 44457 or name == "Living Bomb" or name == "Bomba Vivente" or string.find(name, "Living Bomb") or string.find(name, "Vivente")) then
            local rem = expirationTime and expirationTime > 0 and (expirationTime - GetTime()) or 0
            if rem > 0 then
                if rem <= 3 then
                    return string.format("|cFFFF4444%.1fs|r", rem)
                else
                    return string.format("%.0fs", rem)
                end
            end
        end
    end
    return ""
end""",
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "target",
                        "auranames": [
                            "Living Bomb",
                            "55360",
                            "55359",
                            "44457",
                            "Bomba Vivente"
                        ],
                        "useName": True,
                        "debuffType": "HARMFUL",
                        "matchesShowOn": "showOnActive",
                        "ownOnly": True,
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=11),
            ],
        },
        # Pyroblast (Target Debuff DoT - 12s)
        {
            "id": "Pyroblast",
            "uid": "FMHUD_PYROBLAST",
            "parent": "01 - Procs",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Spell_Fire_Fireball02",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": """function()
    if not UnitExists("target") then return "" end
    for i = 1, 40 do
        local name, _, _, _, _, _, expirationTime, unitCaster, _, _, spellId = UnitDebuff("target", i)
        if not name then break end
        if (unitCaster == "player" or not unitCaster) and (spellId == 42891 or spellId == 33938 or spellId == 27132 or name == "Pyroblast" or name == "Piroclasma" or string.find(name, "Pyroblast") or string.find(name, "Piroclasma")) then
            local rem = expirationTime and expirationTime > 0 and (expirationTime - GetTime()) or 0
            if rem > 0 then
                if rem <= 3 then
                    return string.format("|cFFFF4444%.1fs|r", rem)
                else
                    return string.format("%.0fs", rem)
                end
            end
        end
    end
    return ""
end""",
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "target",
                        "auranames": [
                            "Pyroblast",
                            "42891",
                            "33938",
                            "27132",
                            "Piroclasma"
                        ],
                        "useName": True,
                        "debuffType": "HARMFUL",
                        "matchesShowOn": "showOnActive",
                        "ownOnly": True,
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=11),
            ],
        },
        # Ignite (Target Debuff)
        {
            "id": "Ignite",
            "uid": "FMHUD_IGNITE",
            "parent": "01 - Procs",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Spell_Fire_Incinerate",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": """function()
    if not UnitExists("target") then return "" end
    for i = 1, 40 do
        local name, _, _, _, _, _, expirationTime, unitCaster, _, _, spellId = UnitDebuff("target", i)
        if not name then break end
        if (unitCaster == "player" or not unitCaster) and (spellId == 12654 or name == "Ignite" or name == "Ignizione" or string.find(name, "Ignite") or string.find(name, "Igniz")) then
            local rem = expirationTime and expirationTime > 0 and (expirationTime - GetTime()) or 0
            if rem > 0 then
                if rem <= 1.5 then
                    return string.format("|cFFFF4444%.1fs|r", rem)
                else
                    return string.format("%.1fs", rem)
                end
            end
        end
    end
    return ""
end""",
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "target",
                        "auranames": [
                            "Ignite",
                            "12654",
                            "Ignizione"
                        ],
                        "useName": True,
                        "debuffType": "HARMFUL",
                        "matchesShowOn": "showOnActive",
                        "ownOnly": True,
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=11),
            ],
        },
        # Scorch / Improved Scorch (Target Debuff)
        {
            "id": "Scorch",
            "uid": "FMHUD_SCORCH",
            "parent": "01 - Procs",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Spell_Fire_SoulBurn",
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": """function()
    if not UnitExists("target") then return "" end
    for i = 1, 40 do
        local name, _, _, _, _, duration, expirationTime, _, _, _, spellId = UnitDebuff("target", i)
        if not name then break end
        if spellId == 22959 or spellId == 12873 or spellId == 12872 or spellId == 17800 or name == "Improved Scorch" or name == "Scorch" or name == "Shadow and Flame" or string.find(name, "Scorch") or string.find(name, "Bruciatura") then
            local rem = expirationTime and expirationTime > 0 and (expirationTime - GetTime()) or 0
            if rem > 0 then
                if rem <= 5 then
                    return string.format("|cFFFF4444%.1fs|r", rem)
                else
                    return string.format("%.0fs", rem)
                end
            end
        end
    end
    return ""
end""",
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "event",
                        "events": "UNIT_AURA,PLAYER_TARGET_CHANGED,PLAYER_ENTERING_WORLD",
                        "custom": """function(event, ...)
    if not UnitExists("target") then return false end
    for i = 1, 40 do
        local name, _, _, _, _, duration, expirationTime, _, _, _, spellId = UnitDebuff("target", i)
        if not name then break end
        if spellId == 22959 or spellId == 12873 or spellId == 12872 or spellId == 17800 or name == "Improved Scorch" or name == "Scorch" or name == "Shadow and Flame" or string.find(name, "Scorch") or string.find(name, "Bruciatura") then
            return true
        end
    end
    return false
end""",
                        "customDuration": """function()
    if not UnitExists("target") then return 0, 0 end
    for i = 1, 40 do
        local name, _, _, _, _, duration, expirationTime, _, _, _, spellId = UnitDebuff("target", i)
        if not name then break end
        if spellId == 22959 or spellId == 12873 or spellId == 12872 or spellId == 17800 or name == "Improved Scorch" or name == "Scorch" or name == "Shadow and Flame" or string.find(name, "Scorch") or string.find(name, "Bruciatura") then
            return duration or 30, expirationTime or (GetTime() + 30)
        end
    end
    return 0, 0
end""",
                        "customIcon": """function()
    if not UnitExists("target") then return "Interface\\\\Icons\\\\Spell_Fire_SoulBurn" end
    for i = 1, 40 do
        local name, _, icon, _, _, _, _, _, _, _, spellId = UnitDebuff("target", i)
        if not name then break end
        if spellId == 22959 or spellId == 12873 or spellId == 12872 or spellId == 17800 or name == "Improved Scorch" or name == "Scorch" or name == "Shadow and Flame" or string.find(name, "Scorch") or string.find(name, "Bruciatura") then
            return icon or "Interface\\\\Icons\\\\Spell_Fire_SoulBurn"
        end
    end
    return "Interface\\\\Icons\\\\Spell_Fire_SoulBurn"
end""",
                    },
                    "untrigger": {
                        "custom": """function(event, ...)
    if not UnitExists("target") then return true end
    for i = 1, 40 do
        local name, _, _, _, _, duration, expirationTime, _, _, _, spellId = UnitDebuff("target", i)
        if not name then break end
        if spellId == 22959 or spellId == 12873 or spellId == 12872 or spellId == 17800 or name == "Improved Scorch" or name == "Scorch" or name == "Shadow and Flame" or string.find(name, "Scorch") or string.find(name, "Bruciatura") then
            return false
        end
    end
    return true
end"""
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=11),
            ],
        },
        # Molten Fury (Target <= 35% HP)
        {
            "id": "Molten Fury",
            "uid": "FMHUD_MOLTENFURY",
            "parent": "01 - Procs",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Spell_Fire_MoltenBlood",
            "auto": True,
            "color": [1, 1, 1, 1],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "event",
                        "events": "UNIT_HEALTH,UNIT_MAXHEALTH,PLAYER_TARGET_CHANGED,PLAYER_ENTERING_WORLD",
                        "custom": """function(event, ...)
    -- Filtro sull'unità: evita rivalutazioni inutili su ogni cambio di vita nel raid che non riguarda il bersaglio
    local unit = ...
    if (event == "UNIT_HEALTH" or event == "UNIT_MAXHEALTH") and unit ~= "target" then
        return _G.FMHUD_MF_Active == true
    end
    if not UnitExists("target") or UnitIsDeadOrGhost("target") or not UnitCanAttack("player", "target") then
        _G.FMHUD_MF_Active = false
        return false
    end
    local maxHP = UnitHealthMax("target") or 0
    if maxHP <= 0 then
        _G.FMHUD_MF_Active = false
        return false
    end
    local curHP = UnitHealth("target") or 0
    local isLow = ((curHP / maxHP) * 100) <= 35.0
    _G.FMHUD_MF_Active = isLow
    return isLow
end""",
                    },
                    "untrigger": {
                        "custom": """function(event, ...)
    -- Filtro sull'unità: evita rivalutazioni inutili su ogni cambio di vita nel raid che non riguarda il bersaglio
    local unit = ...
    if (event == "UNIT_HEALTH" or event == "UNIT_MAXHEALTH") and unit ~= "target" then
        return not _G.FMHUD_MF_Active
    end
    if not UnitExists("target") or UnitIsDeadOrGhost("target") or not UnitCanAttack("player", "target") then
        _G.FMHUD_MF_Active = false
        return true
    end
    local maxHP = UnitHealthMax("target") or 0
    if maxHP <= 0 then
        _G.FMHUD_MF_Active = false
        return true
    end
    local curHP = UnitHealth("target") or 0
    local isHigh = ((curHP / maxHP) * 100) > 35.0
    _G.FMHUD_MF_Active = not isHigh
    return isHigh
end"""
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("35%", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=11),
                {
                    "type": "subglow",
                    "glow": True,
                    "glowType": "Pixel",
                    "glowLines": 8,
                    "glowFrequency": 0.25,
                    "glowLength": 10,
                    "glowThickness": 2,
                }
            ],
        },
    ]
