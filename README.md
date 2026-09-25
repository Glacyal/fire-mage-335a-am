# Class Mage (TTW Fire) — WeakAuras Suite

[![WoW Version](https://img.shields.io/badge/World%20of%20Warcraft-3.3.5a%20(12340)-orange.svg)](https://github.com/Glacyal/fire-mage-335a-am)
[![WeakAuras](https://img.shields.io/badge/WeakAuras-4.0.0-blue.svg)](https://github.com/Glacyal/fire-mage-335a-am)
[![Class](https://img.shields.io/badge/Class-Mage%20(Fire%20TTW)-red.svg)](https://github.com/Glacyal/fire-mage-335a-am)
[![GitHub Pages](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-brightgreen.svg)](https://glacyal.github.io/fire-mage-335a-am/)
[![Buy me a coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-gray.svg?logo=paypal&logoColor=white&labelColor=0079c1)](https://www.paypal.me/AMantmar)

Suite WeakAuras completa, modulare e ordinata per **Mago Fire Livello 80** in World of Warcraft 3.3.5a (*Wrath of the Lich King - Build 12340*).  
Progettata per garantire un'elevata fluidità in combattimento, un consumo ridotto di risorse CPU, un monitoraggio chiaro e affidabile dei proc e un'interfaccia pulita senza elementi superflui, orientata all'ottimizzazione del DPS.

---

## 🌐 Anteprima Online (Live Simulator)

Visualizza e interagisci con l'HUD direttamente dal browser senza installare nulla:  
👉 **[Apri il Simulatore Web su GitHub Pages](https://glacyal.github.io/fire-mage-335a-am/)**  
*(Disponibile anche in locale nel file [`docs/index.html`](file:///d:/0Progetti/Fire%20Mage%203.3.5a%20AM/docs/index.html))*

---

## 🌟 Caratteristiche Principali

Tutti i componenti del pacchetto sono organizzati con una numerazione sequenziale ordinata (da **01** a **19**):

### 1. Barra Hot Streak a Doppio Segmento (`15 - Hot Streak Bar`)
Posizionata visivamente a schermo subito sopra la barra del mana, è suddivisa in **due metà indipendenti**:
- **Mezza Barra Sinistra (Segment 1)**:
  - Si illumina in arancione al primo colpo critico diretto (*Fireball, Scorch, Fire Blast, Frostfire Bolt, esplosione di Living Bomb*).
  - Rimane memorizzata nel tempo anche al termine del combattimento, finché non si mette a segno un nuovo colpo diretto.
  - Si azzera solo al secondo critico consecutivo (che attiva il proc) oppure in caso di colpo non critico. Non si azzera lanciando Pyroblast (*Rolling Hot Streak*).
- **Mezza Barra Destra (Proc)**:
  - Mostra il buff **Hot Streak** (Spell ID 48108) con conto alla rovescia di 10 secondi e bordo luminoso dorato.
  - Si spegne quando il buff viene consumato dal lancio della Pyroblast istantanea o alla scadenza naturale. Se il buff scade, l'eventuale singolo critico registrato a sinistra rimane salvato.

### 2. Gruppo Dinamico Procs (`01 - Procs`)
Posizionato nella parte superiore dell'HUD, gestisce fino a 7 icone con riposizionamento orizzontale automatico:
1. **Tier 10 2P (*Pushing the Limit*)**: +12% Haste per 5s con animazione dorata su proc di Hot Streak.
2. **Hot Streak**: Icona del proc con timer e swipe circolare.
3. **Clearcasting**: Lancio gratuito del prossimo incantesimo con timer.
4. **Living Bomb**: Monitoraggio del debuff sul bersaglio con conto alla rovescia per il rinnovo ottimale.
5. **Ignite**: Durata residua del danno periodico da critico sul bersaglio.
6. **Improved Scorch**: Tracciamento del debuff +5% critico magico sul bersaglio.
7. **Molten Fury**: Attivo durante la fase di Execute (bersaglio con salute inferiore al 35%).

### 3. Schermo Pulito ("Zero Clutter")
- **02 - Molten Armor & 03 - Arcane Intellect**: Rimangono nascosti durante il combattimento se hanno più di 5 minuti residui; mostrano il timer solo in scadenza e un avviso visivo in rosso se assenti.
- **04 - Focus Magic**: Nascosto se attivo su un compagno vivo; compare solo se non assegnato, se l'alleato muore, oppure durante il proc personale di 10 secondi (+3% Crit).

### 4. Barre Centrali & Avvisi
- **14 - Mana Bar**: Barra orizzontale con visualizzazione della percentuale numerica e cambio di colore in rosso sotto il 20% di mana.
- **15 - Hot Streak Bar**: Barra centrale posizionata graficamente sopra la barra del mana.
- **16 - Castbar**: Barra di lancio con icona dell'incantesimo attivo, nome, tempo residuo e indicatore di latenza.
- **17 - Alerts**: Messaggio testuale visibile a centro schermo all'attivazione di Hot Streak.

### 5. Riga Utility Adattiva (`05` - `13`, da 3 a 9 Icone)
La riga inferiore si adatta in tempo reale con centratura automatica in base all'equipaggiamento indossato:
- **05 - Trinket 1** e **06 - Trinket 2**: Visibili solo se gli slot sono equipaggiati, con timer del recupero interno (ICD) e bordo luminoso su proc attivo.
- **07 - Cloak**: Compare solo se il mantello ha un incanto con proc attivo (es. *Ricamo di Luce Intessuta*).
- **08 - Tier 8**: Compare solo equipaggiando almeno 2 pezzi del set T8, tracciando il bonus +350 Spell Power.
- **09 - Gloves**: Compare solo se i guanti possiedono gli *Acceleratori Ipersonici* di Ingegneria.
- **10 - Mana Gem**: Mostra le cariche effettive in borsa, il tempo di ricarica e l'attivazione del bonus 2P T7.
- **11 - Combustion**: Monitora stato attivo, tempo di recupero e cariche critiche residue (+10% a carica).
- **12 - Mirror Image**: Durata delle copie, tempo di recupero e bonus 4P T10 (+18% danno).
- **13 - Boots**: Compare solo con incanto di velocità attivo o *Acceleratori a Nitro* di Ingegneria.
- **Centratura Automatica**: Qualsiasi combinazione di icone attive viene allineata in modo simmetrico ed equilibrato rispetto al centro.

### 6. Pannello Statistiche in Tempo Reale (`18 - Stats Panel`)
Aggiorna in tempo reale i valori effettivi tenendo conto di equipaggiamento, talenti, consumabili e sinergie di raid:
- **Spell Power**: Potenza magica Fuoco totale aggiornata con buff e proc.
- **Crit %**: Include Molten Armor, Combustion nativo e debuff sul bersaglio (*Scorch*, *Totem*) senza conteggi duplicati.
- **Haste %**: Calcola il valore reale combinando rating, *Bloodlust*, totem, talenti e bonus set.
- **Hit %**: Precisione con talenti, aura Draenei e debuff boss, con indicatore verde **`(Cap)`** al raggiungimento del 17%.

### 7. Multi-Target Living Bomb Tracker (`19 - Multi-Target Living Bomb`)
Colonna verticale dinamica posizionata sul lato destro dell'HUD (`xOffset = 165, yOffset = 45`) per monitorare fino a 5 Living Bomb attive contemporaneamente su bersagli diversi:
- **Ordinamento Intelligente per Scadenza**: La Living Bomb più vicina all'esplosione (minor tempo residuo) occupa sempre la prima posizione in alto (#1), seguita in ordine cronologico da #2, #3, #4, #5.
- **Timer con Allerta Rossa**:
  - Quando mancano $\le 3$ secondi all'esplosione, il conto alla rovescia si colora di rosso acceso con 1 decimale (`|cFFFF4444%.1fs|r`) per allertare il giocatore di preparare la ri-applicazione.
  - Per tempi $> 3$ secondi, mostra i secondi interi bianchi (`%.0fs`).
- **Motore Real-Time Disaccoppiato**: Frame dedicato `FMHUD_LBFrame` con rilevamento istantaneo del cast (`UNIT_SPELLCAST_SUCCEEDED`), ascolto del combat log multi-bersaglio (`SPELL_AURA_APPLIED/REFRESH/REMOVED`, `UNIT_DIED`) e sincronizzazione con il server via `UnitDebuff`.
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
│   └── tree.py                      # Albero complessivo del gruppo (19 nodi principali, 43 aure)
├── docs/
│   └── index.html                   # Simulatore web interattivo
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
│   ├── test_string_sync.py          # Verifica corrispondenza tra builder e IMPORT_STRING.txt
│   └── test_tree_layout.py          # Verifica gerarchia e ordinamento dell'albero
├── generate.py                      # Script di compilazione della stringa finale
├── IMPORT_STRING.txt                # Stringa WeakAuras pronta per l'importazione
└── scripts/
    └── sync_docs.py                 # Sincronizzazione automatica di IMPORT_STRING.txt in docs/index.html
```

---

## 🚀 Installazione in Gioco (3 Passaggi)

1. **Copia la Stringa**: Apri il file **[`IMPORT_STRING.txt`](file:///d:/0Progetti/Fire%20Mage%203.3.5a%20AM/IMPORT_STRING.txt)** e copia l'intero contenuto (`Ctrl+A`, poi `Ctrl+C`).
2. **Apri WeakAuras**: In gioco, digita il comando `/wa` nella chat.
3. **Importa**: Clicca su **Import** in alto a sinistra, incolla il testo con `Ctrl+V` e conferma l'importazione.

---

## 📌 Compatibilità Addon & Client

| Client / Piattaforma | Versione WeakAuras | Compatibilità | Note |
| :--- | :--- | :---: | :--- |
| **WotLK 3.3.5a (Build 12340)** | **WeakAuras 4.0.0** | ✅ **100% Nativa** | Sviluppata e collaudata su WeakAuras 4.0.0 (`internalVersion: 52`). Importazione rapida e priva di blocchi (~48 KB). |
| **WotLK Classic / Cata Classic** | WeakAuras 5.x (Blizzard) | ⚠️ **Parziale** | Struttura compatibile, ma richiede l'adattamento delle chiamate Lua del Combat Log (`CombatLogGetCurrentEventInfo`). |
| **Retail** | WeakAuras 5.x | ❌ **Non Compatibile** | Meccaniche e abilità della classe sostanzialmente differenti. |

---

## 🧪 Validazione & Test Suite

Il progetto include una suite di 12 test automatici eseguibili sia in parallelo per una verifica rapida, sia in modalità standard:

```bash
# Esecuzione parallela multi-core della suite completa
python tests/run_parallel_tests.py

# Esecuzione standard tramite unittest
python -m unittest discover tests

# Ricompilazione della stringa di importazione
python generate.py
```

---

## 📄 Licenza

Distribuito sotto licenza **MIT**.  
Repository: [Glacyal/fire-mage-335a-am](https://github.com/Glacyal/fire-mage-335a-am)
