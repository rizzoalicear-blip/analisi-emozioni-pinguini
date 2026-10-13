"""
FASE 3 - Mappa di calore delle emozioni per canzone
===================================================================

Obiettivo di questo script:
- leggere emozioni_per_canzone.csv (gia' generato da
  fase2_totale_canzone.py)
- disegnare una mappa di calore con le canzoni sulle righe e le 8
  emozioni sulle colonne, dove il colore indica l'intensita' di ogni
  emozione in ogni canzone

Utile per vedere a colpo d'occhio quale canzone e' la piu' "estrema"
per una certa emozione, e se alcune emozioni tendono a comparire
insieme nelle stesse canzoni.
"""

# ---------------------------------------------------------------------
# IMPORT DELLE LIBRERIE
# ---------------------------------------------------------------------
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ---------------------------------------------------------------------
# CONFIGURAZIONE
# ---------------------------------------------------------------------

# Cartella dove si trova QUESTO script (es. fase_3_grafici/)
CARTELLA_SCRIPT = os.path.dirname(os.path.abspath(__file__))
# Cartella principale del progetto: quella che contiene tutte le cartelle delle fasi
CARTELLA_PROGETTO = os.path.dirname(CARTELLA_SCRIPT)

# Il CSV è stato prodotto dalla Fase 2, quindi sta nella cartella di quella fase
PERCORSO_CSV_CANZONI = os.path.join(CARTELLA_PROGETTO, "fase_2", "emozioni_per_canzone.csv")
# Percorso dove verra' salvata l'immagine della mappa di calore.
PERCORSO_IMMAGINE_OUTPUT = os.path.join(CARTELLA_SCRIPT, "mappa_calore_emozioni.png")

# Le 8 colonne delle emozioni, nello stesso ordine usato negli altri script.
NOMI_EMOZIONI = ["rabbia", "attesa", "disgusto", "paura", "gioia", "tristezza", "sorpresa", "fiducia"]


# ---------------------------------------------------------------------
# FUNZIONI
# ---------------------------------------------------------------------

def disegna_mappa_di_calore(df_canzoni):
    """
    Disegna una mappa di calore con le canzoni sulle righe e le
    emozioni sulle colonne.

    Parametri:
        df_canzoni (pandas.DataFrame): il CSV con i totali per canzone
            (colonne: canzone, le 8 emozioni, emozione_prevalente)
    """
    # set_index("canzone") usa i nomi delle canzoni come etichette di
    # riga (invece dei numeri 0,1,2...), cosi' compaiono sull'asse y
    # della mappa di calore. Selezioniamo poi solo le 8 colonne delle
    # emozioni: non vogliamo che "emozione_prevalente" (che e' testo,
    # non un numero) venga disegnata come se fosse un valore numerico.
    dati_da_disegnare = df_canzoni.set_index("canzone")[NOMI_EMOZIONI]

    # La dimensione della figura si adatta al numero di canzoni: piu'
    # canzoni ci sono, piu' il grafico deve essere alto per restare
    # leggibile (0.4 pollici extra di altezza per ogni canzone).
    altezza_figura = 4 + 0.4 * len(dati_da_disegnare)
    plt.figure(figsize=(16, altezza_figura))

    # annot=True scrive il numero dentro ogni cella, oltre al colore.
    # fmt="d" dice di scrivere quei numeri come interi (senza decimali).
    # cmap="YlOrRd" e' la scala di colori: dal giallo chiaro (valori
    # bassi) al rosso scuro (valori alti).
    sns.heatmap(dati_da_disegnare, annot=True, fmt="d", cmap="YlOrRd", linewidths=0.5)

    plt.title("Intensità delle emozioni per canzone")
    plt.xlabel("Emozione")
    plt.ylabel("Canzone")

    plt.tight_layout()

    # savefig() salva l'immagine su disco PRIMA di mostrarla: se lo
    # facessimo dopo plt.show(), la finestra del grafico "consumerebbe"
    # la figura e il file salvato risulterebbe vuoto.
    # dpi=200 aumenta la risoluzione (dots per inch) rispetto al default,
    # utile se poi vuoi incollare l'immagine in una relazione/tesi senza
    # che risulti sgranata.
    plt.savefig(PERCORSO_IMMAGINE_OUTPUT, dpi=200)
    print(f"Immagine salvata in: {PERCORSO_IMMAGINE_OUTPUT}")

    plt.show()


# ---------------------------------------------------------------------
# FUNZIONE PRINCIPALE
# ---------------------------------------------------------------------

def main():
    df_canzoni = pd.read_csv(PERCORSO_CSV_CANZONI)
    disegna_mappa_di_calore(df_canzoni)


# ---------------------------------------------------------------------
# BLOCCO DI ESECUZIONE
# ---------------------------------------------------------------------
if __name__ == "__main__":
    main()