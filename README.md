# Class Mage (TTW Fire) — WeakAuras Suite

[![WoW Version](https://img.shields.io/badge/World%20of%20Warcraft-3.3.5a%20(12340)-orange.svg)](https://github.com/Glacyal/fire-mage-335a-am)
[![WeakAuras](https://img.shields.io/badge/WeakAuras-5.21.8+%20%2F%204.0.0-blue.svg)](https://github.com/Glacyal/fire-mage-335a-am)
[![Class](https://img.shields.io/badge/Class-Mage%20(Fire%20TTW)-red.svg)](https://github.com/Glacyal/fire-mage-335a-am)
[![GitHub Pages](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-brightgreen.svg)](https://glacyal.github.io/fire-mage-335a-am/)
[![Buy me a coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-gray.svg?logo=paypal&logoColor=white&labelColor=0079c1)](https://www.paypal.me/AMantmar)

Suite WeakAuras completa, modulare e ordinata per **Mago Fire Livello 80** in World of Warcraft 3.3.5a (*Wrath of the Lich King - Build 12340*).  
Progettata per garantire un'elevata fluidità in combattimento, un consumo ridotto di risorse CPU, un monitoraggio chiaro e affidabile dei proc e un'interfaccia pulita senza elementi superflui, orientata all'ottimizzazione del DPS.

---

## 🌐 Anteprima Online (Live Simulator)

Visualizza e interagisci con l'HUD direttamente dal browser senza installare nulla:  
👉 **[Apri il Simulatore Web su GitHub Pages](https://glacyal.github.io/fire-mage-335a-am/)**  
- **Test Interattivo Equip/Unequip**: simula l'indossamento o la rimozione di Anello Ashen, Mantello e Guanti con contrazione/espansione automatica dell'HUD.
- **Precision Timers & Radial Cooldown Clock**: tutti i proc e gli ICD presentano conto alla rovescia al secondo e animazione circolare clock swipe autentica.  

---

## 🌟 Caratteristiche Principali

Tutti i componenti del pacchetto sono organizzati con una numerazione sequenziale ordinata (da **01** a **19** con `06b - Ring` interposto per 20 nodi controllati e 45 aure totali):

### 1. Barra Hot Streak a Doppio Segmento (`15 - Hot Streak Bar`)
Posizionata visivamente a schermo subito sopra la barra del mana, è suddivisa in **due metà indipendenti**:
- **Mezza Barra Sinistra (Segment 1)**:
  - Si illumina in arancione al primo colpo critico diretto (*Fireball, Scorch, Fire Blast, Frostfire Bolt, esplosione di Living Bomb*).
  - **Persistenza Out-of-Combat**: rimane memorizzata nel tempo anche al termine del combattimento, finché non si mette a segno un nuovo colpo diretto.
  - Si azzera solo al secondo critico consecutivo (che attiva il proc) oppure in caso di colpo non critico. Non si azzera lanciando Pyroblast (*Rolling Hot Streak*).
- **Mezza Barra Destra (Proc)**:
  - Mostra il buff **Hot Streak** (Spell ID 48108) con conto alla rovescia di 10 secondi e bordo luminoso dorato.
  - Si spegne quando il buff viene consumato dal lancio della Pyroblast istantanea o alla scadenza naturale. Se il buff scade, l'eventuale singolo critico registrato a sinistra rimane salvato.

### 2. Gruppo Dinamico Procs (`01 - Procs`)
Posizionato nella parte superiore dell'HUD, gestisce fino a 8 icone con riposizionamento orizzontale automatico:
1. **Tier 10 2P (*Pushing the Limit*)**: +12% Haste per 5s con animazione dorata su proc di Hot Streak.
2. **Hot Streak**: Icona del proc con timer e swipe circolare.
3. **Clearcasting**: Lancio gratuito del prossimo incantesimo con timer.
4. **Living Bomb**: Monitoraggio del debuff sul bersaglio con conto alla rovescia per il rinnovo ottimale.
5. **Pyroblast**: Tracciamento del debuff DoT periodico di 12 secondi applicato al bersaglio dal lancio di Pyroblast.
6. **Ignite**: Durata residua del danno periodico da critico sul bersaglio.
7. **Improved Scorch**: Tracciamento del debuff +5% critico magico sul bersaglio.
8. **Molten Fury**: Attivo durante la fase di Execute (bersaglio con salute inferiore al 35%).

### 3. Schermo Pulito ("Zero Clutter")
- **02 - Molten Armor & 03 - Arcane Intellect**: Rimangono nascosti durante il combattimento se hanno più di 5 minuti residui; mostrano il timer solo in scadenza e un avviso visivo in rosso se assenti.
- **04 - Focus Magic**: Nascosto se attivo su un compagno vivo; compare solo se non assegnato, se l'alleato muore, oppure durante il proc personale di 10 secondi (+3% Crit). Tracciamento ultra-leggero via filtro nativo `CLEU:SPELL_AURA_APPLIED:...`.

### 4. Barre Centrali & Avvisi
- **14 - Mana Bar**: Barra orizzontale con visualizzazione della percentuale numerica e cambio di colore in rosso sotto il 20% di mana.
- **15 - Hot Streak Bar**: Barra centrale posizionata graficamente sopra la barra del mana.
- **16 - Castbar**: Barra di lancio con icona dell'incantesimo attivo, nome, tempo residuo e indicatore di latenza.
- **17 - Alerts**: Messaggio testuale visibile a centro schermo all'attivazione di Hot Streak.

### 5. Riga Utility Adattiva (`05` - `13`, da 3 a 10 Icone)
La riga inferiore si adatta in tempo reale con centratura automatica in base all'equipaggiamento indossato:
- **05 - Trinket 1** e **06 - Trinket 2**: Visibili solo se gli slot sono equipaggiati, con timer del recupero interno (ICD reale di 45s/90s/120s o On-Use), animazione cooldown clock swipe radiale e bordo luminoso su proc attivo.
- **06b - Ring**: Compare solo se è equipaggiato nello slot anello (slot 11 o 12) un anello con proc attivo da incantatore/healer (tutti gli anelli del *Verdetto Cinereo*: *Ashen Band of Endless Destruction* / *Wisdom*, e legacy *Band of the Eternal Sage* di Hyjal). Monitora il proc *Frostforged Sage* (+285 SP per 10s, ICD reale di 60s con countdown, clock swipe circolare e Pixel Glow).
- **07 - Cloak**: Compare solo se il mantello possiede un incanto con proc attivo (es. *Ricamo di Luce Intessuta*, +295 SP per 15s, 45s ICD con countdown dinamico di buff e ICD, clock swipe e Pixel Glow).
- **08 - Tier 8**: Compare solo equipaggiando almeno 2 pezzi del set T8, tracciando il bonus *Praxis* (+350 Spell Power, 15s durata, 45s ICD).
- **09 - Gloves**: Compare solo se i guanti possiedono gli *Acceleratori Ipersonici* di Ingegneria (+340 Haste per 12s, 60s CD).
- **10 - Mana Gem**: Mostra le cariche effettive in borsa, il tempo di ricarica e l'attivazione del bonus 2P T7 (*Mana Surge*).
- **11 - Combustion**: Monitora stato attivo, tempo di recupero e cariche critiche residue (+10% a carica).
- **12 - Mirror Image**: Durata delle copie, tempo di recupero e bonus 4P T10 (*Quad Core*, +18% danno).
- **13 - Boots**: Compare solo con incanto di velocità attivo o *Acceleratori a Nitro* di Ingegneria (5s sprint, 3m CD).
- **Centratura Automatica Dinamica**: Qualsiasi combinazione di icone attive (fino a 10 icone con passo adattivo da 26px a 28px) viene allineata in modo perfettamente simmetrico ed equilibrato sotto la barra del mana senza alcun overflow ($\sum x = 0$).

### 6. Pannello Statistiche in Tempo Reale (`18 - Stats Panel`)
Aggiorna in tempo reale i valori effettivi tenendo conto di equipaggiamento, talenti, consumabili e sinergie di raid:
- **Spell Power**: Potenza magica Fuoco totale aggiornata con buff e proc.
- **Crit %**: Include Molten Armor, Combustion nativo e debuff sul bersaglio (*Scorch*, *Totem*) senza conteggi duplicati.
- **Haste %**: Calcola il valore reale combinando rating, *Bloodlust*, totem, talenti e bonus set.
- **Hit %**: Precisione con talenti, aura Draenei e debuff boss, con indicatore verde **`(Cap)`** al raggiungimento del 17%.

### 7. Multi-Target Living Bomb Tracker (`19 - Multi-Target Living Bomb`)
Colonna verticale dinamica posizionata sul lato destro dell'HUD per monitorare fino a 5 Living Bomb attive contemporaneamente su bersagli diversi:
- **Ordinamento Intelligente per Scadenza**: La Living Bomb più vicina all'esplosione (minor tempo residuo) occupa sempre la prima posizione in alto (#1), seguita in ordine cronologico da #2, #3, #4, #5.
- **Timer con Allerta Rossa**:
  - Quando mancano $\le 3$ secondi all'esplosione, il conto alla rovescia si colora di rosso acceso con 1 decimale per allertare il giocatore di preparare la ri-applicazione.
  - Per tempi $> 3$ secondi, mostra i secondi interi bianchi.
- **Motore Real-Time Disaccoppiato**: Frame dedicato `FMHUD_LBFrame` con rilevamento istantaneo del cast (`UNIT_SPELLCAST_SUCCEEDED`), ascolto del combat log multi-bersaglio (`SPELL_AURA_APPLIED/REFRESH/REMOVED`, `UNIT_DIED`) ed emissione dell'evento `FMHUD_LB_UPDATE`.
- **Ritiro Naturale delle Icone**: Quando una bomba esplode o il bersaglio muore, l'icona svanisce e la colonna si contrae automaticamente verso l'alto.

---

## ⚙️ Struttura Modulare del Progetto (`builder/`)

Il codice sorgente separa la compilazione della stringa dalla definizione di ciascun componente dell'interfaccia:

```text
Fire Mage 3.3.5a AM/
├── builder/
│   ├── core/                        # Compressione e codifica stringa WeakAuras
│   │   ├── constants.py             # Costanti, condizioni di caricamento e texture
│   │   ├── serializer.py            # Serializzazione compatibile AceSerializer-3.0
│   │   ├── deflate.py               # Compressione Deflate e codifica LibDeflate
│   │   ├── encoder.py               # Generatore del formato !WA:1!
│   │   └── helpers.py               # Funzioni di supporto per testi e formattazione
│   ├── components/                  # Moduli funzionali dell'HUD
│   │   ├── hot_streak.py            # 15 - Hot Streak Bar (doppio segmento e combat log)
│   │   ├── procs.py                 # 01 - Procs (gruppo dinamico superiore)
│   │   ├── buffs.py                 # 02/03/04 - Molten Armor, Arcane Intellect, Focus Magic
│   │   ├── utility.py               # 05-13 - Monili, Mantello, T8, Guanti, Gemma, Combustion, Copie, Stivali
│   │   ├── bars.py                  # 14 - Mana Bar & 16 - Castbar
│   │   ├── alerts.py                # 17 - Alerts (avvisi testuali centrali)
│   │   ├── stats.py                 # 18 - Stats Panel (pannello statistiche in tempo reale)
│   │   └── multi_lb.py              # 19 - Multi-Target Living Bomb Tracker (colonna destra fino a 5 target)
│   └── tree.py                      # Albero complessivo del gruppo (20 nodi principali, 45 aure)
├── docs/
│   ├── index.html                   # Simulatore web interattivo (tracciato in Git)
│   ├── lich_king_bg.png             # Sfondo grafico del simulatore (tracciato in Git)
│   └── *.md                         # Documentazione interna (RULES, ARCHITECTURE, PRD, DECISIONS, ecc. - esclusa da Git)
├── tests/                           # Suite di test automatici
│   ├── run_parallel_tests.py        # Esecutore parallelo multi-core
│   ├── test_all_utility_cases.py    # Test esaustivo su tutte le combinazioni della riga utility
│   ├── test_components_integrity.py # Verifica integrità strutturale e numerazione 01-19
│   ├── test_equip_switch.py         # Test centratura dinamica durante i cambi di equipaggiamento
│   ├── test_hotstreak_decoupled.py  # Test logica di persistenza Hot Streak e posizionamento
│   ├── test_html_simultaneous.py    # Test di consistenza del simulatore web
│   ├── test_lua.py                  # Controllo sintassi dei blocchi Lua inclusi
│   ├── test_multi_living_bomb.py    # Verifica integrità, triggers e ordinamento del Multi-Target LB
│   ├── test_showcase.py             # Controllo interattività del simulatore
│   ├── test_stats_panel.py          # Verifica formule e moltiplicatori del pannello statistiche
│   ├── test_string_sync.py          # Verifica corrispondenza tra builder e le stringhe WA
│   └── test_tree_layout.py          # Verifica gerarchia e ordinamento dell'albero
├── generate.py                      # Script di compilazione della stringa WeakAuras 5.21.8+
├── IMPORT_STRING_5.21.8.txt         # Stringa WeakAuras 5.21.8+ nativa (Zero Warning, internalVersion: 90)
├── IMPORT_STRING.txt                # Stringa WeakAuras 4.0.0 legacy (CONGELATA permanentemente, internalVersion: 52)
├── IMPORT_STRING_v4.0.0.txt         # Backup certificato v4.0.0
└── scripts/
    └── sync_docs.py                 # Sincronizzazione automatica della stringa v5 in docs/index.html
```

---

## 🚀 Installazione in Gioco (3 Passaggi)

1. **Scegli la Stringa Corretta**:
   - **WeakAuras 5.21.8+ (Consigliata per client moderni)**: Apri **[`IMPORT_STRING_5.21.8.txt`](file:///d:/0Progetti/fire-mage-335a-am/IMPORT_STRING_5.21.8.txt)** (0 warning, 0 triangolini gialli, nativa `internalVersion: 90`).
   - **WeakAuras 4.0.0 (Legacy)**: Apri **[`IMPORT_STRING.txt`](file:///d:/0Progetti/fire-mage-335a-am/IMPORT_STRING.txt)** (versione congelata per client classici, `internalVersion: 52`).
   - Copia l'intero contenuto (`Ctrl+A`, poi `Ctrl+C`).
2. **Apri WeakAuras**: In gioco, digita il comando `/wa` nella chat.
3. **Importa**: Clicca su **Import** in alto a sinistra, incolla il testo con `Ctrl+V` e conferma l'importazione.

---

## 📌 Compatibilità Addon & Client

| Client / Piattaforma | Versione WeakAuras | File Stringa | Compatibilità | Note |
| :--- | :--- | :--- | :---: | :--- |
| **WotLK 3.3.5a (Build 12340)** | **WeakAuras 5.21.8+** | `IMPORT_STRING_5.21.8.txt` | 🏆 **100% Nativa (0 Warning)** | Ottimizzata per motore WA5: usa `WeakAuras.GetRegion(id)`, sandbox protetto con `rawset`, zero chiamate a `GetData`, filtri CLEU selettivi, `internalVersion: 90`. Zero triangolini e zero warning chat. |
| **WotLK 3.3.5a (Build 12340)** | **WeakAuras 4.0.0** | `IMPORT_STRING.txt` | ❄️ **100% Congelata** | Baseline di riferimento per WeakAuras 4.0.0 (`internalVersion: 52`). Non viene mai modificata da script futuri. |

---

## 🧪 Validazione & Test Suite

Il progetto include una suite di 12 test automatici eseguibili sia in parallelo per una verifica rapida, sia in modalità standard:

```bash
# Esecuzione parallela multi-core della suite completa (12 test in ~0.6s)
python tests/run_parallel_tests.py

# Esecuzione standard tramite unittest
python -m unittest discover tests

# Ricompilazione della stringa di importazione nativa WA 5.21.8+
python generate.py

# Sincronizzazione automatica con il simulatore web
python scripts/sync_docs.py
```

---

## 📄 Licenza

Distribuito sotto licenza **MIT**.  
Repository: [Glacyal/fire-mage-335a-am](https://github.com/Glacyal/fire-mage-335a-am)
