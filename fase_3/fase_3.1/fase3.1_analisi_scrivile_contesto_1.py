"""
FASE 3 (caso studio) - Analisi di 'Scrivile Scemo' con contesto
===================================================================

Obiettivo di questo script:
- ripartire DAVVERO dal file Scrivile Scemo.txt (non dal CSV gia'
  calcolato), come per la Fase 2 originale
- pulire il testo, rilevare la lingua di ogni riga (stessa logica gia'
  validata in fase2_analisi_emozioni.py)
- MA, a differenza della Fase 2 originale, il conteggio delle parole
  nel lessico NRC per ciascuna riga include ANCHE le parole delle
  righe vicine (RAGGIO_FINESTRA righe prima e dopo), non solo quelle
  della riga stessa
- salvare il risultato in un CSV dedicato a questa canzone

E' uno script mirato a UNA sola canzone (Scrivile Scemo), pensato per
il caso studio sul limite del linguaggio figurato di cui abbiamo
discusso (es. un verso con parole forti): l'idea e'
vedere se, includendo il contesto circostante nel conteggio, il
punteggio di quella riga risulta piu' equilibrato rispetto all'analisi
sulla riga isolata.
"""

# ---------------------------------------------------------------------
# IMPORT DELLE LIBRERIE
# ---------------------------------------------------------------------
import os
import csv
import hashlib    # per calcolare l'impronta (hash) di ogni riga di testo
import re
from langdetect import detect, LangDetectException
from langdetect.detector_factory import DetectorFactory

DetectorFactory.seed = 0


# ---------------------------------------------------------------------
# CONFIGURAZIONE
# ---------------------------------------------------------------------

CARTELLA_PROGETTO = os.path.dirname(os.path.abspath(__file__))
# Cartella principale del progetto. Lo script sta in una sottocartella di fase_3 (due livelli
# sotto, come fase_3/fase_3.2/), quindi saliamo di DUE cartelle.
# Se lo script stesse in una sola cartella (es. fase_3/), usa un solo dirname:
#   CARTELLA_PRINCIPALE = os.path.dirname(CARTELLA_PROGETTO)
CARTELLA_PRINCIPALE = os.path.dirname(os.path.dirname(CARTELLA_PROGETTO))

CARTELLA_TESTI = os.path.join(CARTELLA_PRINCIPALE, "testi_canzoni")

PERCORSO_LESSICO_NRC = os.path.join(CARTELLA_PRINCIPALE, "fase_2", "Italian-NRC-EmoLex.txt")
PERCORSO_LESSICO_NRC_ES = os.path.join(CARTELLA_PRINCIPALE, "fase_2", "Spanish-NRC-EmoLex.txt")

# La canzone su cui lavora questo script: e' scritta nel codice (non
# come lista) perche' e' un caso studio mirato a una sola canzone.
NOME_CANZONE = "Scrivile Scemo"

# Quante righe PRIMA e DOPO includere nel conteggio di ciascuna riga.
# 0 = nessun contesto (equivalente alla Fase 2 originale, solo la riga
# stessa). 1 = riga corrente + 1 prima + 1 dopo. Cambialo per provare
# un contesto piu' o meno ampio.
RAGGIO_FINESTRA = 1

PERCORSO_CSV_OUTPUT = os.path.join(
    CARTELLA_PROGETTO, f"emozioni_{NOME_CANZONE.replace(' ', '_')}_contesto_raggio{RAGGIO_FINESTRA}.csv"
)

MAPPA_EMOZIONI = {
    "anger": "rabbia", "anticipation": "attesa", "disgust": "disgusto", "fear": "paura",
    "joy": "gioia", "sadness": "tristezza", "surprise": "sorpresa", "trust": "fiducia",
}

LUNGHEZZA_MINIMA_PER_RILEVAZIONE = 15
LINGUA_DI_DEFAULT = "it"

# ---------------------------------------------------------------------
# ECCEZIONI DI LINGUA (lette dal file delle impronte)
# ---------------------------------------------------------------------
# Alcune righe sono sbagliate da langdetect e la lingua e' stata verificata
# a mano. Per non scrivere nel codice i versi (protetti da copyright), nel
# repository c'e' solo un file con l'IMPRONTA (hash) di ogni riga e la sua
# lingua: fase_2/eccezioni_lingua_hash.csv.
#
# Questo script sta in fase_3/fase_3.1/, quindi per arrivare alla cartella
# principale del progetto (quella con fase_2, fase_3...) servono TRE dirname:
#   __file__ -> percorso di questo script
#   dirname 1 -> fase_3.1    dirname 2 -> fase_3    dirname 3 -> cartella principale
PERCORSO_ECCEZIONI_HASH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "fase_2",
    "eccezioni_lingua_hash.csv",
)


def calcola_impronta(testo):
    """
    Trasforma una riga di testo nella sua impronta SHA-256: una stringa di
    64 caratteri, sempre uguale per lo stesso testo e completamente diversa
    se cambia anche una sola lettera.
    (Identica alla funzione usata in crea_hash_eccezioni.py: le due devono
    restare uguali, altrimenti le impronte non coincidono.)
    """
    return hashlib.sha256(testo.encode("utf-8")).hexdigest()


def carica_eccezioni_hash(percorso_file):
    """
    Legge fase_2/eccezioni_lingua_hash.csv (colonne: hash, lingua) e
    restituisce un dizionario {impronta: codice_lingua}.

    Se il file non esiste restituisce un dizionario vuoto e avvisa: lo
    script funziona lo stesso, ma le righe che langdetect sbaglia non
    vengono corrette e i risultati possono differire.
    """
    eccezioni = {}

    if not os.path.exists(percorso_file):
        print(f"ATTENZIONE: file delle impronte non trovato -> {percorso_file}")
        return eccezioni

    with open(percorso_file, "r", encoding="utf-8", newline="") as file:
        # DictReader usa la prima riga ("hash,lingua") come nomi delle colonne.
        for riga in csv.DictReader(file):
            eccezioni[riga["hash"]] = riga["lingua"]

    return eccezioni


# Caricato una sola volta, all'avvio, e usato da rileva_lingua().
ECCEZIONI_LINGUA_HASH = carica_eccezioni_hash(PERCORSO_ECCEZIONI_HASH)

# ---------------------------------------------------------------------
# FUNZIONI: PULIZIA TESTO E RILEVAMENTO LINGUA (identiche alla Fase 2)
# ---------------------------------------------------------------------

def pulisci_punteggiatura(testo):
    """Ripulisce una riga dalla punteggiatura (stessa logica di fase2_analisi_emozioni.py)."""
    testo = re.sub(r"['’-]", " ", testo)
    testo = re.sub(r'[.,:"“”?!()…]', "", testo)
    testo = re.sub(r"\s+", " ", testo)
    return testo


def rileva_lingua(riga):
    """Rileva la lingua di una riga (stessa logica di fase2_analisi_emozioni.py)."""
    # Calcoliamo l'impronta della riga e vediamo se e' tra le eccezioni
    # verificate a mano: in quel caso usiamo la lingua indicata.
    impronta = calcola_impronta(riga)
    if impronta in ECCEZIONI_LINGUA_HASH:
        return ECCEZIONI_LINGUA_HASH[impronta]
    if len(riga.strip()) < LUNGHEZZA_MINIMA_PER_RILEVAZIONE:
        return LINGUA_DI_DEFAULT
    try:
        return detect(riga)
    except LangDetectException:
        return LINGUA_DI_DEFAULT


# ---------------------------------------------------------------------
# FUNZIONI: CARICAMENTO LESSICO (identiche alla Fase 2)
# ---------------------------------------------------------------------

def carica_lessico(percorso_file, nome_colonna_parola):
    """Legge il file NRC e costruisce il dizionario parola -> emozioni (stessa logica della Fase 2)."""
    lessico = {}
    with open(percorso_file, "r", encoding="utf-8") as file:
        lettore = csv.DictReader(file, delimiter="\t")
        for riga_lessico in lettore:
            parola = riga_lessico[nome_colonna_parola].strip().lower()
            if parola == "":
                continue
            emozioni_parola = {}
            for colonna_inglese, nome_italiano in MAPPA_EMOZIONI.items():
                valore = riga_lessico.get(colonna_inglese, "0")
                emozioni_parola[nome_italiano] = int(valore)
            lessico[parola] = emozioni_parola
    return lessico


# ---------------------------------------------------------------------
# FUNZIONI SPECIFICHE DI QUESTO SCRIPT
# ---------------------------------------------------------------------

def carica_e_prepara_righe(nome_canzone, cartella_testi):
    """
    Legge il file .txt della canzone e prepara, per ciascuna riga: il
    testo pulito e la lingua rilevata. E' il passo preliminare prima
    di poter contare le emozioni con o senza contesto.

    Parametri:
        nome_canzone (str): titolo della canzone (senza .txt)
        cartella_testi (str): cartella dove si trova il file

    Restituisce:
        una lista di dizionari, uno per riga:
        [{"numero_riga": 1, "testo": "...", "lingua": "it"}, ...]
    """
    percorso_file = os.path.join(cartella_testi, f"{nome_canzone}.txt")

    with open(percorso_file, "r", encoding="utf-8") as file:
        righe_grezze = file.readlines()

    righe_preparate = []
    for numero_riga, riga in enumerate(righe_grezze, start=1):
        riga_pulita = pulisci_punteggiatura(riga).strip()
        if riga_pulita == "":
            continue

        lingua = rileva_lingua(riga_pulita)
        righe_preparate.append({
            "numero_riga": numero_riga,
            "testo": riga_pulita,
            "lingua": lingua,
        })

    return righe_preparate


def conta_emozioni_con_contesto(righe_preparate, indice_riga, raggio_finestra, lessico_it, lessico_en, lessico_es):
    """
    Conta le emozioni per UNA riga, includendo nel conteggio anche le
    parole delle righe vicine (fino a raggio_finestra righe prima e
    dopo), ciascuna cercata nel lessico della PROPRIA lingua rilevata
    (una riga in inglese vicina a una in italiano usa comunque il
    lessico inglese per le sue parole, non quello italiano).

    Parametri:
        righe_preparate (list): l'elenco completo delle righe della
            canzone (da carica_e_prepara_righe)
        indice_riga (int): la posizione (0-based) della riga per cui
            calcolare il punteggio
        raggio_finestra (int): quante righe prima/dopo includere
        lessico_it, lessico_en, lessico_es (dict): i tre lessici NRC

    Restituisce:
        un dizionario {"rabbia": n, "gioia": n, ...} con il conteggio
        totale sulla finestra di righe
    """
    totale = {nome_italiano: 0 for nome_italiano in MAPPA_EMOZIONI.values()}

    # Calcoliamo l'intervallo di righe da includere, facendo attenzione
    # a non uscire dai confini della lista (max/min tengono la finestra
    # dentro i limiti 0 .. lunghezza-1, invece di andare in errore o
    # "sconfinare" fuori dalla canzone).
    indice_inizio = max(0, indice_riga - raggio_finestra)
    indice_fine = min(len(righe_preparate) - 1, indice_riga + raggio_finestra)

    for indice_corrente in range(indice_inizio, indice_fine + 1):   #blocco si ripete per ogni riga della finestra, non solo per quella centrale
        riga = righe_preparate[indice_corrente]
        lingua_riga = riga["lingua"]

        if lingua_riga == "en":
            lessico_da_usare = lessico_en
        elif lingua_riga == "es":
            lessico_da_usare = lessico_es
        else:
            lessico_da_usare = lessico_it

        for parola in riga["testo"].split():  #spezza in una lista di parole singole, dividendo sugli spazi
            if parola in lessico_da_usare:  #dizionario NRC giusto
                emozioni_parola = lessico_da_usare[parola]  #se la parola è nel dizionario, recuperiamo il suo valore
                for nome_emozione in totale:
                    totale[nome_emozione] += emozioni_parola[nome_emozione] #sommiamo il contributo di questa parola al totale accumulato finora

    return totale


# ---------------------------------------------------------------------
# FUNZIONE PRINCIPALE
# ---------------------------------------------------------------------

def main():
    print("Caricamento del lessico NRC (italiano, inglese, spagnolo)...")
    lessico_it = carica_lessico(PERCORSO_LESSICO_NRC, "Italian Word")
    lessico_en = carica_lessico(PERCORSO_LESSICO_NRC, "English Word")
    lessico_es = carica_lessico(PERCORSO_LESSICO_NRC_ES, "Spanish Word")

    print(f"Lettura e preparazione di '{NOME_CANZONE}.txt'...")
    righe_preparate = carica_e_prepara_righe(NOME_CANZONE, CARTELLA_TESTI)

    print(f"Calcolo delle emozioni con contesto (finestra ±{RAGGIO_FINESTRA} righe)...")
    risultati = []
    for indice, riga in enumerate(righe_preparate):
        emozioni_contesto = conta_emozioni_con_contesto(
            righe_preparate, indice, RAGGIO_FINESTRA, lessico_it, lessico_en, lessico_es
        )

        riga_completa = {
            "canzone": NOME_CANZONE,
            "numero_riga": riga["numero_riga"],
            "testo": riga["testo"],
            "lingua": riga["lingua"],
        }
        riga_completa.update(emozioni_contesto)
        risultati.append(riga_completa)

    nomi_colonne = ["canzone", "numero_riga", "testo", "lingua"] + list(MAPPA_EMOZIONI.values())
    with open(PERCORSO_CSV_OUTPUT, "w", encoding="utf-8", newline="") as file_csv:
        scrittore = csv.DictWriter(file_csv, fieldnames=nomi_colonne)
        scrittore.writeheader()
        scrittore.writerows(risultati)

    print(f"\nFatto. Creato il file: {PERCORSO_CSV_OUTPUT}")
    print("\nAnteprima dei risultati:")
    for riga_risultato in risultati:
        print(f"{riga_risultato['numero_riga']}: {riga_risultato['testo']}")
        print(f"   -> {[(k, v) for k, v in riga_risultato.items() if k in MAPPA_EMOZIONI.values() and v > 0]}")


# ---------------------------------------------------------------------
# BLOCCO DI ESECUZIONE
# ---------------------------------------------------------------------
if __name__ == "__main__":
    main()