"""
WeakAuras String Generator
=========================
Genera la stringa di importazione WeakAuras per la versione nativa WeakAuras 5.21.8+.
NOTA BENE: 'IMPORT_STRING.txt' è congelato permanentemente per WeakAuras 4.0.0
e NON viene mai modificato da questo script.
"""
import os
from builder.core import generate_wa_string
from builder.tree import build_wa_tree

FROZEN_LEGACY_FILE = "IMPORT_STRING.txt"
TARGET_V5_FILE = "IMPORT_STRING_5.21.8.txt"

if __name__ == "__main__":
    print(f"[STATUS] '{FROZEN_LEGACY_FILE}' e' CONGELATO permanentemente per WeakAuras 4.0.0.")
    print(f"[BUILD] Generazione di '{TARGET_V5_FILE}' per WeakAuras 5.21.8+ (internalVersion 90)...")

    wa_tree = build_wa_tree(target_version="5.21.8")
    wa_string = generate_wa_string(wa_tree)

    with open(TARGET_V5_FILE, "w", encoding="utf-8") as f:
        f.write(wa_string)

    print(f"[SUCCESS] Generato '{TARGET_V5_FILE}' con successo! Dimensione: {len(wa_string)} caratteri.")
