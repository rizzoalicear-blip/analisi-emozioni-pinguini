"""
ascolti_kworb.py - scarica da kworb.net gli ASCOLTI SPOTIFY TOTALI di ogni canzone
                   e li scrive nella colonna "ascolti" di canzoni_finale.csv.

DA DOVE PRENDE LE CANZONI
  Dal tuo file emozioni_per_canzone.csv (come anni_genius.py).
  Di ogni riga usa la PRIMA colonna (titolo) e l'ULTIMA (emozione prevalente).
  Esempio:  Pastello Bianco,1,13,1,1,6,7,3,5,attesa   ->   Pastello Bianco | attesa

COSA FA, PASSO PASSO
  1. Prepara la tabella finale canzoni_finale.csv (colonne: titolo, emozione,
     data_uscita, ascolti). Se non esiste la crea, se esiste la riusa:
     per questo puoi lanciare questo script PRIMA o DOPO anni_genius.py.
  2. Scarica UNA SOLA pagina da kworb, che contiene tutte le canzoni dell'artista
     con i loro ascolti totali.
  3. Per ogni canzone della tabella cerca la riga di kworb con il titolo più simile.
  4. Scrive il numero di ascolti nella colonna "ascolti".

COSA NON FA
  - Non tocca la colonna "data_uscita".
  - Se una canzone non viene trovata su kworb, lascia com'è il valore che c'era.

SULLE PAUSE
  A differenza di Genius (una richiesta per canzone), qui scarichiamo UNA pagina sola,
  quindi non serve una pausa tra una canzone e l'altra. Le pause le usiamo dove servono:
  se il download fallisce, aspetta qualche secondo e riprova (vedi TENTATIVI e PAUSA).

ATTENZIONE: gli ascolti cambiano ogni giorno. Il numero salvato è una "fotografia"
del momento in cui lanci lo script. Rilancialo quando vuoi aggiornarli.

FILE NECESSARI (nella stessa cartella dello script)
  - emozioni_per_canzone.csv

LIBRERIE: pip install requests pandas lxml
"""

import csv
import os
import re
import time
import unicodedata
from datetime import date
from difflib import SequenceMatcher
from io import StringIO

import pandas as pd
import requests

# =============================================================================
# IMPOSTAZIONI - qui cambi quello che ti serve
# =============================================================================
# Percorsi: partono dalla posizione dello SCRIPT, non da dove lanci il comando
CARTELLA_SCRIPT = os.path.dirname(os.path.abspath(__file__))        # la cartella di questo script (es. fase_5/)
CARTELLA_PRINCIPALE = os.path.dirname(CARTELLA_SCRIPT)              # la cartella principale del progetto
FILE_EMOZIONI = os.path.join(CARTELLA_PRINCIPALE, "fase_2", "emozioni_per_canzone.csv")   # arriva dalla Fase 2
FILE_FINALE = os.path.join(CARTELLA_SCRIPT, "canzoni_finale.csv")   # viene creato accanto a questo script

# La pagina di kworb con tutte le canzoni dell'artista
URL_KWORB = "https://kworb.net/spotify/artist/6RdcIWVKYYzNzjQRd3oyHS_songs.html"

TENTATIVI = 3         # quante volte provare a scaricare la pagina se qualcosa va storto
PAUSA = 5.0           # secondi di attesa tra un tentativo e il successivo
SOGLIA_TITOLO = 0.85  # quanto deve somigliare il titolo di kworb al nostro (0 = niente, 1 = identico)

# Le colonne della tabella finale, in questo ordine
COLONNE = ["titolo", "emozione", "data_uscita", "ascolti"]


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


def normalizza_completo(testo):
    """Come normalizza(), ma NON toglie il testo tra parentesi: ne toglie solo le
    parentesi e la punteggiatura.
    Esempio: "Il sonno ed il furto (storia di un coinquilino)"
             -> "il sonno ed il furto storia di un coinquilino" """
    testo = unicodedata.normalize("NFKD", str(testo))
    testo = "".join(c for c in testo if not unicodedata.combining(c))
    testo = re.sub(r"[^a-z0-9 ]", " ", testo.lower())   # parentesi e simboli diventano spazi
    return re.sub(r"\s+", " ", testo).strip()


def somiglianza(a, b):
    """Restituisce un numero tra 0 e 1: più è vicino a 1, più i due titoli si somigliano.
    Proviamo DUE confronti e teniamo il migliore:
      1) senza il testo tra parentesi
      2) con il testo tra parentesi (utile quando una fonte scrive il sottotitolo
         senza parentesi e l'altra con)"""
    senza_parentesi = SequenceMatcher(None, normalizza(a), normalizza(b)).ratio()
    con_parentesi = SequenceMatcher(None, normalizza_completo(a), normalizza_completo(b)).ratio()
    return max(senza_parentesi, con_parentesi)


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
        # dtype: leggiamo emozione e data come testo, e gli ascolti come numero intero
        # ("Int64" accetta anche le celle vuote, senza trasformare 123 in 123.0)
        df = pd.read_csv(FILE_FINALE, encoding="utf-8-sig",
                         dtype={"emozione": str, "data_uscita": str, "ascolti": "Int64"})
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
    # Gli ascolti devono essere numeri interi (Int64 permette anche le celle vuote)
    df["ascolti"] = pd.to_numeric(df["ascolti"], errors="coerce").astype("Int64")
    # utf-8-sig = UTF-8 con "firma" iniziale, così Excel mostra bene le lettere accentate
    df.to_csv(FILE_FINALE, index=False, encoding="utf-8-sig")


# =============================================================================
# DOWNLOAD E LETTURA DELLA PAGINA DI KWORB
# =============================================================================
def scarica_pagina():
    """Scarica la pagina di kworb e restituisce il suo testo HTML.
    Se qualcosa va storto (rete, sito che non risponde...) aspetta PAUSA secondi e
    riprova, fino a TENTATIVI volte."""
    # Alcuni siti rifiutano le richieste che si presentano come "programma Python";
    # con questo User-Agent ci presentiamo come un normale browser.
    headers = {"User-Agent": "Mozilla/5.0"}

    for tentativo in range(1, TENTATIVI + 1):
        try:
            risposta = requests.get(URL_KWORB, headers=headers, timeout=20)
            risposta.raise_for_status()      # lancia un errore se il sito risponde 403, 404, 500...
            return risposta.text
        except requests.RequestException as errore:
            print(f"Tentativo {tentativo}/{TENTATIVI} fallito: {errore}")
            if tentativo < TENTATIVI:
                print(f"   riprovo tra {PAUSA:.0f} secondi...")
                time.sleep(PAUSA)            # <-- la pausa: non martelliamo il sito

    raise SystemExit("Impossibile scaricare la pagina di kworb. Controlla la connessione "
                     "o prova ad aprire l'indirizzo nel browser.")


def leggi_tabella_kworb(html):
    """Trasforma la pagina HTML in una tabella pandas con due colonne:
         titolo_kworb : il titolo della canzone come scritto su kworb
         ascolti      : gli ascolti totali, come numero intero"""
    # pandas legge in automatico tutte le tabelle presenti nella pagina
    tabelle = pd.read_html(StringIO(html))

    # Cerchiamo quella delle canzoni: ha una colonna con "song" nel nome
    # (la pagina contiene anche tabelle riassuntive che non ci servono)
    candidate = [t for t in tabelle if any("song" in str(c).lower() for c in t.columns)]
    if not candidate:
        print("Non trovo la tabella delle canzoni. Le tabelle della pagina hanno queste colonne:")
        for numero, t in enumerate(tabelle, start=1):
            print(f"   tabella {numero}: {list(t.columns)}")
        raise SystemExit("Copiami queste righe in chat così sistemiamo lo script.")
    tabella = max(candidate, key=len)         # se sono più d'una prendiamo la più lunga

    colonna_titolo = next(c for c in tabella.columns if "song" in str(c).lower())

    # La colonna degli ascolti totali si chiama di solito "Streams" o "Total".
    # Se non la troviamo per nome, prendiamo la colonna subito dopo il titolo.
    posizione_titolo = list(tabella.columns).index(colonna_titolo)
    colonna_ascolti = next(
        (c for c in tabella.columns if str(c).strip().lower() in ("streams", "total")),
        tabella.columns[posizione_titolo + 1],
    )
    print(f"Colonne usate: titolo = {colonna_titolo!r}, ascolti = {colonna_ascolti!r}")

    risultato = pd.DataFrame({
        "titolo_kworb": tabella[colonna_titolo].astype(str),
        # i numeri su kworb hanno le virgole ("525,252,812"): le togliamo e convertiamo
        "ascolti": pd.to_numeric(
            tabella[colonna_ascolti].astype(str).str.replace(",", ""), errors="coerce"
        ),
    })
    return risultato.dropna(subset=["ascolti"])   # scartiamo righe senza numero (es. totali)


def migliore_corrispondenza(titolo, kworb):
    """Cerca nella tabella di kworb la riga che somiglia di più al nostro titolo.
    Restituisce (ascolti, titolo_su_kworb, punteggio) oppure (None, None, 0)."""
    titolo_cercato = titolo

    # Calcoliamo la somiglianza con TUTTE le righe di kworb
    punteggi = kworb["titolo_kworb"].apply(lambda t: somiglianza(titolo_cercato, t))
    migliore = punteggi.max()
    if migliore < SOGLIA_TITOLO:
        return None, None, 0

    # Può capitare che la stessa canzone compaia più volte (versione live, remix...) con
    # lo stesso titolo "normalizzato". In quel caso teniamo quella con più ascolti,
    # che di solito è la versione originale.
    pari_merito = kworb[punteggi >= migliore - 1e-9]
    riga = pari_merito.sort_values("ascolti", ascending=False).iloc[0]
    return int(riga["ascolti"]), riga["titolo_kworb"], migliore


# =============================================================================
# PROGRAMMA PRINCIPALE
# =============================================================================
def main():
    df = carica_tabella()
    salva_tabella(df)   # salviamo subito: la tabella con i titoli e le emozioni esiste già
    print(f"Canzoni in tabella: {len(df)}")

    print(f"\nScarico la pagina di kworb...")
    html = scarica_pagina()
    kworb = leggi_tabella_kworb(html)
    print(f"Canzoni trovate su kworb: {len(kworb)}\n")

    non_trovate = 0
    for indice, riga in df.iterrows():
        titolo = riga["titolo"]
        ascolti, titolo_kworb, punteggio = migliore_corrispondenza(titolo, kworb)

        if ascolti is None:
            # Non tocchiamo il valore che c'era prima (se c'era)
            print(f"{titolo}: NON TROVATA su kworb (resta vuota per ora)")
            non_trovate += 1
        else:
            df.at[indice, "ascolti"] = ascolti
            # Stampiamo anche il titolo trovato su kworb, così puoi controllare che sia giusto
            # (se la somiglianza non è 1.00 vale la pena guardare con attenzione)
            print(f"{titolo}: {ascolti:,}   (su kworb: '{titolo_kworb}', somiglianza {punteggio:.2f})")

    salva_tabella(df)
    print(f"\nFatto. Salvato in {FILE_FINALE}. Canzoni senza ascolti: {non_trovate}")
    print(f"Ascolti aggiornati al {date.today().strftime('%d/%m/%Y')}")


if __name__ == "__main__":
    main()