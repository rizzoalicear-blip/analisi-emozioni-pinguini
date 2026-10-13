"""
FASE 2 (aggregazione) - Totale delle emozioni per canzone
===================================================================

Obiettivo di questo script:
- leggere il CSV gia' generato da fase2_analisi_emozioni.py
  (una riga per ogni riga di testo, con il conteggio delle 8 emozioni)
- sommare, canzone per canzone, tutte le sue righe: cosi' otteniamo il
  totale di ciascuna emozione per l'intera canzone
- determinare l'emozione prevalente di ogni canzone: quella con il
  punteggio totale piu' alto
- salvare il risultato in un nuovo CSV, con una riga per canzone
  (invece che una riga per ogni riga di testo)

Non serve rifare nessun calcolo sul testo: i dati grezzi (quante parole
di ciascuna emozione ci sono in ogni riga) li abbiamo gia' nel primo
CSV. Qui ci limitiamo a sommarli in modo aggregato con pandas.
"""

# ---------------------------------------------------------------------
# IMPORT DELLE LIBRERIE
# ---------------------------------------------------------------------
import os
import pandas as pd


# ---------------------------------------------------------------------
# CONFIGURAZIONE
# ---------------------------------------------------------------------

# Stessa logica gia' usata in fase2_analisi_emozioni.py: i percorsi si
# basano sulla cartella dove si trova QUESTO script, non su dove lo lanci.
CARTELLA_PROGETTO = os.path.dirname(os.path.abspath(__file__))

# Il CSV di input e' quello gia' creato da fase2_analisi_emozioni.py. Qui sta facendo solo il collegamento su dove si trova il file CSV riga per riga.
PERCORSO_CSV_RIGHE = os.path.join(CARTELLA_PROGETTO, "emozioni_per_riga.csv")

# Il CSV di output che questo script creera', con un totale per canzone.
PERCORSO_CSV_CANZONI = os.path.join(CARTELLA_PROGETTO, "emozioni_per_canzone.csv")

# Le 8 colonne delle emozioni, nello stesso ordine/nome gia' usato nel
# CSV riga-per-riga (deve corrispondere esattamente ai nomi delle
# colonne create da fase2_analisi_emozioni.py).
NOMI_EMOZIONI = ["rabbia", "attesa", "disgusto", "paura", "gioia", "tristezza", "sorpresa", "fiducia"]


# ---------------------------------------------------------------------
# FUNZIONI
# ---------------------------------------------------------------------

def calcola_totali_per_canzone(df_righe):
    """
    Aggrega il DataFrame riga-per-riga in un DataFrame canzone-per-canzone,
    sommando i punteggi delle 8 emozioni e individuando quella prevalente.

    Parametri:
        df_righe (pandas.DataFrame): il CSV letto riga per riga
            (colonne: canzone, numero_riga, testo, lingua, + 8 emozioni)

    Restituisce:
        un pandas.DataFrame con una riga per canzone, contenente i
        totali delle 8 emozioni e una colonna "emozione_prevalente"
    """
    # groupby("canzone") raggruppa tutte le righe che hanno lo stesso
    # valore nella colonna "canzone" (es. tutte le righe di "Ridere"
    # insieme, tutte quelle di "Django" insieme, ecc.).
    # [NOMI_EMOZIONI] seleziona solo le 8 colonne delle emozioni, perche'
    # non ha senso "sommare" numero_riga o il testo.
    # .sum() somma, per ciascun gruppo, tutti i valori di quelle colonne.
    df_totali = df_righe.groupby("canzone")[NOMI_EMOZIONI].sum()

    # A questo punto df_totali ha "canzone" come indice (non come
    # colonna normale): reset_index() la riporta ad essere una colonna
    # vera e propria, piu' comodo da salvare nel CSV.
    df_totali = df_totali.reset_index()

    # idxmax(axis=1) restituisce, per ogni riga, il NOME della colonna
    # (tra quelle indicate) che ha il valore piu' alto in quella riga.
    # axis=1 vuol dire "guarda lungo le colonne", cioe' confronta i
    # valori delle 8 emozioni tra loro, riga per riga (una canzone alla
    # volta), non le canzoni tra loro.
    df_totali["emozione_prevalente"] = df_totali[NOMI_EMOZIONI].idxmax(axis=1)

    return df_totali


# ---------------------------------------------------------------------
# FUNZIONE PRINCIPALE
# ---------------------------------------------------------------------

def main():
    """
    Funzione principale: legge il CSV riga-per-riga, calcola i totali
    per canzone e salva il risultato in un nuovo CSV.
    """
    print("Lettura del CSV riga-per-riga...")
    df_righe = pd.read_csv(PERCORSO_CSV_RIGHE)
    # questa l'istruzione che apre davvero il file CSV e ne carica il contenuto dentro il programma; Solo a questo punto, se il file non esistesse in quella posizione, otterresti un errore
    # pd.read_csv (...) legge il file CSV e restituisce un DataFrame, cioè trasforma il testo del file in una tabella vera e propria con cui Python può lavorare

    print("Calcolo dei totali per canzone...")
    df_totali = calcola_totali_per_canzone(df_righe)

    # Controllo parità: segnala le canzoni in cui più emozioni hanno lo stesso punteggio massimo
    massimo_per_canzone = df_totali[NOMI_EMOZIONI].max(axis=1)
    for _, riga in df_totali.iterrows():
        a_pari_merito = [e for e in NOMI_EMOZIONI if riga[e] == riga[NOMI_EMOZIONI].max()]
        if len(a_pari_merito) > 1:
            print(f"PARITÀ: {riga['canzone']} -> {a_pari_merito} (punteggio {riga[NOMI_EMOZIONI].max()})")

    df_totali.to_csv(PERCORSO_CSV_CANZONI, index=False, encoding="utf-8") # questa e' l'istruzione che scrive davvero il DataFrame su disco come nuovo file CSV
    print("\nAnteprima dei risultati:")
    # to_string(index=False) stampa la tabella senza mostrare l'indice
    # numerico automatico di pandas, solo le colonne che ci interessano.
    print(df_totali.to_string(index=False))


# ---------------------------------------------------------------------
# BLOCCO DI ESECUZIONE
# ---------------------------------------------------------------------
if __name__ == "__main__":
    main()