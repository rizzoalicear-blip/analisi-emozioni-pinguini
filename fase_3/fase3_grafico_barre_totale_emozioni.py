"""
FASE 3 - Grafico a barre: emozioni totali su tutte le canzoni
===================================================================

Obiettivo di questo script:
- sommare, per ciascuna delle 8 emozioni, il punteggio totale su TUTTE
  le canzoni del corpus (le 20 canzoni analizzate)
- disegnare un grafico a barre che mostra quali emozioni sono le piu'
  "presenti" nell'insieme delle canzoni dei Pinguini Tattici Nucleari

Usa il file emozioni_per_canzone.csv, gia' generato da
fase2_totale_canzone.py.
"""

# ---------------------------------------------------------------------
# IMPORT DELLE LIBRERIE
# ---------------------------------------------------------------------
import os
import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------
# CONFIGURAZIONE
# ---------------------------------------------------------------------

# Cartella dove si trova QUESTO script (es. fase_3_grafici/)
CARTELLA_SCRIPT = os.path.dirname(os.path.abspath(__file__))
# Cartella principale del progetto: quella che contiene tutte le cartelle delle fasi
CARTELLA_PROGETTO = os.path.dirname(CARTELLA_SCRIPT)

# Il CSV è stato prodotto dalla Fase 2, quindi sta nella cartella di quella fas
PERCORSO_CSV_CANZONI = os.path.join(CARTELLA_PROGETTO, "fase_2", "emozioni_per_canzone.csv")
# L'immagine invece viene salvata accanto a questo script
PERCORSO_IMMAGINE_OUTPUT = os.path.join(CARTELLA_SCRIPT, "grafico_temi_totale.png")

NOMI_EMOZIONI = ["rabbia", "attesa", "disgusto", "paura", "gioia", "tristezza", "sorpresa", "fiducia"]


# ---------------------------------------------------------------------
# FUNZIONI
# ---------------------------------------------------------------------

def calcola_totali_generali(df_canzoni):
    """
    Somma il punteggio di ciascuna emozione su tutte le righe del
    DataFrame (cioe' su tutte le canzoni insieme).

    Parametri:
        df_canzoni (pandas.DataFrame): il CSV con i totali per canzone

    Restituisce:
        una pandas.Series con 8 valori, uno per emozione (es.
        {"rabbia": 12, "gioia": 45, ...})
    """
    # df_canzoni[NOMI_EMOZIONI] seleziona solo le 8 colonne delle
    # emozioni (scartando "canzone" ed "emozione_prevalente", che non
    # avrebbe senso sommare). .sum() sui una Series/DataFrame senza
    # specificare axis somma lungo le righe per default, cioe' per
    # ciascuna colonna: risultato, un totale per emozione.
    return df_canzoni[NOMI_EMOZIONI].sum()


def disegna_grafico_barre(totali_emozioni):
    """
    Disegna un grafico a barre con un'emozione per barra.

    Parametri:
        totali_emozioni (pandas.Series): il totale di ciascuna emozione
    """
    plt.figure(figsize=(10, 6))

    # totali_emozioni.index sono i nomi delle emozioni (le "etichette"
    # della Series), totali_emozioni.values sono i numeri corrispondenti.
    plt.bar(totali_emozioni.index, totali_emozioni.values, color="steelblue")

    plt.title("Emozioni totali su tutte le canzoni analizzate")
    plt.xlabel("Emozione")
    plt.ylabel("Punteggio totale")
    plt.grid(axis="y", alpha=0.3)  # solo righe orizzontali, piu' leggibili per un grafico a barre

    plt.tight_layout()
    plt.savefig(PERCORSO_IMMAGINE_OUTPUT, dpi=200) #il file PNG viene scritto nella cartella del progetto ogni volta che lanci lo script
    print(f"Immagine salvata in: {PERCORSO_IMMAGINE_OUTPUT}")
    plt.show()


# ---------------------------------------------------------------------
# FUNZIONE PRINCIPALE
# ---------------------------------------------------------------------

def main():
    df_canzoni = pd.read_csv(PERCORSO_CSV_CANZONI)
    totali_emozioni = calcola_totali_generali(df_canzoni)
    disegna_grafico_barre(totali_emozioni)


# ---------------------------------------------------------------------
# BLOCCO DI ESECUZIONE
# ---------------------------------------------------------------------
if __name__ == "__main__":
    main()
