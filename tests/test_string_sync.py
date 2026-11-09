"""
Test di Sincronizzazione Stringhe di Importazione WeakAuras
==========================================================
Verifica la sincronizzazione e l'integrità di entrambe le stringhe:
1. 'IMPORT_STRING.txt': Congelata permanentemente per WeakAuras 4.0.0.
   Verifica che sia identica al backup certificato 'IMPORT_STRING_v4.0.0.txt'.
2. 'IMPORT_STRING_5.21.8.txt': Versione nativa WeakAuras 5.21.8+ (internalVersion 90).
   Verifica che corrisponda esattamente all'output di 'build_wa_tree("5.21.8")'.
"""
import os
import sys
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from builder.core import generate_wa_string
from builder.tree import build_wa_tree


class TestStringSync(unittest.TestCase):

    def test_frozen_legacy_string_integrity(self):
        """Verifica che IMPORT_STRING.txt sia intatta e identica al backup congelato v4.0.0."""
        legacy_path = os.path.join(ROOT_DIR, "IMPORT_STRING.txt")
        backup_path = os.path.join(ROOT_DIR, "IMPORT_STRING_v4.0.0.txt")

        self.assertTrue(os.path.exists(legacy_path), "IMPORT_STRING.txt deve esistere")
        self.assertTrue(os.path.exists(backup_path), "IMPORT_STRING_v4.0.0.txt deve esistere come garanzia di backup")

        with open(legacy_path, "r", encoding="utf-8") as f:
            legacy_content = f.read().strip()

        with open(backup_path, "r", encoding="utf-8") as f:
            backup_content = f.read().strip()

        self.assertEqual(
            legacy_content,
            backup_content,
            "VIOLAZIONE CONTRATTO: 'IMPORT_STRING.txt' è stata alterata rispetto alla versione congelata 4.0.0!"
        )
        self.assertTrue(legacy_content.startswith("!WA:1!"), "La stringa legacy deve iniziare con !WA:1!")

    def test_v5_string_matches_generator(self):
        """Verifica che IMPORT_STRING_5.21.8.txt corrisponda esattamente all'albero 5.21.8 generato."""
        v5_path = os.path.join(ROOT_DIR, "IMPORT_STRING_5.21.8.txt")
        self.assertTrue(os.path.exists(v5_path), "IMPORT_STRING_5.21.8.txt deve esistere (esegui python generate.py)")

        with open(v5_path, "r", encoding="utf-8") as f:
            saved_string = f.read().strip()

        tree_v5 = build_wa_tree(target_version="5.21.8")
        generated_string = generate_wa_string(tree_v5).strip()

        self.assertEqual(
            saved_string,
            generated_string,
            "IMPORT_STRING_5.21.8.txt non corrisponde all'output generato da build_wa_tree('5.21.8')!"
        )
        self.assertTrue(saved_string.startswith("!WA:1!"), "La stringa v5 deve iniziare con !WA:1!")
        self.assertEqual(tree_v5["w"], "5.21.8", "La versione 'w' deve essere '5.21.8'")
        self.assertEqual(tree_v5["d"]["internalVersion"], 90, "internalVersion della radice v5 deve essere 90")


if __name__ == "__main__":
    unittest.main()
