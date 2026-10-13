"""
FASE 4 - Grafico a barre: emozioni secondo pysentimiento (Transformer)
===================================================================

Obiettivo di questo script:
- leggere emozioni_transformer.csv (generato da fase2_confronto_transformer.py,
  che assegna UNA emozione prevalente a ciascuna canzone intera)
- contare quante canzoni sono state classificate con ciascuna emozione
- disegnare un grafico a barre di queste frequenze, da confrontare
  visivamente con grafico_temi_totale.png (basato invece sul conteggio
  di parole del lessico NRC)

NOTA IMPORTANTE sul confronto: i due grafici misurano cose diverse.
- grafico_temi_totale.png (NRC): somma di PAROLE associate a ciascuna
  emozione, su tutte le canzoni insieme (un numero che puo' essere
  grande, decine o centinaia).
- questo grafico (Transformer): numero di CANZONI (su un massimo di 20)
  classificate con ciascuna emozione come prevalente.
Non sono la stessa unita' di misura, ma rispondono alla stessa domanda
("quale emozione domina di piu' nel corpus secondo questo metodo") e
quindi restano confrontabili per capire se i due approcci sono
d'accordo su quali emozioni dominano.
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

CARTELLA_SCRIPT = os.path.dirname(os.path.abspath(__file__))
PERCORSO_CSV_TRANSFORMER = os.path.join(CARTELLA_SCRIPT, "emozioni_transformer.csv")
PERCORSO_IMMAGINE_OUTPUT = os.path.join(CARTELLA_SCRIPT, "grafico_temi_totale_transformer.png")

# pysentimiento restituisce i nomi delle emozioni in inglese: li
# traduciamo in italiano per confrontarli direttamente con i nomi usati
# nel grafico basato su NRC (rabbia, disgusto, paura, gioia, tristezza,
# sorpresa). "others" e' la categoria residua di pysentimiento per
# "nessuna emozione forte riconosciuta": non esiste un equivalente in
# NRC, la teniamo comunque per completezza ma lo segnaliamo nel grafico.
TRADUZIONE_EMOZIONI = {
    "anger": "rabbia",
    "disgust": "disgusto",
    "fear": "paura",
    "joy": "gioia",
    "sadness": "tristezza",
    "surprise": "sorpresa",
    "others": "altro/nessuna",
}

# ---------------------------------------------------------------------
# FUNZIONI
# ---------------------------------------------------------------------

def conta_emozioni_per_canzone(df_transformer):
    """
    Conta quante canzoni sono state classificate con ciascuna emozione,
    traducendo i nomi delle emozioni in italiano.

    Parametri:
        df_transformer (pandas.DataFrame): il CSV generato da
            fase2_confronto_transformer.py

    Restituisce:
        una pandas.Series con il conteggio di canzoni per ciascuna
        emozione (in italiano), ordinata dal piu' frequente al meno
        frequente
    """
    # Sostituiamo i nomi inglesi con quelli italiani usando il
    # dizionario di traduzione, creando una nuova colonna temporanea.
    emozioni_tradotte = df_transformer["emozione_transformer"].map(TRADUZIONE_EMOZIONI)

    # value_counts() conta quante volte compare ciascun valore distinto
    # nella colonna: nel nostro caso, quante canzoni per ciascuna
    # emozione. E' gia' ordinato dal piu' frequente al meno frequente.
    return emozioni_tradotte.value_counts()


def disegna_grafico_barre(conteggio_emozioni):
    """
    Disegna un grafico a barre con il numero di canzoni per emozione.

    Parametri:
        conteggio_emozioni (pandas.Series): il conteggio gia' calcolato
    """
    plt.figure(figsize=(10, 6))
    plt.bar(conteggio_emozioni.index, conteggio_emozioni.values, color="darkorange")

    plt.title("Emozione prevalente per canzone secondo pysentimiento (Transformer)")
    plt.xlabel("Emozione")
    plt.ylabel("Numero di canzoni")
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(PERCORSO_IMMAGINE_OUTPUT, dpi=200)
    print(f"Immagine salvata in: {PERCORSO_IMMAGINE_OUTPUT}")
    plt.show()


# ---------------------------------------------------------------------
# FUNZIONE PRINCIPALE
# ---------------------------------------------------------------------

def main():
    df_transformer = pd.read_csv(PERCORSO_CSV_TRANSFORMER)
    conteggio_emozioni = conta_emozioni_per_canzone(df_transformer)

    print("Conteggio canzoni per emozione (Transformer):")
    print(conteggio_emozioni.to_string())

    disegna_grafico_barre(conteggio_emozioni)


# ---------------------------------------------------------------------
# BLOCCO DI ESECUZIONE
# ---------------------------------------------------------------------
if __name__ == "__main__":
    main()