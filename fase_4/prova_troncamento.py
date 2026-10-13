"""
Controllo del troncamento del modello pysentimiento.

Il modello legge solo i primi ~128 token di ogni testo (il resto viene
scartato dalla libreria). Questo script analizza ogni canzone SOLO con il
modello usato davvero nella fase 4 (colonna lingua_usata di
emozioni_transformer.csv) e per ogni canzone:

1. verifica che il risultato sulla canzone INTERA coincida con quello sul
   solo INIZIO (primi 126 token): se coincide, il modello ha letto solo
   l'inizio;
2. calcola anche il risultato sulla FINE della canzone (ultimi 126 token),
   per vedere se l'emozione prevalente cambierebbe leggendo la parte finale.

126 = 128 (limite del modello) - 2 token speciali (inizio e fine) che il
modello aggiunge da solo: cosi' l'inizio e la fine entrano interi.

I risultati vengono stampati a schermo E salvati in
fase_4/risultati_troncamento.txt (contiene solo nomi di file, numeri di
token e probabilita': nessun verso).
"""
print("Avvio: il caricamento di pysentimiento puo' richiedere anche un minuto...")

import csv
import glob
import os
from pysentimiento import create_analyzer

# Limite effettivo del modello (token, compresi i 2 speciali): vedi il test
# precedente, in cui la canzone intera dava lo stesso risultato dei primi 128.
LIMITE_MODELLO = 128

# Token speciali di inizio e fine che il modello aggiunge da solo.
TOKEN_SPECIALI = 2

# Quanti token di testo "vero" entrano nel modello: 128 - 2 = 126.
TOKEN_TESTO = LIMITE_MODELLO - TOKEN_SPECIALI

# Due probabilita' che differiscono meno di questo valore sono considerate uguali.
TOLLERANZA = 0.01

# Cartella in cui si trova questo script (fase_4)
cartella_script = os.path.dirname(os.path.abspath(__file__))

# Cartella dei testi: sale di uno da fase_4 ed entra in testi_canzoni
cartella_testi = os.path.join(cartella_script, "..", "testi_canzoni")

# File con la lingua usata per ogni canzone nella fase 4 (sta in fase_4).
PERCORSO_LINGUE = os.path.join(cartella_script, "emozioni_transformer.csv")

# File di output: viene creato qui accanto, nella cartella fase_4.
PERCORSO_OUTPUT = os.path.join(cartella_script, "risultati_troncamento.txt")

# Tutti i file .txt dei testi, in ordine alfabetico.
FILE = sorted(glob.glob(os.path.join(cartella_testi, "*.txt")))

# Lista in cui raccogliamo tutte le righe da salvare nel file alla fine.
righe_output = []


def stampa_e_salva(riga):
    """Stampa una riga a schermo e la aggiunge alla lista da scrivere nel file."""
    print(riga)
    righe_output.append(riga)


def carica_lingue(percorso_file):
    """
    Legge emozioni_transformer.csv (colonne: canzone, lingua_usata, ...) e
    restituisce un dizionario {titolo: codice_lingua}, es. {"Pula": "it"}.
    """
    lingue = {}
    with open(percorso_file, "r", encoding="utf-8", newline="") as file:
        # DictReader usa la prima riga come nomi delle colonne.
        for riga in csv.DictReader(file):
            lingue[riga["canzone"]] = riga["lingua_usata"]
    return lingue


def emozione_prevalente(probabilita):
    """
    Restituisce il nome dell'emozione con la probabilita' piu' alta, dato un
    dizionario del tipo {"anger": 0.62, "joy": 0.03, ...}.
    max(..., key=probabilita.get) sceglie la chiave con il valore maggiore.
    """
    return max(probabilita, key=probabilita.get)


# Modelli gia' caricati, per non ricaricare lo stesso modello a ogni canzone.
analizzatori = {}


def ottieni_analizzatore(lingua):
    """
    Restituisce il modello della lingua indicata, creandolo solo la prima
    volta e stampandone le emozioni e i limiti dichiarati.
    """
    if lingua not in analizzatori:
        stampa_e_salva("\n" + "=" * 60)
        stampa_e_salva(f"MODELLO: {lingua}")
        stampa_e_salva("=" * 60)

        analyzer = create_analyzer(task="emotion", lang=lingua)
        analizzatori[lingua] = analyzer

        # Due modi per conoscere il limite: quello del tokenizzatore e quello
        # scritto nella configurazione del modello.
        limite_tokenizzatore = analyzer.tokenizer.model_max_length
        config = getattr(analyzer.model, "config", None)
        limite_config = getattr(config, "max_position_embeddings", None)

        stampa_e_salva(f"Emozioni del modello: {list(analyzer.id2label.values())}")
        stampa_e_salva(f"Limite dichiarato dal tokenizzatore: {limite_tokenizzatore}")
        stampa_e_salva(f"Limite scritto nella configurazione: {limite_config}")
        stampa_e_salva("")

    return analizzatori[lingua]


lingue_per_canzone = carica_lingue(PERCORSO_LINGUE)
stampa_e_salva(f"File trovati: {len(FILE)}")

# Contatori per il riepilogo finale.
canzoni_analizzate = 0
canzoni_intero_uguale_inizio = 0
canzoni_che_cambiano = []   # titoli in cui l'emozione prevalente cambia con la fine

for percorso in FILE:

    # Titolo = nome del file senza ".txt": e' lo stesso nome usato nel CSV.
    nome = os.path.basename(percorso)[:-4]

    lingua = lingue_per_canzone.get(nome)
    if lingua is None:
        stampa_e_salva(f"\n{nome}: non trovata in emozioni_transformer.csv, la salto")
        continue

    analyzer = ottieni_analizzatore(lingua)
    tokenizer = analyzer.tokenizer

    # Leggo il testo e unisco le righe con uno spazio, come fa lo script della
    # fase 4 (le righe vuote vengono saltate).
    with open(percorso, "r", encoding="utf-8") as file:
        testo = " ".join(riga.strip() for riga in file if riga.strip() != "")

    # Trasformo il testo in token (lista di numeri, uno per token), senza i 2
    # token speciali: il conteggio riguarda solo il testo vero.
    token = tokenizer(testo, add_special_tokens=False)["input_ids"]
    canzoni_analizzate += 1

    # Se la canzone sta nel limite il modello la legge tutta: niente da confrontare.
    if len(token) <= TOKEN_TESTO:
        stampa_e_salva(f"{nome} [{lingua}] - {len(token)} token: dentro il limite, letta per intero")
        continue

    # Probabilita' sulla canzone intera. .probas e' un dizionario del tipo
    # {"anger": 0.62, "joy": 0.03, ...}
    p_intero = analyzer.predict(testo).probas

    # INIZIO = primi 126 token, FINE = ultimi 126 token. decode() fa
    # l'operazione inversa: da lista di numeri torna a testo. (La fine puo'
    # cominciare a meta' di una parola: e' un effetto trascurabile.)
    p_inizio = analyzer.predict(tokenizer.decode(token[:TOKEN_TESTO])).probas
    p_fine = analyzer.predict(tokenizer.decode(token[-TOKEN_TESTO:])).probas

    # Verifica 1: la canzone intera da' lo stesso risultato del solo inizio?
    # max(...) prende la differenza piu' grande tra le probabilita' delle emozioni.
    differenza = max(abs(p_intero[e] - p_inizio[e]) for e in p_intero)
    intero_uguale_inizio = differenza < TOLLERANZA
    if intero_uguale_inizio:
        canzoni_intero_uguale_inizio += 1

    # Quanta parte della canzone viene letta: 126 token su len(token).
    percentuale_letta = TOKEN_TESTO / len(token) * 100

    # Verifica 2: l'emozione prevalente cambia leggendo la fine invece dell'inizio?
    prev_intero = emozione_prevalente(p_intero)
    prev_inizio = emozione_prevalente(p_inizio)
    prev_fine = emozione_prevalente(p_fine)
    cambia = prev_inizio != prev_fine
    if cambia:
        canzoni_che_cambiano.append(nome)

    stampa_e_salva(
        f"{nome} [{lingua}] - {len(token)} token, letto circa {percentuale_letta:.0f}% | "
        f"intero = inizio: {'SI' if intero_uguale_inizio else 'NO'} (diff max {differenza:.3f}) | "
        f"prevalente: intero {prev_intero}, inizio {prev_inizio}, fine {prev_fine}"
        f"{' -> CAMBIA' if cambia else ''}"
    )

    # Quando l'emozione prevalente cambia, stampo la tabella completa.
    if cambia:
        stampa_e_salva("  emozione      intero   inizio     fine")
        for emozione in p_intero:
            stampa_e_salva(f"  {emozione:<12} {p_intero[emozione]:.3f}    {p_inizio[emozione]:.3f}    {p_fine[emozione]:.3f}")

# ---------------------------------------------------------------------
# RIEPILOGO FINALE
# ---------------------------------------------------------------------
stampa_e_salva("\n" + "=" * 60)
stampa_e_salva("RIEPILOGO")
stampa_e_salva("=" * 60)
stampa_e_salva(f"Canzoni analizzate: {canzoni_analizzate}")
stampa_e_salva(f"Canzoni in cui il risultato sull'intera canzone coincide con quello sul solo inizio: {canzoni_intero_uguale_inizio}")
stampa_e_salva(f"Canzoni in cui l'emozione prevalente cambia leggendo la fine invece dell'inizio: {len(canzoni_che_cambiano)}")
for titolo in canzoni_che_cambiano:
    stampa_e_salva(f"  - {titolo}")
stampa_e_salva(
    "\nCOME LEGGERE: 'intero = inizio: SI' significa che il modello ha letto solo i "
    f"primi {TOKEN_TESTO} token. 'CAMBIA' significa che, leggendo la parte finale "
    "della canzone, l'emozione prevalente sarebbe stata un'altra."
)

# Alla fine scrivo tutte le righe raccolte nel file di testo.
# "w" = scrittura: se il file esiste gia' viene sostituito.
with open(PERCORSO_OUTPUT, "w", encoding="utf-8") as file_output:
    file_output.write("\n".join(righe_output) + "\n")

print(f"\nRisultati salvati in: {PERCORSO_OUTPUT}")