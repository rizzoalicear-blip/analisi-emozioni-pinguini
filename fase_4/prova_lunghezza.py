"""
prova_lunghezza.py - SCRIPT di controllo.

A COSA SERVE
  Il modello di pysentimiento legge il testo a pezzetti chiamati TOKEN (grosso modo parti di
  parola) e ne può leggere solo un numero massimo in una volta. Una canzone intera potrebbe
  superare quel limite. Questo script misura, per ognuna delle tue canzoni, quanti token ha
  e li confronta con il limite del modello.

COME LEGGERE IL RISULTATO
  - token della canzone MINORI del limite  -> nessun problema, il modello vede tutta la canzone
  - token della canzone MAGGIORI del limite -> il modello non può leggerla tutta
    (o la libreria la taglia, o la gestisce in un modo che va cercato nella documentazione)

Questo script resta nel repository perche' la tabella dei token nel README (§4)
deriva da qui. Conta anche i 2 token speciali (inizio e fine), quindi i valori
vanno confrontati con il limite di 512. L'altro script, prova_troncamento.py,
conta solo il testo (limite 510) e confronta le emozioni calcolate su inizio e fine.

NOTA: il conteggio usa il tokenizzatore del modello italiano per tutte le canzoni.
Il tokenizzatore del modello inglese spezza il testo italiano in molti piu' pezzi
(per la stessa canzone possono essere 377 token contro 591): per le canzoni
analizzate in fase 4 con un altro modello, il numero reale e' diverso
(vedi prova_troncamento.py).
"""

import os
from pysentimiento import create_analyzer

# ---------------------------------------------------------------------
# PERCORSI (partono dalla posizione dello script, non da dove lo lanci)
# ---------------------------------------------------------------------
CARTELLA_SCRIPT = os.path.dirname(os.path.abspath(__file__))

# Lo script sta in fase_4/, quindi la cartella principale è UNA cartella sopra.
# Se lo metti direttamente nella cartella principale, scrivi invece:
#     CARTELLA_PRINCIPALE = CARTELLA_SCRIPT
CARTELLA_PRINCIPALE = os.path.dirname(CARTELLA_SCRIPT)

CARTELLA_TESTI = os.path.join(CARTELLA_PRINCIPALE, "testi_canzoni")

# ---------------------------------------------------------------------
# CARICAMENTO DEL MODELLO
# ---------------------------------------------------------------------
print("Caricamento del modello pysentimiento (italiano)...")
analizzatore = create_analyzer(task="emotion", lang="it")

# Il "tokenizzatore" è la parte che spezza il testo in token.
tokenizzatore = analizzatore.tokenizer

# Due modi per conoscere il limite del modello: quello dichiarato dal tokenizzatore
# e quello scritto nella configurazione del modello. Se uno non è definito, diventa None.
limite_tokenizzatore = tokenizzatore.model_max_length
limite_modello = getattr(getattr(analizzatore.model, "config", None), "max_position_embeddings", None)

# Alcuni tokenizzatori usano un numero gigantesco per dire "limite non dichiarato":
# in quel caso lo trattiamo come non definito.
if limite_tokenizzatore is not None and limite_tokenizzatore > 100000:
    limite_tokenizzatore = None

print(f"\nLimite dichiarato dal tokenizzatore : {limite_tokenizzatore}")
print(f"Limite scritto nella config. modello: {limite_modello}")
print("\n(Quando compare un avviso di Hugging Face sul testo 'più lungo del massimo' è normale.)\n")

# ---------------------------------------------------------------------
# MISURA DI OGNI CANZONE
# ---------------------------------------------------------------------
print(f"{'Canzone':<50} {'Parole':>7} {'Token':>7}")
print("-" * 66)

for nome_file in sorted(os.listdir(CARTELLA_TESTI)):
    if not nome_file.endswith(".txt"):
        continue

    # Uniamo le righe in un unico testo, come fa lo script della Fase 4
    with open(os.path.join(CARTELLA_TESTI, nome_file), "r", encoding="utf-8") as file:
        testo = " ".join(riga.strip() for riga in file if riga.strip() != "")

    numero_parole = len(testo.split())
    numero_token = len(tokenizzatore(testo)["input_ids"])

    print(f"{nome_file[:-4]:<50} {numero_parole:>7} {numero_token:>7}")

print("\nConfronta la colonna Token con il limite stampato in alto.")
