"""
FASE 4 (confronto) - Analisi delle emozioni con pysentimiento (Transformer)
===================================================================

Obiettivo di questo script:
- leggere il testo INTERO di ogni canzone (non riga per riga, a
  differenza dell'analisi con NRC)
- dare in pasto il testo a pysentimiento, un modello Transformer gia'
  addestrato per riconoscere le emozioni in italiano, inglese e spagnolo
- salvare, per ogni canzone, l'emozione prevalente secondo il modello
  e la sua probabilita', cosi' da poterla confrontare con l'emozione
  prevalente ottenuta con il lessico NRC (fase2_totale_canzone.py)

DIFFERENZE IMPORTANTI rispetto al metodo NRC:
- pysentimiento riconosce 6 emozioni (rabbia, disgusto, paura, gioia,
  tristezza, sorpresa) + una categoria "others" per il resto: NON ha
  "fiducia" ne' "attesa/anticipazione", quindi il confronto tra i due
  metodi ha senso solo sulle 6 emozioni in comune.
- E' un modello che valuta il SIGNIFICATO del testo (non conta parole
  isolate come NRC), quindi e' meno "spiegabile": non ti dice quali
  parole hanno determinato l'emozione.
- La prima volta che lo esegui, la libreria scarica automaticamente i
  pesi del modello da internet (qualche centinaio di MB): serve una
  connessione attiva la prima volta, poi il modello resta salvato in
  cache sul tuo computer.
"""

# ---------------------------------------------------------------------
# IMPORT DELLE LIBRERIE
# ---------------------------------------------------------------------
import os
import csv
import pandas as pd
from pysentimiento import create_analyzer


# ---------------------------------------------------------------------
# CONFIGURAZIONE
# ---------------------------------------------------------------------

CARTELLA_PROGETTO = os.path.dirname(os.path.abspath(__file__))
# Cartella principale del progetto: lo script sta in una cartella di primo livello (es. fase_4/),
# quindi saliamo di UNA cartella (se sta in fase_3/qualcosa/ servono due dirname)
CARTELLA_PRINCIPALE = os.path.dirname(CARTELLA_PROGETTO)
CARTELLA_TESTI = os.path.join(CARTELLA_PRINCIPALE, "testi_canzoni")

# Il CSV riga-per-riga gia' generato da fase2_analisi_emozioni.py: lo
# usiamo solo per sapere qual e' la lingua PIU' FREQUENTE in ciascuna
# canzone (non serve rifare il rilevamento lingua da zero).
PERCORSO_CSV_RIGHE = os.path.join(CARTELLA_PRINCIPALE, "fase_2", "emozioni_per_riga.csv")

# Il CSV che questo script generera' come output.
PERCORSO_CSV_CONFRONTO = os.path.join(CARTELLA_PROGETTO, "emozioni_transformer.csv")

# Lingue supportate da pysentimiento per l'analisi delle emozioni.
# Se una canzone ha come lingua prevalente qualcosa di diverso da
# queste tre, usiamo LINGUA_DI_DEFAULT come ripiego.
LINGUE_SUPPORTATE = ["it", "en", "es"]
LINGUA_DI_DEFAULT = "it"


# ---------------------------------------------------------------------
# FUNZIONI
# ---------------------------------------------------------------------

def ottieni_lingua_prevalente(df_righe, nome_canzone):
    """
    Determina la lingua piu' frequente tra le righe di una canzone,
    usando i dati gia' calcolati da fase2_analisi_emozioni.py.

    Parametri:
        df_righe (pandas.DataFrame): il CSV riga-per-riga gia' letto
        nome_canzone (str): il titolo della canzone da controllare

    Restituisce:
        il codice lingua piu' frequente (es. "it", "en"), scelto tra
        LINGUE_SUPPORTATE; se la lingua piu' frequente non e' tra
        quelle supportate, restituisce LINGUA_DI_DEFAULT
    """
    # Filtriamo solo le righe di questa canzone.
    righe_canzone = df_righe[df_righe["canzone"] == nome_canzone]

    # value_counts() conta quante volte compare ciascuna lingua tra le
    # righe della canzone, in ordine decrescente di frequenza.
    conteggio_lingue = righe_canzone["lingua"].value_counts()

    # Scorriamo le lingue dalla piu' frequente in poi, e restituiamo la
    # prima che troviamo tra quelle supportate da pysentimiento.
    for lingua in conteggio_lingue.index:
        if lingua in LINGUE_SUPPORTATE:
            return lingua

    # Se nessuna lingua tra quelle rilevate e' supportata (caso raro),
    # usiamo il default.
    return LINGUA_DI_DEFAULT


def carica_testo_canzone(nome_canzone, cartella_testi):
    """
    Legge il file .txt di una canzone e lo restituisce come un unico
    blocco di testo (le righe vengono unite con uno spazio), pronto
    per essere analizzato tutto insieme da pysentimiento.

    Parametri:
        nome_canzone (str): titolo della canzone (senza .txt)
        cartella_testi (str): cartella dove si trova il file

    Restituisce:
        il testo completo della canzone come unica stringa, oppure
        None se il file non viene trovato
    """
    percorso_file = os.path.join(cartella_testi, f"{nome_canzone}.txt")

    if not os.path.exists(percorso_file):
        print(f"ATTENZIONE: file non trovato -> {percorso_file}")
        return None

    with open(percorso_file, "r", encoding="utf-8") as file:
        righe = file.readlines()

    # Uniamo tutte le righe in un unico testo, separate da uno spazio
    # (togliendo l'invio a fine riga di ciascuna con .strip()).
    testo_completo = " ".join(riga.strip() for riga in righe if riga.strip() != "")

    return testo_completo


def analizza_canzone_transformer(testo, lingua, cache_analyzer):
    """
    Analizza un testo con il modello pysentimiento della lingua indicata,
    restituendo l'emozione prevalente e la sua probabilita'.

    Parametri:
        testo (str): il testo da analizzare (qui: la canzone intera)
        lingua (str): il codice lingua da usare ("it", "en" o "es")
        cache_analyzer (dict): dizionario che tiene in memoria gli
            analizzatori gia' creati, per non ricrearli ogni volta
            (creare un analizzatore e' un'operazione lenta, che carica
            il modello Transformer: lo facciamo una sola volta per
            lingua e poi lo riusiamo per tutte le canzoni in quella
            lingua)

    Restituisce:
        una tupla (emozione_prevalente, probabilita)
    """
    # Se non abbiamo ancora creato l'analizzatore per questa lingua, lo
    # creiamo ora e lo salviamo nella cache per le prossime canzoni.
    if lingua not in cache_analyzer:
        print(f"Caricamento del modello pysentimiento per la lingua '{lingua}'...")
        cache_analyzer[lingua] = create_analyzer(task="emotion", lang=lingua)

    analizzatore = cache_analyzer[lingua]

    risultato = analizzatore.predict(testo)

    # risultato.output e' il nome dell'emozione prevalente (es. "joy").
    # risultato.probas e' un dizionario con la probabilita' di ciascuna
    # emozione: prendiamo quella dell'emozione prevalente.
    emozione_prevalente = risultato.output
    probabilita = risultato.probas[emozione_prevalente]

    return emozione_prevalente, probabilita


# ---------------------------------------------------------------------
# FUNZIONE PRINCIPALE
# ---------------------------------------------------------------------

def main():
    """
    Funzione principale:
    1. legge il CSV riga-per-riga per sapere la lingua prevalente di
       ciascuna canzone
    2. per ogni canzone, carica il testo intero e lo analizza con
       pysentimiento
    3. salva i risultati in un nuovo CSV, pronto per il confronto con
       i risultati del lessico NRC
    """
    print("Lettura del CSV riga-per-riga (per la lingua prevalente)...")
    df_righe = pd.read_csv(PERCORSO_CSV_RIGHE)

    nomi_canzoni = [
        nome_file[:-4]
        for nome_file in os.listdir(CARTELLA_TESTI)
        if nome_file.endswith(".txt")
    ]

    # Dizionario vuoto: ci finiranno gli analizzatori gia' caricati,
    # uno per ciascuna lingua incontrata (al massimo 3: it, en, es).
    cache_analyzer = {}

    risultati = []
    for nome_canzone in nomi_canzoni:
        lingua_prevalente = ottieni_lingua_prevalente(df_righe, nome_canzone)
        testo_completo = carica_testo_canzone(nome_canzone, CARTELLA_TESTI)

        if testo_completo is None:
            continue

        print(f"Analizzando: {nome_canzone} (lingua: {lingua_prevalente})...")
        emozione, probabilita = analizza_canzone_transformer(
            testo_completo, lingua_prevalente, cache_analyzer
        )

        risultati.append({
            "canzone": nome_canzone,
            "lingua_usata": lingua_prevalente,
            "emozione_transformer": emozione,
            "probabilita": round(probabilita, 4),
        })

    with open(PERCORSO_CSV_CONFRONTO, "w", encoding="utf-8", newline="") as file_csv:
        scrittore = csv.DictWriter(
            file_csv, fieldnames=["canzone", "lingua_usata", "emozione_transformer", "probabilita"]
        )
        scrittore.writeheader()
        scrittore.writerows(risultati)

    print(f"\nFatto. Creato il file: {PERCORSO_CSV_CONFRONTO}")


# ---------------------------------------------------------------------
# BLOCCO DI ESECUZIONE
# ---------------------------------------------------------------------
if __name__ == "__main__":
    main()