"""
FASE 1 - Download dei testi delle canzoni tramite l'API di Genius
===================================================================

Obiettivo di questo script di prova:
- collegarsi all'API di Genius usando la libreria lyricsgenius
- scaricare il testo di 20 canzoni
- salvarli in un file di testo, cosi' da poterlo poi usare nella Fase 2
  per l'analisi delle emozioni
"""

# ---------------------------------------------------------------------
# IMPORT DELLE LIBRERIE
# ---------------------------------------------------------------------
import lyricsgenius   # libreria che parla con l'API di Genius e scarica i testi
import os              # libreria standard di Python per gestire file e cartelle
from dotenv import load_dotenv  # per leggere le chiavi dal file .env invece che dal codice


# ---------------------------------------------------------------------
# CONFIGURAZIONE
# ---------------------------------------------------------------------

# Cerchiamo il file .env nella STESSA cartella di questo script (non ci
# affidiamo alla ricerca automatica di load_dotenv(), che a seconda di
# dove lanci lo script potrebbe cercare nel posto sbagliato).
CARTELLA_PROGETTO = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(CARTELLA_PROGETTO, ".env"))

# Il tuo Client Access Token ottenuto da genius.com/api-clients.
# os.getenv("GENIUS_ACCESS_TOKEN") legge il valore della variabile
# GENIUS_ACCESS_TOKEN dal file .env (che tu hai creato a parte, con
# dentro GENIUS_ACCESS_TOKEN=il_tuo_token_vero). Se il file .env non
# esiste o non contiene questa riga, os.getenv restituisce None invece
# di dare errore: per questo aggiungiamo un controllo subito dopo.
GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")

if GENIUS_ACCESS_TOKEN is None:
    raise ValueError(
        "GENIUS_ACCESS_TOKEN non trovato. Crea un file .env nella cartella "
        "del progetto con dentro: GENIUS_ACCESS_TOKEN=il_tuo_token"
    )

# Nome esatto dell'artista, cosi' come compare su Genius.
NOME_ARTISTA = "Pinguini Tattici Nucleari"

# Lista dei titoli delle canzoni da scaricare.
# Per ora c'e' solo la canzone piu' ascoltata ("Ridere"), che useremo come
# test. Quando vorrai passare a 20 canzoni, ti bastera' aggiungere gli
# altri titoli qui dentro, uno per riga, separati da virgola.
LISTA_CANZONI = [
    # --- Top 10 più ascoltate ---
    "Ridere",
    "Pastello Bianco",
    "Giovani Wannabe",
    "Scrivile Scemo",
    "Rubami la Notte",
    "Ricordi",
    "Ringo Starr",
    "Scooby Doo",
    "Islanda",
    "La storia infinita",

    # --- Bottom 10 meno ascoltate ---
    "Rodger",
    "Il sonno ed il furto (storia di un coinquilino)",
    "Me Want Marò Back",
    "Pula",
    "In vento",
    "Gigi cinque ottavi",
    "Il concorso musicale",
    "Django",
    "Sudowoodo",
    "79",
]

# Cartella dove verranno salvati i file di testo con i testi delle canzoni.
CARTELLA_OUTPUT = "testi_canzoni"


# ---------------------------------------------------------------------
# FUNZIONI
# ---------------------------------------------------------------------

def crea_client_genius(token):
    """
    Crea e configura l'oggetto 'genius' che useremo per fare le richieste
    all'API.

    Parametri:
        token (str): il Client Access Token di Genius

    Restituisce:
        un oggetto lyricsgenius.Genius gia' pronto all'uso
    """
    # Creiamo l'oggetto che gestisce la connessione con l'API di Genius,
    # passandogli il token di accesso.
    genius = lyricsgenius.Genius(token)

    # Se True, rimuove dal testo scaricato le intestazioni tipo
    # [Ritornello], [Strofa 1], [Bridge], ecc. Le togliamo perche' non
    # fanno parte del testo vero e proprio e disturberebbero l'analisi
    # delle emozioni nella Fase 2.
    genius.remove_section_headers = True

    # Se True, la libreria stampa a schermo messaggi tipo "Searching for
    # song...". Lo mettiamo a False per avere un output piu' pulito.
    genius.verbose = False

    # Se True, salta automaticamente eventuali remix/traduzioni trovati
    # per errore al posto della canzone originale.
    genius.skip_non_songs = True

    return genius


def scarica_testo_canzone(genius, titolo_canzone, nome_artista):
    """
    Scarica il testo di UNA canzone tramite l'API di Genius.

    Parametri:
        genius (lyricsgenius.Genius): il client creato da crea_client_genius
        titolo_canzone (str): titolo della canzone da cercare
        nome_artista (str): nome dell'artista da cercare

    Restituisce:
        un oggetto Song di lyricsgenius (contiene titolo, testo, url, ecc.)
        oppure None se la canzone non viene trovata
    """
    # genius.search_song() cerca la canzone su Genius e, se la trova,
    # scarica anche il testo completo (facendo scraping della pagina,
    # perche' l'API "pura" non fornisce i testi per motivi di licenza).
    canzone = genius.search_song(titolo_canzone, nome_artista)

    # Se la libreria non trova nulla, search_song restituisce None:
    # gestiamo questo caso per evitare che il programma si blocchi.
    if canzone is None:
        print(f"ATTENZIONE: canzone non trovata -> {titolo_canzone}")
        return None

    return canzone


def salva_testo_su_file(canzone, cartella_output):
    """
    Salva il testo di una canzone in un file .txt dentro la cartella
    indicata. Il nome del file e' il titolo della canzone "ripulito"
    dai caratteri che non si possono usare nei nomi dei file.

    Parametri:
        canzone (lyricsgenius.Song): la canzone scaricata
        cartella_output (str): cartella dove salvare il file
    """
    # os.makedirs crea la cartella se non esiste gia'.
    # exist_ok=True evita errori se la cartella e' gia' presente.
    os.makedirs(cartella_output, exist_ok=True)

    # Ripuliamo il titolo da eventuali caratteri non ammessi nei nomi
    # di file (es. punti interrogativi, slash, due punti...).
    titolo_pulito = "".join(
        carattere for carattere in canzone.title
        if carattere.isalnum() or carattere in (" ", "_", "-")
    ).strip()

    # Costruiamo il percorso completo del file: cartella + nome file + .txt
    percorso_file = os.path.join(cartella_output, f"{titolo_pulito}.txt")

    # MODIFICA RISPETTO ALLA VERSIONE ORIGINALE: aggiunta la scrittura del testo della canzone nel file
    # Puliamo il testo: dividiamo in righe, togliamo gli spazi bianchi
    # a inizio/fine di ogni riga con .strip(), e teniamo solo le righe
    # che contengono davvero del testo (escludendo quelle vuote).
    righe_pulite = [riga.strip() for riga in canzone.lyrics.split("\n") if riga.strip() != ""]

    # Ricomponiamo il testo unendo le righe pulite con un "a capo" tra ognuna.
    testo_pulito = "\n".join(righe_pulite)

    # Apriamo il file in scrittura ("w") con codifica utf-8 (necessaria
    # per gestire correttamente gli accenti dell'italiano) e ci scriviamo
    # dentro il testo della canzone.

    with open(percorso_file, "w", encoding="utf-8") as file:
        file.write(testo_pulito)   # scriviamo il testo pulito invece di canzone.lyrics

    #FINE DELLA MODIFICA RISPETTO ALLA VERSIONE ORIGINALE

    print(f"Salvato: {percorso_file}")


# ---------------------------------------------------------------------
# FUNZIONE PRINCIPALE
# ---------------------------------------------------------------------

def main():
    """
    Funzione principale: mette insieme tutti i passaggi.
    1. crea il client Genius
    2. per ogni canzone nella LISTA_CANZONI, la cerca e scarica il testo
    3. salva ogni testo in un file separato
    """
    # Passo 1: creiamo il client collegato all'API di Genius.
    genius = crea_client_genius(GENIUS_ACCESS_TOKEN)

    # Passo 2 e 3: cicliamo su ogni titolo presente in LISTA_CANZONI.
    # Per ora la lista contiene solo "Ridere", ma il ciclo funzionera'
    # automaticamente anche quando ne aggiungerai altri 19.
    for titolo in LISTA_CANZONI:
        print(f"Scaricando: {titolo}...")

        canzone = scarica_testo_canzone(genius, titolo, NOME_ARTISTA)

        # Se la canzone e' stata trovata (non e' None), la salviamo.
        # Altrimenti passiamo alla prossima del ciclo.
        if canzone is not None:
            salva_testo_su_file(canzone, CARTELLA_OUTPUT)

    print("Download completato.")


# ---------------------------------------------------------------------
# BLOCCO DI ESECUZIONE
# ---------------------------------------------------------------------
# Questo blocco fa si' che main() venga eseguita SOLO quando questo file
# viene lanciato direttamente (es. "python fase1_download_testi.py"),
# e NON quando questo file viene importato da un altro script (utile
# quando nelle fasi successive richiamerai queste funzioni altrove).
if __name__ == "__main__":
    main()