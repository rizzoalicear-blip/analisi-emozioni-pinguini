"""
FASE 3 - Grafico a linee (top 4) per 'Scrivile Scemo' CON CONTESTO
===================================================================

Stessa identica logica di fase3_grafico_linee_canzone_singola.py (le 4
emozioni piu' alte, quella prevalente in risalto, etichette con
l'inizio del verso), ma applicata al file generato da
fase3_scrivile_scemo_contesto.py, cioe' ai punteggi che includono
anche il contesto delle righe vicine, non al CSV originale riga-per-
riga senza contesto.

Confronta il PNG che produce questo script con
andamento_Scrivile Scemo_top4.png (quello senza contesto, se lo hai
gia' generato) per vedere quanto cambia l'andamento includendo le
righe vicine nel conteggio.
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

# Il CSV di input e' quello CON CONTESTO, generato da
# fase3_scrivile_scemo_contesto.py (non emozioni_per_riga.csv).
NOME_CANZONE = "Scrivile Scemo"
PERCORSO_CSV_CONTESTO = os.path.join(
    CARTELLA_PROGETTO, f"emozioni_{NOME_CANZONE.replace(' ', '_')}_contesto_raggio1.csv"
)

NUMERO_PAROLE_ANTEPRIMA = 4

NOMI_EMOZIONI = ["rabbia", "attesa", "disgusto", "paura", "gioia", "tristezza", "sorpresa", "fiducia"]

COLORE_EMOZIONE_PREVALENTE = "crimson"
COLORI_ALTRE_EMOZIONI = ["steelblue", "seagreen", "goldenrod"]
STILI_ALTRE_EMOZIONI = [
    {"linestyle": "-", "marker": "s"},
    {"linestyle": "-", "marker": "^"},
    {"linestyle": "-", "marker": "D"},
]


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


def ottieni_top_n_emozioni(df_canzone, n):
    """Restituisce i nomi delle n emozioni con il totale piu' alto, dalla piu' alta in giu'."""
    totali_emozioni = df_canzone[NOMI_EMOZIONI].sum()
    top_n = totali_emozioni.sort_values(ascending=False).head(n)
    return list(top_n.index)


def stampa_riferimento_versi(df_canzone):
    """Stampa a schermo il testo completo di ogni riga, come riferimento per il grafico."""
    print(f"\n=== Testo completo di '{NOME_CANZONE}' (con contesto) - riferimento per il grafico ===")
    for _, riga in df_canzone.iterrows():
        print(f"{riga['numero_riga']}: {riga['testo']}")
    print()


def disegna_grafico_top4(df_canzone, top4_emozioni):
    """
    Disegna e salva il grafico a linee con le 4 emozioni piu' alte,
    mettendo in risalto quella prevalente (linea spessa e continua) e
    usando stili diversi per le altre tre, cosi' restano
    visibili anche quando si sovrappongono esattamente alla prevalente.
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
            plt.plot(
                range(len(df_canzone)),
                df_canzone[emozione],
                label=f"{emozione} (prevalente)",
                color=COLORE_EMOZIONE_PREVALENTE,
                linewidth=3,
                marker="o",
                zorder=3,
            )
        else:
            colore = COLORI_ALTRE_EMOZIONI[indice - 1]
            stile = STILI_ALTRE_EMOZIONI[indice - 1]
            plt.plot(
                range(len(df_canzone)),
                df_canzone[emozione],
                label=emozione,
                color=colore,
                linewidth=1.5,
                linestyle=stile["linestyle"],
                marker=stile["marker"],
                markersize=5,
                alpha=0.8,
                zorder=2,
            )

    plt.xticks(range(len(df_canzone)), etichette_x, rotation=90, fontsize=7)

    plt.title(f"'{NOME_CANZONE}' (CON CONTESTO) - Le 4 emozioni più presenti (in evidenza: {top4_emozioni[0]})")
    plt.xlabel("Numero di riga della canzone")
    plt.ylabel("Punteggio emozione (con contesto)")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    nome_file = f"andamento_{NOME_CANZONE}_top4_contesto_1.png"
    percorso_output = os.path.join(CARTELLA_PROGETTO, nome_file)
    plt.savefig(percorso_output, dpi=200)
    print(f"Immagine salvata in: {percorso_output}")

    plt.show()


# ---------------------------------------------------------------------
# FUNZIONE PRINCIPALE
# ---------------------------------------------------------------------

def main():
    df_canzone = pd.read_csv(PERCORSO_CSV_CONTESTO).sort_values("numero_riga")

    if df_canzone.empty:
        print(f"ATTENZIONE: il file {PERCORSO_CSV_CONTESTO} risulta vuoto o non trovato.")
        return

    stampa_riferimento_versi(df_canzone)

    top4_emozioni = ottieni_top_n_emozioni(df_canzone, 4)
    print(f"Top 4 emozioni (con contesto): {top4_emozioni}")

    disegna_grafico_top4(df_canzone, top4_emozioni)


# ---------------------------------------------------------------------
# BLOCCO DI ESECUZIONE
# ---------------------------------------------------------------------
if __name__ == "__main__":
    main()