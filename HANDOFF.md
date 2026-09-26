# Class Mage (TTW Fire) — Handoff Tecnico

Manuale di riferimento tecnico per lo sviluppo, la manutenzione e l'estensione della suite **Class Mage (TTW Fire)** per World of Warcraft 3.3.5a (*WotLK Build 12340*).

---

## 1. Panoramica del Progetto

La suite è distribuita come **WeakAura autonoma** in formato compresso `!WA:1!` (serializzazione `AceSerializer-3.0` + compressione `LibDeflate`). Include un simulatore web interattivo per la visualizzazione immediata del layout ospitato su GitHub Pages e una suite completa di test deterministici in Python.

| Proprietà | Dettaglio |
| :--- | :--- |
| **Piattaforma Target** | World of Warcraft 3.3.5a (WotLK Build 12340) |
| **Engine WeakAuras** | WeakAuras 4.0.0 (`internalVersion = 52`, header `!WA:1!`). Tutti i test sono stati eseguiti su questa versione. |
| **File di Distribuzione** | [`IMPORT_STRING.txt`](file:///d:/0Progetti/fire-mage-335a-am/IMPORT_STRING.txt) |
| **Simulatore Web** | [`docs/index.html`](file:///d:/0Progetti/fire-mage-335a-am/docs/index.html) |
| **Live Demo Online** | [GitHub Pages Live Showcase](https://glacyal.github.io/fire-mage-335a-am/) |
| **Controllo Versione** | Git su GitHub: [Glacyal/fire-mage-335a-am](https://github.com/Glacyal/fire-mage-335a-am) (branch: `main`) |

---

## 2. Struttura del Repository

```text
fire-mage-335a-am/
├── IMPORT_STRING.txt                # Stringa WeakAuras pronta all'uso per il comando /wa
├── generate.py                      # Compilatore Python dell'albero WA
├── README.md                        # Documentazione utente, guida installazione e compatibilità
├── HANDOFF.md                       # Specifiche tecniche per sviluppatori e manutentori
├── GEMINI.md                        # Regole di progetto, comandi CP e MODELLO
│
├── builder/                         # Pacchetto Python modulare per la generazione dell'HUD
│   ├── tree.py                      # Assemblatore dell'albero gerarchico (44 aure WeakAuras, 19 nodi principali)
│   ├── core/                        # Moduli core di serializzazione e codifica
│   │   ├── constants.py             # Load conditions (Mage 68), texture, font Expressway
│   │   ├── serializer.py            # Serializzatore AceSerializer-3.0 puro (^1...^^)
│   │   ├── deflate.py               # Compressione Deflate RFC 1951 + LibDeflate Print Encoding
│   │   ├── encoder.py               # Generatore stringa finale (!WA:1!...)
│   │   └── helpers.py               # Generatori di subtext e helper grafici
│   └── components/                  # Moduli dedicati ai singoli componenti dell'HUD
│       ├── hot_streak.py            # 15 - Hot Streak Bar (doppio segmento e combat log)
│       ├── procs.py                 # 01 - Procs (gruppo dinamico superiore)
│       ├── buffs.py                 # 02 - Molten Armor, 03 - Arcane Intellect, 04 - Focus Magic
│       ├── utility.py               # 05-13 - Utility Row (Monili, Mantello, T8, Guanti, Gemma, Combustion, Copie, Stivali)
│       ├── bars.py                  # 14 - Mana Bar & 16 - Castbar
│       ├── alerts.py                # 17 - Alerts (avvisi testuali centrali)
│       ├── stats.py                 # 18 - Stats Panel (SP, Crit, Haste, Hit con cap resolution)
│       └── multi_lb.py              # 19 - Multi-Target Living Bomb Tracker (fino a 5 target)
│
├── docs/                            # Documentazione e anteprima interattiva per GitHub Pages
│   └── index.html                   # Simulatore interattivo HTML/CSS/JS (proporzioni 1:1)
│
└── tests/                           # Suite di test automatici e paralleli
    ├── run_parallel_tests.py        # Test runner parallelo multi-processore (ProcessPoolExecutor)
    ├── test_all_utility_cases.py    # Verifica esaustiva 64 combinazioni riga utility
    ├── test_components_integrity.py # Verifica integrità strutturale moduli (44 aure, sequenza 01-19)
    ├── test_equip_switch.py         # Test transizioni e centratura universale da 3 a 9 icone
    ├── test_hotstreak_decoupled.py  # Test logica Hot Streak persistente e decoppiata
    ├── test_html_simultaneous.py    # Stress test concorrenza simulatore web
    ├── test_showcase.py             # Audit 100% interattività e handler DOM
    ├── test_lua.py                  # Validazione sintassi codice Lua
    ├── test_multi_living_bomb.py    # Verifica integrità, trigger e ordinamento Multi-Target LB
    ├── test_tree_layout.py          # Verifica gerarchia e proporzioni albero WA
    ├── test_focus_magic.py          # Test stati e transizioni Focus Magic
    └── test_stats_panel.py          # Test calcolo statistiche e conflitti raid
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
   - Oppure esegui i test mirati:
     ```bash
     python -m unittest tests/test_hotstreak_decoupled.py
     python tests/test_showcase.py
     ```
3. **Compilazione Stringa di Importazione**:
   - Ricompila la stringa WA eseguendo:
     ```bash
     python generate.py
     ```
   - Questo aggiornerà deterministicamente [`IMPORT_STRING.txt`](file:///d:/0Progetti/Fire%20Mage%203.3.5a%20AM/IMPORT_STRING.txt).
4. **Verifica Simulatore Web**:
   - Se hai modificato il layout o aggiunto elementi visivi, aggiorna `docs/index.html` e lancia:
     ```bash
     python tests/test_showcase.py
     ```
5. **Commit & Push (`CP`)**:
   - Usa il comando utente `CP` per verificare, committare e sincronizzare il branch `main` su GitHub.

---

## 4. Specifiche Architetturali Chiave

### 4.1 Barra Hot Streak Decoppiata (`15 - Hot Streak Bar`)
- **Posizione**: Subito sopra la barra del Mana, perfettamente allineata all'ingombro orizzontale dell'HUD.
- **Architettura a Due Segmenti Decoppiati**:
  1. **Segment 1 (Metà Sinistra)**:
     - Traccia lo stato binario `0` o `1` del 1° colpo critico andato a segno (*Fireball, Scorch, Fire Blast, Frostfire Bolt, esplosione Living Bomb*).
     - **Persistenza**: Non scade nel tempo e non decade uscendo dal combattimento.
     - **Reset**: Si azzera a `0` solo al 2° critico consecutivo (che innesca il proc) o se la spell qualificabile successiva non critta.
     - **Non azzerato da Pyroblast**: Il lancio di Pyroblast non resetta questo segmento, permettendo la gestione del *Rolling Hot Streak*.
  2. **Proc (Metà Destra)**:
     - Traccia nativamente il buff `Hot Streak` (Spell ID 48108) con conto alla rovescia di 10 secondi, swipe circolare e Pixel Glow dorato.
     - È completamente svincolato dal segmento di sinistra: si spegne al consumo o scadenza del buff.

### 4.2 Gruppo Dinamico Procs (`01 - Procs`)
- **Posizione**: Disposto orizzontalmente sopra la Castbar.
- **Ottimizzazione CPU & Filtraggio Eventi**: I trigger custom con ascolto ad alta frequenza (come `Molten Fury` registrato su `UNIT_HEALTH` e `UNIT_MAXHEALTH`) implementano un early-return immediato se l'unità che ha generato l'evento non è `"target"`. Questo evita interrogazioni ridondanti dello stato del bersaglio durante i cambi di vita degli altri membri del raid o dei mob, preservando il framerate anche nelle situazioni di carico massimo.
- **Icone Reattive (fino a 7 contemporanee)**:
  1. `Tier 10 (Pushing the Limit)`: +12% Haste per 5s con Pixel Glow dorato.
  2. `Hot Streak`: Icona proc con timer.
  3. `Clearcasting`: Proc mana free.
  4. `Living Bomb`: Debuff sul target con countdown swipe.
  5. `Ignite`: Debuff di 4s rolling sul target da spell critiche.
  6. `Improved Scorch`: Debuff +5% spell crit sul target.
  7. `Molten Fury`: Bersaglio con salute < 35% (+12% danno aumentato).
- **Combustion**: Collocata **esclusivamente** nella riga utility (`11 - Combustion`), evitando duplicazioni nel gruppo procs.

### 4.3 Focus Magic Anti-Clutter (`04 - Focus Magic`)
- **Invisibile di base**: Se il buff è attivo su un alleato vivo, l'icona è nascosta per preservare la pulizia dello schermo.
- **Proc 10s Personale**: Quando l'alleato mette a segno un critico, compare con swipe e conto alla rovescia (+3% Crit per 10s).
- **Allerta OFF**: Se il buff non è assegnato a nessuno o se l'alleato muore, compare l'icona desaturata con avviso `OFF` rosso.

### 4.4 Centratura Dinamica Riga Utility (`05` - `13`, da 3 a 9 Icone)
- **Ordine rigoroso da sinistra a destra**:
  `[05 - Trinket 1] -> [06 - Trinket 2] -> [07 - Cloak] -> [08 - Tier 8] -> [09 - Gloves] -> [10 - Mana Gem] -> [11 - Combustion] -> [12 - Mirror Image] -> [13 - Boots]`
- **Condizioni di visibilità e attivazione**:
  - **Trinket 1 & 2 (Slot 13 e 14)**: Visibili solo se gli slot sono equipaggiati con un monile valido (nascosti se vuoti).
  - **Mantello (Slot 15)**: Visibile solo se possiede un incanto con proc di potenziamento (*Lightweave*, *Darkglow*, *Swordguard*, *Flexweave*, ecc.).
  - **Tier 8 2P (Praxis)**: Visibile solo con $\ge 2$ pezzi del set T8 Kirin Tor equipaggiati (+350 SP, 45s ICD).
  - **Guanti (Slot 10)**: Visibili solo se equipaggiati con l'incanto Ingegneria *Acceleratori Ipersonici* (+340 Haste per 12s, 60s CD con filtro lockout condiviso < 45s).
  - **Gemma del Mana**: Sempre visibile, con cariche effettive in borsa (`3`, `2`, `1` o `0` in rosso, senza prefisso `x`), icona nativa dinamica (Zaffiro/Smeraldo), cooldown di 2m e proc T7 Mana Surge.
  - **Combustion**: Sempre visibile con icona nativa dell'incantesimo, stato ON, stack critici e cooldown 2m.
  - **Mirror Image**: Sempre visibile con icona nativa dell'incantesimo (`select(3, GetSpellInfo(55342))`), durata copie 30s, cooldown 3m e bonus 4P T10 *Quad Core* (+18% danno).
  - **Stivali (Slot 8)**: Visibili solo se equipaggiati con un incanto che conferisce velocità di movimento (*Acceleratori a Nitro* per Ingegneria con indicatore dei Nitro attivi a 5s con Pixel Glow, countdown di cooldown a 180s e swipe con filtro lockout condiviso < 60s, oppure *Vitalità Tuskarr*, *Rapidità Felina*, *Velocità Superiore*, ecc.). Se non incantati con velocità o se lo slot è vuoto, non compaiono.
  - **Disaccoppiamento Lockout Ingegneria**: In WotLK 3.3.5a l'attivazione di un tinker (es. Guanti) innesca un breve blocco condiviso (10-30s) sugli altri tinker (es. Stivali). Il motore di calcolo ignora questi blocchi temporanei su Guanti e Stivali, impedendo che l'attivazione dei guanti mostri falsi cooldown o swipe sui Nitro (e viceversa).
- **Algoritmo di Centratura Dinamica**:
  Ricalcola dinamicamente la spaziatura orizzontale in base al numero effettivo di icone attive (da 3 a 9), distribuendole simmetricamente attorno all'asse centrale senza sovrapposizioni e mantenendo la riga perfettamente proporzionata alla larghezza complessiva dell'HUD.

### 4.5 Risoluzione Conflitti Statistiche di Raid
Il modulo `builder/components/stats.py` impedisce la duplicazione di buff raid della stessa categoria:
- **Haste 3%**: *Swift Retribution* (Paladino) e *Improved Moonkin Form* (Druido) conteggiati una sola volta.
- **Spell Crit 5%**: *Improved Scorch*, *Winter's Chill* e *Shadow and Flame* conteggiati una sola volta.
- **All Crit 3%**: *Heart of the Crusader*, *Master Poisoner* e *Totem of Wrath* conteggiati una sola volta.
- **Hit 3%**: *Misery* e *Improved Faerie Fire* conteggiati una sola volta.

### 4.6 Castbar e Convenzioni di Struttura (`16 - Castbar`)
- **Castbar con Icona Spell Integrata**: Include l'icona dell'incantesimo attivo posizionata sul bordo sinistro della barra, timer di cast e barra di latenza di rete (*Safe Zone*).
- **Numerazione Continua dei Componenti**: Tutti i componenti primari del gruppo root seguono la sequenza continua `01`–`19`, garantendo perfetta corrispondenza tra i moduli generati da `builder/`, la stringa importabile e il simulatore web.

### 4.7 Multi-Target Living Bomb Tracker (`19 - Multi-Target Living Bomb`)
- **Posizione & Layout**: Dynamic Group verticale posizionato a destra dell'HUD per monitorare fino a 5 Living Bomb attive contemporaneamente.
- **Architettura Autonoma e Disaccoppiata (`SHARED_MULTILB_LUA`)**:
  - Il componente si auto-inizializza all'attivazione del trigger di `Living Bomb Tracker 1` creando il frame dedicato `_G.FMHUD_LBFrame`.
  - **Tracciamento Multi-Canale**: combina `UNIT_SPELLCAST_SUCCEEDED` (lancio immediato a zero latenza), combat log esteso (`SPELL_AURA_APPLIED/REFRESH/REMOVED`, `UNIT_DIED`) e scansione autoritativa via `UnitDebuff`.
  - **Ticker `OnUpdate` (0.15s)**: purga naturale delle bombe al termine dei 12 secondi con notifica `FMHUD_LB_UPDATE`.
- **Ordinamento Intelligente per Scadenza**: Le bombe attive sono disposte con la bomba più vicina all'esplosione in prima posizione (#1), seguita in ordine cronologico dalle successive.
- **Formattazione Timer**: Testo rosso con 1 decimale per $\le 3\text{s}$ residui (allerta esplosione imminente) e testo bianco con secondi interi per durate superiori.

---

## 5. Note di Compatibilità Addon & API

- **Client 3.3.5a**: Compatibilità nativa 100%. Gli script Lua impiegano `COMBAT_LOG_EVENT_UNFILTERED` con passaggio parametri tramite `...`, `UnitBuff` con return a 11 argomenti e `GetNumPartyMembers()`.
- **Client Moderni / Retail**: WeakAuras 5 su client moderni non è compatibile per via delle modifiche alle API Blizzard (`CombatLogGetCurrentEventInfo`, `C_UnitAuras`, rimozione di `GetNumPartyMembers`) e della diversa rotazione del Mago Fuoco.
