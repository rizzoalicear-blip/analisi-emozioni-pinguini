"""
FASE 3 - Grafico a barre: confronto emozioni Top 10 vs Bottom 10
===================================================================

Obiettivo di questo script:
- dividere le 20 canzoni in due gruppi: le 10 piu' ascoltate e le 10
  meno ascoltate (secondo i dati di streaming Spotify/kworb)
- per ciascun gruppo, calcolare quanto pesa ciascuna delle 8 emozioni
  IN PROPORZIONE al totale del gruppo (non il conteggio grezzo)
- disegnare un grafico a barre affiancate (due barre per ogni
  emozione, una per gruppo) per vedere se i due gruppi hanno un
  profilo emotivo simile o diverso

NOTA METODOLOGICA sulla proporzione: usiamo la percentuale sul totale
del gruppo, invece del conteggio grezzo, perche' i due gruppi
potrebbero avere una quantita' diversa di testo o di parole
"emotive" complessive. Sommando i valori grezzi, il gruppo con piu'
testo risulterebbe quasi sempre "piu' emotivo" solo per una questione
di lunghezza, non di contenuto: la percentuale toglie questo effetto
e permette un confronto piu' onesto tra i due gruppi.

Usa il file emozioni_per_canzone.csv, gia' generato da
fase2_totale_canzone.py.
"""

# ---------------------------------------------------------------------
# IMPORT DELLE LIBRERIE
# ---------------------------------------------------------------------
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------
# CONFIGURAZIONE
# ---------------------------------------------------------------------

# Cartella dove si trova QUESTO script (es. fase_3_grafici/)
CARTELLA_SCRIPT = os.path.dirname(os.path.abspath(__file__))
# Cartella principale del progetto: quella che contiene tutte le cartelle delle fasi
CARTELLA_PROGETTO = os.path.dirname(CARTELLA_SCRIPT)

# Il CSV è stato prodotto dalla Fase 2, quindi sta nella cartella di quella fase
PERCORSO_CSV_CANZONI = os.path.join(CARTELLA_PROGETTO, "fase_2", "emozioni_per_canzone.csv")
# L'immagine invece viene salvata accanto a questo script
PERCORSO_IMMAGINE_OUTPUT = os.path.join(CARTELLA_SCRIPT, "grafico_temi_top_bottom.png")

NOMI_EMOZIONI = ["rabbia", "attesa", "disgusto", "paura", "gioia", "tristezza", "sorpresa", "fiducia"]

# Le 10 canzoni piu' ascoltate (escludendo featuring/strumentali/versioni
# speciali, come deciso all'inizio del progetto).
CANZONI_TOP_10 = [
    "Ridere", "Pastello Bianco", "Giovani Wannabe", "Scrivile Scemo",
    "Rubami la Notte", "Ricordi", "Ringo Starr", "Scooby Doo",
    "Islanda", "La storia infinita",
]

# Le 10 canzoni meno ascoltate (stessi criteri di esclusione).
CANZONI_BOTTOM_10 = [
    "Rodger", "Il sonno ed il furto (storia di un coinquilino)", "Me Want Marò Back",
    "Pula", "In vento", "Gigi cinque ottavi", "Il concorso musicale",
    "Django", "Sudowoodo", "79",
]


# ---------------------------------------------------------------------
# FUNZIONI
# ---------------------------------------------------------------------

def calcola_percentuali_gruppo(df_canzoni, lista_canzoni):
    """
    Calcola, per un gruppo di canzoni, la percentuale di ciascuna
    emozione sul totale delle emozioni del gruppo.

    Parametri:
        df_canzoni (pandas.DataFrame): il CSV con i totali per canzone
        lista_canzoni (list): i titoli delle canzoni che fanno parte
            di questo gruppo (es. CANZONI_TOP_10)

    Restituisce:
        una pandas.Series con 8 valori percentuali (che sommano a 100),
        uno per emozione
    """
    # isin() seleziona solo le righe il cui titolo e' presente nella
    # lista fornita: cosi' filtriamo il DataFrame al solo gruppo scelto.
    df_gruppo = df_canzoni[df_canzoni["canzone"].isin(lista_canzoni)]

    # Controllo di sicurezza: se qualche titolo nella lista non
    # corrisponde esattamente a quello nel CSV (es. per un errore di
    # battitura), avvisiamo, perche' altrimenti il gruppo risulterebbe
    # incompleto senza che ce ne accorgiamo.
    canzoni_trovate = set(df_gruppo["canzone"])
    canzoni_mancanti = set(lista_canzoni) - canzoni_trovate
    if canzoni_mancanti:
        print(f"ATTENZIONE: canzoni non trovate nel CSV: {canzoni_mancanti}")

    totali_gruppo = df_gruppo[NOMI_EMOZIONI].sum()

    # Dividiamo ogni totale per la somma di TUTTI i totali del gruppo,
    # poi moltiplichiamo per 100 per ottenere una percentuale.
    totale_complessivo = totali_gruppo.sum()
    percentuali = (totali_gruppo / totale_complessivo) * 100

    return percentuali


def disegna_grafico_confronto(percentuali_top, percentuali_bottom):
    """
    Disegna un grafico a barre affiancate: per ogni emozione, una barra
    per il gruppo Top 10 e una per il gruppo Bottom 10.

    Parametri:
        percentuali_top (pandas.Series): percentuali del gruppo Top 10
        percentuali_bottom (pandas.Series): percentuali del gruppo Bottom 10
    """
    # np.arange crea le posizioni numeriche (0, 1, 2, ...) sull'asse x,
    # una per ciascuna emozione: ci servono per poter disegnare due
    # barre leggermente spostate una accanto all'altra sulla stessa
    # posizione, invece che sovrapposte.
    posizioni = np.arange(len(NOMI_EMOZIONI))
    larghezza_barra = 0.35  # quanto e' larga ciascuna barra

    plt.figure(figsize=(12, 6))

    # Spostiamo le barre "Top 10" un po' a sinistra della posizione
    # centrale (- larghezza_barra/2) e quelle "Bottom 10" un po' a
    # destra (+ larghezza_barra/2), cosi' risultano affiancate invece
    # che sovrapposte.
    plt.bar(posizioni - larghezza_barra/2, percentuali_top.values, larghezza_barra,
            label="Top 10 più ascoltate", color="seagreen")
    plt.bar(posizioni + larghezza_barra/2, percentuali_bottom.values, larghezza_barra,
            label="Bottom 10 meno ascoltate", color="indianred")

    # xticks sostituisce le posizioni numeriche (0,1,2...) con i nomi
    # veri delle emozioni come etichette sull'asse x.
    plt.xticks(posizioni, NOMI_EMOZIONI)

    plt.title("Confronto emozioni: canzoni più ascoltate vs meno ascoltate")
    plt.xlabel("Emozione")
    plt.ylabel("Percentuale sul totale del gruppo (%)")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(PERCORSO_IMMAGINE_OUTPUT, dpi=200) #il file PNG viene scritto nella cartella del progetto ogni volta che lanci lo script
    print(f"Immagine salvata in: {PERCORSO_IMMAGINE_OUTPUT}")
    plt.show()


# ---------------------------------------------------------------------
# FUNZIONE PRINCIPALE
# ---------------------------------------------------------------------

def main():
    df_canzoni = pd.read_csv(PERCORSO_CSV_CANZONI)

    percentuali_top = calcola_percentuali_gruppo(df_canzoni, CANZONI_TOP_10)
    percentuali_bottom = calcola_percentuali_gruppo(df_canzoni, CANZONI_BOTTOM_10)

    disegna_grafico_confronto(percentuali_top, percentuali_bottom)


# ---------------------------------------------------------------------
# BLOCCO DI ESECUZIONE
# ---------------------------------------------------------------------
if __name__ == "__main__":
    main()