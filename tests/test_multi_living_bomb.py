"""
Test di Validazione per il Componente: 19 - Multi-Target Living Bomb Tracker
===========================================================================
Verifica:
1. Integrità del Dynamic Group e delle 5 icone tracker (24x24 px).
2. Configurazione di posizionamento: xOffset = 169, grow = 'DOWN', space = 3.
3. Presenza del trigger custom con ordinamento FIFO inverso (_G.FMHUD_GetActiveLivingBombs).
4. Correttezza del customText (timer allerta rossa <= 3s, secondi interi > 3s).
5. Integrazione completa nell'albero gerarchico Class Mage (TTW Fire).
"""
import os
import sys
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from builder.tree import build_wa_tree
from builder.components.multi_lb import build_multi_lb_auras


class TestMultiLivingBomb(unittest.TestCase):

    def test_multi_lb_component_auras(self):
        """Verifica che il modulo generi esattamente 6 elementi (1 gruppo + 5 icone)."""
        auras = build_multi_lb_auras()
        self.assertEqual(len(auras), 6, f"Previste 6 aure in multi_lb, trovate {len(auras)}")

        grp = auras[0]
        self.assertEqual(grp["id"], "19 - Multi-Target Living Bomb")
        self.assertEqual(grp["regionType"], "dynamicgroup")
        self.assertEqual(grp["grow"], "DOWN")
        self.assertEqual(grp["space"], 3)
        self.assertEqual(grp["xOffset"], 169)
        self.assertEqual(grp["yOffset"], 45)
        self.assertEqual(len(grp["controlledChildren"]), 5)

        for i in range(1, 6):
            expected_id = f"Living Bomb Tracker {i}"
            icon = next((a for a in auras if a.get("id") == expected_id), None)
            self.assertIsNotNone(icon, f"Icona {expected_id} non trovata")
            self.assertEqual(icon["regionType"], "icon")
            self.assertEqual(icon["parent"], "19 - Multi-Target Living Bomb")
            self.assertEqual(icon["width"], 24)
            self.assertEqual(icon["height"], 24)
            self.assertEqual(icon["displayIcon"], "Interface\\Icons\\Ability_Mage_LivingBomb")
            self.assertTrue(icon["cooldown"])
            self.assertTrue(icon["cooldownSwipe"])
            self.assertTrue(icon["cooldownEdge"])
            self.assertTrue(icon["cooldownTextDisabled"])

            # Custom text
            ct = icon["customText"]
            self.assertIn("FMHUD_GetActiveLivingBombs", ct)
            self.assertIn(f"list[{i}]", ct)
            self.assertIn("|cFFFF4444%.1fs|r", ct)

            # Trigger
            trig = icon["triggers"][1]["trigger"]
            self.assertEqual(trig["type"], "custom")
            self.assertEqual(trig["custom_type"], "status")
            self.assertEqual(trig["check"], "event")
            self.assertIn("FMHUD_LB_UPDATE", trig["events"])
            self.assertIn("FMHUD_GetActiveLivingBombs", trig["custom"])
            self.assertIn(f"list[{i}]", trig["custom"])

    def test_tree_integration(self):
        """Verifica la corretta integrazione nel tree master."""
        tree = build_wa_tree()
        root = tree["d"]
        self.assertIn("19 - Multi-Target Living Bomb", root["controlledChildren"])

        children_ids = {a["id"] for a in tree["c"]}
        self.assertIn("19 - Multi-Target Living Bomb", children_ids)
        for i in range(1, 6):
            self.assertIn(f"Living Bomb Tracker {i}", children_ids)


if __name__ == "__main__":
    unittest.main()

