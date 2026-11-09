"""
Test di Integrità e Robustezza Architetturale dei Componenti WeakAuras
=====================================================================
Verifica la conformità di tutti i 7 moduli in builder/components/:
- Correttezza delle strutture dati e assenza di campi mancanti
- Unicità assoluta di tutti gli ID e UID
- Integrità referenziale tra controlledChildren e nodi figli
- Conformità con WeakAuras 4.0.0
"""
import os
import sys
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from builder.tree import build_wa_tree
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


class TestComponentsIntegrity(unittest.TestCase):

    def test_each_component_produces_auras(self):
        """Verifica che ogni modulo builder produca una lista non vuota di dizionari."""
        components = [
            ("procs", build_procs_auras()),
            ("buffs", build_buffs_auras()),
            ("utility", build_utility_auras()),
            ("bars", build_bars_auras()),
            ("hotstreak", build_hotstreak_auras()),
            ("alerts", build_alerts_auras()),
            ("stats", build_stats_auras()),
            ("multi_lb", build_multi_lb_auras()),
        ]
        for name, auras in components:
            self.assertIsInstance(auras, list, f"Componente {name} non restituisce una lista")
            self.assertGreater(len(auras), 0, f"Componente {name} restituisce una lista vuota")
            for a in auras:
                self.assertIsInstance(a, dict, f"Un elemento in {name} non è un dizionario")
                self.assertIn("id", a, f"Elemento in {name} privo di 'id'")
                self.assertIn("uid", a, f"Elemento in {name} privo di 'uid'")
                self.assertIn("regionType", a, f"Elemento in {name} privo di 'regionType'")

    def test_total_aura_count_and_uniqueness(self):
        """Verifica il conteggio totale delle aure (44) e l'unicità di ID e UID."""
        tree = build_wa_tree()
        children = tree["c"]
        self.assertEqual(len(children), 45, f"Previste 45 aure, trovate {len(children)}")

        seen_ids = set()
        seen_uids = set()
        for a in children:
            aid = a["id"]
            auid = a["uid"]
            self.assertNotIn(aid, seen_ids, f"ID duplicato rilevato: {aid}")
            self.assertNotIn(auid, seen_uids, f"UID duplicato rilevato: {auid}")
            seen_ids.add(aid)
            seen_uids.add(auid)

    def test_referential_integrity(self):
        """Verifica che ogni aura referenziata in controlledChildren esista realmente."""
        tree = build_wa_tree()
        root = tree["d"]
        all_ids = {a["id"] for a in tree["c"]}

        # Controlla la radice
        for child_id in root["controlledChildren"]:
            self.assertIn(child_id, all_ids, f"Radice referenzia figlio inesistente: {child_id}")

        # Controlla i gruppi intermedi
        for a in tree["c"]:
            if "controlledChildren" in a:
                for child_id in a["controlledChildren"]:
                    self.assertIn(child_id, all_ids, f"Gruppo {a['id']} referenzia figlio inesistente: {child_id}")

    def test_procs_children_order(self):
        """Verifica che 01 - Procs contenga Pyroblast immediatamente a destra di Living Bomb."""
        tree = build_wa_tree()
        procs_dg = next(a for a in tree["c"] if a["id"] == "01 - Procs")
        children = procs_dg["controlledChildren"]
        self.assertIn("Living Bomb", children)
        self.assertIn("Pyroblast", children)
        lb_idx = children.index("Living Bomb")
        pyro_idx = children.index("Pyroblast")
        self.assertEqual(pyro_idx, lb_idx + 1, "Pyroblast deve essere posizionato immediatamente a destra di Living Bomb")

    def test_castbar_spell_icon_enabled(self):
        """Verifica che 16 - Castbar abbia l'icona della spell attiva abilitata a sinistra."""
        tree = build_wa_tree()
        castbar = next((a for a in tree["c"] if a.get("id") == "16 - Castbar"), None)
        self.assertIsNotNone(castbar, "16 - Castbar non trovata nell'albero")
        self.assertTrue(castbar.get("icon"), "L'icona della spell sulla castbar deve essere True")
        self.assertEqual(castbar.get("icon_side"), "LEFT", "L'icona della spell deve essere posizionata a sinistra (LEFT)")
        self.assertEqual(castbar.get("iconSource"), -1, "iconSource deve essere -1 (automatico da trigger/spell)")

    def test_controlled_children_continuous_numbering(self):
        """Verifica che le voci abbiano numerazione continua da 01 a 19 con '06b - Ring' interposto (Opzione B)."""
        tree = build_wa_tree()
        children = tree["d"]["controlledChildren"]
        self.assertEqual(len(children), 20, f"Previsti 20 controlledChildren, trovati {len(children)}")
        # Controlla 01 - Procs fino a 06 - Trinket 2
        for i in range(1, 7):
            expected_prefix = f"{i:02d} - "
            self.assertTrue(children[i - 1].startswith(expected_prefix))
        # Controlla 06b - Ring
        self.assertEqual(children[6], "06b - Ring")
        # Controlla 07 - Cloak fino a 19 - Multi-Target Living Bomb
        for i in range(7, 20):
            expected_prefix = f"{i:02d} - "
            self.assertTrue(children[i].startswith(expected_prefix))

    def test_molten_fury_unit_filter_in_lua_code(self):
        """
        [FIX 7] Verifica statica della presenza del filtro sull'unità nel trigger e untrigger di Molten Fury:
        1. Entrambe le funzioni devono estrarre l'unità (local unit = ...)
        2. Entrambe le funzioni devono avere l'early return se unit ~= "target" per UNIT_HEALTH/UNIT_MAXHEALTH
        3. Entrambe devono preservare la soglia del 35% HP
        4. Nessuna chiamata UnitExists/UnitHealth deve essere eseguita prima del filtro unit
        """
        auras = build_procs_auras()
        mf_aura = next((a for a in auras if a.get("id") == "Molten Fury"), None)
        self.assertIsNotNone(mf_aura, "Aura 'Molten Fury' non trovata in procs.py")

        trigger_data = mf_aura["triggers"][1]["trigger"]
        untrigger_data = mf_aura["triggers"][1]["untrigger"]

        custom_code = trigger_data["custom"]
        untrigger_code = untrigger_data["custom"]

        # 1. Verifica estrazione unità e controllo early return in custom
        self.assertIn("local unit = ...", custom_code, "custom di Molten Fury deve estrarre l'unità con 'local unit = ...'")
        self.assertIn('event == "UNIT_HEALTH" or event == "UNIT_MAXHEALTH"', custom_code)
        self.assertIn('unit ~= "target"', custom_code)
        self.assertIn("_G.FMHUD_MF_Active", custom_code)

        # 2. Verifica estrazione unità e controllo early return in untrigger
        self.assertIn("local unit = ...", untrigger_code, "untrigger di Molten Fury deve estrarre l'unità con 'local unit = ...'")
        self.assertIn('event == "UNIT_HEALTH" or event == "UNIT_MAXHEALTH"', untrigger_code)
        self.assertIn('unit ~= "target"', untrigger_code)
        self.assertIn("_G.FMHUD_MF_Active", untrigger_code)

        # 3. Verifica presenza del commento esplicativo in italiano
        self.assertIn("Filtro sull'unità", custom_code, "custom deve includere il commento in italiano sul filtro unità")
        self.assertIn("Filtro sull'unità", untrigger_code, "untrigger deve includere il commento in italiano sul filtro unità")

        # 4. Verifica che il controllo UnitExists avvenga DOPO il controllo unit
        unit_filter_pos_custom = custom_code.find('unit ~= "target"')
        unit_exists_pos_custom = custom_code.find('UnitExists("target")')
        self.assertLess(unit_filter_pos_custom, unit_exists_pos_custom, "In custom, il filtro sull'unità deve precedere UnitExists('target')")

        unit_filter_pos_untrigger = untrigger_code.find('unit ~= "target"')
        unit_exists_pos_untrigger = untrigger_code.find('UnitExists("target")')
        self.assertLess(unit_filter_pos_untrigger, unit_exists_pos_untrigger, "In untrigger, il filtro sull'unità deve precedere UnitExists('target')")

        # 5. Verifica che la soglia del 35% sia inalterata
        self.assertIn("35.0", custom_code)
        self.assertIn("35.0", untrigger_code)

    def test_subtext_anchor_point_dual_keys_and_offsets(self):
        """Verifica che tutte le subRegion di tipo subtext abbiano le chiavi anchor_point, anchorPoint, text_anchorPoint e offset."""
        tree = build_wa_tree()
        all_d = [tree["d"]] + tree["c"]
        subtext_count = 0
        for aura in all_d:
            subregions = aura.get("subRegions", [])
            for sub in subregions:
                if sub.get("type") == "subtext":
                    subtext_count += 1
                    self.assertIn("anchor_point", sub, f"anchor_point mancante nell'aura {aura.get('id')}")
                    self.assertIn("anchorPoint", sub, f"anchorPoint mancante nell'aura {aura.get('id')}")
                    self.assertIn("text_anchorPoint", sub, f"text_anchorPoint mancante nell'aura {aura.get('id')}")
                    self.assertEqual(sub["anchor_point"], sub["anchorPoint"])
                    self.assertEqual(sub["anchor_point"], sub["text_anchorPoint"])
                    self.assertIn("anchorXOffset", sub)
                    self.assertIn("anchorYOffset", sub)
                    self.assertIn("text_anchorXOffset", sub)
                    self.assertIn("text_anchorYOffset", sub)
        self.assertGreater(subtext_count, 15, "Numero insufficiente di subtext rilevati")

    def test_specific_bars_and_gem_text_anchors(self):
        """Verifica che 14 - Mana Bar, 16 - Castbar e 10 - Mana Gem abbiano gli ancoraggi conformi alle richieste visive."""
        tree = build_wa_tree()
        all_d = {a.get("id"): a for a in [tree["d"]] + tree["c"]}
        
        # 14 - Mana Bar: centrato
        mana_bar = all_d.get("14 - Mana Bar")
        self.assertIsNotNone(mana_bar)
        mana_subtexts = [s for s in mana_bar.get("subRegions", []) if s.get("type") == "subtext"]
        self.assertEqual(len(mana_subtexts), 1)
        self.assertEqual(mana_subtexts[0]["anchor_point"], "CENTER")
        self.assertEqual(mana_subtexts[0]["text_justify"], "CENTER")

        # 16 - Castbar: nome a sinistra, tempo a destra
        castbar = all_d.get("16 - Castbar")
        self.assertIsNotNone(castbar)
        cast_subtexts = [s for s in castbar.get("subRegions", []) if s.get("type") == "subtext"]
        self.assertEqual(len(cast_subtexts), 2)
        self.assertEqual(cast_subtexts[0]["text_text"], "%n")
        self.assertEqual(cast_subtexts[0]["anchor_point"], "INNER_LEFT")
        self.assertEqual(cast_subtexts[1]["text_text"], "%p")
        self.assertEqual(cast_subtexts[1]["anchor_point"], "INNER_RIGHT")

        # 10 - Mana Gem: timer su INNER_BOTTOM e cariche su INNER_TOPRIGHT
        mana_gem = all_d.get("10 - Mana Gem")
        self.assertIsNotNone(mana_gem)
        gem_subtexts = [s for s in mana_gem.get("subRegions", []) if s.get("type") == "subtext"]
        self.assertEqual(len(gem_subtexts), 2)
        self.assertEqual(gem_subtexts[0]["text_text"], "%p")
        self.assertEqual(gem_subtexts[0]["anchor_point"], "INNER_BOTTOM")
        self.assertEqual(gem_subtexts[1]["text_text"], "%c")
        self.assertEqual(gem_subtexts[1]["anchor_point"], "INNER_TOPRIGHT")


if __name__ == "__main__":
    unittest.main()
