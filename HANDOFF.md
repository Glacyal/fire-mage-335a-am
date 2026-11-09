# Class Mage (TTW Fire) — Handoff Tecnico

Manuale di riferimento tecnico per lo sviluppo, la manutenzione e l'estensione della suite **Class Mage (TTW Fire)** per World of Warcraft 3.3.5a (*WotLK Build 12340*).

---

## 1. Panoramica del Progetto

La suite è distribuita come **WeakAura autonoma** in formato compresso `!WA:1!` (serializzazione binaria `AceSerializer-3.0` + compressione Deflate RFC 1951 livello 9 + codifica di stampa `LibDeflate`).  
Include un simulatore web interattivo per la visualizzazione immediata del layout ospitato su GitHub Pages, una suite completa di test deterministici in Python con runner multi-core parallelo e una gestione dual-engine per client classici e moderni.

| Proprietà | Dettaglio |
| :--- | :--- |
| **Piattaforma Target** | World of Warcraft 3.3.5a (WotLK Build 12340) |
| **Engine WeakAuras Target** | **WeakAuras 5.21.8+** (`internalVersion = 90`, `w = "5.21.8"`, Zero Warning nativa). |
| **File di Distribuzione** | [`IMPORT_STRING_v5.21.8.txt`](file:///d:/0Progetti/fire-mage-335a-am/IMPORT_STRING_v5.21.8.txt) (stringa ufficiale pronta per l'importazione) |
| **Simulatore Web** | [`docs/index.html`](file:///d:/0Progetti/fire-mage-335a-am/docs/index.html) |
| **Live Demo Online** | [GitHub Pages Live Showcase](https://glacyal.github.io/fire-mage-335a-am/) |
| **Controllo Versione** | Git su GitHub: [Glacyal/fire-mage-335a-am](https://github.com/Glacyal/fire-mage-335a-am) (branch: `main`) |
| **Politica Documentazione** | `docs/*.md` esclusi dal controllo versione via `.gitignore` per preservare il contesto locale senza appesantire il repository Git. |

---

## 2. Struttura del Repository

```text
fire-mage-335a-am/
├── IMPORT_STRING_v5.21.8.txt        # Stringa WeakAuras 5.21.8+ nativa (Zero warning, internalVersion: 90)
├── generate.py                      # Compilatore Python dell'albero WA (compila v5 nativo)
├── README.md                        # Documentazione utente, guida installazione e compatibilità
├── HANDOFF.md                       # Specifiche tecniche per sviluppatori e manutentori
│
├── builder/                         # Pacchetto Python modulare per la generazione dell'HUD
│   ├── tree.py                      # Assemblatore dell'albero gerarchico (45 aure, 20 nodi controllati)
│   ├── core/                        # Moduli core di serializzazione e codifica
│   │   ├── constants.py             # Load conditions (Mage + Living Bomb), texture, font Expressway
│   │   ├── serializer.py            # Serializzatore AceSerializer-3.0 puro (^1...^^)
│   │   ├── deflate.py               # Compressione Deflate RFC 1951 + LibDeflate Print Encoding
│   │   ├── encoder.py               # Generatore stringa finale (!WA:1!...)
│   │   └── helpers.py               # Generatori di subtext e helper grafici
│   └── components/                  # Moduli dedicati ai singoli componenti dell'HUD
│       ├── hot_streak.py            # 15 - Hot Streak Bar (doppio segmento e combat log disaccoppiato)
│       ├── procs.py                 # 01 - Procs (gruppo dinamico superiore orizzontale a 8 icone)
│       ├── buffs.py                 # 02 - Molten Armor, 03 - Arcane Intellect, 04 - Focus Magic (filtro CLEU)
│       ├── utility.py               # 05-13 - Utility Row (Monili, Anello, Mantello, T8, Guanti, Gemma, Combustion, Copie, Stivali)
│       ├── bars.py                  # 14 - Mana Bar & 16 - Castbar
│       ├── alerts.py                # 17 - Alerts (avvisi testuali centrali HOT STREAK!)
│       ├── stats.py                 # 18 - Stats Panel (SP, Crit, Haste, Hit con cap resolution)
│       └── multi_lb.py              # 19 - Multi-Target Living Bomb Tracker (fino a 5 target)
│
├── docs/                            # Documentazione e anteprima interattiva per GitHub Pages
│   ├── index.html                   # Simulatore interattivo HTML/CSS/JS (proporzioni 1:1, tracciato in Git)
│   ├── lich_king_bg.png             # Sfondo grafico del simulatore (tracciato in Git)
│   ├── RULES.md                     # Regole operative inviolabili e guardrail (locale)
│   ├── ARCHITECTURE.md              # Architettura del sistema e compilatore (locale)
│   ├── PRD.md                       # Requisiti di prodotto e meccaniche TTW Fire (locale)
│   ├── DECISIONS.md                 # Architectural Decision Records da ADR-001 ad ADR-012 (locale)
│   ├── TASKS.md                     # Roadmap e avanzamento task Fasi 0-9 (locale)
│   ├── MEMORY.md                    # Memoria tecnica persistente, spell ID e bugfix storici (locale)
│   ├── DESIGN.md                    # Design system, token cromatici e geometrie al pixel (locale)
│   ├── TEST_PLAN.md                 # Piano di test e matrice di QA (locale)
│   ├── WORKFLOW.md                  # Workflow di sviluppo e comandi rapidi (locale)
│   └── WEAKAURAS_5.21.8_COMPATIBILITY.md # Specifica migrazione WA 5.21.8+ (locale)
│
├── scripts/
│   └── sync_docs.py                 # Sincronizzazione automatica della stringa v5 in docs/index.html
│
└── tests/                           # Suite di test automatici e paralleli
    ├── run_parallel_tests.py        # Test runner parallelo multi-processore (ProcessPoolExecutor)
    ├── test_all_utility_cases.py    # Verifica esaustiva 64 combinazioni riga utility (da 3 a 10 icone)
    ├── test_components_integrity.py # Verifica integrità strutturale moduli (45 aure, sequenza 01-19)
    ├── test_equip_switch.py         # Test transizioni e centratura universale da 3 a 10 icone
    ├── test_hotstreak_decoupled.py  # Test logica Hot Streak persistente e decoppiata
    ├── test_html_simultaneous.py    # Stress test concorrenza simulatore web
    ├── test_showcase.py             # Audit 100% interattività e handler DOM
    ├── test_lua.py                  # Validazione sintassi codice Lua (token matcher)
    ├── test_multi_living_bomb.py    # Verifica integrità, trigger e ordinamento Multi-Target LB
    ├── test_tree_layout.py          # Verifica gerarchia e proporzioni albero WA
    ├── test_focus_magic.py          # Test stati e transizioni Focus Magic
    ├── test_stats_panel.py          # Test calcolo statistiche e conflitti raid
    └── test_string_sync.py          # Verifica integrità stringa congelata v4 e stringa compilata v5
```

---

## 3. Workflow di Sviluppo

Per apportare modifiche alla suite o estendere la logica:

1. **Modifica Componenti**:
   - Modifica i moduli Python in `builder/components/` o le librerie in `builder/core/`.
2. **Esecuzione Test Paralleli**:
   - Lancia la suite di test completa sfruttando tutti i core della CPU:
     ```bash
     python tests/run_parallel_tests.py
     ```
   - Tutti i 12 test devono risultare `[OK] PASSED` in meno di 1 secondo.
3. **Compilazione Stringa di Importazione**:
   - Ricompila la stringa nativa WA 5.21.8+ eseguendo:
     ```bash
     python generate.py
     ```
   - Questo aggiornerà deterministicamente [`IMPORT_STRING_v5.21.8.txt`](file:///d:/0Progetti/fire-mage-335a-am/IMPORT_STRING_v5.21.8.txt).
4. **Sincronizzazione Simulatore Web**:
   - Sincronizza la stringa compilata all'interno del simulatore web:
     ```bash
     python scripts/sync_docs.py
     ```
5. **Commit & Push (`CP`)**:
   - Verifica lo stato Git con `git status` (assicurati che i file `docs/*.md` rimangano ignorati).
   - Esegui lo staging dei soli file di codice o documentazione pubblica (`git add <file>`).
   - Esegui commit e push sul branch `main`.

---

## 4. Specifiche Architetturali e Soluzioni WeakAuras 5+

### 4.1 Barra Hot Streak Decoppiata (`15 - Hot Streak Bar`)
- **Architettura a Due Segmenti Decoppiati**:
  1. **Segment 1 (Metà Sinistra)**:
     - Traccia lo stato binario `0` o `1` del 1° colpo critico andato a segno (*Fireball, Scorch, Fire Blast, Frostfire Bolt, esplosione Living Bomb*).
     - **Persistenza Out-of-Combat**: non scade nel tempo e non decade uscendo dal combattimento.
     - **Reset**: si azzera a `0` solo al 2° critico consecutivo (che innesca il proc) o se la spell qualificabile successiva non critta.
     - **Rolling Hot Streak**: il lancio di Pyroblast non resetta questo segmento.
  2. **Proc (Metà Destra)**:
     - Traccia nativamente il buff `Hot Streak` (Spell ID 48108) con conto alla rovescia di 10 secondi, swipe circolare e Pixel Glow dorato.
- **Isolamento Sandbox**:
  - Il frame listener eventi è instanziato in modo anonimo (`CreateFrame("Frame")`) e salvato tramite `rawset(_G, "FMHUD_HSFrame", f)` per evitare il warning di sovrascrittura di variabili globali (`checkGlobals`).

### 4.2 Gruppo Dinamico Procs (`01 - Procs`)
- **Posizione**: Disposto orizzontalmente sopra la Castbar con riposizionamento automatico.
- **Ottimizzazione CPU**: `Molten Fury` implementa un filtro rigido (`unit ~= "target"` con early return) su `UNIT_HEALTH` e `UNIT_MAXHEALTH`, azzerando i calcoli su cambi salute dei compagni di raid.
- **Icone Reattive (fino a 8 contemporanee)**:
  1. `Tier 10 2P (Pushing the Limit)`: +12% Haste per 5s con Pixel Glow dorato.
  2. `Hot Streak`: Icona proc con timer.
  3. `Clearcasting`: Proc mana free.
  4. `Living Bomb`: Debuff sul target con countdown swipe.
  5. `Pyroblast`: DoT periodico di 12s applicato sul target.
  6. `Ignite`: Debuff di 4s rolling sul target da spell critiche.
  7. `Improved Scorch`: Debuff +5% spell crit sul target.
  8. `Molten Fury`: Bersaglio con salute $< 35\%$ (+12% danno aumentato).

### 4.3 Focus Magic Anti-Clutter (`04 - Focus Magic`)
- **Filtro CLEU Selettivo**:
  - Non utilizza `COMBAT_LOG_EVENT_UNFILTERED` grezzo, bensì il filtro nativo:
    ```text
    CLEU:SPELL_AURA_APPLIED:SPELL_AURA_REFRESH:SPELL_AURA_REMOVED:SPELL_AURA_BROKEN:UNIT_DIED
    ```
  - Questo elimina al 100% l'errore rosso di WeakAuras 5 e taglia il 99.9% dei cicli CPU non necessari.
- **Comportamento Visivo**: Nascosto se attivo su alleato vivo; compare durante il proc personale di 10 secondi (+3% Crit) o come allerta `OFF` rossa se assente.

### 4.4 Centratura Dinamica Riga Utility (`05` - `13`, da 3 a 10 Icone)
- **Ordine rigoroso da sinistra a destra**:
  `[05 - Trinket 1] -> [06 - Trinket 2] -> [06b - Ring] -> [07 - Cloak] -> [08 - Tier 8] -> [09 - Gloves] -> [10 - Mana Gem] -> [11 - Combustion] -> [12 - Mirror Image] -> [13 - Boots]`
- **Eliminazione di `WeakAuras.regions`**:
  - Sostituito ovunque dall'accessor ufficiale `WeakAuras.GetRegion(id)`, eliminando il warning di deprecazione su tutte le 10 icone.
- **Eliminazione di `WeakAuras.GetData(id)` a Runtime**:
  - Il riposizionamento al pixel e ridimensionamento opera unicamente sull'oggetto Frame nativo (`r:ClearAllPoints()`, `r:SetPoint(...)`, `r:SetWidth(...)`), eliminando l'avviso del profiler di WA 5 (*"calls GetData a lot"*).
- **Eliminazione di `COMBAT_LOG_EVENT_UNFILTERED` Grezzo**:
  - Rimosso da `events_list`. Il frame `FMHUD_LayoutFrame` intercetta gli eventi necessari ed emette `WeakAuras.ScanEvents("FMHUD_ROW_UPDATE")`.
- **Passo Adattivo e Dimensioni**:
  - 10 icone: step = 26px, dimensione = 26px
  - 9 icone: step = 29px, dimensione = 28px
  - 8 icone: step = 32px, dimensione = 28px
  - 7 icone: step = 38px, dimensione = 28px
  - 6 icone: step = 44px, dimensione = 28px
  - 5 icone: step = 48px, dimensione = 28px
  - $\le 4$ icone: step = 52px, dimensione = 28px
  - Centratura garantita dalla formula: $x_i = \left(i - \frac{N + 1}{2}\right) \times \text{step}$.

### 4.5 Multi-Target Living Bomb Tracker (`19 - Multi-Target Living Bomb`)
- **Architettura Disaccoppiata**: Frame dedicato `FMHUD_LBFrame` registrato su CLEU che emette l'evento custom `FMHUD_LB_UPDATE`.
- **Nessun CLEU Grezzo nei Trigger**: I 5 tracker ascoltano unicamente `FMHUD_LB_UPDATE`, azzerando gli errori di WeakAuras 5.
- **Ordinamento Intelligente per Scadenza**: La bomba con minor tempo residuo occupa sempre la posizione #1 in alto, con timer rosso sotto i 3 secondi.

---

## 5. Matrice di Compatibilità Addon & API

| Client / Addon | Compatibilità | Note Tecniche |
| :--- | :---: | :--- |
| **WeakAuras 5.21.8+ (WotLK 3.3.5a)** | 🏆 **100% Nativa (0 Warning)** | `internalVersion: 90`, `w: "5.21.8"`, `WeakAuras.GetRegion(id)`, sandbox `rawset`, zero `GetData` a runtime, filtri CLEU selettivi. File: `IMPORT_STRING_v5.21.8.txt`. |
| **Client Retail / Moderni** | ❌ **Non Supportato** | Specifico per World of Warcraft 3.3.5a (WotLK Build 12340). |
