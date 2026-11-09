import re
import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Target principale moderno: WeakAuras 5.21.8+
import_path = os.path.join(root_dir, "IMPORT_STRING_v5.21.8.txt")
docs_path = os.path.join(root_dir, "docs", "index.html")

with open(import_path, "r", encoding="utf-8") as f:
    wa_str = f.read().strip()

with open(docs_path, "r", encoding="utf-8") as f:
    html = f.read()

pattern = re.compile(r'(<textarea id="hiddenWaString"[^>]*>).*?(</textarea>)', re.DOTALL)
new_html, count = pattern.subn(r'\g<1>' + wa_str + r'\g<2>', html)

if count > 0:
    with open(docs_path, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"docs/index.html updated successfully with IMPORT_STRING_v5.21.8.txt! String length: {len(wa_str)}")
else:
    print("Warning: textarea id='hiddenWaString' not found in docs/index.html")
