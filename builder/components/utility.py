"""
Modulo Componente: 05 - Trinkets & 06 - Utility Row
====================================================
Gestisce la fila orizzontale utility a y = -45 con riposizionamento dinamico
naturale (espansione quando un oggetto/incanto è attivo, contrazione verso il centro
quando viene rimosso), rispettando rigorosamente la sequenza stabilita da sinistra a destra:
1. 05 - Trinket 1 (Slot 13, ICD 45s/90s/120s o On-Use, Pixel Glow su proc)
2. 05 - Trinket 2 (Slot 14, ICD 45s/90s/120s o On-Use, Pixel Glow su proc)
3. 06 - Cloak (Slot 15, Attivo SOLO con incanto con proc di potenziamento)
4. 06 - Tier 8 (Attivo SOLO con >= 2 pezzi T8 Kirin Tor, Praxis +350 SP, 45s ICD)
5. 06 - Gloves (Slot 10, Attivo SOLO con incanto Ingegneria Acceleratori Ipersonici)
6. 06 - Mana Gem (Gemma del Mana, Cooldown + cariche effettive in borsa x3/x2/x1/0 + Proc T7 Mana Surge)
7. 06 - Combustion (Combustione, stato ON, stack critici rimanenti, cooldown)
8. 06 - Mirror Image (Copie, durata 30s + Bonus T10 4P Quad Core +18% danni)
9. 06 - Boots (Slot 8, Attivo SOLO con incanto che dà velocità/speed: Nitro Boosts, Tuskarr's Vitality, ecc.)

Compatibilità: WeakAuras 4.0.0 (internalVersion: 52). Tutti i test sono stati eseguiti su questa versione.
"""
from builder.core.helpers import make_subtext


# =============================================================================
# LOGICA LUA CONDIVISA CENTRALIZZATA (BOOTSTRAP UNIFICATO)
# =============================================================================
SHARED_CORE_BOOTSTRAP_LUA = r"""function()
    _G.FMHUD_GetPlayerBuffs = _G.FMHUD_GetPlayerBuffs or function()
        local now_b = GetTime()
        local c = _G.FMHUD_BuffCache
        if c and c.time == now_b then
            return c
        end
        c = { time = now_b, bySpellId = {}, byName = {}, list = {} }
        for i = 1, 40 do
            local name, rank, icon, count, debuffType, duration, expirationTime, unitCaster, isStealable, shouldConsolidate, spellId = UnitBuff("player", i)
            if not name then break end
            local b = {
                name = name,
                rank = rank,
                icon = icon,
                count = count,
                debuffType = debuffType,
                duration = duration,
                expirationTime = expirationTime,
                unitCaster = unitCaster,
                isStealable = isStealable,
                shouldConsolidate = shouldConsolidate,
                spellId = spellId,
            }
            c.list[#c.list + 1] = b
            if spellId then c.bySpellId[spellId] = b end
            if name then c.byName[name] = b end
        end
        _G.FMHUD_BuffCache = c
        return c
    end

    if _G.FMHUD_CoreInitDone then return end

    _G.FMHUD_ICD = _G.FMHUD_ICD or {
        [8]  = { lastStart = 0, lastEnd = 0, isProc = false, lastItemID = 0 },
        [10] = { lastStart = 0, lastEnd = 0, isProc = false, lastItemID = 0 },
        [13] = { lastStart = 0, lastEnd = 0, isProc = false, lastItemID = 0 },
        [14] = { lastStart = 0, lastEnd = 0, isProc = false, lastItemID = 0 },
        [15] = { lastStart = 0, lastEnd = 0, isProc = false, lastItemID = 0 },
    }

    _G.FMHUD_TrinketDB = {
        -- The Dying Curse
        [40255] = { keywords = { "dyingcurse", "curseoftheeye", "thedyingcurse" }, spellIds = { [60494] = true, [60493] = true, [60492] = true, [60491] = true }, icd = 45, dur = 10 },
        -- Sundial of the Exiled
        [40682] = { keywords = { "nowisthetime", "sundial" }, spellIds = { [60064] = true, [60063] = true }, icd = 45, dur = 10 },
        -- Living Flame (On-Use)
        [40685] = { keywords = { "livingflame" }, spellIds = { [64701] = true, [60480] = true }, icd = 120, dur = 20, onUse = true },
        -- Mark of the War Prisoner (On-Use)
        [37873] = { keywords = { "soulpower" }, spellIds = { [60481] = true, [60480] = true }, icd = 120, dur = 20, onUse = true },
        -- Forge Ember
        [37660] = { keywords = { "forgedember", "forgeember" }, spellIds = { [60479] = true, [60478] = true }, icd = 45, dur = 10 },
        -- Embrace of the Spider
        [37264] = { keywords = { "suddenvelocity", "embraceofthespider" }, spellIds = { [60492] = true, [60491] = true }, icd = 45, dur = 10 },
        [39229] = { keywords = { "suddenvelocity", "embraceofthespider" }, spellIds = { [60492] = true, [60491] = true }, icd = 45, dur = 10 },
        -- Illustration of the Dragon Soul
        [40432] = { keywords = { "dragonsoul" }, spellIds = { [60486] = true, [60485] = true }, icd = 0, dur = 10 },
        -- Eye of the Broodmother
        [45308] = { keywords = { "broodmother", "blessingofthebroodmother" }, spellIds = { [65006] = true, [65004] = true, [65005] = true }, icd = 0, dur = 10 },
        -- DMC Greatness
        [44253] = { keywords = { "greatness" }, spellIds = { [60233] = true, [60234] = true, [60235] = true }, icd = 45, dur = 15 },
        [44255] = { keywords = { "greatness" }, spellIds = { [60233] = true, [60234] = true, [60235] = true }, icd = 45, dur = 15 },
        [42987] = { keywords = { "greatness" }, spellIds = { [60233] = true, [60234] = true, [60235] = true }, icd = 45, dur = 15 },
        [44254] = { keywords = { "greatness" }, spellIds = { [60233] = true, [60234] = true, [60235] = true }, icd = 45, dur = 15 },
        -- Scale of Fates (On-Use)
        [45466] = { keywords = { "velocity" }, spellIds = { [64707] = true, [64708] = true }, icd = 120, dur = 20, onUse = true },
        -- Flare of the Heavens
        [45518] = { keywords = { "elusivepower" }, spellIds = { [64713] = true, [64712] = true }, icd = 45, dur = 10 },
        -- Pandora's Plea
        [45490] = { keywords = { "pandorasplea", "pandora" }, spellIds = { [64741] = true, [64740] = true }, icd = 45, dur = 10 },
        -- Reign of the Dead / Unliving
        [47271] = { keywords = { "motesofflame", "pillarofflame" }, spellIds = { [67759] = true, [67760] = true }, icd = 2, dur = 0 },
        [47477] = { keywords = { "motesofflame", "pillarofflame" }, spellIds = { [67759] = true, [67760] = true }, icd = 2, dur = 0 },
        [47182] = { keywords = { "motesofflame", "pillarofflame" }, spellIds = { [67713] = true, [67714] = true }, icd = 2, dur = 0 },
        [47316] = { keywords = { "motesofflame", "pillarofflame" }, spellIds = { [67713] = true, [67714] = true }, icd = 2, dur = 0 },
        -- Abyssal Rune
        [47213] = { keywords = { "deadlyprecision" }, spellIds = { [67669] = true, [67668] = true }, icd = 45, dur = 10 },
        -- Talisman of Resurgence (On-Use)
        [48722] = { keywords = { "volatilepower" }, spellIds = { [67702] = true, [67701] = true }, icd = 120, dur = 20, onUse = true },
        -- Shard of the Crystal Heart (On-Use)
        [48724] = { keywords = { "chilledheart" }, spellIds = { [67696] = true, [67695] = true }, icd = 120, dur = 20, onUse = true },
        -- Dislodged Foreign Object
        [50348] = { keywords = { "celestialinfusion" }, spellIds = { [71601] = true, [71644] = true }, icd = 45, dur = 20 },
        [50345] = { keywords = { "celestialinfusion" }, spellIds = { [71601] = true, [71644] = true }, icd = 45, dur = 20 },
        -- Phylactery of the Nameless Lich
        [50360] = { keywords = { "siphonofaethas", "aethassiphon", "aethas" }, spellIds = { [71605] = true, [71636] = true }, icd = 90, dur = 20 },
        [50365] = { keywords = { "siphonofaethas", "aethassiphon", "aethas" }, spellIds = { [71605] = true, [71636] = true }, icd = 90, dur = 20 },
        -- Muradin's Spyglass
        [50340] = { keywords = { "gatheringtracker" }, spellIds = { [71570] = true, [71572] = true }, icd = 0, dur = 10 },
        [50353] = { keywords = { "gatheringtracker" }, spellIds = { [71570] = true, [71572] = true }, icd = 0, dur = 10 },
        -- Charred Twilight Scale
        [54572] = { keywords = { "sharedtwilight", "twilightflame" }, spellIds = { [75473] = true, [75466] = true }, icd = 45, dur = 15 },
        [54588] = { keywords = { "sharedtwilight", "twilightflame" }, spellIds = { [75473] = true, [75466] = true }, icd = 45, dur = 15 },
        -- Nevermelting Ice Crystal (On-Use)
        [50259] = { keywords = { "deadlyprecision" }, spellIds = { [71563] = true, [71562] = true }, icd = 180, dur = 20, onUse = true },
        -- Maghia's Misguided Quill (On-Use)
        [50357] = { keywords = { "maghiasmisguidedquill", "maghia", "elusivepower" }, spellIds = { [71584] = true }, icd = 120, dur = 20, onUse = true },
        -- Sliver of Pure Ice (On-Use)
        [50339] = { keywords = { "pureenergy" }, spellIds = { [71586] = true }, icd = 120, dur = 0, onUse = true },
        [50346] = { keywords = { "pureenergy" }, spellIds = { [71586] = true }, icd = 120, dur = 0, onUse = true },
        -- Tears of the Vanquished
        [47215] = { keywords = { "revitalized" }, spellIds = { [67700] = true }, icd = 45, dur = 0 },
        -- Jewelcrafting Figurines (On-Use)
        [42395] = { keywords = { "twilightserpent" }, spellIds = { [59757] = true }, icd = 120, dur = 20, onUse = true },
        [42413] = { keywords = { "sapphireowl" }, spellIds = { [59758] = true }, icd = 120, dur = 20, onUse = true },
        -- Cannoneer's
        [44013] = { keywords = { "fusillade" }, icd = 120, dur = 20, onUse = true },
        [44014] = { keywords = { "morale" }, icd = 120, dur = 20, onUse = true },
        -- DMC Death
        [42990] = { keywords = { "darkmooncarddeath" }, spellIds = { [60203] = true }, icd = 45, dur = 0 },
        -- Ashen Band
        [50398] = { keywords = { "peerlessdestruction" }, spellIds = { [73077] = true }, icd = 60, dur = 10 },
        [50400] = { keywords = { "peerlessdestruction" }, spellIds = { [73077] = true }, icd = 60, dur = 10 },
    }

    _G.FMHUD_AllCasterKeywords = {
        "dyingcurse", "curseoftheeye", "thedyingcurse", "nowisthetime", "sundial", "livingflame",
        "soulpower", "forgedember", "suddenvelocity", "dragonsoul", "broodmother",
        "blessingofthebroodmother", "greatness", "velocity", "elusivepower",
        "pandorasplea", "pandora", "motesofflame", "pillarofflame", "deadlyprecision",
        "volatilepower", "chilledheart", "celestialinfusion", "siphonofaethas",
        "aethassiphon", "aethas", "gatheringtracker", "sharedtwilight",
        "twilightflame", "twilightserpent", "sapphireowl", "pureenergy", "revitalized",
        "fusillade", "morale", "battlemaster", "medallion", "peerlessdestruction"
    }

    _G.FMHUD_CloakKeywords = { "lightweave", "darkglow", "swordguard", "parachute", "flexweave", "springyarachnoweave", "luce intessuta", "spadatesta", "bagliore oscuro", "flessibile", "aracnide" }
    _G.FMHUD_CloakSpellIds = { [55637] = true, [73849] = true, [55775] = true, [55767] = true, [73850] = true, [73851] = true, [54865] = true, [54353] = true, [54753] = true }
    _G.FMHUD_CloakEnchantIDs = { [3722] = true, [3730] = true, [3728] = true, [3729] = true, [3731] = true, [3732] = true, [3859] = true, [3605] = true }

    _G.FMHUD_GlovesSpellIds = { [54758] = true }
    _G.FMHUD_GlovesKeywords = { "hyperspeed", "accelerat", "ipersonic", "340 haste", "fretta di 340", "celere di 340" }

    -- Feet: Enchants that give speed (Nitro Boosts, Tuskarr's Vitality, Cat's Swiftness, Greater Speed, Boar's Speed, Minor Speed)
    _G.FMHUD_BootsEnchantIDs = {
        [3601] = true, -- Nitro Boosts (Engineering)
        [3784] = true, -- Tuskarr's Vitality (+15 Stam & Minor Speed Increase)
        [3232] = true, -- Cat's Swiftness (+6 Agi & Minor Speed Increase)
        [983]  = true, -- Greater Speed (+8% Speed Increase)
        [2679] = true, -- Boar's Speed (+9 Stam & Minor Speed Increase)
        [911]  = true, -- Minor Speed
        [464]  = true, -- Minor Speed
    }
    _G.FMHUD_BootsSpellIds = { [54861] = true }
    _G.FMHUD_BootsKeywords = { "nitro", "boosts", "acceleratori a nitro", "speed", "velocit", "rapidit", "movimento", "swiftness", "tuskarr" }

    _G.FMHUD_ArmorSlots = { 1, 3, 5, 7, 10 }
    _G.FMHUD_T8_SetIDs = {
        [45367] = true, [45369] = true, [45365] = true, [45366] = true, [45368] = true,
        [45357] = true, [45359] = true, [45355] = true, [45356] = true, [45358] = true,
    }
    _G.FMHUD_T8_State = _G.FMHUD_T8_State or { lastStart = 0, lastEnd = 0, isProc = false }

    _G.FMHUD_T10_4P_Pieces = {
        [50069]=true,[51159]=true,[51284]=true,
        [50073]=true,[51155]=true,[51280]=true,
        [50070]=true,[51158]=true,[51283]=true,
        [50071]=true,[51157]=true,[51282]=true,
        [50072]=true,[51156]=true,[51281]=true,
    }

    _G.FMHUD_CheckSlotEquipped = function(s)
        local now_t = GetTime()
        _G.FMHUD_SlotEquipCache = _G.FMHUD_SlotEquipCache or {}
        local cache = _G.FMHUD_SlotEquipCache[s]
        if cache and (now_t - cache.time < 0.25) then
            return cache.isEquipped
        end
        if not cache then
            cache = { time = 0, isEquipped = false }
            _G.FMHUD_SlotEquipCache[s] = cache
        end
        cache.time = now_t

        local itemID = GetInventoryItemID and GetInventoryItemID("player", s)
        if not itemID then
            local link = GetInventoryItemLink("player", s)
            if link then itemID = tonumber(link:match("item:(%d+)")) end
        end

        -- Slot 13 & 14 (Trinkets): visible only if an item is equipped
        if s == 13 or s == 14 then
            local eq = (itemID ~= nil and itemID > 0)
            cache.isEquipped = eq
            return eq
        end

        -- If no item equipped on slot 8, 10, or 15, then not equipped
        if not itemID or itemID == 0 then
            cache.isEquipped = false
            return false
        end

        local itemLink = GetInventoryItemLink("player", s)
        local enchantID = nil
        if itemLink then
            enchantID = tonumber(itemLink:match("item:%d+:(%d+)"))
        end

        local function scanTT(keywords)
            local tt = _G.FMHUD_ScanTT
            if not tt then
                tt = CreateFrame("GameTooltip", "FMHUD_ScanTT", UIParent, "GameTooltipTemplate")
                tt:SetOwner(UIParent, "ANCHOR_NONE")
                _G.FMHUD_ScanTT = tt
            end
            tt:ClearLines()
            tt:SetInventoryItem("player", s)
            for j = 1, tt:NumLines() do
                local line = _G["FMHUD_ScanTTTextLeft"..j]
                local text = line and line:GetText()
                if text then
                    local lt = text:lower()
                    local ltClean = lt:gsub("[%s%p%c]", "")
                    for _, kw in ipairs(keywords) do
                        local kwClean = kw:lower():gsub("[%s%p%c]", "")
                        if lt:find(kw, 1, true) or ltClean:find(kwClean, 1, true) then
                            return true
                        end
                    end
                end
            end
            return false
        end

        -- Slot 10 (Gloves): must have Hyperspeed Accelerators (enchant 3604 or buff 54758 or keyword)
        if s == 10 then
            local buffs = _G.FMHUD_GetPlayerBuffs and _G.FMHUD_GetPlayerBuffs()
            if buffs then
                if buffs.bySpellId[54758] then
                    cache.isEquipped = true
                    return true
                end
                for _, b in ipairs(buffs.list) do
                    if b.name and (b.name:find("Hyperspeed") or b.name:find("Ipersonic")) then
                        cache.isEquipped = true
                        return true
                    end
                end
            else
                for i = 1, 40 do
                    local name, _, _, _, _, _, _, _, _, _, spellId = UnitBuff("player", i)
                    if not name then break end
                    if spellId == 54758 or (name and (name:find("Hyperspeed") or name:find("Ipersonic"))) then
                        cache.isEquipped = true
                        return true
                    end
                end
            end
            if enchantID == 3604 then
                cache.isEquipped = true
                return true
            end
            if scanTT({"hyperspeed", "ipersonic", "340 haste", "fretta di 340", "celere di 340"}) then
                cache.isEquipped = true
                return true
            end
            cache.isEquipped = false
            return false
        end

        -- Slot 8 (Boots): must have speed enchant (Nitro Boosts, Tuskarr's, Cat's Swiftness, Greater Speed, or buff)
        if s == 8 then
            local buffs = _G.FMHUD_GetPlayerBuffs and _G.FMHUD_GetPlayerBuffs()
            if buffs then
                if (_G.FMHUD_BootsSpellIds and (buffs.bySpellId[54861] or buffs.bySpellId[54858] or buffs.bySpellId[55016])) then
                    cache.isEquipped = true
                    return true
                end
                for _, b in ipairs(buffs.list) do
                    if (b.spellId and _G.FMHUD_BootsSpellIds and _G.FMHUD_BootsSpellIds[b.spellId]) or (b.name and (b.name:find("Nitro") or b.name:find("Boosts"))) then
                        cache.isEquipped = true
                        return true
                    end
                end
            else
                for i = 1, 40 do
                    local name, _, _, _, _, _, _, _, _, _, spellId = UnitBuff("player", i)
                    if not name then break end
                    if (spellId and _G.FMHUD_BootsSpellIds and _G.FMHUD_BootsSpellIds[spellId]) or (name and (name:find("Nitro") or name:find("Boosts"))) then
                        cache.isEquipped = true
                        return true
                    end
                end
            end
            if enchantID and _G.FMHUD_BootsEnchantIDs and _G.FMHUD_BootsEnchantIDs[enchantID] then
                cache.isEquipped = true
                return true
            end
            if scanTT(_G.FMHUD_BootsKeywords) then
                cache.isEquipped = true
                return true
            end
            cache.isEquipped = false
            return false
        end

        -- Slot 15 (Cloak): must have an empowerment proc enchant (Lightweave, Darkglow, Swordguard, Springy, Flexweave)
        if s == 15 then
            local buffs = _G.FMHUD_GetPlayerBuffs and _G.FMHUD_GetPlayerBuffs()
            if buffs then
                if _G.FMHUD_CloakSpellIds then
                    for id, _ in pairs(_G.FMHUD_CloakSpellIds) do
                        if buffs.bySpellId[id] then
                            cache.isEquipped = true
                            return true
                        end
                    end
                end
            else
                for i = 1, 40 do
                    local name, _, _, _, _, _, _, _, _, _, spellId = UnitBuff("player", i)
                    if not name then break end
                    if spellId and _G.FMHUD_CloakSpellIds and _G.FMHUD_CloakSpellIds[spellId] then
                        cache.isEquipped = true
                        return true
                    end
                end
            end
            if enchantID and _G.FMHUD_CloakEnchantIDs and _G.FMHUD_CloakEnchantIDs[enchantID] then
                cache.isEquipped = true
                return true
            end
            if scanTT({"lightweave", "luce intessuta", "darkglow", "bagliore oscuro", "swordguard", "spadatesta", "springy arachnoweave", "aracnide", "flexweave", "flessibile"}) then
                cache.isEquipped = true
                return true
            end
            cache.isEquipped = false
            return false
        end

        cache.isEquipped = true
        return true
    end

    _G.FMHUD_CheckSlot = function(slot)
        local now = GetTime()
        _G.FMHUD_SlotCache = _G.FMHUD_SlotCache or {}
        if _G.FMHUD_SlotCache[slot] and _G.FMHUD_SlotCache[slot].time == now then
            local c = _G.FMHUD_SlotCache[slot]
            return c.state, c.rem, c.dur, c.icon
        end

        local function finish(st, r, d, ic)
            local c = _G.FMHUD_SlotCache[slot]
            if not c then
                c = {}
                _G.FMHUD_SlotCache[slot] = c
            end
            c.time = now
            c.state = st
            c.rem = r
            c.dur = d
            c.icon = ic
            return st, r, d, ic
        end

        local itemID = nil
        if GetInventoryItemID then itemID = GetInventoryItemID("player", slot) end
        if not itemID then
            local link = GetInventoryItemLink("player", slot)
            if link then itemID = tonumber(link:match("item:(%d+)")) end
        end
        local icdState = _G.FMHUD_ICD[slot]
        if icdState.lastItemID and itemID and icdState.lastItemID ~= itemID then
            icdState.lastStart = 0
            icdState.lastEnd = 0
            icdState.isProc = false
        end
        if itemID then icdState.lastItemID = itemID end

        local entry = itemID and _G.FMHUD_TrinketDB[itemID]
        local targetICD = (entry and entry.icd) or (slot == 10 and 60) or (slot == 8 and 180) or (slot == 15 and 45) or 45
        local defaultDur = (entry and entry.dur) or (slot == 10 and 12) or (slot == 8 and 5) or (slot == 15 and 15) or 10

        -- Native On-Use cooldown
        local itemStart, itemDur = GetInventoryItemCooldown("player", slot)
        if slot == 8 then
            -- Only consider cooldown if duration is consistent with Nitro Boosts (180s).
            -- Ignore short category lockouts (<= 30s) triggered by activating Gloves, Trinkets, or Potions.
            if itemStart and itemDur and itemDur < 60 then
                itemStart, itemDur = 0, 0
            end
            if not itemStart or itemDur == 0 or itemDur <= 1.5 then
                local sStart, sDur = GetSpellCooldown(54861)
                if not sStart or sDur == 0 or sDur < 60 then sStart, sDur = GetSpellCooldown(54858) end
                if not sStart or sDur == 0 or sDur < 60 then sStart, sDur = GetSpellCooldown(55016) end
                if not sStart or sDur == 0 or sDur < 60 then sStart, sDur = GetSpellCooldown("Nitro Boosts") end
                if not sStart or sDur == 0 or sDur < 60 then sStart, sDur = GetSpellCooldown("Acceleratori a Nitro") end
                if sStart and sDur and sDur >= 60 then
                    itemStart, itemDur = sStart, sDur
                end
            end
        elseif slot == 10 then
            -- Only consider cooldown if duration is consistent with Hyperspeed Accelerators (60s).
            -- Ignore short category lockouts (< 45s) triggered by other items.
            if itemStart and itemDur and itemDur < 45 then
                itemStart, itemDur = 0, 0
            end
            if not itemStart or itemDur == 0 or itemDur <= 1.5 then
                local sStart, sDur = GetSpellCooldown(54758)
                if not sStart or sDur == 0 or sDur < 45 then sStart, sDur = GetSpellCooldown(54757) end
                if not sStart or sDur == 0 or sDur < 45 then sStart, sDur = GetSpellCooldown(54998) end
                if not sStart or sDur == 0 or sDur < 45 then sStart, sDur = GetSpellCooldown(54999) end
                if not sStart or sDur == 0 or sDur < 45 then sStart, sDur = GetSpellCooldown("Hyperspeed Acceleration") end
                if not sStart or sDur == 0 or sDur < 45 then sStart, sDur = GetSpellCooldown("Acceleratori Ipersonici") end
                if sStart and sDur and sDur >= 45 then
                    itemStart, itemDur = sStart, sDur
                end
            end
        end

        local isOnUseCooldown = false
        local remItemCD = 0
        if itemStart and itemDur and itemStart > 0 and itemDur > 1.5 then
            remItemCD = (itemStart + itemDur) - now
            if remItemCD > 0.1 then isOnUseCooldown = true end
        end

        local otherSlot = (slot == 13) and 14 or ((slot == 14) and 13 or nil)
        local otherID = nil
        if otherSlot then
            if GetInventoryItemID then otherID = GetInventoryItemID("player", otherSlot) end
            if not otherID then
                local otherLink = GetInventoryItemLink("player", otherSlot)
                if otherLink then otherID = tonumber(otherLink:match("item:(%d+)")) end
            end
        end
        local otherEntry = otherID and _G.FMHUD_TrinketDB[otherID]

        local foundBuff = false
        local remBuff = 0
        local durBuff = 0
        local buffIcon = nil

        local buffs = _G.FMHUD_GetPlayerBuffs and _G.FMHUD_GetPlayerBuffs()
        local buffList = buffs and buffs.list
        local numBuffs = buffList and #buffList or 40

        for i = 1, numBuffs do
            local name, icon, count, duration, expirationTime, spellId
            if buffList then
                local b = buffList[i]
                if not b then break end
                name = b.name
                icon = b.icon
                count = b.count
                duration = b.duration
                expirationTime = b.expirationTime
                spellId = b.spellId
            else
                local n, _, ic, ct, _, dur, exp, _, _, _, spId = UnitBuff("player", i)
                if not n then break end
                name = n
                icon = ic
                count = ct
                duration = dur
                expirationTime = exp
                spellId = spId
            end
            local isMatch = false

            if slot == 15 then
                if spellId and _G.FMHUD_CloakSpellIds and _G.FMHUD_CloakSpellIds[spellId] then
                    isMatch = true
                else
                    local cName = string.lower(name):gsub("[%s%p%c]", "")
                    for _, kw in ipairs(_G.FMHUD_CloakKeywords) do
                        local kwClean = kw:lower():gsub("[%s%p%c]", "")
                        if cName:find(kwClean, 1, true) then isMatch = true break end
                    end
                end
            elseif slot == 10 then
                if spellId and _G.FMHUD_GlovesSpellIds and _G.FMHUD_GlovesSpellIds[spellId] then
                    isMatch = true
                else
                    local cName = string.lower(name):gsub("[%s%p%c]", "")
                    for _, kw in ipairs(_G.FMHUD_GlovesKeywords) do
                        local kwClean = kw:lower():gsub("[%s%p%c]", "")
                        if cName:find(kwClean, 1, true) then isMatch = true break end
                    end
                end
            elseif slot == 8 then
                if (spellId and (spellId == 54861 or spellId == 54858 or spellId == 55016)) or
                   (name and (name == "Nitro Boosts" or name == "Acceleratori a Nitro" or name:find("Nitro"))) then
                    isMatch = true
                end
            else
                if entry and spellId and entry.spellIds and entry.spellIds[spellId] then
                    isMatch = true
                else
                    local cName = string.lower(name):gsub("[%s%p%c]", "")
                    if entry and entry.keywords then
                        for _, kw in ipairs(entry.keywords) do
                            if cName:find(kw, 1, true) then isMatch = true break end
                        end
                    end

                    if not isMatch then
                        local isOther = false
                        if otherEntry then
                            if spellId and otherEntry.spellIds and otherEntry.spellIds[spellId] then
                                isOther = true
                            elseif otherEntry.keywords then
                                for _, kw in ipairs(otherEntry.keywords) do
                                    if cName:find(kw, 1, true) then isOther = true break end
                                end
                            end
                        end

                        if not isOther then
                            for _, kw in ipairs(_G.FMHUD_AllCasterKeywords) do
                                if cName:find(kw, 1, true) then isMatch = true break end
                            end
                        end
                    end
                end
            end

            if isMatch then
                foundBuff = true
                durBuff = (duration and duration > 0) and duration or defaultDur
                remBuff = (expirationTime and expirationTime > 0) and (expirationTime - now) or durBuff
                buffIcon = icon
                if not buffIcon then
                    if slot == 10 then buffIcon = "Interface/Icons/spell_nature_shamanrage"
                    elseif slot == 8 then buffIcon = "Interface/Icons/ability_rogue_sprint"
                    elseif slot == 15 then buffIcon = "Interface/Icons/INV_Misc_Cape_19"
                    end
                end
                break
            end
        end

        if foundBuff then
            if not icdState.isProc or (now - icdState.lastStart > durBuff + 2) then
                icdState.lastStart = now - (durBuff - remBuff)
                icdState.lastEnd = icdState.lastStart + targetICD
                icdState.isProc = true
            end
            return finish("ACTIVE", remBuff, durBuff, buffIcon)
        end

        if icdState.isProc then
            icdState.isProc = false
            if icdState.lastEnd == 0 or icdState.lastEnd > now then
                icdState.lastEnd = now
            end
        end

        if isOnUseCooldown then
            return finish("COOLDOWN", remItemCD, itemDur, nil)
        end

        if icdState.lastStart > 0 and targetICD > 0 then
            local elapsed = now - icdState.lastStart
            if elapsed < targetICD then
                local remICD = targetICD - elapsed
                return finish("COOLDOWN", remICD, targetICD, nil)
            end
        end

        return finish("READY", 0, 0, nil)
    end

    _G.FMHUD_CheckT8Equipped = function()
        local now = GetTime()
        local cache = _G.FMHUD_T8_EquipCache
        if cache and (now - cache.time < 0.25) then
            return cache.isEquipped
        end
        if not cache then
            cache = { time = 0, isEquipped = false }
            _G.FMHUD_T8_EquipCache = cache
        end
        cache.time = now

        for i = 1, 40 do
            local name, _, _, _, _, _, _, _, _, _, spellId = UnitBuff("player", i)
            if not name then break end
            if spellId == 64868 or name == "Praxis" or name == "Prassi" or name:find("T8 2P") then
                cache.isEquipped = true
                return true
            end
        end

        local count = 0
        local slots = _G.FMHUD_ArmorSlots or { 1, 3, 5, 7, 10 }
        local setIDs = _G.FMHUD_T8_SetIDs
        for _, s in ipairs(slots) do
            local id = GetInventoryItemID("player", s)
            if id and setIDs and setIDs[id] then
                count = count + 1
            end
        end
        if count >= 2 then
            cache.isEquipped = true
            return true
        end

        local ttCount = 0
        local tt = _G.FMHUD_ScanTT
        if not tt then
            tt = CreateFrame("GameTooltip", "FMHUD_ScanTT", UIParent, "GameTooltipTemplate")
            tt:SetOwner(UIParent, "ANCHOR_NONE")
            _G.FMHUD_ScanTT = tt
        end
        for _, s in ipairs(slots) do
            local id = GetInventoryItemID("player", s)
            if id then
                tt:ClearLines()
                tt:SetInventoryItem("player", s)
                for j = 1, tt:NumLines() do
                    local line = _G["FMHUD_ScanTTTextLeft"..j]
                    local text = line and line:GetText()
                    if text then
                        local lt = text:lower()
                        if lt:find("kirin tor") or lt:find("praxis") or lt:find("prassi") then
                            ttCount = ttCount + 1
                            break
                        end
                    end
                end
            end
        end
        if ttCount >= 2 then
            cache.isEquipped = true
            return true
        end

        cache.isEquipped = false
        return false
    end

    _G.FMHUD_CheckT8 = function()
        local isEquipped = _G.FMHUD_CheckT8Equipped()
        local defIcon = select(3, GetSpellInfo(64868)) or select(3, GetSpellInfo("Praxis")) or "Interface/Icons/Spell_Arcane_StudentOfMagic"
        local icon = defIcon
        if not isEquipped then return "NONE", 0, 0, defIcon, false end

        local now = GetTime()
        local state = _G.FMHUD_T8_State
        local foundBuff = false
        local remBuff = 0
        local durBuff = 15

        for i = 1, 40 do
            local name, _, buffIcon, count, _, duration, expirationTime, _, _, _, spellId = UnitBuff("player", i)
            if not name then break end
            if spellId == 64868 or name == "Praxis" or name == "Prassi" or name:find("T8 2P") then
                foundBuff = true
                durBuff = (duration and duration > 0) and duration or 15
                remBuff = (expirationTime and expirationTime > 0) and (expirationTime - now) or durBuff
                icon = buffIcon or defIcon
                break
            end
        end

        if foundBuff then
            if not state.isProc or (now - state.lastStart > durBuff + 2) then
                state.lastStart = now - (durBuff - remBuff)
                state.lastEnd = state.lastStart + 45
                state.isProc = true
            end
            return "ACTIVE", remBuff, durBuff, icon, true
        end

        if state.isProc then
            state.isProc = false
            if state.lastEnd == 0 or state.lastEnd > now then
                state.lastEnd = now
            end
        end

        if state.lastStart > 0 then
            local elapsed = now - state.lastStart
            if elapsed < 45 then
                local remICD = 45 - elapsed
                return "ICD", remICD, 45, icon, true
            end
        end

        return "READY", 0, 0, icon, true
    end

    _G.FMHUD_CheckCombustion = function()
        local now = GetTime()
        local defIcon = select(3, GetSpellInfo(11129)) or select(3, GetSpellInfo("Combustion")) or select(3, GetSpellInfo("Combustione")) or "Interface/Icons/Spell_Fire_SealOfFire"
        for i = 1, 40 do
            local name, _, icon, count, _, duration, expirationTime = UnitBuff("player", i)
            if not name then break end
            if name == "Combustion" then
                local rem = expirationTime and expirationTime > 0 and (expirationTime - now) or 0
                local dur = duration and duration > 0 and duration or 0
                return "ACTIVE", rem, dur, count or 1, icon or defIcon
            end
        end

        local start, duration = GetSpellCooldown(11129)
        if not start or duration == 0 then start, duration = GetSpellCooldown("Combustion") end
        if not start or duration == 0 then start, duration = GetSpellCooldown("Combustione") end
        if start and duration and start > 0 and duration > 1.5 then
            local remCD = (start + duration) - now
            if remCD > 0.1 then
                return "COOLDOWN", remCD, duration, 0, defIcon
            end
        end

        return "READY", 0, 0, 0, defIcon
    end

    _G.FMHUD_CheckMirrorImage = function()
        local now = GetTime()
        local baseIcon = select(3, GetSpellInfo(55342)) or select(3, GetSpellInfo("Mirror Image")) or select(3, GetSpellInfo("Immagine Speculare")) or "Interface/Icons/Spell_Magic_LesserInvisibilty"
        local quadCoreIcon = select(3, GetSpellInfo(70747)) or select(3, GetSpellInfo("Quad Core")) or "Interface/Icons/Spell_Nature_Invisibilty"

        local hasT10_4P = false
        local t10Pieces = _G.FMHUD_T10_4P_Pieces
        local slots = _G.FMHUD_ArmorSlots or { 1, 3, 5, 7, 10 }
        local t10Count = 0
        for _, slot in ipairs(slots) do
            local id = GetInventoryItemID("player", slot)
            if id and t10Pieces and t10Pieces[id] then
                t10Count = t10Count + 1
            end
        end
        if t10Count >= 4 then hasT10_4P = true end

        for i = 1, 40 do
            local name, _, buffIcon, count, _, duration, expirationTime, _, _, _, spellId = UnitBuff("player", i)
            if not name then break end
            if spellId == 70747 or spellId == 70748 or spellId == 70754 or spellId == 70752 or
               name == "Quad Core" or name == "Item - Mage T10 4P Bonus" then
                local rem = (expirationTime and expirationTime > 0) and (expirationTime - now) or 0
                local dur = (duration and duration > 0) and duration or 30
                local icon = buffIcon or quadCoreIcon
                return "ACTIVE", rem, dur, icon, true
            elseif name == "Mirror Image" or name == "Immagine Speculare" or spellId == 55342 then
                local rem = (expirationTime and expirationTime > 0) and (expirationTime - now) or 0
                local dur = (duration and duration > 0) and duration or 30
                local icon = hasT10_4P and (buffIcon or quadCoreIcon) or baseIcon
                return "ACTIVE", rem, dur, icon, hasT10_4P
            end
        end

        local start, duration = GetSpellCooldown(55342)
        if not start or duration == 0 then start, duration = GetSpellCooldown("Mirror Image") end
        if not start or duration == 0 then start, duration = GetSpellCooldown("Immagine Speculare") end

        if start and duration and start > 0 and duration > 1.5 then
            local elapsed = now - start
            if not hasT10_4P and elapsed >= 0 and elapsed < 30 then
                local remActive = 30 - elapsed
                return "ACTIVE", remActive, 30, baseIcon, false
            else
                local remCD = (start + duration) - now
                if remCD > 0.1 then
                    return "COOLDOWN", remCD, duration, baseIcon, false
                end
            end
        end

        return "READY", 0, 0, baseIcon, false
    end

    _G.FMHUD_GetManaGemCharges = function()
        local now_c = GetTime()
        _G.FMHUD_ManaGemChargeCache = _G.FMHUD_ManaGemChargeCache or { time = 0, charges = 0 }
        local cache = _G.FMHUD_ManaGemChargeCache
        if cache.time and cache.time > 0 and (now_c - cache.time < 1.5) then
            return cache.charges
        end
        cache.time = now_c

        -- Identificativi di tutte le gemme del mana conjurate (Zaffiro, Smeraldo, Rubino, Citrino, Giada, Agata)
        local gemIDs = { [33312] = true, [22044] = true, [8008] = true, [8007] = true, [5513] = true, [5514] = true }
        local foundGem = false

        -- 1. Scansione borse con lettura diretta del tooltip dell'oggetto per cariche esatte (3, 2, 1)
        local tt = _G.FMHUD_ScanTT
        if not tt then
            tt = CreateFrame("GameTooltip", "FMHUD_ScanTT", UIParent, "GameTooltipTemplate")
            tt:SetOwner(UIParent, "ANCHOR_NONE")
            _G.FMHUD_ScanTT = tt
        end

        for bag = 0, 4 do
            local numSlots = GetContainerNumSlots(bag)
            for slot = 1, numSlots do
                local id = GetContainerItemID(bag, slot)
                if id and gemIDs[id] then
                    foundGem = true
                    tt:ClearLines()
                    tt:SetBagItem(bag, slot)
                    for j = 1, tt:NumLines() do
                        local line = _G["FMHUD_ScanTTTextLeft"..j]
                        local txt = line and line:GetText()
                        if txt then
                            local ch = txt:match("%((%d+)%s+[^%)]+%)") or txt:match("(%d+)%s+[Cc]harg") or txt:match("(%d+)%s+[Cc]aric") or txt:match("(%d+)%s+[Aa]uflad")
                            if ch then
                                local charges = tonumber(ch)
                                cache.charges = charges
                                return charges
                            end
                        end
                    end
                end
            end
        end

        -- 2. Fallback via API GetItemCount con parametro includeCharges = true
        for id in pairs(gemIDs) do
            local c = GetItemCount(id, false, true)
            if c and c > 0 then
                cache.charges = c
                return c
            end
        end

        local res = foundGem and 1 or 0
        cache.charges = res
        return res
    end
    -- [OTTIMIZZAZIONE FIX 5]: Cache temporale a 1.5s su FMHUD_ManaGemChargeCache per evitare la pesante scansione di tutte le borse e il parsing del tooltip ad ogni evento ad altissima frequenza (es. CLEU in raid).

    _G.FMHUD_CheckManaGem = function()
        local now = GetTime()
        local isT7Active = false
        local remT7 = 0
        local durT7 = 15
        local baseIcon = (GetItemCount(33312) == 0 and GetItemCount(22044) > 0)
                         and (GetItemIcon(22044) or "Interface/Icons/INV_Misc_Gem_Emerald_01")
                         or  (GetItemIcon(33312) or select(3, GetSpellInfo(5405)) or "Interface/Icons/INV_Misc_Gem_Sapphire_02")
        local procIcon = nil

        for i = 1, 40 do
            local n, _, icon, _, _, dur, exp, _, _, _, spellId = UnitBuff("player", i)
            if not n then break end
            if spellId == 61062 or spellId == 37447 or
               n == "Mana Surge" or n == "Improved Mana Gems" or n == "Gemme di Mana Migliorate" or
               n == "Gemme del Mana Migliorate" or n == "Gemma del Mana Migliorata" or n == "Ondata di Mana" then
                local rem = (exp and exp > now) and (exp - now) or 0
                if rem > 0.05 then
                    isT7Active = true
                    remT7 = rem
                    durT7 = (dur and dur > 0) and dur or 15
                    procIcon = icon or select(3, GetSpellInfo(61062)) or "Interface/Icons/Spell_Arcane_ManaSurge" or "Interface/Icons/Spell_Holy_MagicalSentry"
                    break
                end
            end
        end

        local start, duration = GetItemCooldown(33312)
        if not start or duration == 0 then start, duration = GetItemCooldown(22044) end
        local isCD = false
        local remCD = 0
        if start and duration and duration > 1.5 and (start + duration) > now then
            remCD = (start + duration) - now
            if remCD > 0.1 then isCD = true end
        end

        if isT7Active then
            local activeIcon = procIcon or select(3, GetSpellInfo(61062)) or "Interface/Icons/Spell_Arcane_ManaSurge" or "Interface/Icons/Spell_Holy_MagicalSentry"
            return "ACTIVE", remT7, durT7, activeIcon
        elseif isCD then
            return "COOLDOWN", remCD, duration, baseIcon
        else
            return "READY", 0, 0, baseIcon
        end
    end

    local lastRowUpdate = 0
    _G.FMHUD_UpdateUtilityRowPositions = function(force)
        local now = GetTime()
        if not force and (now - lastRowUpdate < 0.15) then return end
        lastRowUpdate = now

        if not WeakAuras or not WeakAuras.regions then return end
        local groupObj = WeakAuras.regions["Class Mage (TTW Fire)"]
        local group = groupObj and (groupObj.region or (groupObj.GetPoint and groupObj))
        if not group then return end

        local hasT1 = _G.FMHUD_CheckSlotEquipped and _G.FMHUD_CheckSlotEquipped(13)
        local hasT2 = _G.FMHUD_CheckSlotEquipped and _G.FMHUD_CheckSlotEquipped(14)
        local hasCloak = _G.FMHUD_CheckSlotEquipped and _G.FMHUD_CheckSlotEquipped(15)
        local hasT8 = _G.FMHUD_CheckT8Equipped and _G.FMHUD_CheckT8Equipped()
        local hasGloves = _G.FMHUD_CheckSlotEquipped and _G.FMHUD_CheckSlotEquipped(10)
        local hasBoots = _G.FMHUD_CheckSlotEquipped and _G.FMHUD_CheckSlotEquipped(8)

        local activeOrder = {}
        if hasT1 then table.insert(activeOrder, "05 - Trinket 1") end
        if hasT2 then table.insert(activeOrder, "06 - Trinket 2") end
        if hasCloak then table.insert(activeOrder, "07 - Cloak") end
        if hasT8 then table.insert(activeOrder, "08 - Tier 8") end
        if hasGloves then table.insert(activeOrder, "09 - Gloves") end
        table.insert(activeOrder, "10 - Mana Gem")
        table.insert(activeOrder, "11 - Combustion")
        table.insert(activeOrder, "12 - Mirror Image")
        if hasBoots then table.insert(activeOrder, "13 - Boots") end

        local N = #activeOrder
        local step = 38
        if N >= 9 then step = 29
        elseif N == 8 then step = 32
        elseif N == 7 then step = 38
        elseif N == 6 then step = 44
        elseif N == 5 then step = 48
        else step = 52 end

        local targetW = 28
        for i, id in ipairs(activeOrder) do
            local targetX = math.floor(((i - (N + 1) / 2) * step) + 0.5)
            local regObj = WeakAuras.regions[id]
            local r = regObj and (regObj.region or (regObj.GetPoint and regObj))
            if r then
                local point, relTo, relPoint, curX, curY = r:GetPoint(1)
                if force or not curX or math.abs(curX - targetX) > 0.5 or (curY and math.abs(curY - (-45)) > 0.5) then
                    r:ClearAllPoints()
                    r:SetPoint("CENTER", group, "CENTER", targetX, -45)
                end
                if r.GetWidth and math.abs(r:GetWidth() - targetW) > 0.5 then
                    r:SetWidth(targetW)
                    r:SetHeight(targetW)
                end
            end
            if WeakAuras and WeakAuras.GetData then
                local data = WeakAuras.GetData(id)
                if data and (data.xOffset ~= targetX or data.yOffset ~= -45) then
                    data.xOffset = targetX
                    data.yOffset = -45
                end
            end
        end
    end

    if not _G.FMHUD_LayoutFrame then
        local f = CreateFrame("Frame", "FMHUD_LayoutFrame")
        local playerGUID = UnitGUID("player")
        f:RegisterEvent("PLAYER_EQUIPMENT_CHANGED")
        f:RegisterEvent("UNIT_INVENTORY_CHANGED")
        f:RegisterEvent("PLAYER_ENTERING_WORLD")
        f:RegisterEvent("ZONE_CHANGED_NEW_AREA")
        f:RegisterEvent("UNIT_AURA")
        f:RegisterEvent("SPELL_UPDATE_COOLDOWN")
        f:RegisterEvent("ACTIONBAR_UPDATE_COOLDOWN")
        f:RegisterEvent("BAG_UPDATE_COOLDOWN")
        f:RegisterEvent("BAG_UPDATE")
        f:RegisterEvent("UNIT_SPELLCAST_SUCCEEDED")
        f:RegisterEvent("COMBAT_LOG_EVENT_UNFILTERED")
        f.pendingUpdates = 0
        f:SetScript("OnEvent", function(self, event, ...)
            if event == "COMBAT_LOG_EVENT_UNFILTERED" then
                local _, subEvent, _, sourceGUID, _, _, _, _, _, _, _, spellId, spellName = ...
                if not playerGUID then playerGUID = UnitGUID("player") end
                if sourceGUID == playerGUID then
                    if subEvent == "SPELL_CAST_SUCCESS" or subEvent == "SPELL_AURA_APPLIED" then
                        local now = GetTime()
                        if spellId == 54861 or spellId == 54858 or spellId == 55016 or spellName == "Nitro Boosts" or spellName == "Acceleratori a Nitro" then
                            _G.FMHUD_ICD[8].lastStart = now
                            _G.FMHUD_ICD[8].lastEnd = now + 180
                            _G.FMHUD_ICD[8].isProc = true
                            if WeakAuras and WeakAuras.ScanEvents then
                                WeakAuras.ScanEvents("FMHUD_ROW_UPDATE")
                            end
                        elseif spellId == 54758 or spellId == 54757 or spellId == 54998 or spellId == 54999 or spellName == "Hyperspeed Acceleration" or spellName == "Acceleratori Ipersonici" or spellName == "Hyperspeed Accelerators" or spellName == "Acceleratori ad Alta Velocità" then
                            _G.FMHUD_ICD[10].lastStart = now
                            _G.FMHUD_ICD[10].lastEnd = now + 60
                            _G.FMHUD_ICD[10].isProc = true
                            if WeakAuras and WeakAuras.ScanEvents then
                                WeakAuras.ScanEvents("FMHUD_ROW_UPDATE")
                            end
                        end
                    end
                end
                return
            end
            if event == "UNIT_AURA" then
                local unit = ...
                if unit ~= "player" then return end
            end
            if event == "BAG_UPDATE" then
                if _G.FMHUD_ManaGemChargeCache then
                    _G.FMHUD_ManaGemChargeCache.time = 0
                end
                if WeakAuras and WeakAuras.ScanEvents then
                    WeakAuras.ScanEvents("FMHUD_ROW_UPDATE")
                end
                return
            end
            if event == "UNIT_SPELLCAST_SUCCEEDED" then
                local unit, spellName, _, _, spellId = ...
                if unit == "player" then
                    if spellId == 759 or spellId == 3552 or spellId == 10053 or spellId == 10054 or spellId == 27101 or spellId == 42985 or spellId == 5405 or
                       (spellName and (spellName:find("Mana Gem") or spellName:find("Gemma del Mana") or spellName:find("Gemme di Mana"))) then
                        if _G.FMHUD_ManaGemChargeCache then
                            _G.FMHUD_ManaGemChargeCache.time = 0
                        end
                        if WeakAuras and WeakAuras.ScanEvents then
                            WeakAuras.ScanEvents("FMHUD_ROW_UPDATE")
                        end
                    end
                end
                return
            end
            if _G.FMHUD_ManaGemChargeCache then
                _G.FMHUD_ManaGemChargeCache.time = 0
            end
            _G.FMHUD_BuffCache = nil
            _G.FMHUD_T8_EquipCache = nil
            _G.FMHUD_SlotEquipCache = nil
            if WeakAuras and WeakAuras.ScanEvents then
                WeakAuras.ScanEvents("FMHUD_ROW_UPDATE")
            end
            _G.FMHUD_UpdateUtilityRowPositions(true)
            self.pendingUpdates = 5
            self:SetScript("OnUpdate", function(sf, el)
                if sf.pendingUpdates and sf.pendingUpdates > 0 then
                    sf.pendingUpdates = sf.pendingUpdates - 1
                    _G.FMHUD_UpdateUtilityRowPositions(true)
                else
                    sf:SetScript("OnUpdate", nil)
                end
            end)
        end)
        _G.FMHUD_LayoutFrame = f
    end
    -- [OTTIMIZZAZIONE FIX 6]: Cache dell'upvalue playerGUID in FMHUD_LayoutFrame per evitare chiamate a UnitGUID("player") su ogni riga di COMBAT_LOG_EVENT_UNFILTERED.

    _G.FMHUD_CoreInitDone = true
end"""


def make_slot_custom_text(slot: int) -> str:
    """Testo descrittivo del monile/mantello/guanti/scarpe (%c), con pixel glow su proc attivo e riposizionamento dinamico."""
    bootstrap = f"""    _G.FMHUD_InitCore = _G.FMHUD_InitCore or {SHARED_CORE_BOOTSTRAP_LUA}
    if not _G.FMHUD_CoreInitDone then _G.FMHUD_InitCore() end""" if slot == 13 else """    if not _G.FMHUD_CoreInitDone and _G.FMHUD_InitCore then _G.FMHUD_InitCore() end"""
    return f"""function()
{bootstrap}
    if _G.FMHUD_UpdateUtilityRowPositions then
        _G.FMHUD_UpdateUtilityRowPositions()
    end
    if not _G.FMHUD_CheckSlot then return "" end
    local state, rem, dur, icon = _G.FMHUD_CheckSlot({slot})
    local LCG = LibStub and LibStub("LibCustomGlow-1.0", true)
    local glowKey = "FMHUD_SLOT_{slot}_GLOW"
    if state == "ACTIVE" then
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Start(aura_env.region, {{1, 0.85, 0.1, 1}}, 8, 0.25, 10, 2, 0, 0, false, glowKey)
        end
        return string.format("|cFFFFFF00%.1fs|r", rem)
    else
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Stop(aura_env.region, glowKey)
        end
        if (state == "ICD" or state == "COOLDOWN") and rem > 0.1 then
            if rem >= 60 then
                local m = math.floor(rem / 60)
                local s = math.floor(rem % 60)
                return string.format("%d:%02d", m, s)
            else
                return string.format("%.0f", rem)
            end
        end
        return ""
    end
end"""


def make_slot_custom_duration(slot: int) -> str:
    """Durata e scadenza dello swipe di ricarica per lo slot indicato."""
    return f"""function()
    if not _G.FMHUD_CheckSlot then return 0, 0 end
    local state, rem, dur = _G.FMHUD_CheckSlot({slot})
    if (state == "ACTIVE" or state == "ICD" or state == "COOLDOWN") and rem > 0 and dur > 0 then
        return dur, GetTime() + rem
    end
    return 0, 0
end"""


def make_slot_custom_icon(slot: int, default_icon: str) -> str:
    """Restituisce dinamicamente l'icona dell'oggetto equipaggiato o del proc attivo."""
    return f"""function()
    if _G.FMHUD_CheckSlot then
        local state, rem, dur, icon = _G.FMHUD_CheckSlot({slot})
        if state == "ACTIVE" and icon then
            return icon
        end
    end
    return GetInventoryItemTexture("player", {slot}) or "{default_icon}"
end"""


def make_slot_trigger_custom(slot: int) -> str:
    """Trigger custom per verificare se lo slot è equipaggiato / possiede l'incanto idoneo."""
    return f"""function(event, ...)
    if not _G.FMHUD_CoreInitDone and _G.FMHUD_InitCore then _G.FMHUD_InitCore() end
    if not _G.FMHUD_CheckSlotEquipped then return false end
    return _G.FMHUD_CheckSlotEquipped({slot})
end"""


def make_slot_untrigger_custom(slot: int) -> str:
    """Untrigger custom quando lo slot non è equipaggiato o non ha l'incanto richiesto."""
    return f"""function(event, ...)
    if not _G.FMHUD_CheckSlotEquipped then return true end
    return not _G.FMHUD_CheckSlotEquipped({slot})
end"""


def make_t8_custom_text() -> str:
    """Testo descrittivo del Tier 8 2P (%c), con pixel glow su proc attivo e timer ICD."""
    return """function()
    if not _G.FMHUD_CoreInitDone and _G.FMHUD_InitCore then _G.FMHUD_InitCore() end
    if _G.FMHUD_UpdateUtilityRowPositions then
        _G.FMHUD_UpdateUtilityRowPositions()
    end
    if not _G.FMHUD_CheckT8 then return "" end
    local state, rem, dur, icon, isEquipped = _G.FMHUD_CheckT8()
    local LCG = LibStub and LibStub("LibCustomGlow-1.0", true)
    if state == "ACTIVE" then
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Start(aura_env.region, {{1, 0.85, 0.1, 1}}, 8, 0.25, 10, 2, 0, 0, false, "FMHUD_T8_GLOW")
        end
        return string.format("|cFFFFFF00%.1fs|r", rem)
    else
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Stop(aura_env.region, "FMHUD_T8_GLOW")
        end
        if state == "ICD" and rem > 0.1 then
            if rem >= 60 then
                local m = math.floor(rem / 60)
                local s = math.floor(rem % 60)
                return string.format("%d:%02d", m, s)
            else
                return string.format("%.0f", rem)
            end
        end
        return ""
    end
end"""


def make_t8_custom_duration() -> str:
    """Durata e scadenza dello swipe di ricarica per il Tier 8 2P."""
    return """function()
    if not _G.FMHUD_CheckT8 then return 0, 0 end
    local state, rem, dur, icon, isEquipped = _G.FMHUD_CheckT8()
    if (state == "ACTIVE" or state == "ICD") and rem > 0 and dur > 0 then
        return dur, GetTime() + rem
    end
    return 0, 0
end"""


def make_t8_custom_icon() -> str:
    """Icona del Tier 8 2P (Praxis / Kirin Tor)."""
    return """function()
    if not _G.FMHUD_CoreInitDone and _G.FMHUD_InitCore then _G.FMHUD_InitCore() end
    if _G.FMHUD_CheckT8 then
        local state, rem, dur, icon, isEquipped = _G.FMHUD_CheckT8()
        if icon then return icon end
    end
    local icon = select(3, GetSpellInfo(64868)) or select(3, GetSpellInfo("Praxis"))
    return icon or "Interface/Icons/Spell_Arcane_StudentOfMagic"
end"""


def make_combustion_custom_text() -> str:
    """Testo descrittivo (%c) di Combustion con conteggio cariche critiche e pixel glow dorato."""
    return """function()
    if not _G.FMHUD_CoreInitDone and _G.FMHUD_InitCore then _G.FMHUD_InitCore() end
    if _G.FMHUD_UpdateUtilityRowPositions then
        _G.FMHUD_UpdateUtilityRowPositions()
    end
    if not _G.FMHUD_CheckCombustion then return "" end
    local state, rem, dur, count, icon = _G.FMHUD_CheckCombustion()
    local LCG = LibStub and LibStub("LibCustomGlow-1.0", true)

    if state == "ACTIVE" then
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Start(aura_env.region, {{1, 0.85, 0.1, 1}}, 8, 0.25, 10, 2, 0, 0, false, "FMHUD_COMB_GLOW")
        end
        if count and count > 0 then
            return string.format("|cFFFFFF00x%d|r", count)
        elseif rem > 0 then
            return string.format("|cFFFFFF00%.1fs|r", rem)
        end
        return "|cFFFFFF00ON|r"
    else
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Stop(aura_env.region, "FMHUD_COMB_GLOW")
        end
        if state == "COOLDOWN" and rem > 0.1 then
            if rem >= 60 then
                local m = math.floor(rem / 60)
                local s = math.floor(rem % 60)
                return string.format("%d:%02d", m, s)
            else
                return string.format("%.0f", rem)
            end
        end
        return ""
    end
end"""


def make_combustion_custom_duration() -> str:
    """Durata e scadenza per lo swipe di Combustion (CD o buff attivo)."""
    return """function()
    if not _G.FMHUD_CheckCombustion then return 0, 0 end
    local state, rem, dur = _G.FMHUD_CheckCombustion()
    if (state == "ACTIVE" or state == "COOLDOWN") and rem > 0 and dur > 0 then
        return dur, GetTime() + rem
    end
    return 0, 0
end"""


def make_combustion_custom_icon() -> str:
    """Icona di Combustion."""
    return """function()
    if not _G.FMHUD_CoreInitDone and _G.FMHUD_InitCore then _G.FMHUD_InitCore() end
    if _G.FMHUD_CheckCombustion then
        local state, rem, dur, count, icon = _G.FMHUD_CheckCombustion()
        if icon then return icon end
    end
    local icon = select(3, GetSpellInfo(11129)) or select(3, GetSpellInfo("Combustion")) or select(3, GetSpellInfo("Combustione"))
    return icon or "Interface/Icons/Spell_Fire_SealOfFire"
end"""


def make_mirrorimage_custom_text() -> str:
    """Testo descrittivo (%c) delle Copie (Mirror Image): durata attiva 30s con proc T10 (+18% danni) o CD 3 min."""
    return """function()
    if not _G.FMHUD_CoreInitDone and _G.FMHUD_InitCore then _G.FMHUD_InitCore() end
    if _G.FMHUD_UpdateUtilityRowPositions then
        _G.FMHUD_UpdateUtilityRowPositions()
    end
    if not _G.FMHUD_CheckMirrorImage then return "" end
    local state, rem, dur, icon, isT10 = _G.FMHUD_CheckMirrorImage()
    local LCG = LibStub and LibStub("LibCustomGlow-1.0", true)

    if state == "ACTIVE" then
        if LCG and aura_env and aura_env.region then
            if isT10 then
                LCG.PixelGlow_Start(aura_env.region, {{1, 0.85, 0.1, 1}}, 8, 0.25, 10, 2, 0, 0, false, "FMHUD_MI_GLOW")
            else
                LCG.PixelGlow_Start(aura_env.region, {{0.2, 0.8, 1.0, 1}}, 8, 0.25, 10, 2, 0, 0, false, "FMHUD_MI_GLOW")
            end
        end
        if rem > 0 then
            if isT10 then
                if rem <= 3.0 then
                    return string.format("|cFFFF2222%.1fs|r", rem)
                else
                    return string.format("|cFFFFFF00%.1fs|r", rem)
                end
            else
                return string.format("|cFF33FFFF%.1fs|r", rem)
            end
        end
        return isT10 and "|cFFFFFF00T10|r" or "|cFF33FFFFON|r"
    else
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Stop(aura_env.region, "FMHUD_MI_GLOW")
        end
        if state == "COOLDOWN" and rem > 0.1 then
            if rem >= 60 then
                local m = math.floor(rem / 60)
                local s = math.floor(rem % 60)
                return string.format("%d:%02d", m, s)
            else
                return string.format("%.0f", rem)
            end
        end
        return ""
    end
end"""


def make_mirrorimage_custom_duration() -> str:
    """Durata e scadenza per lo swipe di Mirror Image / proc T10."""
    return """function()
    if not _G.FMHUD_CheckMirrorImage then return 0, 0 end
    local state, rem, dur = _G.FMHUD_CheckMirrorImage()
    if (state == "ACTIVE" or state == "COOLDOWN") and rem > 0 and dur > 0 then
        return dur, GetTime() + rem
    end
    return 0, 0
end"""


def make_mirrorimage_custom_icon() -> str:
    """Icona Quad Core (Spell_Nature_Invisibilty) durante il proc T10, altrimenti Mirror Image."""
    return """function()
    if not _G.FMHUD_CoreInitDone and _G.FMHUD_InitCore then _G.FMHUD_InitCore() end
    if _G.FMHUD_CheckMirrorImage then
        local state, rem, dur, icon, isT10 = _G.FMHUD_CheckMirrorImage()
        if icon then return icon end
    end
    local icon = select(3, GetSpellInfo(55342)) or select(3, GetSpellInfo("Mirror Image")) or select(3, GetSpellInfo("Immagine Speculare"))
    return icon or "Interface/Icons/Spell_Magic_LesserInvisibilty"
end"""


def make_managem_custom_text() -> str:
    """Testo descrittivo (%c) delle cariche effettive della Gemma del Mana (3, 2, 1, 0), con Pixel Glow durante proc T7."""
    return f"""function()
    _G.FMHUD_InitCore = _G.FMHUD_InitCore or {SHARED_CORE_BOOTSTRAP_LUA}
    if not _G.FMHUD_CoreInitDone then _G.FMHUD_InitCore() end
    if _G.FMHUD_UpdateUtilityRowPositions then
        _G.FMHUD_UpdateUtilityRowPositions()
    end
    if not _G.FMHUD_CheckManaGem then return "" end
    local state, rem, dur, icon = _G.FMHUD_CheckManaGem()
    local LCG = LibStub and LibStub("LibCustomGlow-1.0", true)

    if state == "ACTIVE" then
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Start(aura_env.region, {{1, 0.85, 0.1, 1}}, 8, 0.25, 10, 2, 0, 0, false, "FMHUD_T7_GLOW")
        end
    else
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Stop(aura_env.region, "FMHUD_T7_GLOW")
        end
    end

    if aura_env and aura_env.region and aura_env.region.subRegions then
        local timerSub = aura_env.region.subRegions[2]
        if timerSub and timerSub.text and timerSub.text.SetTextColor then
            if state == "ACTIVE" then
                timerSub.text:SetTextColor(1, 0.9, 0.1, 1)
            else
                timerSub.text:SetTextColor(1, 1, 1, 1)
            end
        end
    end

    local charges = _G.FMHUD_GetManaGemCharges and _G.FMHUD_GetManaGemCharges() or 0
    if charges > 0 then
        return string.format("%d", charges)
    else
        return "|cFFFF00000|r"
    end
end"""


def make_managem_custom_duration() -> str:
    """Durata e scadenza dello swipe per la Gemma del Mana (proc T7 o CD 2 min)."""
    return """function()
    if not _G.FMHUD_CheckManaGem then return 0, 0 end
    local state, rem, dur = _G.FMHUD_CheckManaGem()
    if (state == "ACTIVE" or state == "COOLDOWN") and rem > 0 and dur > 0 then
        return dur, GetTime() + rem
    end
    return 0, 0
end"""


def make_managem_custom_icon() -> str:
    """Icona della Gemma del Mana (Zaffiro / Smeraldo) o dell'Ondata di Mana (Proc T7)."""
    return """function()
    if _G.FMHUD_CheckManaGem then
        local state, rem, dur, icon = _G.FMHUD_CheckManaGem()
        if state == "ACTIVE" and icon then return icon end
    end
    if GetItemCount(33312) == 0 and GetItemCount(22044) > 0 then
        return GetItemIcon(22044) or "Interface/Icons/INV_Misc_Gem_Emerald_01"
    end
    return GetItemIcon(33312) or select(3, GetSpellInfo(5405)) or "Interface/Icons/INV_Misc_Gem_Sapphire_02"
end"""


# =============================================================================
# BUILDER: AURE WEAKAURAS PER LA FILA UTILITY
# =============================================================================
def build_utility_auras() -> list[dict]:
    """
    Costruisce e restituisce le 9 aure che compongono la fila utility inferiore:
    - 05 - Trinket 1 (Icon, Slot 13)
    - 06 - Trinket 2 (Icon, Slot 14)
    - 07 - Cloak (Icon, Slot 15)
    - 08 - Tier 8 (Icon, T8 2P)
    - 09 - Gloves (Icon, Slot 10 - Acceleratori Ipersonici Ingegneria)
    - 10 - Mana Gem (Icon, Gemma del Mana + Proc T7)
    - 11 - Combustion (Icon, Combustione)
    - 12 - Mirror Image (Icon, Copie + Bonus T10 4P)
    - 13 - Boots (Icon, Slot 8 - Acceleratori a Nitro o incanto speed)
    """
    events_list = "PLAYER_EQUIPMENT_CHANGED,UNIT_INVENTORY_CHANGED,PLAYER_ENTERING_WORLD,ZONE_CHANGED_NEW_AREA,UNIT_AURA,SPELL_UPDATE_COOLDOWN,ACTIONBAR_UPDATE_COOLDOWN,BAG_UPDATE_COOLDOWN,COMBAT_LOG_EVENT_UNFILTERED,FMHUD_ROW_UPDATE"

    return [
        # 05 - Trinket 1 (Slot 13)
        {
            "id": "05 - Trinket 1",
            "uid": "FMHUD_TRINKET1",
            "parent": "Class Mage (TTW Fire)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": -116,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_slot_custom_text(13),
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "events": events_list,
                        "custom": make_slot_trigger_custom(13),
                        "customDuration": make_slot_custom_duration(13),
                        "customIcon": make_slot_custom_icon(13, "Interface/Icons/INV_Misc_QuestionMark"),
                    },
                    "untrigger": {
                        "custom": make_slot_untrigger_custom(13)
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        },

        # 06 - Trinket 2 (Slot 14)
        {
            "id": "06 - Trinket 2",
            "uid": "FMHUD_TRINKET2",
            "parent": "Class Mage (TTW Fire)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": -87,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_slot_custom_text(14),
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "events": events_list,
                        "custom": make_slot_trigger_custom(14),
                        "customDuration": make_slot_custom_duration(14),
                        "customIcon": make_slot_custom_icon(14, "Interface/Icons/INV_Misc_QuestionMark"),
                    },
                    "untrigger": {
                        "custom": make_slot_untrigger_custom(14)
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        },

        # 07 - Cloak (Slot 15)
        {
            "id": "07 - Cloak",
            "uid": "FMHUD_CLOAK",
            "parent": "Class Mage (TTW Fire)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": -58,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface/Icons/INV_Misc_Cape_19",
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_slot_custom_text(15),
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "events": events_list,
                        "custom": make_slot_trigger_custom(15),
                        "customDuration": make_slot_custom_duration(15),
                        "customIcon": make_slot_custom_icon(15, "Interface/Icons/INV_Misc_Cape_19"),
                    },
                    "untrigger": {
                        "custom": make_slot_untrigger_custom(15)
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        },

        # 08 - Tier 8
        {
            "id": "08 - Tier 8",
            "uid": "FMHUD_TIER8",
            "parent": "Class Mage (TTW Fire)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": -29,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface/Icons/Spell_Arcane_StudentOfMagic",
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_t8_custom_text(),
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "events": events_list,
                        "custom": """function(event, ...)
    if not _G.FMHUD_CoreInitDone and _G.FMHUD_InitCore then _G.FMHUD_InitCore() end
    if not _G.FMHUD_CheckT8Equipped then return false end
    return _G.FMHUD_CheckT8Equipped()
end""",
                        "customDuration": make_t8_custom_duration(),
                        "customIcon": make_t8_custom_icon(),
                    },
                    "untrigger": {
                        "custom": """function(event, ...)
    if not _G.FMHUD_CheckT8Equipped then return true end
    return not _G.FMHUD_CheckT8Equipped()
end"""
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        },

        # 09 - Gloves (Slot 10 - Hyperspeed Accelerators)
        {
            "id": "09 - Gloves",
            "uid": "FMHUD_GLOVES",
            "parent": "Class Mage (TTW Fire)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": 0,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface/Icons/spell_nature_shamanrage",
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_slot_custom_text(10),
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "events": events_list,
                        "custom": make_slot_trigger_custom(10),
                        "customDuration": make_slot_custom_duration(10),
                        "customIcon": make_slot_custom_icon(10, "Interface/Icons/spell_nature_shamanrage"),
                    },
                    "untrigger": {
                        "custom": make_slot_untrigger_custom(10)
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        },

        # 10 - Mana Gem
        {
            "id": "10 - Mana Gem",
            "uid": "FMHUD_MANAGEM",
            "parent": "Class Mage (TTW Fire)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": 29,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface/Icons/INV_Misc_Gem_Sapphire_02",
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_managem_custom_text(),
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "custom": """function(event, ...)
    if not _G.FMHUD_CoreInitDone and _G.FMHUD_InitCore then _G.FMHUD_InitCore() end
    return true
end""",
                        "customDuration": make_managem_custom_duration(),
                        "customIcon": make_managem_custom_icon(),
                    },
                    "untrigger": {
                        "custom": """function(event, ...)
    return false
end"""
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext(
                    "%p",
                    justify="CENTER",
                    anchor_point="INNER_BOTTOM",
                    font_size=10,
                    y_offset=1,
                    extra_props={
                        "text_text_format_p_format": "timed",
                        "text_text_format_p_time_precision": 1,
                        "text_text_format_p_time_dynamic_threshold": 60,
                    }
                ),
                make_subtext(
                    "%c",
                    justify="RIGHT",
                    anchor_point="INNER_TOPRIGHT",
                    font_size=9,
                    extra_props={
                        "anchorXOffset": -1,
                        "anchorYOffset": -1,
                    }
                ),
            ],
        },

        # 11 - Combustion
        {
            "id": "11 - Combustion",
            "uid": "FMHUD_COMBUSTION",
            "parent": "Class Mage (TTW Fire)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": 58,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface/Icons/Spell_Fire_SealOfFire",
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_combustion_custom_text(),
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "custom": """function(event, ...)
    return true
end""",
                        "customDuration": make_combustion_custom_duration(),
                        "customIcon": make_combustion_custom_icon(),
                    },
                    "untrigger": {
                        "custom": """function(event, ...)
    return false
end"""
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        },

        # 12 - Mirror Image
        {
            "id": "12 - Mirror Image",
            "uid": "FMHUD_MIRRORIMAGE",
            "parent": "Class Mage (TTW Fire)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": 87,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface/Icons/Spell_Magic_LesserInvisibilty",
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_mirrorimage_custom_text(),
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "custom": """function(event, ...)
    return true
end""",
                        "customDuration": make_mirrorimage_custom_duration(),
                        "customIcon": make_mirrorimage_custom_icon(),
                    },
                    "untrigger": {
                        "custom": """function(event, ...)
    return false
end"""
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        },

        # 13 - Boots (Slot 8 - Nitro Boosts o Incanto Speed)
        {
            "id": "13 - Boots",
            "uid": "FMHUD_BOOTS",
            "parent": "Class Mage (TTW Fire)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": 116,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface/Icons/ability_rogue_sprint",
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_slot_custom_text(8),
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "events": events_list,
                        "custom": make_slot_trigger_custom(8),
                        "customDuration": make_slot_custom_duration(8),
                        "customIcon": make_slot_custom_icon(8, "Interface/Icons/ability_rogue_sprint"),
                    },
                    "untrigger": {
                        "custom": make_slot_untrigger_custom(8)
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        },
    ]


# =============================================================================
# NOTA OTTIMIZZAZIONE CPU/GC (FIX 3):
# - Integrazione Cache Buffs Condivisa (_G.FMHUD_GetPlayerBuffs):
#   All'interno di FMHUD_CheckSlotEquipped (slot 10, slot 8, slot 15) e in
#   FMHUD_CheckSlot, la ricerca dell'equipaggiamento attivo e dei proc di buff
#   sfrutta la cache centralizzata _G.FMHUD_GetPlayerBuffs().
#   Questo elimina scansioni multiple e concorrenti di UnitBuff("player", i) ad
#   ogni ciclo di ridisegno o cambio equipaggiamento, condividendo un'unica lista
#   indicizzata per spellId e nome con timestamp GetTime().
#   La cache viene invalidata istantaneamente su UNIT_AURA per il player
#   all'interno di FMHUD_LayoutFrame.
# =============================================================================
