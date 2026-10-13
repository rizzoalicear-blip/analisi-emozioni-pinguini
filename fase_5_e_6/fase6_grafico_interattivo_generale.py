"""
grafico_interattivo.py - crea un grafico INTERATTIVO in un file HTML.

COSA OTTIENI
  Un file grafico_interattivo.html che apri con un doppio clic nel browser
  (Safari, Chrome, Firefox...). Il grafico è lo stesso di grafico_ascolti.py
  (anni sull'asse X, ascolti sull'asse Y, un colore per ogni emozione), ma:
    - passando il mouse sopra un pallino (o toccandolo, da telefono o tablet)
      compare una scheda con titolo, emozione, anno di uscita e ascolti ESATTI;
    - puoi zoomare (trascinando un rettangolo) e spostare il grafico;
      un doppio clic riporta alla vista iniziale;
    - cliccando un'emozione nella legenda la nascondi o la rimostri
      (un doppio clic su un'emozione mostra SOLO quella).

FUNZIONA SENZA INTERNET
  Con FILE_AUTONOMO = True (consigliato) il codice che fa funzionare il grafico viene
  scritto DENTRO il file HTML. Il file pesa circa 4-5 MB, ma si apre anche offline
  e puoi consegnarlo insieme al progetto: non serve altro.

DA DOVE PRENDE I DATI
  Solo da canzoni_finale.csv (colonne: titolo, emozione, data_uscita, ascolti).
  Nessun titolo è scritto dentro lo script.

SCALA LOGARITMICA
  Vale quello che ti ho spiegato per il grafico normale: con SCALA_LOG = True le
  distanze verticali misurano il RAPPORTO tra gli ascolti, non la differenza.
  Sotto il grafico compare una nota che lo ricorda a chi lo guarda.

LIBRERIE: pip install pandas numpy plotly
"""

import math
import webbrowser
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

# =============================================================================
# IMPOSTAZIONI - qui cambi quello che ti serve
# =============================================================================
# Percorsi: partono dalla posizione dello SCRIPT (fase_5/), non da dove lanci il comando
CARTELLA_SCRIPT = Path(__file__).resolve().parent
FILE_FINALE = CARTELLA_SCRIPT / "canzoni_finale.csv"
FILE_HTML = CARTELLA_SCRIPT / "grafico_interattivo.html"

SCALA_LOG = True          # True = asse Y logaritmico, False = asse Y lineare (normale)
MOSTRA_ETICHETTE = False  # True = scrive "Titolo (emozione)" anche accanto ai pallini
                          # (di solito con 20 canzoni risulta affollato: la scheda al
                          #  passaggio del mouse basta; prova pure a metterlo a True)
FILE_AUTONOMO = True      # True = il file HTML funziona anche SENZA internet (pesa ~4-5 MB)
                          # False = file leggerissimo, ma per aprirlo serve internet
APRI_NEL_BROWSER = True   # True = a fine script apre il grafico nel browser da solo

# Se più canzoni escono nello stesso anno le allarghiamo un po' a sinistra e a destra
# dell'anno, così i pallini non si sovrappongono. È SOLO uno spostamento grafico:
# nella scheda compare sempre l'anno giusto.
SPAZIO_ANNO = 0.3

# Un colore fisso per ognuna delle 8 emozioni di base del lessico NRC
# (gli stessi colori di grafico_ascolti.py)
COLORI_EMOZIONI = {
    "gioia": "#f2c600",      # giallo
    "fiducia": "#4caf50",    # verde
    "paura": "#00695c",      # verde scuro
    "sorpresa": "#4fc3f7",   # azzurro
    "tristezza": "#1e63c9",  # blu
    "disgusto": "#8e44ad",   # viola
    "rabbia": "#d32f2f",     # rosso
    "attesa": "#ff8f00",     # arancione
}
COLORE_ALTRE = "#7f7f7f"     # grigio, per emozioni non previste nell'elenco qui sopra


# =============================================================================
# LETTURA DEI DATI
# =============================================================================
def carica_dati():
    """Legge canzoni_finale.csv e restituisce solo le canzoni con anno e ascolti presenti."""
    # dtype=str: leggiamo la data come testo, poi ne prendiamo noi i primi 4 caratteri (l'anno)
    df = pd.read_csv(FILE_FINALE, encoding="utf-8-sig",
                     dtype={"emozione": str, "data_uscita": str})

    # data_uscita contiene già solo l'anno ("2017"); .str[:4] è una sicurezza nel caso
    # fosse rimasta qualche data completa ("2017-05-11")
    df["anno"] = pd.to_numeric(df["data_uscita"].str[:4], errors="coerce")
    df["ascolti"] = pd.to_numeric(df["ascolti"], errors="coerce")
    df["emozione"] = df["emozione"].fillna("n.d.")

    # Teniamo solo le righe con anno E ascolti: senza uno dei due non si può disegnare il pallino
    complete = df.dropna(subset=["anno", "ascolti"]).copy()
    for titolo in df.loc[~df.index.isin(complete.index), "titolo"]:
        print(f"Attenzione: '{titolo}' non è nel grafico (manca anno o ascolti)")

    complete["anno"] = complete["anno"].astype(int)
    return complete


def formatta_numero_italiano(numero):
    """Scrive un numero con il punto come separatore delle migliaia, all'italiana:
    171188119 -> '171.188.119'.
    f"{n:,}" mette le virgole (171,188,119), poi le sostituiamo con i punti."""
    return f"{int(numero):,}".replace(",", ".")


def prepara_dati(dati):
    """Aggiunge due colonne:
       x            = posizione orizzontale del pallino (l'anno, allargato se ci sono più
                      canzoni nello stesso anno)
       ascolti_testo = gli ascolti scritti per esteso, da mostrare nella scheda"""
    dati["x"] = dati["anno"].astype(float)
    for anno, gruppo in dati.groupby("anno"):
        n = len(gruppo)
        if n > 1:
            ordinate = gruppo.sort_values("ascolti").index          # dalla meno alla più ascoltata
            # np.linspace(-0.3, 0.3, 5) = 5 numeri equidistanti tra -0.3 e +0.3
            dati.loc[ordinate, "x"] = anno + np.linspace(-SPAZIO_ANNO, SPAZIO_ANNO, n)

    dati["ascolti_testo"] = dati["ascolti"].apply(formatta_numero_italiano)
    return dati


# =============================================================================
# IL GRAFICO INTERATTIVO
# =============================================================================
def crea_grafico(dati):
    fig = go.Figure()

    # ---- I pallini: un gruppo (una "traccia") per emozione, così la legenda è cliccabile ----
    for emozione, gruppo in dati.groupby("emozione"):
        colore = COLORI_EMOZIONI.get(emozione, COLORE_ALTRE)

        # "customdata" = i dati nascosti dietro ogni pallino, quelli che la scheda mostra.
        # Per ogni canzone una riga con 4 valori, che nella scheda richiamiamo come
        # %{customdata[0]} (titolo), [1] (emozione), [2] (anno), [3] (ascolti).
        dati_scheda = gruppo[["titolo", "emozione", "anno", "ascolti_testo"]].to_numpy()

        # Testo accanto al pallino (solo se MOSTRA_ETICHETTE = True)
        etichette = [f"{t} ({e})" for t, e in zip(gruppo["titolo"], gruppo["emozione"])]

        fig.add_trace(go.Scatter(
            x=gruppo["x"],
            y=gruppo["ascolti"],
            mode="markers+text" if MOSTRA_ETICHETTE else "markers",
            name=f"{emozione} ({len(gruppo)})",             # tra parentesi: quante canzoni
            text=etichette if MOSTRA_ETICHETTE else None,
            textposition="middle right",
            marker=dict(size=16, color=colore, line=dict(width=1, color="black")),
            customdata=dati_scheda,
            # La scheda che compare passando sul pallino. <b> = grassetto, <br> = a capo.
            # <extra></extra> toglie la scritta con il nome della traccia, che è superflua.
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Emozione: %{customdata[1]}<br>"
                "Anno di uscita: %{customdata[2]}<br>"
                "Ascolti: %{customdata[3]}"
                "<extra></extra>"
            ),
        ))

    # ---- Asse X: un segno per OGNI anno dal primo all'ultimo, anche quelli senza canzoni ----
    primo_anno = int(dati["anno"].min())
    ultimo_anno = int(dati["anno"].max())
    asse_x = dict(
        title="Anno di uscita",
        tickmode="array",
        tickvals=list(range(primo_anno, ultimo_anno + 1)),
        range=[primo_anno - 0.6, ultimo_anno + 0.6],          # un po' di margine ai lati
        gridcolor="rgba(0,0,0,0.12)",
    )

    # ---- Asse Y: lineare o logaritmico ----
    minimo, massimo = float(dati["ascolti"].min()), float(dati["ascolti"].max())
    if SCALA_LOG:
        asse_y = dict(
            title="Ascolti Spotify (scala logaritmica)",
            type="log",
            # ATTENZIONE: su un asse logaritmico plotly vuole gli estremi come LOGARITMO
            # in base 10 (es. 5 = 100.000, 6 = 1 milione), non come numeri normali
            range=[math.log10(minimo * 0.6), math.log10(massimo * 1.8)],
            tickformat="~s",         # numeri abbreviati: 1M, 2M, 500k...
            gridcolor="rgba(0,0,0,0.12)",
        )
    else:
        asse_y = dict(
            title="Ascolti Spotify",
            range=[0, massimo * 1.1],
            tickformat="~s",
            gridcolor="rgba(0,0,0,0.12)",
        )

    # ---- Nota sotto il grafico: chi lo guarda deve sapere come leggere la scala ----
    note = []
    if SCALA_LOG:
        note.append(dict(
            text=("Asse verticale logaritmico: distanze uguali = stesso rapporto tra gli ascolti "
                  "(non la stessa differenza)."),
            xref="paper", yref="paper", x=0.5, y=-0.2, showarrow=False,
            font=dict(size=12, color="dimgray"),
        ))

    fig.update_layout(
        title="Pinguini Tattici Nucleari: ascolti Spotify, anno di uscita ed emozione prevalente",
        xaxis=asse_x,
        yaxis=asse_y,
        legend=dict(title="Emozione (n. canzoni)"),
        hovermode="closest",          # la scheda compare per il pallino più vicino al mouse
        hoverlabel=dict(bgcolor="white", font_size=14),
        template="plotly_white",      # sfondo bianco e pulito
        height=750,
        margin=dict(b=110),           # spazio in basso per la nota
        annotations=note,
    )
    return fig


# =============================================================================
# PROGRAMMA PRINCIPALE
# =============================================================================
def main():
    dati = carica_dati()
    print(f"Canzoni nel grafico: {len(dati)}  (anni da {dati['anno'].min()} a {dati['anno'].max()})")
    dati = prepara_dati(dati)

    fig = crea_grafico(dati)

    # include_plotlyjs=True  -> il codice del grafico viene scritto DENTRO il file (funziona offline)
    # include_plotlyjs="cdn" -> il file è leggero ma al momento dell'apertura scarica il codice da internet
    fig.write_html(
        FILE_HTML,
        include_plotlyjs=True if FILE_AUTONOMO else "cdn",
        config={"displaylogo": False, "responsive": True},   # toglie il logo plotly, adatta alla finestra
    )
    peso_mb = Path(FILE_HTML).stat().st_size / (1024 * 1024)
    print(f"Grafico salvato in {FILE_HTML} ({peso_mb:.1f} MB)")

    if APRI_NEL_BROWSER:
        # as_uri() trasforma il percorso del file in un indirizzo che il browser capisce
        webbrowser.open(Path(FILE_HTML).resolve().as_uri())


if __name__ == "__main__":
    main()