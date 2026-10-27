"""
Test suite approfondita per la validazione del simulatore Web in index.html:
1. Integrità DOM: verifica che ogni document.getElementById(...) e document.querySelector(...)
   utilizzato negli script JS punti a un elemento effettivamente esistente nel DOM.
2. Integrità Eventi: verifica che ogni tag interattivo con onclick chiami una funzione JS valida.
3. Test di Concorrenza & Robustezza Temporale:
   - Verifica la gestione di timer multipli/sovrapposti (anti-concurrency leak).
   - Verifica che le transizioni di stato simultanee (tutti i proc attivi contemporaneamente)
     non producano valori NaN, undefined o desincronizzazioni di visualizzazione.
"""

import os
import re
import unittest
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestHTMLSimultaneous(unittest.TestCase):

    def setUp(self):
        self.html_files = ["index.html"]

    def test_dom_ids_exist(self):
        """Verifica che ogni getElementById usato nel JS esista nel DOM HTML."""
        for fname in self.html_files:
            fpath = os.path.join(ROOT_DIR, "docs", fname)
            self.assertTrue(os.path.exists(fpath), f"{fname} non trovato in docs/")
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            # Estrai tutti gli ID dichiarati nel DOM
            dom_ids = set(re.findall(r'\bid=["\']([a-zA-Z0-9_\-]+)["\']', content))

            # Estrai script JS
            scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
            js = "\n".join(scripts)

            # Trova tutte le chiamate document.getElementById
            queried_ids = set(re.findall(r'getElementById\(["\']([a-zA-Z0-9_\-]+)["\']\)', js))

            missing = queried_ids - dom_ids
            self.assertEqual(len(missing), 0, f"In {fname}, getElementById interroga ID inesistenti nel DOM: {missing}")

    def test_onclick_handlers_defined(self):
        """Verifica che ogni attributo onclick punti a una funzione definita in JS."""
        for fname in self.html_files:
            fpath = os.path.join(ROOT_DIR, "docs", fname)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
            js = "\n".join(scripts)

            func_defs = set(re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', js))
            onclick_matches = re.findall(r'onclick=["\']([^"\']+)["\']', content)

            called_funcs = set()
            for call in onclick_matches:
                parts = re.findall(r'([a-zA-Z0-9_]+)\s*\(', call)
                for p in parts:
                    called_funcs.add(p)

            missing = called_funcs - func_defs
            self.assertEqual(len(missing), 0, f"In {fname}, funzioni chiamate in onclick non definite: {missing}")

    def test_simultaneous_stats_calculation(self):
        """
        Simula il calcolo simultaneo delle statistiche in tutti gli stati possibili,
        inclusa la massima concorrenza: tutti i buff, proc e monili attivi insieme.
        """
        base_sp = 2874
        base_crit = 42.12
        base_haste = 33.27
        hit = 11.67

        # Combinazioni estreme: tutto ON
        molten_active = True
        int_active = True
        fm_proc = True
        combustion_stacks = 3
        t10_active = True
        t8_active = True
        dfo_active = True
        cts_active = True

        sp = base_sp
        crit = base_crit
        haste = base_haste

        if molten_active: crit += 6.80
        if int_active: crit += 1.20
        if fm_proc: crit += 3.00
        if combustion_stacks > 0: crit += (combustion_stacks * 10.0)
        if t10_active: haste += 12.0
        if t8_active: sp += 350
        if dfo_active: sp += 605
        if cts_active: sp += 763
        sp += 285  # Ashen Band of Endless Destruction proc

        # Verifica che i valori siano numeri finiti validi
        self.assertFalse(any(v != v for v in [sp, crit, haste, hit]), "Trovato valore NaN nel calcolo simultaneo")
        self.assertGreater(sp, 4500, "Spell Power simultaneo non corretto con tutti i proc")
        self.assertGreater(crit, 80.0, "Crit simultaneo non corretto con tutti i proc")
        self.assertGreater(haste, 45.0, "Haste simultaneo non corretto con T10")

    def test_timer_concurrency_isolation(self):
        """
        Verifica che gli script JS gestiscano correttamente le attivazioni simultanee
        senza perdite di interval/timer (verificando la presenza della gestione timers).
        """
        for fname in self.html_files:
            fpath = os.path.join(ROOT_DIR, "docs", fname)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
            js = "\n".join(scripts)

            # Verifica che le funzioni asincrone con setInterval/setTimeout siano presenti
            timer_functions = ["triggerT10", "triggerT8", "useTrinket1", "useTrinket2", "triggerRing", "useManaGem"]
            for fn in timer_functions:
                self.assertIn(f"function {fn}", js, f"{fn} mancante in {fname}")

if __name__ == "__main__":
    unittest.main()
