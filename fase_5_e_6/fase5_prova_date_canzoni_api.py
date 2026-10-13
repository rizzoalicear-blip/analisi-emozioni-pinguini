"""
anni_genius.py - trova la DATA DI USCITA di ogni canzone usando SOLO l'API di Genius.

DA DOVE PRENDE LE CANZONI
  Dal tuo file emozioni_per_canzone.csv (nessun altro elenco da mantenere).
  Di ogni riga usa la PRIMA colonna (titolo) e l'ULTIMA (emozione prevalente).
  Esempio:  Pastello Bianco,1,13,1,1,6,7,3,5,attesa   ->   Pastello Bianco | attesa
  I numeri in mezzo vengono ignorati.

COSA FA, PASSO PASSO
  1. Prepara la tabella finale canzoni_finale.csv (colonne: titolo, emozione,
     data_uscita, ascolti). Se non esiste la crea da emozioni_per_canzone.csv;
     se esiste la riusa e la tiene aggiornata con il file delle emozioni.
  2. Per ogni canzone senza data chiede a Genius: "cerca <titolo> + <artista>".
  3. Tra i risultati tiene solo quelli dell'artista giusto e con titolo molto simile al nostro.
  4. Scrive la data di uscita nella colonna "data_uscita".

COSA NON FA
  - Non tocca la colonna "ascolti" (la riempirà lo script degli ascolti).
  - Non sovrascrive le date già presenti: le tue correzioni a mano restano.

FILE NECESSARI: 
  - emozioni_per_canzone.csv (nella cartella fase_2).
  - .env nella cartella principale.

LIBRERIE: pip install requests pandas python-dotenv

FORMATO DELLA DATA SALVATA
  "2018-05-11" se Genius conosce anno, mese e giorno
  "2018-05"    se conosce solo anno e mese
  "2018"       se conosce solo l'anno
  Se la data è incompleta lo script NON inventa il mese o il giorno.
"""

import csv
import os
import re
import time
import unicodedata
from difflib import SequenceMatcher

import pandas as pd
import requests
from dotenv import load_dotenv

# =============================================================================
# IMPOSTAZIONI - qui cambi quello che ti serve
# =============================================================================
# Percorsi: partono dalla posizione dello SCRIPT, non da dove lanci il comando
CARTELLA_SCRIPT = os.path.dirname(os.path.abspath(__file__))        # la cartella di questo script (es. fase_5/)
CARTELLA_PRINCIPALE = os.path.dirname(CARTELLA_SCRIPT)              # la cartella principale del progetto
FILE_EMOZIONI = os.path.join(CARTELLA_PRINCIPALE, "fase_2", "emozioni_per_canzone.csv")   # arriva dalla Fase 2
FILE_FINALE = os.path.join(CARTELLA_SCRIPT, "canzoni_finale.csv")   # viene creato accanto a questo script
ARTISTA = "Pinguini Tattici Nucleari"

PAUSA = 1.0           # secondi di attesa tra una richiesta e la successiva
SOGLIA_TITOLO = 0.80  # quanto deve somigliare il titolo trovato al nostro (0 = niente, 1 = identico)
MAX_CANZONI = 3       # 3 per fare una PROVA veloce su sole 3 canzoni; None = tutte
RIFAI_TUTTO = False   # True = ricerca di nuovo anche le canzoni che hanno già una data

# Le colonne della tabella finale, in questo ordine
COLONNE = ["titolo", "emozione", "data_uscita", "ascolti"]

# Indirizzi dell'API di Genius
URL_RICERCA = "https://api.genius.com/search"
URL_CANZONE = "https://api.genius.com/songs/{}"


# =============================================================================
# FUNZIONI PER CONFRONTARE I TITOLI
# =============================================================================
def normalizza(testo):
    """Trasforma un titolo in una forma 'semplice' per poterlo confrontare:
    minuscolo, senza accenti, senza punteggiatura, senza testo tra parentesi.
    Esempio: "Me Want Marò Back" -> "me want maro back"
    Serve perché fonti diverse scrivono lo stesso titolo in modo leggermente diverso."""
    testo = re.sub(r"\(.*?\)", "", str(testo))                 # toglie le parti tra parentesi
    testo = unicodedata.normalize("NFKD", testo)               # separa le lettere dagli accenti
    testo = "".join(c for c in testo if not unicodedata.combining(c))  # butta gli accenti
    testo = re.sub(r"[^a-z0-9 ]", "", testo.lower())           # tiene solo lettere, numeri, spazi
    return re.sub(r"\s+", " ", testo).strip()                  # spazi doppi -> spazio singolo


def somiglianza(a, b):
    """Restituisce un numero tra 0 e 1: più è vicino a 1, più i due titoli si somigliano."""
    return SequenceMatcher(None, normalizza(a), normalizza(b)).ratio()


# =============================================================================
# LETTURA DEL FILE DELLE EMOZIONI E GESTIONE DELLA TABELLA FINALE
# =============================================================================
def e_un_numero(testo):
    """True se il testo è un numero (es. '13'), False altrimenti (es. 'attesa')."""
    try:
        float(testo)
        return True
    except ValueError:
        return False


def leggi_analisi():
    """Legge emozioni_per_canzone.csv e restituisce un dizionario:
         { titolo normalizzato : (titolo originale, emozione) }
    nello stesso ordine del file.
    Usiamo il modulo 'csv' (e non pandas) perché non conosciamo il numero esatto di
    colonne: così prendiamo comunque la prima (titolo) e l'ultima (emozione)."""
    analisi = {}
    with open(FILE_EMOZIONI, newline="", encoding="utf-8-sig") as file:
        for numero_riga, riga in enumerate(csv.reader(file), start=1):
            if len(riga) < 2:
                continue                                   # riga vuota o incompleta

            titolo = riga[0].strip()
            emozione = riga[-1].strip()                    # [-1] = l'ultima colonna

            # Se la seconda colonna non è un numero, la riga non è una canzone
            # analizzata (di solito è l'intestazione): la saltiamo
            if not e_un_numero(riga[1].strip()):
                print(f"Riga {numero_riga} di {FILE_EMOZIONI} saltata (sembra un'intestazione)")
                continue

            analisi[normalizza(titolo)] = (titolo, emozione)
    return analisi


def carica_tabella():
    """Prepara la tabella finale:
       - se canzoni_finale.csv non esiste, la crea dalle canzoni di emozioni_per_canzone.csv;
       - se esiste, la riapre e aggiunge le eventuali canzoni nuove del file delle emozioni;
       - in ogni caso riallinea la colonna "emozione" con il file delle emozioni.
    Le date e gli ascolti già presenti NON vengono toccati."""
    analisi = leggi_analisi()

    if os.path.exists(FILE_FINALE):
        # dtype=str: leggiamo emozione e data come testo, per non farle confondere con numeri
        df = pd.read_csv(FILE_FINALE, encoding="utf-8-sig",
                         dtype={"emozione": str, "data_uscita": str})
    else:
        df = pd.DataFrame({"titolo": []})

    # Se manca qualche colonna la creiamo vuota
    for colonna in COLONNE:
        if colonna not in df.columns:
            df[colonna] = None

    # Aggiungiamo le canzoni che sono nel file delle emozioni ma non ancora nella tabella
    gia_presenti = {normalizza(t) for t in df["titolo"]}
    nuove = [titolo for chiave, (titolo, _) in analisi.items() if chiave not in gia_presenti]
    if nuove:
        df = pd.concat([df, pd.DataFrame({"titolo": nuove})], ignore_index=True)
        for colonna in COLONNE:
            if colonna not in df.columns:
                df[colonna] = None

    # Riallineiamo l'emozione: l'analisi è la fonte "giusta"
    for indice, titolo in df["titolo"].items():
        chiave = normalizza(titolo)
        if chiave in analisi:
            df.at[indice, "emozione"] = analisi[chiave][1]

    return df[COLONNE]


def salva_tabella(df):
    # utf-8-sig = UTF-8 con "firma" iniziale, così Excel mostra bene le lettere accentate
    df.to_csv(FILE_FINALE, index=False, encoding="utf-8-sig")


# =============================================================================
# DIALOGO CON GENIUS
# =============================================================================
def chiedi_a_genius(url, headers, parametri=None):
    """Fa UNA richiesta a Genius e restituisce la parte 'response' della risposta JSON."""
    risposta = requests.get(url, headers=headers, params=parametri, timeout=15)
    if risposta.status_code == 401:
        # 401 = non autorizzato: il token è sbagliato o scaduto. Inutile continuare.
        raise SystemExit("Genius ha rifiutato il token (errore 401). Controlla GENIUS_ACCESS_TOKEN nel .env")
    risposta.raise_for_status()   # per qualsiasi altro errore HTTP lancia un'eccezione
    return risposta.json()["response"]


def data_da_componenti(componenti):
    """Genius dà la data come dizionario, es. {"year": 2018, "month": 5, "day": 11}.
    Qui la trasformiamo nel testo "2018-05-11", fermandoci dove i dati finiscono."""
    if not componenti or not componenti.get("year"):
        return None
    testo = str(componenti["year"])
    if componenti.get("month"):
        testo += f"-{int(componenti['month']):02d}"           # :02d = sempre due cifre (5 -> 05)
        if componenti.get("day"):
            testo += f"-{int(componenti['day']):02d}"
    return testo


def trova_data(titolo, headers):
    """Cerca la canzone su Genius e restituisce (data, titolo_trovato_su_genius),
    oppure (None, None) se non trova niente di affidabile."""

    # PASSO 1 - Ricerca: Genius risponde con una lista di risultati ("hits")
    risposta = chiedi_a_genius(URL_RICERCA, headers, {"q": f"{titolo} {ARTISTA}"})

    # PASSO 2 - Filtro: scartiamo i risultati di altri artisti (traduzioni, cover...)
    # e quelli con un titolo troppo diverso dal nostro
    candidati = []
    for hit in risposta["hits"]:
        canzone = hit["result"]
        artista_giusto = normalizza(ARTISTA) in normalizza(canzone["primary_artist"]["name"])
        punteggio = somiglianza(titolo, canzone["title"])
        if artista_giusto and punteggio >= SOGLIA_TITOLO:
            candidati.append((punteggio, canzone))

    # Mettiamo per primo il candidato con il titolo più simile al nostro
    candidati.sort(key=lambda coppia: coppia[0], reverse=True)

    # PASSO 3 - Per ogni candidato cerchiamo la data
    for _, canzone in candidati:
        # 3a) a volte la data è già nel risultato della ricerca
        data = data_da_componenti(canzone.get("release_date_components"))

        # 3b) altrimenti chiediamo la "scheda" completa della canzone (seconda richiesta)
        if data is None:
            time.sleep(PAUSA)
            scheda = chiedi_a_genius(URL_CANZONE.format(canzone["id"]), headers)["song"]
            data = data_da_componenti(scheda.get("release_date_components"))
            if data is None:
                # ultimo tentativo: campo "release_date", già in formato "2018-05-11"
                data = scheda.get("release_date") or None

        if data:
            return data, canzone["title"]

    return None, None


# =============================================================================
# PROGRAMMA PRINCIPALE
# =============================================================================
def main():
    # Legge il file .env e rende disponibili le variabili che contiene
    load_dotenv()
    token = os.getenv("GENIUS_ACCESS_TOKEN")   # il nome deve essere uguale a quello scritto nel .env
    if not token:
        raise SystemExit("Token non trovato: nel file .env deve esserci GENIUS_ACCESS_TOKEN=...")

    # Genius vuole il token nell'intestazione (header) di ogni richiesta
    headers = {"Authorization": f"Bearer {token}"}

    df = carica_tabella()
    salva_tabella(df)   # salviamo subito: la tabella con i titoli e le emozioni esiste già
    print(f"Canzoni in tabella: {len(df)}\n")
    elaborate = 0       # conta le canzoni cercate in questo lancio (serve per MAX_CANZONI)

    for indice, riga in df.iterrows():
        titolo = riga["titolo"]

        # Se la data c'è già e non vogliamo rifare tutto, passiamo alla canzone dopo
        if pd.notna(riga["data_uscita"]) and not RIFAI_TUTTO:
            print(f"{titolo}: già presente ({riga['data_uscita']}), salto")
            continue

        # Modalità prova: ci fermiamo dopo MAX_CANZONI canzoni
        if MAX_CANZONI is not None and elaborate >= MAX_CANZONI:
            print(f"\nProva terminata dopo {MAX_CANZONI} canzoni (MAX_CANZONI).")
            break
        elaborate += 1

        try:
            data, titolo_genius = trova_data(titolo, headers)
        except requests.RequestException as errore:
            # Problemi di rete o errore del server: non fermiamo tutto, andiamo avanti
            print(f"{titolo}: ERRORE DI RETE ({errore})")
            data, titolo_genius = None, None

        if data:
            df.at[indice, "data_uscita"] = data
            # Stampiamo anche il titolo trovato su Genius, così puoi controllare
            # che sia davvero la canzone giusta
            print(f"{titolo}: {data}   (titolo su Genius: '{titolo_genius}')")
        else:
            print(f"{titolo}: NON TROVATA su Genius (resta vuota per ora)")

        salva_tabella(df)    # salviamo dopo ogni canzone: se qualcosa si blocca non perdi nulla
        time.sleep(PAUSA)    # pausa prima della prossima canzone

    salva_tabella(df)
    senza_data = df["data_uscita"].isna().sum()
    print(f"\nFatto. Salvato in {FILE_FINALE}. Canzoni ancora senza data: {senza_data}")


if __name__ == "__main__":
    main()