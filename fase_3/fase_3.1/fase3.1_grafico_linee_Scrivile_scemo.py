"""
FASE 3 - Grafico a linee per una singola canzone (prova)
===================================================================

Obiettivo di questo script:
- prendere UNA canzone a scelta (impostala in NOME_CANZONE qui sotto)
- calcolare qual e' la sua emozione prevalente (quella con il punteggio
  totale piu' alto, sommando tutte le righe della canzone) e quali sono
  le 4 emozioni piu' alte in generale
- disegnare UN grafico a linee con le 4 emozioni piu' alte insieme,
  mettendo in risalto quella prevalente (linea piu' spessa e colore
  acceso) rispetto alle altre tre (piu' sottili e tenui)

Come riferimento visivo di "quale riga e' quale", ogni punto del
grafico riporta sull'asse x l'inizio del verso (le prime parole della
riga), invece del solo numero di riga. Il testo completo di ogni riga
viene comunque stampato a schermo per un confronto piu' comodo.

Usa emozioni_per_riga.csv (il CSV riga-per-riga), NON quello per
canzone: ci serve il dettaglio riga per riga per disegnare l'andamento.
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
# Questo script sta due livelli sotto la cartella principale (fase_3/fase_3.1/): saliamo di due cartelle
CARTELLA_PRINCIPALE = os.path.dirname(os.path.dirname(CARTELLA_PROGETTO))
PERCORSO_CSV_RIGHE = os.path.join(CARTELLA_PRINCIPALE, "fase_2", "emozioni_per_riga.csv")

# Cambia solo questo valore per rifare la stessa identica analisi su un'altra canzone
NOME_CANZONE = "Scrivile Scemo"

# Quante parole della riga mostrare come etichetta sull'asse x (per
# darti un riferimento visivo di "quale verso e' quale" senza dover
# scrivere la riga per intero, che sarebbe troppo lunga da leggere).
NUMERO_PAROLE_ANTEPRIMA = 4

NOMI_EMOZIONI = ["rabbia", "attesa", "disgusto", "paura", "gioia", "tristezza", "sorpresa", "fiducia"]

# Colori usati nel grafico con le 4 emozioni: il primo (indice 0) e'
# quello riservato all'emozione prevalente, gli altri tre alle
# emozioni "di contorno".
COLORE_EMOZIONE_PREVALENTE = "crimson"
COLORI_ALTRE_EMOZIONI = ["steelblue", "seagreen", "goldenrod"]


# ---------------------------------------------------------------------
# FUNZIONI
# ---------------------------------------------------------------------

def tronca_testo(testo, numero_parole):
    """
    Restituisce solo le prime N parole di un testo, seguite da "..." se
    il testo originale era piu' lungo. Usata per creare etichette corte
    da mettere sull'asse x del grafico.

    Parametri:
        testo (str): il testo completo della riga
        numero_parole (int): quante parole iniziali mantenere

    Restituisce:
        il testo troncato (str)
    """
    parole = testo.split()
    testo_troncato = " ".join(parole[:numero_parole])

    # Aggiungiamo i puntini di sospensione solo se abbiamo davvero
    # tagliato qualcosa (cioe' se la riga aveva piu' parole di quelle
    # mostrate).
    if len(parole) > numero_parole:
        testo_troncato += "..."

    return testo_troncato


def ottieni_top_n_emozioni(df_canzone, n):
    """
    Calcola il totale di ciascuna emozione sull'intera canzone e
    restituisce i nomi delle N emozioni con il punteggio piu' alto,
    dalla piu' alta alla meno alta.

    Parametri:
        df_canzone (pandas.DataFrame): le righe di UNA sola canzone
        n (int): quante emozioni restituire (es. 1 per la sola
            emozione prevalente, 4 per le prime quattro)

    Restituisce:
        una lista di n nomi di emozioni, in ordine decrescente di
        punteggio totale (es. ["tristezza", "rabbia", "paura", "gioia"])
    """
    totali_emozioni = df_canzone[NOMI_EMOZIONI].sum()

    # sort_values(ascending=False) ordina la Series dal valore piu' alto
    # al piu' basso. .head(n) prende solo le prime n righe di questo
    # ordinamento. .index restituisce i NOMI delle emozioni (non i
    # punteggi), che e' quello che ci serve per sapere "quali" sono.
    top_n = totali_emozioni.sort_values(ascending=False).head(n)

    return list(top_n.index)


def stampa_riferimento_versi(df_canzone):
    """
    Stampa a schermo l'elenco completo delle righe della canzone, con
    il loro numero, come riferimento testuale da consultare insieme al
    grafico (che invece mostra solo l'inizio di ogni verso).

    Parametri:
        df_canzone (pandas.DataFrame): le righe di UNA sola canzone
    """
    print(f"\n=== Testo completo di '{NOME_CANZONE}' (riferimento per il grafico) ===")
    for _, riga in df_canzone.iterrows():
        print(f"{riga['numero_riga']}: {riga['testo']}")
    print()


def disegna_grafico_top4(df_canzone, top4_emozioni):
    """
    Disegna e salva il grafico a linee con le 4 emozioni piu' alte
    della canzone, mettendo in risalto quella prevalente (la prima
    della lista top4_emozioni) con una linea piu' spessa e un colore
    acceso, mentre le altre tre restano piu' sottili e tenui.

    Parametri:
        df_canzone (pandas.DataFrame): le righe di UNA sola canzone,
            gia' ordinate per numero_riga
        top4_emozioni (list): le 4 emozioni da disegnare, in ordine
            decrescente (la prima e' la prevalente)
    """
    # Come etichette dell'asse x usiamo il NUMERO DI RIGA e non il testo:
    # cosi' il grafico non contiene nessuna parte del testo della canzone
    # (protetto da copyright). I numeri sono gli stessi che
    # stampa_riferimento_versi() mostra nel terminale, quindi per sapere
    # a quale verso corrisponde un punto basta guardare quell'elenco.
    etichette_x = [str(numero) for numero in df_canzone["numero_riga"]]

    plt.figure(figsize=(14, 6))

    for indice, emozione in enumerate(top4_emozioni):
        if indice == 0:
            # La prima emozione della lista e' quella prevalente: la
            # disegniamo con linea piu' spessa (linewidth), colore
            # acceso, sopra le altre linee (zorder alto) e con i
            # marker sui punti, per farla risaltare visivamente.
            plt.plot(
                range(len(df_canzone)),
                df_canzone[emozione],
                label=f"{emozione} (prevalente)",
                color=COLORE_EMOZIONE_PREVALENTE,
                linewidth=3,
                marker="o",
                zorder=3,  # zorder piu' alto = disegnata "sopra" le altre linee
            )
        else:
            # Le altre 3 emozioni: linea piu' sottile, colore piu'
            # tenue (alpha < 1 le rende semi-trasparenti) e senza
            # marker, cosi' restano leggibili come "sfondo" senza
            # rubare l'attenzione dalla linea principale.
            colore = COLORI_ALTRE_EMOZIONI[indice - 1]
            plt.plot(
                range(len(df_canzone)),
                df_canzone[emozione],
                label=emozione,
                color=colore,
                linewidth=1,
                alpha=0.6,
                zorder=1,
            )

    plt.xticks(range(len(df_canzone)), etichette_x, rotation=90, fontsize=7)

    plt.title(f"'{NOME_CANZONE}' - Le 4 emozioni più presenti (in evidenza: {top4_emozioni[0]})")
    plt.xlabel("Numero di riga della canzone")
    plt.ylabel("Punteggio emozione")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    nome_file = f"andamento_{NOME_CANZONE}_top4.png"
    percorso_output = os.path.join(CARTELLA_PROGETTO, nome_file)
    plt.savefig(percorso_output, dpi=200)
    print(f"Immagine salvata in: {percorso_output}")

    plt.show()


# ---------------------------------------------------------------------
# FUNZIONE PRINCIPALE
# ---------------------------------------------------------------------

def main():
    df_righe = pd.read_csv(PERCORSO_CSV_RIGHE)

    # Filtriamo solo le righe della canzone scelta, ordinate per
    # numero_riga (fondamentale per un grafico di "andamento").
    df_canzone = df_righe[df_righe["canzone"] == NOME_CANZONE].sort_values("numero_riga")

    if df_canzone.empty:
        print(f"ATTENZIONE: nessuna riga trovata per '{NOME_CANZONE}'. "
              f"Controlla che il nome sia scritto esattamente come nel CSV.")
        return

    stampa_riferimento_versi(df_canzone)

    emozione_prevalente = ottieni_top_n_emozioni(df_canzone, 1)[0]
    top4_emozioni = ottieni_top_n_emozioni(df_canzone, 4)

    print(f"Emozione prevalente di '{NOME_CANZONE}': {emozione_prevalente}")
    print(f"Top 4 emozioni: {top4_emozioni}")

    disegna_grafico_top4(df_canzone, top4_emozioni)


# ---------------------------------------------------------------------
# BLOCCO DI ESECUZIONE
# ---------------------------------------------------------------------
if __name__ == "__main__":
    main()