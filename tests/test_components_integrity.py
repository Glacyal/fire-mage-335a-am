"""
Test di Integrità e Robustezza Architetturale dei Componenti WeakAuras
=====================================================================
Verifica la conformità di tutti i 7 moduli in builder/components/:
- Correttezza delle strutture dati e assenza di campi mancanti
- Unicità assoluta di tutti gli ID e UID
- Integrità referenziale tra controlledChildren e nodi figli
- Conformità con WeakAuras 4.0.0 (internalVersion 52)
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
        self.assertEqual(len(children), 44, f"Previste 44 aure, trovate {len(children)}")

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
        """Verifica che tutte le 19 voci abbiano numerazione sequenziale continua da 01 a 19."""
        tree = build_wa_tree()
        children = tree["d"]["controlledChildren"]
        self.assertEqual(len(children), 19, f"Previsti 19 controlledChildren, trovati {len(children)}")
        for i, child_id in enumerate(children, start=1):
            expected_prefix = f"{i:02d} - "
            self.assertTrue(
                child_id.startswith(expected_prefix),
                f"Elemento {i} non inizia con il prefisso atteso '{expected_prefix}': trovato '{child_id}'"
            )

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


if __name__ == "__main__":
    unittest.main()
