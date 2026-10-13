"""
FASE 2 - Analisi delle emozioni riga per riga con il lessico NRC
===================================================================

Obiettivo di questo script:
- leggere tutti i file .txt gia' scaricati nella Fase 1 (dentro testi_canzoni/)
- per ogni riga di ogni canzone:
    1. rilevare la lingua (riusando la stessa logica gia' testata: langdetect
       + dizionario di eccezioni verificate a mano)
    2. dividere la riga in parole singole
    3. per ogni parola, cercarla nel dizionario NRC della lingua giusta
       (italiano o inglese) e contare a quali delle 8 emozioni base
       appartiene
    4. sommare i conteggi di tutte le parole della riga
- salvare tutto in un unico file CSV, con una riga di tabella per ogni
  riga di testo: questo ci permette sia l'analisi per riga (andamento
  dentro la canzone) sia l'analisi totale per canzone (basta sommare
  con pandas, non serve calcolarla qui).

NOTA IMPORTANTE: questo script richiede il file del lessico NRC gia'
scaricato (vedi PERCORSO_LESSICO_NRC qui sotto). Il file usato e'
"Italian-NRC-EmoLex.txt" dalla cartella OneFilePerLanguage del NRC
Emotion Lexicon: contiene sia la colonna della parola italiana sia
quella della parola inglese originale, quindi basta questo unico file
per costruire ENTRAMBI i dizionari (italiano e inglese).
"""

# ---------------------------------------------------------------------
# IMPORT DELLE LIBRERIE
# ---------------------------------------------------------------------
import os                                              # per leggere i file dalla cartella
import csv 
import hashlib    # per calcolare l'impronta (hash) di ogni riga di testo                                            # per scrivere il file CSV di output
from langdetect import detect, LangDetectException     # per rilevare la lingua
from langdetect.detector_factory import DetectorFactory  # per rendere i risultati riproducibili

# Fissiamo il seed per avere risultati riproducibili tra un'esecuzione e
# l'altra (stessa logica gia' usata nello script di test della lingua).
DetectorFactory.seed = 0


# ---------------------------------------------------------------------
# CONFIGURAZIONE
# ---------------------------------------------------------------------

# CARTELLA_PROGETTO e' la cartella dove si trova FISICAMENTE questo file
# .py (non quella da cui lo lanci). __file__ e' una variabile speciale
# che Python valorizza automaticamente con il percorso di questo script;
# os.path.abspath() lo trasforma in un percorso completo (assoluto), e
# os.path.dirname() ne prende solo la cartella, scartando il nome del file.
# Costruendo tutti i percorsi a partire da qui, lo script funziona allo
# stesso modo indipendentemente da dove lo esegui (VS Code, terminale,
# doppio click, ecc.).
CARTELLA_PROGETTO = os.path.dirname(os.path.abspath(__file__))
# Cartella principale del progetto: quella che contiene fase_1, fase_2, fase_3...
CARTELLA_PRINCIPALE = os.path.dirname(CARTELLA_PROGETTO)
# Cartella dove la Fase 1 ha salvato i testi puliti.
CARTELLA_TESTI = os.path.join(CARTELLA_PRINCIPALE, "testi_canzoni")

# Percorso del file del lessico NRC scaricato. Deve stare nella stessa
# cartella di questo script (vedi CARTELLA_PROGETTO sopra).
PERCORSO_LESSICO_NRC = os.path.join(CARTELLA_PROGETTO, "Italian-NRC-EmoLex.txt")

# Nome del file CSV che questo script generera' come output (verra'
# creato anch'esso nella cartella del progetto).
PERCORSO_CSV_OUTPUT = os.path.join(CARTELLA_PROGETTO, "emozioni_per_riga.csv")

# Le 8 emozioni base del modello NRC, con il nome della colonna nel file
# scaricato (in inglese, così come lo troverai nel file) associato al
# nome italiano che useremo invece nel nostro CSV di output (piu' comodo
# da leggere per il resto del progetto).
MAPPA_EMOZIONI = {
    "anger": "rabbia",
    "anticipation": "attesa",
    "disgust": "disgusto",
    "fear": "paura",
    "joy": "gioia",
    "sadness": "tristezza",
    "surprise": "sorpresa",
    "trust": "fiducia",
}

# Soglia minima di caratteri sotto la quale non ci fidiamo di langdetect.
LUNGHEZZA_MINIMA_PER_RILEVAZIONE = 15

# Lingua di default quando la rilevazione fallisce o la riga e' troppo corta.
LINGUA_DI_DEFAULT = "it"

# ECCEZIONI DI LINGUA (lette dal file delle impronte)
# ---------------------------------------------------------------------
# Alcune righe sono sbagliate da langdetect e la lingua e' stata verificata
# a mano. Per non scrivere nel codice i versi (protetti da copyright), nel
# repository c'e' solo un file con l'IMPRONTA (hash) di ogni riga e la sua
# lingua. Il file sta nella stessa cartella di questo script (fase_2).
PERCORSO_ECCEZIONI_HASH = os.path.join(CARTELLA_PROGETTO, "eccezioni_lingua_hash.csv")


def calcola_impronta(testo):
    """
    Trasforma una riga di testo nella sua impronta SHA-256: una stringa di
    64 caratteri, sempre uguale per lo stesso testo e completamente diversa
    se cambia anche una sola lettera.
    (Identica alla funzione di crea_hash_eccezioni.py: le due devono
    restare uguali, altrimenti le impronte non coincidono.)
    """
    return hashlib.sha256(testo.encode("utf-8")).hexdigest()


def carica_eccezioni_hash(percorso_file):
    """
    Legge eccezioni_lingua_hash.csv (colonne: hash, lingua) e restituisce
    un dizionario {impronta: codice_lingua}.

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
# FUNZIONI: RILEVAMENTO LINGUA (identiche allo script di test)
# ---------------------------------------------------------------------

def rileva_lingua(riga):
    """
    Rileva la lingua di una riga di testo, controllando prima le
    eccezioni verificate a mano e solo dopo tentando langdetect.

    Parametri:
        riga (str): la riga di cui rilevare la lingua

    Restituisce:
        il codice della lingua rilevata (es. "it", "en", "es")
    """
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
# FUNZIONI: CARICAMENTO DEL LESSICO NRC
# ---------------------------------------------------------------------

def carica_lessico(percorso_file, nome_colonna_parola):
    """
    Legge il file del lessico NRC e costruisce un dizionario che associa
    ad ogni parola (in minuscolo) l'elenco delle emozioni a cui è
    associata secondo NRC.

    Questa funzione viene chiamata due volte nel programma: una volta
    con nome_colonna_parola="Italian Word" per ottenere il lessico
    italiano, una volta con "English Word" per ottenere quello inglese
    — dallo stesso identico file, perché il file scaricato contiene
    entrambe le colonne allineate alle stesse emozioni.

    Parametri:
        percorso_file (str): percorso del file del lessico NRC
        nome_colonna_parola (str): nome della colonna da usare come
            parola-chiave del dizionario ("Italian Word" o "English Word")

    Restituisce:
        un dizionario {"rabbia": 0 o 1, "gioia": 0 o 1, ...}
    """
    lessico = {}

    with open(percorso_file, "r", encoding="utf-8") as file:
        # csv.DictReader legge il file riga per riga e restituisce ogni
        # riga come un dizionario {nome_colonna: valore}, usando la
        # prima riga del file come intestazione delle colonne.
        lettore = csv.DictReader(file, delimiter="\t")

        for riga_lessico in lettore:
            # .lower() serve per il DIZIONARIO NRC, non per i testi: i testi delle canzoni
            # sono già in minuscolo dalla Fase 1, ma le voci del file del lessico potrebbero
            # avere maiuscole. Senza questa riga "Amore" nel lessico non troverebbe
            # corrispondenza con "amore" nel testo e i punti verrebbero persi in silenzio.
            parola = riga_lessico[nome_colonna_parola].strip().lower() #.lower: necessario a prescindere da quello inserito in Fase 1, perché riguarda la capitalizzazione del dizionario esterno

            # Se la parola e' vuota (puo' capitare in alcune righe del
            # file di traduzione), la saltiamo.
            if parola == "":
                continue

            # Costruiamo il dizionario delle emozioni per questa parola,
            # leggendo le colonne indicate in MAPPA_EMOZIONI e
            # convertendo il valore ("0" o "1", come testo) in intero.
            emozioni_parola = {}
            for colonna_inglese, nome_italiano in MAPPA_EMOZIONI.items():
                valore = riga_lessico.get(colonna_inglese, "0")
                emozioni_parola[nome_italiano] = int(valore)

            lessico[parola] = emozioni_parola

    return lessico


# ---------------------------------------------------------------------
# FUNZIONI: CONTEGGIO DELLE EMOZIONI DI UNA RIGA
# ---------------------------------------------------------------------

def conta_emozioni_riga(riga_pulita, lingua, lessico_it, lessico_en):
    """
    Conta le emozioni presenti in una riga di testo, sommando i punteggi
    di ogni singola parola trovata nel dizionario NRC della lingua giusta.

    Parametri:
        riga_pulita (str): la riga di testo (gia' pulita dalla punteggiatura)
        lingua (str): il codice lingua rilevato per questa riga
        lessico_it (dict): il dizionario NRC italiano
        lessico_en (dict): il dizionario NRC inglese

    Restituisce:
        un dizionario {"rabbia": n, "gioia": n, ...} con il conteggio
        totale della riga per ciascuna delle 8 emozioni
    """
    # Scegliamo quale dizionario usare in base alla lingua rilevata.
    # Per lingue diverse da italiano/inglese (es. "es" per lo spagnolo
    # di Gigi cinque ottavi), non abbiamo un lessico dedicato: usiamo
    # comunque quello italiano come fallback, sapendo che quelle
    # specifiche parole (essendo spagnole) probabilmente non troveranno
    # corrispondenza e contribuiranno con 0 a tutte le emozioni. Questo
    # e' un limite noto del metodo, da segnalare nella relazione finale.
    if lingua == "en":
        lessico_da_usare = lessico_en
    else:
        lessico_da_usare = lessico_it

    # Inizializziamo il totale della riga a 0 per ciascuna emozione.
    totale_riga = {nome_italiano: 0 for nome_italiano in MAPPA_EMOZIONI.values()}

    # Dividiamo la riga in singole parole (lo spazio e' gia' l'unico
    # separatore rimasto, grazie alla pulizia fatta nella Fase 1).
    parole = riga_pulita.split()

    for parola in parole:
        # Non serve piu' trasformare la parola in minuscolo qui: la
        # Fase 1 salva gia' il testo tutto minuscolo, quindi "parola"
        # e' gia' nella forma giusta per il confronto con il lessico
        # (che a sua volta e' stato caricato gia' minuscolo).
        if parola in lessico_da_usare:
            emozioni_parola = lessico_da_usare[parola]
            for nome_emozione in totale_riga:
                totale_riga[nome_emozione] += emozioni_parola[nome_emozione]
        # Se la parola non e' nel lessico (es. nomi propri, congiunzioni,
        # parole di un'altra lingua), semplicemente non contribuisce a
        # nessuna emozione: non serve gestire questo caso esplicitamente.

    return totale_riga


# ---------------------------------------------------------------------
# FUNZIONE: ANALISI DI UNA CANZONE
# ---------------------------------------------------------------------

def analizza_canzone(nome_canzone, cartella_testi, lessico_it, lessico_en):
    """
    Analizza tutte le righe di una canzone e restituisce una lista di
    dizionari, uno per riga, pronti per essere scritti nel CSV finale.

    Parametri:
        nome_canzone (str): titolo della canzone (senza estensione .txt)
        cartella_testi (str): cartella dove si trova il file .txt
        lessico_it (dict): il dizionario NRC italiano
        lessico_en (dict): il dizionario NRC inglese

    Restituisce:
        una lista di dizionari, es.
        [{"canzone": "Ridere", "numero_riga": 1, "testo": "...",
          "lingua": "it", "rabbia": 0, "gioia": 1, ...}, ...]
    """
    percorso_file = os.path.join(cartella_testi, f"{nome_canzone}.txt")
    righe_risultato = []

    if not os.path.exists(percorso_file):
        print(f"ATTENZIONE: file non trovato -> {percorso_file}")
        return righe_risultato

    with open(percorso_file, "r", encoding="utf-8") as file:
        righe = file.readlines()

    # enumerate(righe, start=1) ci da' sia l'indice (a partire da 1,
    # non da 0) sia il contenuto di ogni riga, comodo per numero_riga.
    for numero_riga, riga in enumerate(righe, start=1):
        riga = riga.strip()
        if riga == "":
            continue

        lingua = rileva_lingua(riga)
        conteggio_emozioni = conta_emozioni_riga(riga, lingua, lessico_it, lessico_en)

        # Costruiamo il dizionario completo per questa riga, unendo i
        # dati descrittivi (canzone, numero riga, testo, lingua) con i
        # conteggi delle emozioni appena calcolati.
        riga_completa = {
            "canzone": nome_canzone,
            "numero_riga": numero_riga,
            "testo": riga,
            "lingua": lingua,
        }
        riga_completa.update(conteggio_emozioni)

        righe_risultato.append(riga_completa)

    return righe_risultato


# ---------------------------------------------------------------------
# FUNZIONE PRINCIPALE
# ---------------------------------------------------------------------

def main():
    """
    Funzione principale:
    1. carica i due lessici NRC (italiano e inglese) dallo stesso file
    2. analizza tutte le canzoni presenti nella cartella testi_canzoni
    3. scrive tutti i risultati in un unico file CSV
    """
    print("Caricamento del lessico NRC...")
    lessico_it = carica_lessico(PERCORSO_LESSICO_NRC, "Italian Word")
    lessico_en = carica_lessico(PERCORSO_LESSICO_NRC, "English Word")
    print(f"Lessico italiano: {len(lessico_it)} parole. Lessico inglese: {len(lessico_en)} parole.")

    # Invece di riscrivere a mano la lista delle 20 canzoni, leggiamo
    # direttamente tutti i file .txt presenti nella cartella: cosi', se
    # in futuro aggiungi o togli canzoni, non devi aggiornare questo
    # script, ti basta aggiungere/togliere il file .txt corrispondente.
    nomi_canzoni = [
        nome_file[:-4]  # togliamo l'estensione ".txt" dal nome del file
        for nome_file in os.listdir(CARTELLA_TESTI)
        if nome_file.endswith(".txt")
    ]

    tutte_le_righe = []
    for nome_canzone in nomi_canzoni:
        print(f"Analizzando: {nome_canzone}...")
        righe_canzone = analizza_canzone(nome_canzone, CARTELLA_TESTI, lessico_it, lessico_en)
        tutte_le_righe.extend(righe_canzone)

    # Costruiamo l'elenco delle colonne del CSV: prima quelle descrittive,
    # poi le 8 colonne delle emozioni (nell'ordine di MAPPA_EMOZIONI).
    nomi_colonne = ["canzone", "numero_riga", "testo", "lingua"] + list(MAPPA_EMOZIONI.values())

    with open(PERCORSO_CSV_OUTPUT, "w", encoding="utf-8", newline="") as file_csv:
        scrittore = csv.DictWriter(file_csv, fieldnames=nomi_colonne)
        scrittore.writeheader()
        scrittore.writerows(tutte_le_righe)

    print(f"\nFatto. Creato il file: {PERCORSO_CSV_OUTPUT}")
    print(f"Totale righe analizzate: {len(tutte_le_righe)}")


# ---------------------------------------------------------------------
# BLOCCO DI ESECUZIONE
# ---------------------------------------------------------------------
if __name__ == "__main__":
    main()