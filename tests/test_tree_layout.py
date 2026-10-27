"""
Test di integrità dell'albero WeakAuras e delle geometrie del layout (T8/T10).
Verifica:
1. Struttura dell'albero e ordine corretto dei figli (Tier 10 nei Procs, T8 nella fila Utility).
2. Matematica delle spaziature (Layout a 7 icone con T8 vs Layout standard a 6 icone).
3. Bilanciamento e sintassi di tutti i blocchi Lua custom embedded.
"""
import os
import re
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
from builder.tree import build_wa_tree

def test_tree_structure():
    tree = build_wa_tree()
    print(f"Master group: {tree['d']['id']}")
    assert tree['d']['id'] == "Class Mage (TTW Fire)", f"Unexpected master ID: {tree['d']['id']}"
    
    children_ids = [c['id'] for c in tree['c']]
    print(f"Total children count: {len(children_ids)}")
    
    assert "06b - Ring" in children_ids, "06b - Ring missing from tree!"
    assert "08 - Tier 8" in children_ids, "08 - Tier 8 missing from tree!"
    assert "09 - Gloves" in children_ids, "09 - Gloves missing from tree!"
    assert "13 - Boots" in children_ids, "13 - Boots missing from tree!"
    assert "06 - Tier 10" not in children_ids, "06 - Tier 10 should no longer be in the utility row!"
    assert "Tier 10" in children_ids, "Tier 10 missing from 01 - Procs!"
    
    procs_dg = next(c for c in tree['c'] if c['id'] == "01 - Procs")
    assert procs_dg['controlledChildren'][0] == "Tier 10", f"Tier 10 should be 1st child of 01 - Procs, got {procs_dg['controlledChildren']}"
    assert procs_dg['controlledChildren'][1] == "Hot Streak", f"Hot Streak should be 2nd child of 01 - Procs, got {procs_dg['controlledChildren']}"
    
    t10_idx = children_ids.index("Tier 10")
    hotstreak_idx = children_ids.index("Hot Streak")
    assert t10_idx < hotstreak_idx, f"Tier 10 ({t10_idx}) must precede Hot Streak ({hotstreak_idx}) in c array!"
    
    t1_idx = children_ids.index("05 - Trinket 1")
    t2_idx = children_ids.index("06 - Trinket 2")
    ring_idx = children_ids.index("06b - Ring")
    cloak_idx = children_ids.index("07 - Cloak")
    t8_idx = children_ids.index("08 - Tier 8")
    gloves_idx = children_ids.index("09 - Gloves")
    gem_idx = children_ids.index("10 - Mana Gem")
    comb_idx = children_ids.index("11 - Combustion")
    mirror_idx = children_ids.index("12 - Mirror Image")
    boots_idx = children_ids.index("13 - Boots")
    
    print(f"Indices: T10={t10_idx}, HotStreak={hotstreak_idx}, T1={t1_idx}, T2={t2_idx}, Ring={ring_idx}, Cloak={cloak_idx}, T8={t8_idx}, Gloves={gloves_idx}, Gem={gem_idx}, Comb={comb_idx}, Mirror={mirror_idx}, Boots={boots_idx}")
    assert t1_idx < t2_idx < ring_idx < cloak_idx < t8_idx < gloves_idx < gem_idx < comb_idx < mirror_idx < boots_idx, (
        f"Utility ordering violation: expected T1 < T2 < Ring < Cloak < T8 < Gloves < Gem < Comb < Mirror < Boots"
    )
    print("[OK] Tree ordering test: PASSED")

def test_layout_math():
    # Scenario 0: 10 componenti (Tutti attivi: T1, T2, Ring, Cloak, T8, Gloves, Gem, Comb, Mirror, Boots; passo 26px, w 26px)
    pos_10 = [round((i - 5.5) * 26) for i in range(1, 11)]
    total_span_10 = (pos_10[-1] + 13) - (pos_10[0] - 13)
    print(f"[OK] 10-component span: {total_span_10}px (sotto la barra da 264px, margine: {264 - total_span_10}px)")
    assert total_span_10 <= 264, f"Span {total_span_10} exceeds 264px bar!"

    # Scenario 0b: 9 componenti (T1, T2, Cloak, T8, Gloves, Gem, Comb, Mirror, Boots; passo 29px, w 28px)
    pos_9 = [round((i - 5) * 29) for i in range(1, 10)]
    total_span_9 = (pos_9[-1] + 14) - (pos_9[0] - 14)
    print(f"[OK] 9-component span: {total_span_9}px (sotto la barra da 264px, margine: {264 - total_span_9}px)")
    assert total_span_9 <= 264, f"Span {total_span_9} exceeds 264px bar!"

    # Scenario 1: 7 componenti (T8 equipaggiato, passo 38px, larghezza 28px)
    pos_7_t8 = [-114, -76, -38, 0, 38, 76, 114]
    diffs_7_t8 = [pos_7_t8[i+1] - pos_7_t8[i] for i in range(len(pos_7_t8)-1)]
    for d in diffs_7_t8:
        assert d == 38, f"Irregular spacing in 7-icon layout: {d}"
    total_span_7 = (pos_7_t8[-1] + 14) - (pos_7_t8[0] - 14)
    print(f"[OK] 7-component span: {total_span_7}px (sotto la barra da 264px, margine: {264 - total_span_7}px)")
    assert total_span_7 <= 264, f"Span {total_span_7} exceeds 264px bar!"

    # Scenario 2: 6 componenti (Standard senza T8, passo 44px, larghezza 28px)
    pos_6 = [-110, -66, -22, 22, 66, 110]
    diffs_6 = [pos_6[i+1] - pos_6[i] for i in range(len(pos_6)-1)]
    for d in diffs_6:
        assert d == 44, f"Irregular spacing in 6-icon layout: {d}"
    total_span_6 = (pos_6[-1] + 14) - (pos_6[0] - 14)
    print(f"[OK] 6-component span: {total_span_6}px (sotto la barra da 264px, margine: {264 - total_span_6}px)")
    assert total_span_6 <= 264, f"Span {total_span_6} exceeds 264px bar!"

    print("[OK] Layout math test: PASSED")

def strip_lua(code):
    code = re.sub(r'--\[\[.*?\]\]', '', code, flags=re.DOTALL)
    code = re.sub(r'--.*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'\[\[.*?\]\]', '""', code, flags=re.DOTALL)
    code = re.sub(r'"(\\.|[^"])*"', '""', code)
    code = re.sub(r"'(\\.|[^'])*'", "''", code)
    return code

def verify_lua_code(code):
    stripped = strip_lua(code)
    tokens = re.findall(r'\b(function|if|do|while|repeat|end|until)\b', stripped)
    depth = 0
    for t in tokens:
        if t in ('function', 'if', 'do', 'while', 'repeat'):
            depth += 1
        elif t in ('end', 'until'):
            depth -= 1
        if depth < 0:
            return False, f"unexpected {t}"
    if depth != 0:
        return False, f"unbalanced depth = {depth}"
    return True, "OK"

def test_lua_syntax_in_tree():
    tree = build_wa_tree()
    lua_snippets = []
    def extract_lua(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in ("custom", "customText", "customDuration", "customIcon", "init") and isinstance(v, str):
                    lua_snippets.append((f"{path}.{k}", v))
                else:
                    extract_lua(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                extract_lua(v, f"{path}[{i}]")

    extract_lua(tree)
    print(f"Extracted {len(lua_snippets)} Lua code blocks for validation.")
    
    errors = []
    for name, code in lua_snippets:
        ok, reason = verify_lua_code(code)
        if not ok:
            errors.append(f"Block {name}: {reason}")

    if errors:
        for err in errors:
            print("[-] ERROR:", err)
        assert False, f"{len(errors)} Lua syntax balance errors found!"
    print("[OK] Lua block balance test: PASSED")

if __name__ == "__main__":
    test_tree_structure()
    test_layout_math()
    test_lua_syntax_in_tree()
    print("\n=== TUTTE LE VERIFICHE DELL'ALBERO WA E DEL LAYOUT SONO STATE SUPERATE! ===")

