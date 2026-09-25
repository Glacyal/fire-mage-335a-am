"""
Modulo Componente: 19 - Multi-Target Living Bomb Tracker
=========================================================
Gestisce la colonna verticale dinamica sul lato destro dell'HUD per monitorare fino a 5 Living Bomb attive:
- Dynamic Group con crescita verso il basso (grow = 'DOWN', space = 3px, icone compatte 24x24px).
- Posizione: xOffset = 169, yOffset = 45 (a destra della barra centrale e dei proc).
- Completamente autoportante e disaccoppiato:
  * Frame dedicato FMHUD_LBFrame con event listener & ticker OnUpdate (0.15s).
  * Tracciamento istantaneo del lancio su target tramite UNIT_SPELLCAST_SUCCEEDED.
  * Sincronizzazione millisecondo-precisa con il server tramite UNIT_AURA, PLAYER_TARGET_CHANGED, PLAYER_FOCUS_CHANGED.
  * Tracciamento multi-bersaglio tramite COMBAT_LOG_EVENT_UNFILTERED (SPELL_AURA_APPLIED, SPELL_AURA_REFRESH, SPELL_AURA_REMOVED, UNIT_DIED, UNIT_DESTROYED).
  * Ordinamento FIFO inverso: Tracker 1 è la bomba più vicina all'esplosione (tempo residuo minore), seguita da 2, 3, 4, 5.
  * Timer allerta rossa <= 3s (|cFFFF4444%.1fs|r) per segnalare il tick di esplosione imminente; secondi interi > 3s (%.0fs).
  * Cooldown swipe nativo 24x24 con texture Living Bomb.
"""
from builder.core.helpers import make_subtext


SHARED_MULTILB_LUA = r"""function()
    _G.FMHUD_LivingBombs = _G.FMHUD_LivingBombs or {}
    _G.FMHUD_LBCache = _G.FMHUD_LBCache or { time = 0, sorted = {} }

    _G.FMHUD_GetActiveLivingBombs = function()
        local now_lb = GetTime()
        local c = _G.FMHUD_LBCache
        if c and (now_lb - c.time < 0.05) then
            return c.sorted
        end
        local active = {}
        local raw = _G.FMHUD_LivingBombs
        if raw then
            for guid, data in pairs(raw) do
                if data.expirationTime and data.expirationTime > now_lb then
                    active[#active + 1] = data
                else
                    raw[guid] = nil
                end
            end
        end
        table.sort(active, function(a, b)
            return (a.expirationTime or 0) < (b.expirationTime or 0)
        end)
        _G.FMHUD_LBCache = { time = now_lb, sorted = active }
        return active
    end

    local function notifyLB()
        _G.FMHUD_LBCache = { time = 0, sorted = {} }
        if WeakAuras and WeakAuras.ScanEvents then
            WeakAuras.ScanEvents("FMHUD_LB_UPDATE")
        end
    end

    local f = _G.FMHUD_LBFrame
    if not f then
        f = CreateFrame("Frame", "FMHUD_LBFrame")
        _G.FMHUD_LBFrame = f
    end

    local playerGUID = UnitGUID("player")
    local playerName = UnitName("player")

    local function handleEvent(ev, ...)
        local now = GetTime()

        if ev == "PLAYER_ENTERING_WORLD" then
            playerGUID = UnitGUID("player")
            playerName = UnitName("player")
            _G.FMHUD_LivingBombs = {}
            notifyLB()
            return
        end

        -- 1. Tracciamento istantaneo al completamento del cast sul target attuale
        if ev == "UNIT_SPELLCAST_SUCCEEDED" then
            local unit, spellName, _, _, spellId = ...
            if unit == "player" then
                local isLB = (spellId == 44457 or spellId == 55359 or spellId == 55360)
                if not isLB and spellName then
                    local sn = tostring(spellName):lower()
                    if sn:find("living bomb") or sn:find("bomba vivente") then
                        isLB = true
                    end
                end
                if isLB and UnitExists("target") and not UnitIsDead("target") then
                    local tg = UnitGUID("target")
                    if tg then
                        _G.FMHUD_LivingBombs[tg] = {
                            destGUID = tg,
                            destName = UnitName("target") or "Target",
                            expirationTime = now + 12,
                            duration = 12,
                        }
                        notifyLB()
                    end
                end
            end
            return
        end

        -- 2. Sincronizzazione autoritativa dal server tramite debuff reali
        if ev == "UNIT_AURA" or ev == "PLAYER_TARGET_CHANGED" or ev == "PLAYER_FOCUS_CHANGED" then
            local u = (ev == "UNIT_AURA") and (...) or ((ev == "PLAYER_TARGET_CHANGED") and "target" or "focus")
            if u and u ~= "player" and UnitExists(u) and not UnitIsDead(u) then
                local ug = UnitGUID(u)
                if ug then
                    for i = 1, 40 do
                        local dname, _, _, _, _, dduration, dexpirationTime, dunitCaster, _, _, dspellId = UnitDebuff(u, i)
                        if not dname then break end
                        local isLbDebuff = (dspellId == 55360 or dspellId == 55359 or dspellId == 44457)
                        if not isLbDebuff and dname then
                            local ln = tostring(dname):lower()
                            if ln:find("living bomb") or ln:find("bomba vivente") then
                                isLbDebuff = true
                            end
                        end
                        if isLbDebuff and (dunitCaster == "player" or not dunitCaster) then
                            if dexpirationTime and dexpirationTime > 0 then
                                local dur = (dduration and dduration > 0) and dduration or 12
                                local current = _G.FMHUD_LivingBombs[ug]
                                if not current or math.abs(current.expirationTime - dexpirationTime) > 0.2 then
                                    _G.FMHUD_LivingBombs[ug] = {
                                        destGUID = ug,
                                        destName = UnitName(u) or "Target",
                                        expirationTime = dexpirationTime,
                                        duration = dur,
                                    }
                                    notifyLB()
                                end
                            end
                            break
                        end
                    end
                end
            end
            if ev ~= "COMBAT_LOG_EVENT_UNFILTERED" then return end
        end

        -- 3. Combat Log Multi-Target (applicazione, rinnovo, rimozione, morte bersaglio)
        if ev == "COMBAT_LOG_EVENT_UNFILTERED" then
            local subEvent = select(2, ...)
            if not subEvent then return end

            local sourceGUID = select(3, ...)
            local sourceName = select(4, ...)
            local sourceFlags = select(5, ...)
            local destGUID = select(6, ...)
            local destName = select(7, ...)
            local spellId = select(9, ...)
            local spellName = select(10, ...)

            if not playerGUID then playerGUID = UnitGUID("player") end
            if not playerName then playerName = UnitName("player") end

            local isPlayer = false
            if sourceGUID and playerGUID and sourceGUID == playerGUID then
                isPlayer = true
            elseif sourceName and playerName and sourceName == playerName then
                isPlayer = true
            elseif sourceFlags and bit and bit.band and bit.band(sourceFlags, 0x00000001) > 0 then
                isPlayer = true
            end

            local isLB = (spellId == 44457 or spellId == 55359 or spellId == 55360)
            if not isLB then
                local s10 = select(10, ...)
                if s10 == 44457 or s10 == 55359 or s10 == 55360 then
                    isLB = true
                    spellId = s10
                    spellName = select(11, ...)
                end
            end
            if not isLB and spellName then
                local sn = tostring(spellName):lower()
                if sn:find("living bomb") or sn:find("bomba vivente") or sn:find("lebende bombe") or sn:find("bombe vivante") or sn:find("bomba viva") then
                    isLB = true
                end
            end

            if isPlayer and (subEvent == "SPELL_AURA_APPLIED" or subEvent == "SPELL_AURA_REFRESH" or subEvent == "SPELL_CAST_SUCCESS") and isLB then
                local tg = destGUID
                local tn = destName
                if not tg or tg == "" then
                    if UnitExists("target") and not UnitIsDead("target") then
                        tg = UnitGUID("target")
                        tn = UnitName("target")
                    end
                end
                if tg and tg ~= "" then
                    _G.FMHUD_LivingBombs[tg] = {
                        destGUID = tg,
                        destName = tn or "Target",
                        expirationTime = now + 12,
                        duration = 12,
                    }
                    notifyLB()
                end
            elseif isPlayer and (subEvent == "SPELL_AURA_REMOVED" or subEvent == "SPELL_AURA_DISPEL") and isLB then
                if destGUID and _G.FMHUD_LivingBombs[destGUID] then
                    _G.FMHUD_LivingBombs[destGUID] = nil
                    notifyLB()
                end
            elseif (subEvent == "UNIT_DIED" or subEvent == "UNIT_DESTROYED") and destGUID then
                if _G.FMHUD_LivingBombs[destGUID] then
                    _G.FMHUD_LivingBombs[destGUID] = nil
                    notifyLB()
                end
            end
        end
    end

    _G.FMHUD_LB_HandleEvent = handleEvent

    f:UnregisterAllEvents()
    f:RegisterEvent("PLAYER_ENTERING_WORLD")
    f:RegisterEvent("UNIT_SPELLCAST_SUCCEEDED")
    f:RegisterEvent("COMBAT_LOG_EVENT_UNFILTERED")
    f:RegisterEvent("UNIT_AURA")
    f:RegisterEvent("PLAYER_TARGET_CHANGED")
    f:RegisterEvent("PLAYER_FOCUS_CHANGED")
    f:SetScript("OnEvent", function(self, ev, ...)
        if _G.FMHUD_LB_HandleEvent then
            _G.FMHUD_LB_HandleEvent(ev, ...)
        end
    end)

    local elapsed = 0
    f:SetScript("OnUpdate", function(self, el)
        elapsed = elapsed + el
        if elapsed < 0.15 then return end
        elapsed = 0
        local raw = _G.FMHUD_LivingBombs
        if raw then
            local now_t = GetTime()
            local changed = false
            for guid, data in pairs(raw) do
                if not data.expirationTime or data.expirationTime <= now_t then
                    raw[guid] = nil
                    changed = true
                end
            end
            if changed then
                notifyLB()
            end
        end
    end)

    _G.FMHUD_LB_InitDone = true
end"""


def make_lb_custom_text(idx: int) -> str:
    """Restituisce la funzione customText per l'icona idx-esima."""
    return f"""function()
    local list = _G.FMHUD_GetActiveLivingBombs and _G.FMHUD_GetActiveLivingBombs()
    local d = list and list[{idx}]
    if d and d.expirationTime then
        local rem = d.expirationTime - GetTime()
        if rem > 0 then
            if rem <= 3 then
                return string.format("|cFFFF4444%.1fs|r", rem)
            else
                return string.format("%.0fs", rem)
            end
        end
    end
    return ""
end"""


def make_lb_trigger_custom(idx: int) -> str:
    """Restituisce la funzione trigger custom per l'icona idx-esima."""
    return f"""function(event, ...)
    _G.FMHUD_LB_Init = _G.FMHUD_LB_Init or ({SHARED_MULTILB_LUA})
    if not _G.FMHUD_LB_InitDone and _G.FMHUD_LB_Init then
        _G.FMHUD_LB_Init()
    end
    if _G.FMHUD_LB_HandleEvent and event then
        _G.FMHUD_LB_HandleEvent(event, ...)
    end
    local list = _G.FMHUD_GetActiveLivingBombs and _G.FMHUD_GetActiveLivingBombs()
    local d = list and list[{idx}]
    return (d ~= nil and d.expirationTime and d.expirationTime > GetTime())
end"""


def make_lb_trigger_duration(idx: int) -> str:
    """Restituisce la durata e l'expirationTime per l'animazione cooldown swipe."""
    return f"""function()
    local list = _G.FMHUD_GetActiveLivingBombs and _G.FMHUD_GetActiveLivingBombs()
    local d = list and list[{idx}]
    if d and d.expirationTime then
        return d.duration or 12, d.expirationTime
    end
    return 0, 0
end"""


def make_lb_untrigger_custom(idx: int) -> str:
    """Restituisce la funzione untrigger custom per l'icona idx-esima."""
    return f"""function(event, ...)
    local list = _G.FMHUD_GetActiveLivingBombs and _G.FMHUD_GetActiveLivingBombs()
    local d = list and list[{idx}]
    return not (d ~= nil and d.expirationTime and d.expirationTime > GetTime())
end"""


def build_multi_lb_auras() -> list[dict]:
    """
    Costruisce e restituisce le 6 aure del componente Multi-Target Living Bomb Tracker:
    - 19 - Multi-Target Living Bomb (Dynamic Group)
    - Living Bomb Tracker 1..5 (Icone 24x24)
    """
    controlled_children = [f"Living Bomb Tracker {i}" for i in range(1, 6)]

    auras = [
        # Dynamic Group
        {
            "id": "19 - Multi-Target Living Bomb",
            "uid": "FMHUD_MULTILB_GRP",
            "parent": "Class Mage (TTW Fire)",
            "regionType": "dynamicgroup",
            "internalVersion": 52,
            "scale": 1.0,
            "xOffset": 169,
            "yOffset": 45,
            "grow": "DOWN",
            "space": 3,
            "align": "CENTER",
            "stagger": 0,
            "sort": "none",
            "controlledChildren": controlled_children,
        }
    ]

    for i in range(1, 6):
        auras.append({
            "id": f"Living Bomb Tracker {i}",
            "uid": f"FMHUD_MULTILB_{i}",
            "parent": "19 - Multi-Target Living Bomb",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 24,
            "height": 24,
            "displayIcon": "Interface\\Icons\\Ability_Mage_LivingBomb",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_lb_custom_text(i),
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "event",
                        "events": "FMHUD_LB_UPDATE,PLAYER_ENTERING_WORLD,UNIT_AURA,COMBAT_LOG_EVENT_UNFILTERED,PLAYER_TARGET_CHANGED,PLAYER_FOCUS_CHANGED,PLAYER_REGEN_ENABLED,UNIT_SPELLCAST_SUCCEEDED",
                        "custom": make_lb_trigger_custom(i),
                        "customDuration": make_lb_trigger_duration(i),
                        "customIcon": """function()
    return "Interface\\\\Icons\\\\Ability_Mage_LivingBomb"
end""",
                    },
                    "untrigger": {
                        "custom": make_lb_untrigger_custom(i),
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        })

    return auras
