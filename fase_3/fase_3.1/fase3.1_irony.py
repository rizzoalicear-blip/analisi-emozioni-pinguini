"""
FASE 3.1 - Rilevamento ironia in 'Scrivile Scemo' (caso studio qualitativo)
===========================================================================

COSA FA QUESTO SCRIPT, IN SINTESI
---------------------------------
1. Carica un modello di intelligenza artificiale (irony-it) che sa dire,
   per una frase italiana, quanto e' probabile che sia ironica.
2. Controlla che il modello funzioni, usando due frasi di prova (una
   ironica e una no): serve a capire quale delle due etichette del
   modello (LABEL_0 / LABEL_1) significa "ironico".
3. Legge dal CSV della fase 2 le righe della canzone "Scrivile Scemo".
4. Per ogni riga calcola la probabilita' di ironia in TRE modi:
      - raggio 0: guardando solo la riga da sola
      - raggio 1: guardando la riga + 1 riga prima + 1 riga dopo
      - raggio 2: guardando la riga + 2 righe prima + 2 righe dopo
   (stessa idea delle finestre di contesto che hai usato con NRC)
5. Stampa i risultati a schermo e li salva in un CSV.

PERCHE' SOLO UNA CANZONE
------------------------
E' un caso studio qualitativo: serve per discutere, nella relazione, il
limite dei metodi a lessico (NRC) davanti a linguaggio figurato o
iperbolico, non per analizzare tutto il corpus.

INSTALLAZIONE RICHIESTA
-----------------------
    pip install transformers torch pandas
Alla prima esecuzione il modello viene scaricato da Hugging Face (serve
internet); poi resta in cache e non viene riscaricato.
"""

# ---------------------------------------------------------------------
# IMPORT DELLE LIBRERIE
# ---------------------------------------------------------------------

# os: permette di costruire i percorsi dei file in modo corretto su
# qualsiasi sistema operativo (Windows usa "\", Mac/Linux usano "/").
import os

# pandas: libreria per lavorare con tabelle (qui la usiamo per leggere
# e salvare i CSV). Per convenzione si importa con il nome corto "pd".
import pandas as pd

# Dalla libreria transformers di Hugging Face prendiamo tre strumenti:
#  - AutoModelForSequenceClassification: carica un modello che assegna
#    un'etichetta a un testo (nel nostro caso: ironico / non ironico)
#  - AutoTokenizer: carica il "tokenizer", cioe' il pezzo che trasforma
#    il testo in numeri comprensibili dal modello (il modello non legge
#    le parole, legge numeri)
#  - pipeline: "scatola pronta" che mette insieme modello + tokenizer e
#    permette di classificare un testo con una sola chiamata
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline


# ---------------------------------------------------------------------
# CONFIGURAZIONE
# (tutte le cose che potresti voler cambiare stanno qui, in cima)
# ---------------------------------------------------------------------

# __file__ e' il percorso di questo script.
# os.path.abspath(...)  lo trasforma in percorso assoluto completo.
# os.path.dirname(...)  toglie il nome del file e lascia solo la cartella.
# Risultato: CARTELLA_SCRIPT = la cartella fase_3/fase_3.1/
CARTELLA_SCRIPT = os.path.dirname(os.path.abspath(__file__))

# Per trovare la radice del repository dobbiamo salire di due cartelle:
#   fase_3.1  ->  fase_3  ->  radice del progetto
# Ogni os.path.dirname(...) sale di un livello.
RADICE = os.path.dirname(os.path.dirname(CARTELLA_SCRIPT))

# Il CSV di input, creato in fase 2, si trova in fase_2/.
# os.path.join(...) unisce i pezzi di percorso con il separatore giusto.
PERCORSO_CSV_RIGHE = os.path.join(RADICE, "fase_2", "emozioni_per_riga.csv")

# Il CSV di output viene salvato accanto a questo script, in fase_3.1/.
PERCORSO_CSV_OUTPUT = os.path.join(CARTELLA_SCRIPT, "ironia_Scrivile_Scemo.csv")

# Titolo della canzone da analizzare: deve essere scritto ESATTAMENTE
# come compare nella colonna "canzone" del CSV. Cambialo per provare
# lo stesso esperimento su un'altra canzone.
NOME_CANZONE = "Scrivile Scemo"

# Raggi di contesto da provare. Il raggio e' quante righe prendere
# PRIMA e DOPO la riga analizzata:
#   0 = solo la riga, 1 = 1 prima + riga + 1 dopo, 2 = 2 prima + riga + 2 dopo
RAGGI_CONTESTO = [0, 1, 2]

# Nome del modello su Hugging Face: e' gia' addestrato a riconoscere
# l'ironia in italiano. Noi non lo addestriamo, lo usiamo e basta.
NOME_MODELLO = "aequa-tech/irony-it"

# Nome del tokenizer. Il modello irony-it e' costruito sopra AlBERTo
# (un BERT italiano), quindi per trasformare il testo in numeri
# bisogna usare il tokenizer di AlBERTo: il repository di irony-it
# contiene solo i pesi del modello, non un tokenizer suo.
NOME_TOKENIZER = "m-polignano-uniba/bert_uncased_L-12_H-768_A-12_italian_alb3rt0"

# Frasi per la calibrazione. Il modello risponde con etichette generiche
# ("LABEL_0" e "LABEL_1") senza dire quale sia "ironico". Per scoprirlo
# gli diamo una frase che sappiamo essere ironica (presa dalla scheda
# del modello) e una frase piatta e chiaramente non ironica, e vediamo
# quali etichette assegna.
FRASE_IRONICA = "Prendi una gioia. Ora posala, che non è tua."
FRASE_NON_IRONICA = "Oggi il treno per Milano parte alle otto e dieci dal binario due."


# ---------------------------------------------------------------------
# FUNZIONI
# ---------------------------------------------------------------------

def crea_classificatore():
    """
    Carica modello e tokenizer e li impacchetta in una pipeline,
    cioe' un oggetto che si usa come una funzione: gli dai un testo
    (o una lista di testi) e ti restituisce le probabilita' delle etichette.

    Restituisce:
        la pipeline di classificazione, pronta all'uso
    """
    # from_pretrained scarica (la prima volta) e carica in memoria i pesi
    # del modello. Il numero di etichette (2) il modello lo sa gia'.
    modello = AutoModelForSequenceClassification.from_pretrained(NOME_MODELLO)

    # Carica il tokenizer di AlBERTo.
    tokenizer = AutoTokenizer.from_pretrained(NOME_TOKENIZER)

    # Costruiamo la pipeline. Parametri:
    #  - "text-classification": il tipo di compito (assegnare etichette a testi)
    #  - model, tokenizer: i due pezzi appena caricati
    #  - top_k=None: restituisci il punteggio di TUTTE le etichette, non
    #    solo quella vincente. Cosi' possiamo leggere direttamente la
    #    probabilita' di "ironico", anche quando il modello sceglie "non ironico".
    #  - truncation=True: se un testo e' troppo lungo, taglialo invece
    #    di andare in errore (utile con le finestre di contesto, che
    #    uniscono piu' righe)
    #  - max_length=128: lunghezza massima in "token" (pezzetti di parola)
    return pipeline(
        "text-classification",
        model=modello,
        tokenizer=tokenizer,
        top_k=None,
        truncation=True,
        max_length=128,
    )


def trova_etichetta_ironica(classificatore):
    """
    Capisce quale etichetta (LABEL_0 o LABEL_1) corrisponde a "ironico".

    Come: classifica una frase ironica e una non ironica e guarda
    l'etichetta vincente di ciascuna. Se sono diverse, l'etichetta
    vincente della frase ironica e' quella che significa "ironico".
    Se invece sono uguali, qualcosa non va (il modello non distingue
    i due casi) e lo script si ferma, per non farti interpretare
    risultati sbagliati.

    Parametri:
        classificatore: la pipeline creata da crea_classificatore()

    Restituisce:
        una stringa, ad esempio "LABEL_1"
    """
    # Con top_k=None la pipeline restituisce, per ogni testo, una lista
    # di dizionari, uno per etichetta, ad esempio:
    #   [[{'label': 'LABEL_1', 'score': 0.93}, {'label': 'LABEL_0', 'score': 0.07}]]
    # (lista dentro lista perche' la pipeline e' pensata per piu' testi).
    # Il [0] finale prende la lista di etichette del nostro unico testo.
    out_iro = classificatore(FRASE_IRONICA)[0]
    out_neutra = classificatore(FRASE_NON_IRONICA)[0]

    # max(lista, key=...) trova l'elemento con il valore piu' alto di
    # "score". La parte "lambda o: o['score']" e' una mini-funzione
    # che dice a max() per quale campo confrontare i dizionari.
    top_iro = max(out_iro, key=lambda o: o["score"])
    top_neutra = max(out_neutra, key=lambda o: o["score"])

    print("=== Calibrazione ===")
    print(f"Frase ironica      -> {top_iro['label']} ({top_iro['score']:.3f})")
    print(f"Frase non ironica  -> {top_neutra['label']} ({top_neutra['score']:.3f})")

    # Se le due frasi hanno la stessa etichetta vincente, la mappatura
    # non e' affidabile: interrompiamo con un messaggio chiaro.
    if top_iro["label"] == top_neutra["label"]:
        raise RuntimeError(
            "Il modello assegna la stessa etichetta a una frase ironica e a una "
            "non ironica: la mappatura non e' affidabile. Controlla le frasi di "
            "calibrazione o il tokenizer."
        )

    print(f"Etichetta usata come 'ironico': {top_iro['label']}\n")
    return top_iro["label"]


def prob_ironia(output, etichetta_ironica):
    """
    Estrae da un output della pipeline la probabilita' dell'etichetta "ironico".

    Parametri:
        output: lista di dizionari {'label': ..., 'score': ...} per UN testo
        etichetta_ironica (str): l'etichetta che significa "ironico"

    Restituisce:
        un numero tra 0 e 1 (0 = per niente ironico, 1 = sicuramente ironico)
    """
    # La parte tra parentesi scorre i dizionari e tiene solo lo score
    # di quello con l'etichetta giusta; next() prende il primo (e unico)
    # risultato.
    return next(o["score"] for o in output if o["label"] == etichetta_ironica)


def costruisci_finestra(testi, i, raggio):
    """
    Costruisce il testo di contesto attorno alla riga numero i,
    unendo la riga con le sue vicine.

    Parametri:
        testi (list): lista di tutte le righe della canzone, in ordine
        i (int): posizione della riga centrale nella lista (parte da 0)
        raggio (int): quante righe prendere prima e dopo

    Restituisce:
        una stringa con le righe della finestra unite da uno spazio
    """
    # max(0, ...) evita di andare sotto la prima riga (per le prime righe
    # della canzone non esistono righe "prima").
    inizio = max(0, i - raggio)

    # min(len(testi), ...) evita di andare oltre l'ultima riga. Il +1 serve
    # perche' in Python l'estremo finale di una fetta [inizio:fine] e'
    # escluso: per includere la riga i + raggio dobbiamo spingerci di uno oltre.
    fine = min(len(testi), i + raggio + 1)

    # Prende la fetta di righe e le unisce in un unico testo.
    return " ".join(testi[inizio:fine])


# ---------------------------------------------------------------------
# FUNZIONE PRINCIPALE
# ---------------------------------------------------------------------

def main():
    # --- Passo 1: caricare il modello e calibrarlo ---
    print("Caricamento del modello irony-it...")
    classificatore = crea_classificatore()
    etichetta_ironica = trova_etichetta_ironica(classificatore)

    # --- Passo 2: leggere le righe della canzone ---
    # Legge tutto il CSV della fase 2 (contiene tutte le canzoni).
    df = pd.read_csv(PERCORSO_CSV_RIGHE)

    # Tiene solo le righe di "Scrivile Scemo" e le mette in ordine di riga.
    df = df[df["canzone"] == NOME_CANZONE].sort_values("numero_riga")

    # Elimina le righe senza testo. Una cella vuota nel CSV viene letta
    # da pandas come NaN (un "non-numero"), e passarla al modello
    # causerebbe un errore.
    df = df.dropna(subset=["testo"])

    # Elimina anche le righe fatte solo di spazi. astype(str) garantisce
    # che .str.strip() funzioni; strip() toglie gli spazi ai lati.
    df = df[df["testo"].astype(str).str.strip() != ""]

    # Dopo aver tolto delle righe, gli indici della tabella hanno "buchi"
    # (0, 1, 3, 4...). reset_index li rinumera da 0 senza buchi;
    # drop=True evita di tenere i vecchi indici come colonna in piu'.
    df = df.reset_index(drop=True)

    # Se non e' rimasto niente, quasi certamente il titolo non coincide
    # con quello del CSV: meglio fermarsi con un messaggio chiaro.
    if df.empty:
        raise RuntimeError(f"Nessuna riga trovata per '{NOME_CANZONE}' in {PERCORSO_CSV_RIGHE}")

    # Lista Python con il testo di tutte le righe, nell'ordine della canzone.
    testi = df["testo"].astype(str).tolist()

    # Tabella dei risultati: parte con due colonne copiate dal CSV.
    # Le colonne con le probabilita' verranno aggiunte nel ciclo qui sotto.
    risultati = df[["numero_riga", "testo"]].copy()

    # --- Passo 3: calcolare la probabilita' di ironia per ogni raggio ---
    for raggio in RAGGI_CONTESTO:
        # Costruisce, per ogni riga i, il testo della sua finestra di contesto.
        # (E' una "list comprehension": una lista costruita con un ciclo in una riga.)
        finestre = [costruisci_finestra(testi, i, raggio) for i in range(len(testi))]

        # Classifica tutte le finestre in un colpo solo. batch_size=16 vuol
        # dire che il modello le elabora a gruppi di 16, piu' veloce che una
        # alla volta. Restituisce una lista con un risultato per ogni finestra.
        output = classificatore(finestre, batch_size=16)

        # Per ogni risultato estrae la probabilita' di "ironico" e la arrotonda
        # a 4 decimali. Il risultato diventa una nuova colonna della tabella
        # (es. p_ironia_r0, p_ironia_r1, p_ironia_r2).
        risultati[f"p_ironia_r{raggio}"] = [
            round(prob_ironia(o, etichetta_ironica), 4) for o in output
        ]

    # --- Passo 4: salvare il CSV ---
    # index=False evita di scrivere nel file la colonna con i numeri di indice.
    # encoding="utf-8" conserva correttamente le lettere accentate.
    risultati.to_csv(PERCORSO_CSV_OUTPUT, index=False, encoding="utf-8")

    # --- Passo 5: stampare i risultati a schermo ---
    print(f"=== Risultati per '{NOME_CANZONE}' (probabilita' di ironia) ===")
    # iterrows() scorre la tabella una riga alla volta; "_" e' l'indice,
    # che qui non ci serve.
    for _, r in risultati.iterrows():
        # Costruisce una stringa tipo "r0=0.12 | r1=0.35 | r2=0.41".
        # :.2f significa "numero con 2 decimali".
        valori = " | ".join(f"r{k}={r[f'p_ironia_r{k}']:.2f}" for k in RAGGI_CONTESTO)
        print(f"{r['numero_riga']}: [{valori}] {r['testo']}")

    print(f"\nFatto. Creato il file: {PERCORSO_CSV_OUTPUT}")


# ---------------------------------------------------------------------
# BLOCCO DI ESECUZIONE
# ---------------------------------------------------------------------
# Questa condizione e' vera solo quando lanci direttamente questo file
# (python fase3.1_ironia_scrivile.py). Se invece un altro script lo
# importasse, main() non partirebbe da solo.
if __name__ == "__main__":
    main()