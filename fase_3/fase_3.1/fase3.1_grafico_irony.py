"""
FASE 3.1 - Grafico dell'andamento dell'ironia in 'Scrivile Scemo'
=================================================================

COSA FA QUESTO SCRIPT, IN SINTESI
---------------------------------
1. Legge ironia_Scrivile_Scemo.csv, creato da fase3.1_ironia_scrivile.py
   (una riga per verso, con la probabilita' di ironia calcolata con tre
   finestre di contesto: raggio 0, 1 e 2).
2. Disegna un grafico a linee: sull'asse x i versi della canzone, sull'asse
   y la probabilita' di ironia (da 0 a 1), con una linea per ogni raggio.
3. Segna con una linea tratteggiata la soglia 0.5 e annota il verso piu'
   ironico secondo il modello (raggio 0).
4. Salva il grafico in PNG e stampa a schermo i versi piu' ironici.

COME LEGGERE IL GRAFICO
-----------------------
- Una linea sopra 0.5 = il modello considera quel punto piu' probabilmente
  ironico che non ironico.
- Se le tre linee sono vicine, il contesto cambia poco il giudizio; se si
  allontanano, il giudizio dipende molto dalle righe vicine.

INSTALLAZIONE RICHIESTA
-----------------------
    pip install pandas matplotlib
(sono gia' nel requirements.txt)
"""

# ---------------------------------------------------------------------
# IMPORT DELLE LIBRERIE
# ---------------------------------------------------------------------

# os: costruisce i percorsi dei file in modo corretto su ogni sistema operativo.
import os

# pandas: legge il CSV e lo gestisce come tabella.
import pandas as pd

# matplotlib.pyplot: la libreria per disegnare i grafici. Per convenzione
# si importa con il nome corto "plt".
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------
# CONFIGURAZIONE
# (tutto quello che puoi voler cambiare sta qui, in cima)
# ---------------------------------------------------------------------

# Cartella in cui si trova questo script (fase_3/fase_3.1/).
# __file__ e' il percorso dello script; abspath lo rende assoluto;
# dirname toglie il nome del file e lascia la cartella.
CARTELLA_SCRIPT = os.path.dirname(os.path.abspath(__file__))

# File di input: lo script dell'ironia lo ha salvato proprio qui accanto.
PERCORSO_CSV = os.path.join(CARTELLA_SCRIPT, "ironia_Scrivile_Scemo.csv")

# File di output: il grafico in formato immagine.
PERCORSO_PNG = os.path.join(CARTELLA_SCRIPT, "andamento_ironia_Scrivile_Scemo.png")

# Titolo della canzone, usato solo nel titolo del grafico.
NOME_CANZONE = "Scrivile Scemo"

# I raggi di contesto presenti nel CSV (devono coincidere con quelli usati
# nello script dell'ironia: le colonne si chiamano p_ironia_r0, p_ironia_r1...).
RAGGI_CONTESTO = [0, 1, 2]

# Aspetto di ogni linea, per raggio: colore, spessore, stile e descrizione
# che comparira' nella legenda.
STILE_LINEE = {
    0: {"colore": "#d62728", "spessore": 2.2, "stile": "-",  "etichetta": "Solo la riga (raggio 0)", "alpha": 1.00},
    1: {"colore": "#1f77b4", "spessore": 1.0, "stile": "-", "etichetta": "Contesto ±1 riga (raggio 1)", "alpha": 0.60},
    2: {"colore": "#2ca02c", "spessore": 1.0, "stile": "-",  "etichetta": "Contesto ±2 righe (raggio 2)", "alpha": 0.30},
}

# Soglia oltre la quale il modello considera una frase piu' ironica che no.
SOGLIA_IRONIA = 0.5

# Se True, oltre a salvare il PNG apre il grafico in una finestra.
# Mettilo a False se lanci lo script su un computer senza schermo
# (es. un server) o se ti basta il file salvato.
MOSTRA_GRAFICO = True

# Quanti versi stampare nella classifica finale a schermo.
NUMERO_TOP = 5

# Numero massimo di caratteri del verso mostrato nell'annotazione del
# grafico (i versi lunghi verrebbero tagliati dal bordo dell'immagine).
LUNGHEZZA_MAX_ANNOTAZIONE = 45

# Quante parole iniziali di ogni verso mostrare sull'asse x. Con piu' parole
# le etichette sono piu' riconoscibili ma occupano piu' spazio.
PAROLE_ETICHETTA = 4


# ---------------------------------------------------------------------
# FUNZIONI
# ---------------------------------------------------------------------

def carica_dati():
    """
    Legge il CSV dell'ironia e controlla che abbia le colonne attese.

    Restituisce:
        un DataFrame (tabella pandas) ordinato per numero di riga
    """
    # Se il file non esiste, fermiamo lo script con un messaggio chiaro
    # invece del lungo errore tecnico che darebbe pandas.
    if not os.path.exists(PERCORSO_CSV):
        raise FileNotFoundError(
            f"Non trovo {PERCORSO_CSV}. Esegui prima fase3.1_ironia_scrivile.py."
        )

    df = pd.read_csv(PERCORSO_CSV)

    # Elenco delle colonne che servono: numero_riga, testo e una colonna
    # p_ironia_rX per ogni raggio (la parte tra parentesi quadre e' una
    # "list comprehension": una lista costruita con un ciclo in una riga).
    colonne_attese = ["numero_riga", "testo"] + [f"p_ironia_r{r}" for r in RAGGI_CONTESTO]

    # Cerca le colonne mancanti: quelle attese che non sono nel file.
    mancanti = [c for c in colonne_attese if c not in df.columns]
    if mancanti:
        raise ValueError(f"Nel CSV mancano queste colonne: {mancanti}")

    # Ordina per numero di riga, cosi' le linee seguono l'ordine della canzone.
    return df.sort_values("numero_riga").reset_index(drop=True)


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
    # split() spezza il testo in una lista di parole (separate da spazi).
    parole = testo.split()

    # parole[:numero_parole] prende solo le prime N; join le riunisce
    # in una stringa con uno spazio in mezzo.
    testo_troncato = " ".join(parole[:numero_parole])

    # Aggiungiamo i puntini di sospensione solo se abbiamo davvero
    # tagliato qualcosa (cioe' se la riga aveva piu' parole di quelle
    # mostrate).
    if len(parole) > numero_parole:
        testo_troncato += "..."

    return testo_troncato


def crea_grafico(df):
    """
    Disegna il grafico a linee dell'ironia e lo salva in PNG.

    Parametri:
        df (pandas.DataFrame): la tabella letta da carica_dati()
    """
    # plt.subplots crea due oggetti:
    #  - fig: la "figura", cioe' l'immagine intera
    #  - ax: gli "assi", cioe' l'area dove si disegna il grafico
    # figsize e' la dimensione in pollici (larghezza, altezza). Dato che ora
    # ogni verso ha una sua etichetta sull'asse x, la larghezza cresce con il
    # numero di versi (0.4 pollici a verso, minimo 12), altrimenti le
    # etichette si sovrapporrebbero. L'altezza e' maggiore per far stare
    # le etichette ruotate.
    larghezza = max(12, 0.4 * len(df))
    fig, ax = plt.subplots(figsize=(larghezza, 8))

    # --- Una linea per ogni raggio di contesto ---
    for raggio in [2, 1, 0]:
        stile = STILE_LINEE[raggio]
        ax.plot(
            df["numero_riga"],               # asse x: numero del verso
            df[f"p_ironia_r{raggio}"],       # asse y: probabilita' di ironia
            color=stile["colore"],
            linewidth=stile["spessore"],
            linestyle=stile["stile"],
            label=stile["etichetta"],        # testo mostrato nella legenda
            alpha=stile["alpha"]
        )

    # --- Linea orizzontale della soglia 0.5 ---
    # axhline disegna una linea orizzontale a un certo valore di y.
    ax.axhline(
        SOGLIA_IRONIA,
        color="gray",
        linestyle="--",
        linewidth=1,
        alpha=0.7,                           # alpha = trasparenza (0-1)
        label=f"Soglia {SOGLIA_IRONIA}",
    )

    # --- Titoli, etichette e aspetto degli assi ---
    # pad=40 lascia spazio sopra il grafico, dove mettiamo la legenda.
    ax.set_title(f"Andamento dell'ironia in «{NOME_CANZONE}» (irony-it)", fontsize=14, pad=40)
    ax.set_xlabel("Numero di riga della canzone")
    ax.set_ylabel("Probabilità di ironia")

    # --- Etichette dell'asse x: SOLO il numero di riga ---
    # Non mettiamo nessuna parte del testo della canzone (protetto da
    # copyright): sotto ogni tacca scriviamo solo il numero del verso.
    # Per sapere a quale verso corrisponde un numero si guarda l'elenco
    # che stampa il terminale (stampa_versi_piu_ironici), che resta sul
    # tuo computer e non finisce nel repository.
    etichette = [str(numero) for numero in df["numero_riga"]]

    # set_xticks decide in quali posizioni mettere le tacche dell'asse x
    # (una per verso); set_xticklabels decide cosa scrivere sotto ciascuna.
    # I numeri sono corti, quindi non serve ruotarli (rotation=0).
    ax.set_xticks(df["numero_riga"])
    ax.set_xticklabels(etichette, rotation=0, fontsize=8)

    # Un po' di margine a sinistra e a destra, per non attaccare le linee ai bordi.
    ax.set_xlim(df["numero_riga"].min() - 1, df["numero_riga"].max() + 1)

    # L'asse y va fissato attorno all'intervallo 0-1, essendo una probabilita':
    # senza questo limite, matplotlib adatterebbe la scala ai dati e le
    # differenze sembrerebbero piu' grandi di quello che sono. Il limite
    # superiore e' 1.05 (non 1) per lasciare un po' d'aria sopra al picco.
    ax.set_ylim(0, 1.05)

    ax.grid(alpha=0.3)                       # griglia leggera di sfondo

    # Legenda sopra il grafico (sotto il titolo), su una riga sola, cosi' non
    # copre le linee ne' le etichette dell'asse x.
    #  - loc="lower center": il punto della legenda che viene ancorato
    #  - bbox_to_anchor=(0.5, 1.0): dove ancorarlo, in frazioni dell'area
    #    del grafico (0.5 = centro orizzontale, 1.0 = bordo superiore)
    #  - ncol: quante colonne usare (4 voci = 4 colonne = una riga)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=4, frameon=False)

    # tight_layout sistema automaticamente i margini per non tagliare il testo.
    fig.tight_layout()

    # Salva il grafico. dpi=150 = buona risoluzione per la relazione.
    # bbox_inches="tight" include nell'immagine anche la legenda messa
    # fuori dall'area del grafico, che altrimenti verrebbe tagliata.
    fig.savefig(PERCORSO_PNG, dpi=150, bbox_inches="tight")

    # Apre il grafico in una finestra. Va messo DOPO savefig: dopo che
    # chiudi la finestra, matplotlib svuota la figura e un salvataggio
    # successivo produrrebbe un'immagine bianca. Lo script resta in pausa
    # finche' non chiudi la finestra.
    if MOSTRA_GRAFICO:
        plt.show()

    # Chiude la figura per liberare memoria (utile se la funzione viene
    # richiamata piu' volte).
    plt.close(fig)

# ---------------------------------------------------------------------
# FUNZIONE PRINCIPALE
# ---------------------------------------------------------------------

def main():
    df = carica_dati()
    print(f"Letti {len(df)} versi da {os.path.basename(PERCORSO_CSV)}")

    crea_grafico(df)
    print(f"Grafico salvato in: {PERCORSO_PNG}")


# ---------------------------------------------------------------------
# BLOCCO DI ESECUZIONE
# ---------------------------------------------------------------------
# Questa condizione e' vera solo quando lanci direttamente questo file
# (python fase3.1_grafico_ironia_Scrivile.py). Se un altro script lo
# importasse, main() non partirebbe da solo.
if __name__ == "__main__":
    main()