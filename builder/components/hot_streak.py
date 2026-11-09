"""
Modulo Componente: 15 - Hot Streak Bar (Doppio Segmento Decoppiato)
===================================================================
Gestisce la barra orizzontale centrale di Hot Streak (sopra la barra del mana a y = -7):
1. Background Frame (278x7px)
2. Mezza Barra Sinistra (Segment 1 - 137x5px a x = -70.5):
   - Stato binario 0 o 1.
   - Traccia il 1° critico diretto (Fireball, Scorch, Fire Blast, Frostfire, Living Bomb esplosione).
   - Persistente nel tempo e fuori dal combattimento (non scade mai finché non si lancia un'altra spell).
   - Si azzera a 0 solo al 2° critico consecutivo (proc) o se il colpo andato a segno non è critico.
   - NON si azzera lanciando la Pyroblast o altre spell non qualificabili.
3. Mezza Barra Destra (Proc - 137x5px a x = +70.5):
   - Tracciamento nativo del buff Hot Streak (48108) con countdown 10s e Pixel Glow dorato.
   - Completamente indipendente dalla barra di sinistra (consente Rolling Hot Streak continuo).
"""
from builder.core.helpers import make_subtext
from builder.core.constants import TEXTURE_STATUSBAR, TEXTURE_WHITE8X8


# =============================================================================
# LOGICA LUA CONDIVISA: TRACCIAMENTO COMBAT LOG PERSISTENTE E DECOPPIATO
# =============================================================================
SHARED_HOTSTREAK_CHECK_LUA = r"""function(event, ...)
    _G.FMHUD_HS = _G.FMHUD_HS or {
        streak = 0,
        lastEventKey = nil,
    }
    local hs = _G.FMHUD_HS

    local f = _G.FMHUD_HSFrame
    if not f then
        f = CreateFrame("Frame")
        rawset(_G, "FMHUD_HSFrame", f)
        local playerGUID = UnitGUID("player")

        _G.FMHUD_QualifyingSpells = _G.FMHUD_QualifyingSpells or {
            [133]=true,[143]=true,[145]=true,[3140]=true,[8400]=true,[8401]=true,[8402]=true,[10148]=true,[10149]=true,[10150]=true,[10151]=true,[25306]=true,[27070]=true,[38692]=true,[42832]=true,[42833]=true, -- Fireball
            [2136]=true,[2137]=true,[2138]=true,[8412]=true,[8413]=true,[10197]=true,[10199]=true,[27078]=true,[27079]=true,[42872]=true,[42873]=true, -- Fire Blast
            [2948]=true,[8444]=true,[8445]=true,[8446]=true,[10205]=true,[10206]=true,[10207]=true,[27073]=true,[27074]=true,[42858]=true,[42859]=true, -- Scorch
            [44614]=true,[47610]=true, -- Frostfire Bolt
            [44461]=true,[55361]=true,[55362]=true,[44457]=true,[55359]=true,[55360]=true, -- Living Bomb
        }

        local function isQualifying(spellId, spellName)
            if spellId and _G.FMHUD_QualifyingSpells[spellId] then return true end
            if spellName then
                if string.find(spellName, "Fireball") or string.find(spellName, "Palla di Fuoco") or
                   string.find(spellName, "Fire Blast") or string.find(spellName, "Deflagrazione") or
                   string.find(spellName, "Scorch") or string.find(spellName, "Bruciatura") or
                   string.find(spellName, "Frostfire") or string.find(spellName, "Fuocogelo") or
                   string.find(spellName, "Living Bomb") or string.find(spellName, "Bomba Vivente") then
                    return true
                end
            end
            return false
        end

        local function notifyWA()
            if WeakAuras and WeakAuras.ScanEvents then
                WeakAuras.ScanEvents("FMHUD_HS_UPDATE")
            end
        end

        local function handleEvent(ev, ...)
            if ev == "PLAYER_ENTERING_WORLD" or ev == "PLAYER_DEAD" or ev == "PLAYER_UNGHOST" then
                hs.streak = 0
                notifyWA()
            elseif ev == "COMBAT_LOG_EVENT_UNFILTERED" then
                local subEvent = select(2, ...)
                if subEvent ~= "SPELL_DAMAGE" then return end

                local sourceGUID = select(3, ...)
                if not playerGUID then playerGUID = UnitGUID("player") end
                local isPlayer = (sourceGUID == playerGUID)
                if not isPlayer then
                    local sourceName = select(4, ...)
                    if sourceName and sourceName == UnitName("player") then
                        isPlayer = true
                    else
                        local sourceFlags = select(5, ...)
                        if sourceFlags and bit and bit.band and bit.band(sourceFlags, 0x00000001) > 0 then
                            isPlayer = true
                        end
                    end
                end
                if not isPlayer then return end

                local spellId = select(9, ...)
                local spellName = select(10, ...)
                if not isQualifying(spellId, spellName) then
                    spellId = select(10, ...)
                    spellName = select(11, ...)
                end

                if isQualifying(spellId, spellName) then
                    local timestamp = select(1, ...)
                    local destGUID = select(6, ...) or ""
                    local eventKey = tostring(timestamp) .. "_" .. tostring(spellId) .. "_" .. tostring(destGUID)

                    if hs.lastEventKey ~= eventKey then
                        hs.lastEventKey = eventKey

                        local c18, c19, c20 = select(18, ...)
                        local isCrit = (c18 == true or c18 == 1 or c19 == true or c19 == 1 or c20 == true or c20 == 1)

                        if isCrit then
                            if hs.streak == 0 then
                                hs.streak = 1
                            else
                                hs.streak = 0
                            end
                        else
                            hs.streak = 0
                        end
                        notifyWA()
                    end
                end
            end
        end

        _G.FMHUD_HandleHSEvent = handleEvent

        f:UnregisterAllEvents()
        f:RegisterEvent("PLAYER_ENTERING_WORLD")
        f:RegisterEvent("PLAYER_DEAD")
        f:RegisterEvent("PLAYER_UNGHOST")
        f:RegisterEvent("COMBAT_LOG_EVENT_UNFILTERED")
        f:SetScript("OnEvent", function(self, ev, ...)
            if _G.FMHUD_HandleHSEvent then
                _G.FMHUD_HandleHSEvent(ev, ...)
            end
        end)
    end

    if _G.FMHUD_HandleHSEvent and event then
        _G.FMHUD_HandleHSEvent(event, ...)
    end
    -- [OTTIMIZZAZIONE FIX 1]: Setup frame, eventi e closure eseguito una sola volta per sessione nel blocco 'if not f', azzerando riallocazioni inutili di closure e chiamate f:RegisterEvent per ogni frame o trigger.
    -- [OTTIMIZZAZIONE FIX 6]: Cache locale/upvalue playerGUID per evitare chiamate ripetute a UnitGUID("player") su ogni riga di COMBAT_LOG_EVENT_UNFILTERED del raid.
    return hs
end"""


def make_hotstreak_bg_trigger() -> str:
    """Trigger di stato per il Background Frame di Hot Streak."""
    return """function(event, ...)
    _G.FMHUD_InitHotStreak = _G.FMHUD_InitHotStreak or (""" + SHARED_HOTSTREAK_CHECK_LUA + """)
    if _G.FMHUD_InitHotStreak then _G.FMHUD_InitHotStreak(event, ...) end
    return not UnitIsDeadOrGhost("player")
end"""


def make_hotstreak_bg_untrigger() -> str:
    """Untrigger per il Background Frame di Hot Streak."""
    return """function(event, ...)
    return UnitIsDeadOrGhost("player")
end"""


def make_hotstreak_seg1_trigger() -> str:
    """Trigger per la mezza barra sinistra (1° Critico): attiva se hs.streak == 1."""
    return """function(event, ...)
    if _G.FMHUD_InitHotStreak then
        _G.FMHUD_InitHotStreak(event, ...)
    end
    local hs = _G.FMHUD_HS
    return (hs and hs.streak == 1)
end"""


def make_hotstreak_seg1_untrigger() -> str:
    """Untrigger per la mezza barra sinistra: si spegne se hs.streak != 1."""
    return """function(event, ...)
    local hs = _G.FMHUD_HS
    return not (hs and hs.streak == 1)
end"""


# =============================================================================
# BUILDER: AURE WEAKAURAS PER IL COMPONENTE HOT STREAK
# =============================================================================
def build_hotstreak_auras() -> list[dict]:
    """
    Costruisce e restituisce le 4 aure che compongono il componente Hot Streak:
    - 15 - Hot Streak Bar (Group)
    - Hot Streak Bar - Background (Texture 278x7px)
    - Hot Streak Bar - Segment 1 (Texture 137x5px a x = -70.5)
    - Hot Streak Bar - Proc (Aurabar 137x5px a x = +70.5 con Pixel Glow)
    """
    return [
        # Gruppo contenitore
        {
            "id": "15 - Hot Streak Bar",
            "uid": "FMHUD_HOTSTREAK_BAR_GRP",
            "parent": "Class Mage (TTW Fire)",
            "regionType": "group",
            "internalVersion": 52,
            "xOffset": 0,
            "yOffset": -7,
            "anchorPoint": "CENTER",
            "selfPoint": "CENTER",
            "controlledChildren": [
                "Hot Streak Bar - Background",
                "Hot Streak Bar - Segment 1",
                "Hot Streak Bar - Proc",
            ],
        },
        # Background Frame (278x7px, scuro semitrasparente)
        {
            "id": "Hot Streak Bar - Background",
            "uid": "FMHUD_HSBAR_BG",
            "parent": "15 - Hot Streak Bar",
            "regionType": "texture",
            "internalVersion": 52,
            "xOffset": 0,
            "yOffset": 0,
            "width": 278,
            "height": 7,
            "texture": TEXTURE_WHITE8X8,
            "color": [0.05, 0.05, 0.05, 0.85],
            "selfPoint": "CENTER",
            "anchorPoint": "CENTER",
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "event",
                        "events": "PLAYER_ENTERING_WORLD,PLAYER_ALIVE,PLAYER_DEAD",
                        "custom": make_hotstreak_bg_trigger(),
                    },
                    "untrigger": {
                        "custom": make_hotstreak_bg_untrigger(),
                    }
                },
                "activeTriggerMode": -10,
            },
        },
        # Segment 1 (Mezza barra sinistra: 137x5px a x = -70.5, arancione brillante, persistente)
        {
            "id": "Hot Streak Bar - Segment 1",
            "uid": "FMHUD_HSBAR_SEG1",
            "parent": "15 - Hot Streak Bar",
            "regionType": "texture",
            "internalVersion": 52,
            "width": 137,
            "height": 5,
            "xOffset": -70.5,
            "yOffset": 0,
            "texture": TEXTURE_STATUSBAR,
            "color": [1.0, 0.55, 0.0, 1.0],
            "selfPoint": "CENTER",
            "anchorPoint": "CENTER",
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "event",
                        "events": "FMHUD_HS_UPDATE,PLAYER_ENTERING_WORLD,PLAYER_DEAD,PLAYER_ALIVE",
                        "custom": make_hotstreak_seg1_trigger(),
                    },
                    "untrigger": {
                        "custom": make_hotstreak_seg1_untrigger(),
                    }
                },
                "activeTriggerMode": -10,
            },
        },
        # Proc Segment (Mezza barra destra: 137x5px a x = +70.5, timer 10s e Pixel Glow dorato)
        {
            "id": "Hot Streak Bar - Proc",
            "uid": "FMHUD_HSBAR_SEG2",
            "parent": "15 - Hot Streak Bar",
            "regionType": "aurabar",
            "internalVersion": 52,
            "width": 137,
            "height": 5,
            "xOffset": 70.5,
            "yOffset": 0,
            "barColor": [1.0, 0.35, 0.0, 1.0],
            "backgroundColor": [0.1, 0.1, 0.1, 0.8],
            "texture": TEXTURE_STATUSBAR,
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
                {"type": "subforeground"},
                {
                    "type": "subglow",
                    "glow": True,
                    "glowType": "Pixel",
                    "glowLines": 8,
                    "glowFrequency": 0.25,
                    "glowLength": 6,
                    "glowThickness": 2,
                    "glowColor": [1.0, 0.6, 0.0, 1.0],
                }
            ],
        },
    ]
