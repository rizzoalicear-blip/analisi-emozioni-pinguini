"""
FASE 3 - Confronto riga per riga tra grezzo, contesto ±1 e contesto ±2
===================================================================

Obiettivo di questo script:
- a differenza del boxplot (che confronta le DISTRIBUZIONI complessive
  dei tre gruppi, perdendo il collegamento tra una riga e l'altra),
  qui confrontiamo i tre valori di CIASCUNA riga, uno accanto
  all'altro, cosi' vediamo esattamente quali versi cambiano di piu'
  passando da grezzo a ±1 a ±2
- disegniamo due grafici:
    1. un grafico a linee con le tre versioni sovrapposte, verso per
       verso (confronto diretto, "appaiato")
    2. un grafico a barre con la DIFFERENZA tra contesto ±2 e grezzo,
       riga per riga: le barre piu' alte indicano i versi su cui il
       contesto ha inciso di piu'

Usa i tre file gia' generati: emozioni_per_riga.csv (filtrato sulla
canzone), e i due CSV con contesto da fase3_scrivile_scemo_contesto.py.
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

CARTELLA_PROGETTO = os.path.dirname(os.path.abspath(__file__))
# Cartella principale del progetto: lo script sta in fase_3/<sottocartella>/,
# quindi saliamo di DUE cartelle (con un solo livello, es. fase_3/, usa un solo dirname)
CARTELLA_PRINCIPALE = os.path.dirname(os.path.dirname(CARTELLA_PROGETTO))
NOME_CANZONE = "Scrivile Scemo"

# Il CSV riga per riga viene dalla Fase 2
PERCORSO_CSV_GREZZO = os.path.join(CARTELLA_PRINCIPALE, "fase_2", "emozioni_per_riga.csv")
PERCORSO_CSV_RAGGIO1 = os.path.join(
    CARTELLA_PROGETTO, f"emozioni_{NOME_CANZONE.replace(' ', '_')}_contesto_raggio1.csv"
)
PERCORSO_CSV_RAGGIO2 = os.path.join(
    CARTELLA_PROGETTO, f"emozioni_{NOME_CANZONE.replace(' ', '_')}_contesto_raggio2.csv"
)

NOMI_EMOZIONI = ["rabbia", "attesa", "disgusto", "paura", "gioia", "tristezza", "sorpresa", "fiducia"]
NUMERO_PAROLE_ANTEPRIMA = 4


# ---------------------------------------------------------------------
# FUNZIONI
# ---------------------------------------------------------------------

def tronca_testo(testo, numero_parole):
    """Restituisce solo le prime N parole di un testo (per le etichette dell'asse x)."""
    parole = testo.split()
    testo_troncato = " ".join(parole[:numero_parole])
    if len(parole) > numero_parole:
        testo_troncato += "..."
    return testo_troncato


def trova_emozione_prevalente(df_grezzo_canzone):
    """Determina l'emozione prevalente sommando le 8 emozioni sul dato grezzo."""
    totali = df_grezzo_canzone[NOMI_EMOZIONI].sum()
    return totali.idxmax()


def disegna_confronto_a_linee(df_unito, nome_emozione):
    """
    Disegna le tre versioni (grezzo, ±1, ±2) come linee sovrapposte,
    riga per riga, per un confronto diretto verso per verso.

    Parametri:
        df_unito (pandas.DataFrame): le tre colonne allineate per
            numero_riga (vedi main per come viene costruito)
        nome_emozione (str): nome dell'emozione confrontata
    """
    # Come etichette dell'asse x usiamo il NUMERO DI RIGA e non il testo:
    # cosi' il grafico non contiene nessuna parte del testo della canzone
    # (protetto da copyright). I numeri sono gli stessi che
    # stampa_riferimento_versi() mostra nel terminale, quindi per sapere
    # a quale verso corrisponde un punto basta guardare quell'elenco.
    etichette_x = [str(numero) for numero in df_unito["numero_riga"]]
    posizioni_x = range(len(df_unito))

    plt.figure(figsize=(14, 6))

    plt.plot(posizioni_x, df_unito["grezzo"], label="Grezzo (±0)",
              color="gold", linewidth=1.5, marker="o", markersize=4)
    plt.plot(posizioni_x, df_unito["raggio1"], label="Contesto ±1",
              color="darkorange", linewidth=2, marker="s", markersize=4)
    plt.plot(posizioni_x, df_unito["raggio2"], label="Contesto ±2",
              color="red", linewidth=2.5, marker="^", markersize=5)

    plt.xticks(posizioni_x, etichette_x, rotation=90, fontsize=7)
    plt.title(f"'{NOME_CANZONE}' - Confronto riga per riga di '{nome_emozione}' nei 3 contesti")
    plt.xlabel("Numero di riga della canzone")
    plt.ylabel(f"Punteggio {nome_emozione}")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    percorso_output = os.path.join(
        CARTELLA_PROGETTO, f"confronto_righe_{NOME_CANZONE.replace(' ', '_')}_{nome_emozione}.png"
    )
    plt.savefig(percorso_output, dpi=200)
    print(f"Immagine salvata in: {percorso_output}")
    plt.show()


def disegna_differenze_a_barre(df_unito, nome_emozione):
    """
    Disegna un grafico a barre con la differenza (contesto ±2 - grezzo)
    per ciascuna riga: le barre piu' alte mostrano i versi su cui il
    contesto ha inciso di piu'.

    Parametri:
        df_unito (pandas.DataFrame): le tre colonne allineate
        nome_emozione (str): nome dell'emozione confrontata
    """
    differenza = df_unito["raggio2"] - df_unito["grezzo"]
    # Come etichette dell'asse x usiamo il NUMERO DI RIGA e non il testo:
    # cosi' il grafico non contiene nessuna parte del testo della canzone
    # (protetto da copyright). I numeri sono gli stessi che
    # stampa_riferimento_versi() mostra nel terminale, quindi per sapere
    # a quale verso corrisponde un punto basta guardare quell'elenco.
    etichette_x = [str(numero) for numero in df_unito["numero_riga"]]

    plt.figure(figsize=(14, 5))
    plt.bar(range(len(df_unito)), differenza, color="mediumpurple")
    plt.xticks(range(len(df_unito)), etichette_x, rotation=90, fontsize=7)
    plt.title(f"'{NOME_CANZONE}' - Differenza (contesto ±2 - grezzo) di '{nome_emozione}' per riga")
    plt.xlabel("Numero di riga della canzone")
    plt.ylabel(f"Differenza punteggio {nome_emozione}")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    percorso_output = os.path.join(
        CARTELLA_PROGETTO, f"differenza_righe_{NOME_CANZONE.replace(' ', '_')}_{nome_emozione}.png"
    )
    plt.savefig(percorso_output, dpi=200)
    print(f"Immagine salvata in: {percorso_output}")
    plt.show()


# ---------------------------------------------------------------------
# FUNZIONE PRINCIPALE
# ---------------------------------------------------------------------

def main():
    df_grezzo = pd.read_csv(PERCORSO_CSV_GREZZO)
    df_grezzo_canzone = df_grezzo[df_grezzo["canzone"] == NOME_CANZONE].sort_values("numero_riga")

    df_raggio1 = pd.read_csv(PERCORSO_CSV_RAGGIO1).sort_values("numero_riga")
    df_raggio2 = pd.read_csv(PERCORSO_CSV_RAGGIO2).sort_values("numero_riga")

    emozione_prevalente = trova_emozione_prevalente(df_grezzo_canzone)
    print(f"Emozione prevalente rilevata automaticamente: {emozione_prevalente}\n")

    # Costruiamo un unico DataFrame con una riga per verso e tre
    # colonne (grezzo, raggio1, raggio2): usiamo numero_riga come
    # "chiave" per allineare correttamente i tre valori della stessa
    # riga, anche se nei tre file fossero in un ordine leggermente
    # diverso (qui non dovrebbe succedere, ma e' una sicurezza in piu').
    df_unito = pd.DataFrame({
        "numero_riga": df_grezzo_canzone["numero_riga"].values,
        "testo": df_grezzo_canzone["testo"].values,
        "grezzo": df_grezzo_canzone[emozione_prevalente].values,
        "raggio1": df_raggio1[emozione_prevalente].values,
        "raggio2": df_raggio2[emozione_prevalente].values,
    })

    # Controllo di coerenza: se i tre file avessero un numero diverso
    # di righe (es. uno dei CSV e' stato generato da una versione
    # diversa del testo), ce ne accorgiamo subito invece di avere un
    # confronto silenziosamente sbagliato.
    if not (len(df_grezzo_canzone) == len(df_raggio1) == len(df_raggio2)):
        print("ATTENZIONE: i tre file hanno un numero diverso di righe, il confronto potrebbe essere disallineato!")
        print(f"Grezzo: {len(df_grezzo_canzone)} righe, Raggio1: {len(df_raggio1)} righe, Raggio2: {len(df_raggio2)} righe")

    print(df_unito.to_string(index=False))

    disegna_confronto_a_linee(df_unito, emozione_prevalente)
    disegna_differenze_a_barre(df_unito, emozione_prevalente)


# ---------------------------------------------------------------------
# BLOCCO DI ESECUZIONE
# ---------------------------------------------------------------------
if __name__ == "__main__":
    main()