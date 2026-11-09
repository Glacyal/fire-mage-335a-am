"""
WeakAuras String Generator
=========================
Genera la stringa di importazione WeakAuras per la versione nativa WeakAuras 5.21.8+.
Target: 'IMPORT_STRING_v5.21.8.txt'
"""
import os
from builder.core import generate_wa_string
from builder.tree import build_wa_tree

TARGET_V5_FILE = "IMPORT_STRING_v5.21.8.txt"

if __name__ == "__main__":
    print(f"[BUILD] Generazione di '{TARGET_V5_FILE}' per WeakAuras 5.21.8+ (internalVersion 90)...")

    wa_tree = build_wa_tree(target_version="5.21.8")
    wa_string = generate_wa_string(wa_tree)

    with open(TARGET_V5_FILE, "w", encoding="utf-8") as f:
        f.write(wa_string)

    print(f"[SUCCESS] Generato '{TARGET_V5_FILE}' con successo! Dimensione: {len(wa_string)} caratteri.")

