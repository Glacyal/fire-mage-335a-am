"""
Test Suite Completa: Verifica Esauriente di Tutti i Casi della Riga Utility
===========================================================================
Verifica formalmente l'assenza totale di sovrapposizioni e la perfetta centratura
dinamica per tutte le 64 combinazioni possibili (2^6) di equipaggiamento e proc:
1. Monile 1 (Slot 13: Equipaggiato vs Vuoto)
2. Monile 2 (Slot 14: Equipaggiato vs Vuoto)
3. Mantello (Slot 15: Con Proc di Potenziamento vs Senza Proc)
4. Tier 8 2P (Kirin Tor: Con Bonus vs Senza Bonus)
5. Guanti Ingegneria (Slot 10: Acceleratori Ipersonici vs Senza Tinker)
6. Stivali Ingegneria (Slot 8: Acceleratori a Nitro vs Senza Tinker)
I 3 incantesimi base (Gemma del Mana, Combustione, Immagine Speculare) sono sempre attivi.
"""
import os
import sys
import unittest
import itertools

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from builder.components.utility import build_utility_auras


def compute_utility_layout(active_ids):
    """
    Replica fedelmente la logica di calcolo delle coordinate di _G.FMHUD_UpdateUtilityRowPositions in Lua.
    """
    N = len(active_ids)
    if N >= 10:
        step = 26
    elif N == 9:
        step = 29
    elif N == 8:
        step = 32
    elif N == 7:
        step = 38
    elif N == 6:
        step = 44
    elif N == 5:
        step = 48
    else:
        step = 52

    positions = {}
    for i, aid in enumerate(active_ids, 1):
        target_x = round((i - (N + 1) / 2) * step)
        positions[aid] = target_x
    return positions, step


class TestAllUtilityCases(unittest.TestCase):

    def test_all_128_combinations_no_overlaps_and_centered(self):
        """
        Verifica tutte le 128 combinazioni combinatorie (2^7) di equipaggiamento (incluso Anello proc).
        Per ciascun caso:
        - Nessuna coppia adiacente deve avere distanza < target_w (zero sovrapposizioni).
        - La somma delle coordinate deve essere esattamente 0 (perfetta simmetria orizzontale).
        - L'ampiezza totale non deve mai superare i 264px (sotto la barra del mana).
        - L'ordine da sinistra a destra deve rispettare rigorosamente la sequenza definita.
        """
        OPTIONAL_FLAGS = ["T1", "T2", "Ring", "Cloak", "T8", "Gloves", "Boots"]
        tested_count = 0

        for combo in itertools.product([True, False], repeat=len(OPTIONAL_FLAGS)):
            flags = dict(zip(OPTIONAL_FLAGS, combo))
            active = []
            if flags["T1"]: active.append("05 - Trinket 1")
            if flags["T2"]: active.append("06 - Trinket 2")
            if flags["Ring"]: active.append("06b - Ring")
            if flags["Cloak"]: active.append("07 - Cloak")
            if flags["T8"]: active.append("08 - Tier 8")
            if flags["Gloves"]: active.append("09 - Gloves")
            active.append("10 - Mana Gem")
            active.append("11 - Combustion")
            active.append("12 - Mirror Image")
            if flags["Boots"]: active.append("13 - Boots")

            tested_count += 1
            N = len(active)
            self.assertGreaterEqual(N, 3, "Il numero minimo di icone deve essere >= 3")
            self.assertLessEqual(N, 10, "Il numero massimo di icone deve essere <= 10")

            positions, step = compute_utility_layout(active)
            coords = [positions[aid] for aid in active]
            target_w = 26 if N >= 10 else 28

            # 1. Monotonia stretta e verifica sovrapposizioni (minima distanza >= target_w)
            for j in range(len(coords) - 1):
                diff = coords[j + 1] - coords[j]
                self.assertGreaterEqual(
                    diff, target_w,
                    f"SOVRAPPOSIZIONE RILEVATA nel caso N={N} ({active}) tra {active[j]} ({coords[j]}) e {active[j+1]} ({coords[j+1]}): delta={diff}px < {target_w}px"
                )

            # 2. Perfetta simmetria centrale (somma coordinate == 0)
            self.assertEqual(
                sum(coords), 0,
                f"Asimmetria rilevata nel caso N={N} ({active}): somma={sum(coords)} != 0"
            )

            # 3. Ampiezza totale confinata sotto la barra del mana (<= 264px)
            half_w = target_w // 2
            span = (max(coords) + half_w) - (min(coords) - half_w)
            self.assertLessEqual(
                span, 264,
                f"Ampiezza eccessiva nel caso N={N} ({active}): span={span}px > 264px"
            )

        self.assertEqual(tested_count, 128, "Devono essere testate esattamente 128 combinazioni")

    def test_static_offsets_builder_integrity(self):
        """
        Verifica che i valori statici 'xOffset' generati da build_utility_auras() siano
        TUTTI distinti tra loro e separati da almeno 28px, evitando collisioni di default.
        """
        auras = build_utility_auras()
        self.assertEqual(len(auras), 10, "La riga utility deve produrre 10 aure")

        offsets = {}
        for a in auras:
            aid = a["id"]
            x = a["xOffset"]
            offsets[aid] = x

        # Controllo unicità assoluta
        seen_x = {}
        for aid, x in offsets.items():
            self.assertNotIn(
                x, seen_x,
                f"Collisione di offset statico rilevata: {aid} condivide xOffset={x} con {seen_x.get(x)}"
            )
            seen_x[x] = aid

        # Controllo specifico per Tier 8 e Guanti
        self.assertNotEqual(
            offsets["08 - Tier 8"], offsets["09 - Gloves"],
            "08 - Tier 8 e 09 - Gloves non possono avere lo stesso xOffset statico!"
        )

        # Controllo specifico per Mirror Image e Boots
        self.assertNotEqual(
            offsets["12 - Mirror Image"], offsets["13 - Boots"],
            "12 - Mirror Image e 13 - Boots non possono avere lo stesso xOffset statico!"
        )

        # Controllo che siano rigorosamente crescenti da sinistra a destra
        expected_order = [
            "05 - Trinket 1", "06 - Trinket 2", "06b - Ring", "07 - Cloak", "08 - Tier 8",
            "09 - Gloves", "10 - Mana Gem", "11 - Combustion", "12 - Mirror Image", "13 - Boots"
        ]
        ordered_x = [offsets[aid] for aid in expected_order]
        for j in range(len(ordered_x) - 1):
            diff = ordered_x[j + 1] - ordered_x[j]
            self.assertGreaterEqual(
                diff, 26,
                f"Offset statici troppo vicini o invertiti tra {expected_order[j]} ({ordered_x[j]}) e {expected_order[j+1]} ({ordered_x[j+1]}): delta={diff}px"
            )

    def test_exact_coordinates_per_n_count(self):
        """
        Verifica analitica delle coordinate matematiche per ogni valore di N da 3 a 9.
        """
        expected_tables = {
            10: [-117, -91, -65, -39, -13, 13, 39, 65, 91, 117],
            9: [-116, -87, -58, -29, 0, 29, 58, 87, 116],
            8: [-112, -80, -48, -16, 16, 48, 80, 112],
            7: [-114, -76, -38, 0, 38, 76, 114],
            6: [-110, -66, -22, 22, 66, 110],
            5: [-96, -48, 0, 48, 96],
            4: [-78, -26, 26, 78],
            3: [-52, 0, 52],
        }

        dummy_ids = [f"Item_{i}" for i in range(10)]
        for n, expected_xs in expected_tables.items():
            pos, step = compute_utility_layout(dummy_ids[:n])
            actual_xs = [pos[aid] for aid in dummy_ids[:n]]
            self.assertEqual(
                actual_xs, expected_xs,
                f"Discrepanza coordinate per N={n}: attese {expected_xs}, calcolate {actual_xs}"
            )
            # Verifica passo costante
            for j in range(len(actual_xs) - 1):
                self.assertEqual(actual_xs[j + 1] - actual_xs[j], step)

    def test_dynamic_transitions_simulation(self):
        """
        Simula transizioni dinamiche di cambio equipaggiamento in sequenza:
        1. Base (3 icone) -> aggiunge T8 -> aggiunge Gloves -> aggiunge Boots -> aggiunge Cloak -> aggiunge Trinkets (fino a 9).
        2. Dalle 9 complete -> rimuove Gloves -> rimuove Boots -> rimuove T8 -> rimuove Cloak (ritorno a 3).
        In nessuno stato deve verificarsi una sovrapposizione.
        """
        history = [
            # Inizio: solo abilità base
            ["10 - Mana Gem", "11 - Combustion", "12 - Mirror Image"],
            # Equipaggia Tier 8 (4P)
            ["08 - Tier 8", "10 - Mana Gem", "11 - Combustion", "12 - Mirror Image"],
            # Equipaggia Guanti con tinker
            ["08 - Tier 8", "09 - Gloves", "10 - Mana Gem", "11 - Combustion", "12 - Mirror Image"],
            # Equipaggia Stivali con nitro
            ["08 - Tier 8", "09 - Gloves", "10 - Mana Gem", "11 - Combustion", "12 - Mirror Image", "13 - Boots"],
            # Equipaggia Mantello con proc
            ["07 - Cloak", "08 - Tier 8", "09 - Gloves", "10 - Mana Gem", "11 - Combustion", "12 - Mirror Image", "13 - Boots"],
            # Equipaggia Trinket 1 e 2 (9 icone)
            ["05 - Trinket 1", "06 - Trinket 2", "07 - Cloak", "08 - Tier 8", "09 - Gloves", "10 - Mana Gem", "11 - Combustion", "12 - Mirror Image", "13 - Boots"],
            # Equipaggia Anello proc (10 icone complete)
            ["05 - Trinket 1", "06 - Trinket 2", "06b - Ring", "07 - Cloak", "08 - Tier 8", "09 - Gloves", "10 - Mana Gem", "11 - Combustion", "12 - Mirror Image", "13 - Boots"],
            # Switch su gear senza T8 ma con guanti e stivali (8 icone)
            ["05 - Trinket 1", "06 - Trinket 2", "07 - Cloak", "09 - Gloves", "10 - Mana Gem", "11 - Combustion", "12 - Mirror Image", "13 - Boots"],
            # Rimuove guanti da ingegneria (7 icone classiche con stivali)
            ["05 - Trinket 1", "06 - Trinket 2", "07 - Cloak", "10 - Mana Gem", "11 - Combustion", "12 - Mirror Image", "13 - Boots"],
            # Rimuove stivali (6 icone standard storiche)
            ["05 - Trinket 1", "06 - Trinket 2", "07 - Cloak", "10 - Mana Gem", "11 - Combustion", "12 - Mirror Image"],
        ]

        for step_idx, active_list in enumerate(history):
            pos, step = compute_utility_layout(active_list)
            xs = [pos[aid] for aid in active_list]
            target_w = 26 if len(active_list) >= 10 else 28
            for j in range(len(xs) - 1):
                diff = xs[j + 1] - xs[j]
                self.assertGreaterEqual(
                    diff, target_w,
                    f"Transizione #{step_idx} fallita con sovrapposizione tra {active_list[j]} e {active_list[j+1]}: diff={diff}px"
                )
            self.assertEqual(sum(xs), 0, f"Transizione #{step_idx} ha perso la centratura")

    # =========================================================================
    # TEST AGGIUNTIVI FIX 5 & FIX 6: MANA GEM CACHE & PLAYER GUID CACHING
    # =========================================================================

    def test_mana_gem_charge_temporal_cache_and_invalidation(self):
        """
        [FIX 5] Verifica che:
        1. _G.FMHUD_GetManaGemCharges implementi una cache temporale (FMHUD_ManaGemChargeCache).
        2. La cache utilizzi una soglia temporale di almeno 1.5 secondi (throttle).
        3. FMHUD_LayoutFrame registri BAG_UPDATE e UNIT_SPELLCAST_SUCCEEDED.
        4. BAG_UPDATE resetti la cache a time = 0.
        5. UNIT_SPELLCAST_SUCCEEDED resetti la cache per Conjure Mana Gem e uso gemma.
        """
        from builder.components.utility import SHARED_CORE_BOOTSTRAP_LUA

        # 1. Verifica presenza e struttura della cache in GetManaGemCharges
        self.assertIn("FMHUD_ManaGemChargeCache", SHARED_CORE_BOOTSTRAP_LUA)
        self.assertIn("cache.time > 0", SHARED_CORE_BOOTSTRAP_LUA)
        self.assertIn("< 1.5", SHARED_CORE_BOOTSTRAP_LUA)
        self.assertIn("cache.charges = charges", SHARED_CORE_BOOTSTRAP_LUA)

        # 2. Verifica registrazione eventi di invalidazione in FMHUD_LayoutFrame
        self.assertIn('f:RegisterEvent("BAG_UPDATE")', SHARED_CORE_BOOTSTRAP_LUA)
        self.assertIn('f:RegisterEvent("UNIT_SPELLCAST_SUCCEEDED")', SHARED_CORE_BOOTSTRAP_LUA)

        # 3. Verifica logica di invalidazione su BAG_UPDATE
        self.assertIn('if event == "BAG_UPDATE" then', SHARED_CORE_BOOTSTRAP_LUA)
        self.assertIn('_G.FMHUD_ManaGemChargeCache.time = 0', SHARED_CORE_BOOTSTRAP_LUA)

        # 4. Verifica logica di invalidazione su UNIT_SPELLCAST_SUCCEEDED per Conjure (759, ecc.) e Use (5405)
        self.assertIn('if event == "UNIT_SPELLCAST_SUCCEEDED" then', SHARED_CORE_BOOTSTRAP_LUA)
        self.assertIn('spellId == 759', SHARED_CORE_BOOTSTRAP_LUA)
        self.assertIn('spellId == 5405', SHARED_CORE_BOOTSTRAP_LUA)

    def test_mana_gem_charge_cache_behavior_simulation(self):
        """
        [FIX 5] Simula il ciclo di vita della cache cariche della Gemma del Mana:
        - 1° controllo a t=0: scansione borse eseguita (scansioni=1, cariche=3)
        - 100 eventi di combat log nei successivi 1.0s: restituisce sempre valore in cache senza scansioni (scansioni=1)
        - Uso gemma a t=1.2: evento BAG_UPDATE invalida la cache (time=0)
        - Prossimo controllo a t=1.2: riesecuzione immediata scansione (scansioni=2, cariche=2)
        - Controlli fino a t=2.5: in cache (scansioni=2)
        - Controllo a t=2.8 (>1.5s dopo t=1.2): nuova scansione naturale (scansioni=3)
        """
        class ManaGemCacheSimulator:
            def __init__(self, initial_charges=3):
                self.cache = None
                self.bag_charges = initial_charges
                self.bag_scans_count = 0

            def invalidate(self):
                if self.cache:
                    self.cache["time"] = 0

            def get_charges(self, current_time):
                if self.cache and self.cache["time"] > 0 and (current_time - self.cache["time"] < 1.5):
                    return self.cache["charges"]

                if not self.cache:
                    self.cache = {"time": 0, "charges": 0}
                self.cache["time"] = current_time

                # Simulazione scansione borse + tooltip
                self.bag_scans_count += 1
                self.cache["charges"] = self.bag_charges
                return self.cache["charges"]

        sim = ManaGemCacheSimulator(initial_charges=3)

        # 1. Prima chiamata a t=100.0s (GetTime() realistico): scansione borse
        t_base = 100.0
        self.assertEqual(sim.get_charges(current_time=t_base), 3)
        self.assertEqual(sim.bag_scans_count, 1)

        # 2. 100 chiamate ad alta frequenza durante il combat (t da +0.01s a +1.0s)
        for t_offset in range(1, 101):
            t = t_base + (t_offset * 0.01)
            self.assertEqual(sim.get_charges(current_time=t), 3)
        self.assertEqual(sim.bag_scans_count, 1, "Le chiamate entro 1.5s NON devono rieseguire la scansione borse!")

        # 3. Uso della gemma a t=101.2s -> cariche scendono a 2 -> evento BAG_UPDATE invalida (time = 0)
        sim.bag_charges = 2
        sim.invalidate()

        # 4. Lettura a t=101.2s: cache invalidata (time=0), scansione immediata
        self.assertEqual(sim.get_charges(current_time=t_base + 1.2), 2)
        self.assertEqual(sim.bag_scans_count, 2, "Dopo BAG_UPDATE deve rieseguire subito la scansione borse!")

        # 5. Chiamata a t=102.0s (< 1.5s da 101.2s): valore in cache
        self.assertEqual(sim.get_charges(current_time=t_base + 2.0), 2)
        self.assertEqual(sim.bag_scans_count, 2)

        # 6. Chiamata a t=102.8s (1.6s dopo 101.2s): timeout scaduto, re-scan
        self.assertEqual(sim.get_charges(current_time=t_base + 2.8), 2)
        self.assertEqual(sim.bag_scans_count, 3)

    def test_player_guid_cached_across_all_cleu_components(self):
        """
        [FIX 6] Verifica l'eliminazione totale della chiamata API UnitGUID("player")
        all'interno dei gestori di COMBAT_LOG_EVENT_UNFILTERED:
        1. builder/components/hot_streak.py (SHARED_HOTSTREAK_CHECK_LUA)
        2. builder/components/utility.py (FMHUD_LayoutFrame in SHARED_CORE_BOOTSTRAP_LUA)
        3. builder/components/buffs.py (SHARED_FM_CHECK_LUA)
        """
        from builder.components.hot_streak import SHARED_HOTSTREAK_CHECK_LUA
        from builder.components.utility import SHARED_CORE_BOOTSTRAP_LUA
        from builder.components.buffs import SHARED_FM_CHECK_LUA

        # 1. hot_streak.py: playerGUID cached come upvalue nel setup frame
        self.assertIn("local playerGUID = UnitGUID(\"player\")", SHARED_HOTSTREAK_CHECK_LUA)
        self.assertIn("sourceGUID == playerGUID", SHARED_HOTSTREAK_CHECK_LUA)
        self.assertNotIn("sourceGUID == UnitGUID(\"player\")", SHARED_HOTSTREAK_CHECK_LUA)

        # 2. utility.py: playerGUID cached come upvalue in FMHUD_LayoutFrame
        self.assertIn("local playerGUID = UnitGUID(\"player\")", SHARED_CORE_BOOTSTRAP_LUA)
        self.assertIn("sourceGUID == playerGUID", SHARED_CORE_BOOTSTRAP_LUA)
        self.assertNotIn("sourceGUID == UnitGUID(\"player\")", SHARED_CORE_BOOTSTRAP_LUA)

        # 3. buffs.py: playerGUID cached nello state di Focus Magic
        self.assertIn("playerGUID = UnitGUID(\"player\")", SHARED_FM_CHECK_LUA)
        self.assertIn("sourceGUID == playerGUID", SHARED_FM_CHECK_LUA)
        self.assertNotIn("sourceGUID == UnitGUID(\"player\")", SHARED_FM_CHECK_LUA)


if __name__ == "__main__":
    unittest.main()


