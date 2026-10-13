# Analisi delle emozioni nei testi dei Pinguini Tattici Nucleari

Progetto universitario in Python che analizza i testi di 20 canzoni dei **Pinguini Tattici Nucleari** (le 10 più ascoltate e le 10 meno ascoltate su Spotify) per capire quale emozione prevale in ciascuna e come questa si lega all'anno di uscita e al numero di ascolti.

**Risultato finale:** un *grafico interattivo* in cui ogni pallino è una canzone: passandoci sopra con il mouse si vedono titolo, emozione prevalente, anno e ascolti esatti.
**Sito con tutti i grafici:** <https://rizzoalicear-blip.github.io/analisi-emozioni-pinguini/>

> **Per chi valuta il progetto:** il percorso più rapido è aprire `index.html` nel browser (basta un doppio clic, non serve internet), che raccoglie tutti i grafici con spiegazione, e leggere le sezioni [Metodo](#metodo), [Risultati](#risultati) e [Limiti](#limiti-dellanalisi). Per rieseguire tutto serve la sezione [Come eseguirlo](#come-eseguirlo).

---

## Indice

1. [Domande di ricerca](#domande-di-ricerca)
2. [Contenuto del repository](#contenuto-del-repository)
3. [Come eseguirlo](#come-eseguirlo)
4. [Metodo](#metodo)
5. [Risultati](#risultati)
6. [Conclusioni](#conclusioni)
7. [Limiti dell'analisi](#limiti-dellanalisi)
8. [Risorse esterne e crediti](#risorse-esterne-e-crediti)
9. [Librerie usate](#librerie-usate)
10. [Note legali](#note-legali)

---

## Domande di ricerca

- Gli ascolti di una canzone dipendono dall’emozione che suscitano?
- Le canzoni più ascoltate hanno emozioni diverse da quelle meno ascoltate?
- Come cambia il punteggio di un verso se si considera anche il contesto delle righe vicine?
- Il metodo a lessico e il modello Transformer danno risultati coerenti?

---

## Contenuto del repository
```
progetto_università/
├── .env.example                   <- esempio del file .env (senza token)
├── .gitignore                     <- file che NON vanno su GitHub (.env, testi, venv, ecc.)
├── fase_1/                     <- scaricare i testi delle canzoni
        ├── fase1_prova_api_genius.py
        ├── fase1_prova_api_genius_pulizia_spazi.py
        ├── fase1_tutte_le_canzoni.py
        ├── fase1_tutte_le_canzoni_pulite_punteggiatura.py
        ├── fase1_tutte_le_canzoni_pulite_punteggiatura_e_maiuscole.py
├── fase_2/                     <- analizzare i testi per derivare le emozioni
        ├── fase2_analisi_emozioni.py
        ├── eccezioni_lingua_hash.csv         <- impronte (hash) delle eccezioni di lingua, senza testo
        ├── fase2_analisi_emozioni_eccezioni_aggiunte.py
        ├── fase2_analisi_emozioni_eccezioni_e_spagnolo.py
        ├── fase2_emozioni_totali.py
        ├── emozioni_per_canzone.csv

├── fase_3/                     <- creare grafici dalla fase precedente
        ├── fase3_grafico_barre_totale_emozioni.py
        ├── grafico_temi_totale.png
        ├── fase3_grafico_barre_totale_per_canzone.py
        ├── grafico_temi_totale_per_canzone.png
        ├── fase3_grafico_barre_diviso.py
        ├── grafico_temi_top_bottom.png
        ├── fase3_mappa_di_calore.py
        ├── mappa_calore_emozioni.png
        ├── fase_3.1/                     <- analisi approfondita della canzone “Scrivile Scemo”
                ├── fase3.1_grafico_linee_Scrivile_scemo.py
                ├── andamento_Scrivile Scemo_top4.png
                ├── fase3.1_analisi_scrivile_contesto_1.py
                ├── fase3.1_analisi_scrivile_contesto_2.py
                ├── fase3.1_grafico_linee_Scrivile_contesto_1.py
                ├── andamento_Scrivile Scemo_top4_contesto_1.png
                ├── fase3.1_grafico_linee_Scrivile_contesto_2.py
                ├── andamento_Scrivile Scemo_top4_contesto_2.png
                ├── fase3.1_grafici_Scrivile_confronto_contesto.py
                ├── confronto_righe_Scrivile_Scemo_rabbia.png
                ├── differenza_righe_Scrivile_Scemo_rabbia.png
                ├── fase3.1_irony.py
                ├── fase3.1_grafico_irony.py
                ├── andamento_ironia_Scrivile_Scemo.png
├── fase_4/                     <- analisi con transformer
        ├── fase4_emozioni_transformer_scrivile.py
        ├── fase4_grafico_barre_transformer_scrivile.py
        ├── emozioni_transformer.csv
        ├── grafico_temi_totale_transformer.png
        ├── prova_lunghezza.py
        ├── prova_troncamento.py
        ├── risultati_troncamento.txt
├── fase_5_e_6/                     <- trovare data uscita e ascolti e confrontarli con grafico interattivo
        ├── fase5_prova_date_canzoni_api.py
        ├── fase5_date_canzoni_api.py
        ├── fase5_date_canzoni_api_il_sonno.py
        ├── fase5_diagnosi_genius_il_sonno.py
        ├── fase5_date_canzoni_api_il_sonno2.py
        ├── fase5_ascolti_canzoni.py
        ├── canzoni_finale.csv             <- tabella finale: titolo, emozione, anno, ascolti
        ├── fase6_grafico_interattivo_generale.py
        ├── grafico_interattivo.html       <- risultato finale, si apre nel browser
├── index.html                     <- html contenente i grafici
├── crea_hash_eccezioni.py         <- rigenera le impronte delle eccezioni di lingua (rif. fase_2/)
├── README.md                      <- questo documento
└── requirements.txt               <- librerie da installare
```
**Nota bene:** i file sono disposti in ordine di esecuzione. 

**File non inclusi nel repository:** testi_canzoni/ e i file: fase_2/emozioni_per_riga.csv, fase_3/fase_3.1/emozioni_Scrivile_Scemo_contesto_raggio1.csv, fase_3/fase_3.1/emozioni_Scrivile_Scemo_contesto_raggio2.csv, fase_3/fase_3.1/ironia_Scrivile_Scemo.csv e fase_2/eccezioni_lingua.csv contengono il testo dei versi, protetto da copyright, quindi non sono caricati. I testi si ottengono lanciando la fase 1 e i CSV si ricreano lanciando gli script della fase corrispondente, nell’ordine indicato in «Come eseguirlo». Anche il lessico NRC non è incluso (vedi «Lessico NRC»).

---

## Come eseguirlo

Il progetto è stato sviluppato con **Python 3.14** su macOS.

### 1. Preparare l'ambiente

```bash
# dalla cartella del progetto
python3 -m venv .venv
source .venv/bin/activate          # su Windows: .venv\Scripts\activate
python3 -m pip install -r requirements.txt
```

### 2. Token di Genius

Gli script che usano Genius hanno bisogno di un token personale (gratuito):

1. Vai su <https://genius.com/api-clients> e crea un'app per ottenere un *Client Access Token*.
2. Copia il file `.env.example` in un nuovo file chiamato `.env`.
3. Incolla il tuo token nel `.env`:

```
GENIUS_ACCESS_TOKEN=il_tuo_token_qui
```

Il file `.env` non è su GitHub di proposito: contiene un dato personale.

### 3. Lessico NRC

Il lessico NRC (versioni italiana e spagnola) **non si installa con pip** e non è incluso nel repository: vedi [Risorse esterne](#risorse-esterne-e-crediti) per scaricarlo e per sapere dove metterlo.

### 4. Ordine di esecuzione

| Fase | Cosa fa | Script | Risultato |
|---|---|---|---|
| 1 | Scarica e pulisce i testi da Genius | `fase1_tutte_le_canzoni_pulite_punteggiatura_e_maiuscole.py` | testi in `testi_canzoni/` (non inclusi nel repository) |
| 2 | Analizza le emozioni riga per riga | `fase2_analisi_emozioni_eccezioni_e_spagnolo.py` | `emozioni_per_riga.csv (non incluso nel repository per copyright)`|
| 2 | Aggrega il totale per canzone | `fase2_emozioni_totali.py` | `emozioni_per_canzone.csv` |
| 3 | Grafici sulle emozioni | `fase3_grafico_barre_totale_emozioni.py`, `fase3_grafico_barre_totale_per_canzone.py`, `fase3_grafico_barre_diviso.py`, `fase3_mappa_di_calore.py` | mappa di calore, grafici barre (vedi elenco in Metodo) |
| 3.1 | Caso studio "Scrivile Scemo" con contesto | `fase3.1_analisi_scrivile_contesto_1.py`, `fase3.1_analisi_scrivile_contesto_2.py`, `fase3.1_grafico_linee_Scrivile_scemo.py`, `fase3.1_grafico_linee_Scrivile_contesto_1.py`, `fase3.1_grafico_linee_Scrivile_contesto_2.py`, `fase3.1_grafici_Scrivile_confronto_contesto.py`, `fase3.1_irony.py`, `fase3.1_grafico_irony.py` | Grafici andamento emozioni Scrivile Scemo e analisi delle differenze + ironia |
| 4 | Confronto con modello Transformer | `fase4_emozioni_transformer_scrivile.py`, `fase4_grafico_barre_transformer_scrivile.py` | `emozioni_transformer.csv` e grafico |
| 4.1 | Verifica quanti token legge il modello Transformer (circa 128) e se l’emozione cambierebbe leggendo la fine della canzone (richiede i testi della fase 1) | `prova_lunghezza.py`, `prova_troncamento.py` | `risultati_troncamento.txt` |
| 5a | Anno di uscita (Genius) | `fase5_date_canzoni_api_il_sonno2.py` | colonna `data_uscita` di `canzoni_finale.csv` |
| 5b | Ascolti Spotify (kworb) | `fase5_ascolti_canzoni.py` | colonna `ascolti` di `canzoni_finale.csv` |
| 6 | Grafico interattivo | `fase6_grafico_interattivo_generale.py` | `grafico_interattivo.html` |

Le fasi 5a e 5b si possono lanciare in qualsiasi ordine: ciascuna legge i titoli e le emozioni da `emozioni_per_canzone.csv`, crea `canzoni_finale.csv` se non esiste e compila solo la propria colonna, senza toccare le altre. Al primo avvio i modelli Transformer della fase 3.1 (ironia) e della fase 4 (confronto delle emozioni) vengono scaricati da internet (vedi [Risorse esterne](#risorse-esterne-e-crediti)).

---

## Metodo

### 1. Download dei testi

I testi sono scaricati dall'API di **Genius** tramite la libreria `lyricsgenius`, usando il token personale, e salvati già puliti dalla punteggiatura e in minuscolo.

Criterio di selezione delle 20 canzoni: le 10 canzoni più ascoltate e le 10 meno ascoltate su Spotify (dati kworb.net), escludendo: i brani in featuring, le versioni strumentali/intro, e le versioni speciali (live, acustiche, edizione natalizia). Quando una canzone esclusa lasciava un "buco" in classifica, è stata ripescata la canzone successiva che rispettava i criteri.

### 2. Emozioni con il lessico NRC

Per ogni canzone il testo viene letto riga per riga. Di ogni riga la libreria `langdetect` riconosce la lingua (italiano, inglese o spagnolo), con un dizionario di eccezioni verificate a mano per le righe dove il rilevamento automatico sbagliava (tipicamente per nomi propri stranieri, righe brevi o ripetitive). Le parole vengono confrontate con la versione corrispondente del **NRC Emotion Lexicon (EmoLex)**, un lessico che associa ogni parola a 8 emozioni di base (rabbia, attesa, disgusto, paura, gioia, tristezza, sorpresa, fiducia). I punteggi di tutte le righe vengono sommati e l'**emozione prevalente** della canzone è quella con il punteggio più alto.

Dettagli che influenzano i risultati:

- le parole vuote (articoli, preposizioni, congiunzioni...) semplicemente non compaiono nel lessico NRC, quindi non contribuiscono a nessuna emozione — non serve escluderle a parte;
- i ritornelli ripetuti vengono contati a ogni ripetizione, non solo una volta: una riga che compare 10 volte nel testo pesa 10 volte nel totale della canzone;
- le parole non trovate nel lessico (nomi propri, slang, parole straniere non coperte) non contribuiscono a nessuna emozione: sono "invisibili" al conteggio;
- in caso di parità tra due o più emozioni, viene scelta la prima in ordine di colonna (rabbia, attesa, disgusto, paura, gioia, tristezza, sorpresa, fiducia) — non è un criterio neutro, va tenuto presente come limite quando il punteggio più alto è condiviso da più emozioni.

Casi particolari: sono stati rilevati durante l'analisi alcune frasi contenenti caratteri speciali (anche in alfabeto cirillico), che hanno reso necessaria l'introduzione di alcune frasi nella categoria "ECCEZIONI" per l'identificazione della lingua. Genius è noto per inserire deliberatamente questo tipo di caratteri "camuffati" nei testi come forma di watermark anti-copia (per rilevare chi ricopia i testi senza autorizzazione). 

Il file `emozioni_per_canzone.csv` ha una riga per canzone: il titolo, i punteggi numerici delle 8 emozioni (nell'ordine: rabbia, attesa, disgusto, paura, gioia, tristezza, sorpresa, fiducia) e, nell'ultima colonna, l'emozione prevalente. Esempio: `Pastello Bianco,1,13,1,1,6,7,3,5,attesa`.

**Eccezioni di lingua.** `langdetect` sbaglia la lingua di alcune righe (nomi propri stranieri, righe brevi o ripetitive). Per queste righe la lingua è stata verificata a mano e salvata in `fase_2/eccezioni_lingua_hash.csv`, che non contiene i versi ma solo l'impronta (hash SHA-256) di ogni riga e la lingua. Lo script della fase 2 lo legge in automatico. Come funziona l'impronta e quali sono i suoi limiti è spiegato nei [Limiti](#limiti-dellanalisi). `crea_hash_eccezioni.py` serve solo a chi vuole rigenerare il file partendo da un proprio `fase_2/eccezioni_lingua.csv` (colonne `testo` e `lingua`), non incluso perché contiene righe di testo delle canzoni.

**ECCEZIONE da tenere in considerazione:** la canzone Il sonno ed il furto storia di un coinquilino presenta 3 emozioni con punteggio massimo equivalente (12): rabbia, paura e tristezza. Lo script sceglie l'emozione prevalente con `idxmax`. Con due o più emozioni al punteggio massimo, `idxmax` prende la prima nell'ordine di `NOMI_EMOZIONI` (rabbia, attesa, disgusto, ...). Questa canzone è quindi etichettata rabbia solo perché rabbia viene per prima nell'elenco.

**Caso NRC spagnolo:** Nelle prime versioni dell’analisi le righe in spagnolo venivano contate con il lessico italiano e quindi non contribuivano a nessuna emozione. Dopo l’integrazione del lessico NRC spagnolo, l’emozione prevalente di Gigi cinque ottavi è cambiata da rabbia ad attesa.

### 3. Grafici

I quattro grafici creati in questa fase sono:

- **Barre - emozioni totali:** somma dei punteggi di ciascuna delle 8 emozioni su tutte le 20 canzoni (non solo dell’emozione prevalente).
- **Barre - emozioni totali per canzone:** mostra il numero di canzoni che ha quella indicata come emozione prevalente (serve anche per un confronto con il grafico prodotto nella fase 4).
- **Barre affiancate Top 10 vs Bottom 10:** confronto in percentuale (non in valore grezzo, per non favorire il gruppo con più testo) tra il profilo emotivo delle canzoni più ascoltate e quello delle meno ascoltate.
- **Mappa di calore (canzoni × 8 emozioni):** intensità di ciascuna emozione in ciascuna canzone, in un colpo d'occhio su tutto il corpus.

**Nota bene:** nel grafico a barre "emozioni totali" i punti dipendono dalla lunghezza dei testi e dai ritornelli ripetuti, quindi una canzone lunga pesa di più. È lo stesso motivo per cui per il confronto Top 10 / Bottom 10 è stato usato il punteggio percentuale. Il lessico non ha lo stesso numero di parole per ogni emozione. Per le emozioni con più parole nel lessico è più facile accumulare punti, quindi confrontare le altezze delle barre tra emozioni diverse va fatto con cautela.

#### 3.1. Scrivile Scemo: analisi con contesto

Caso studio su Scrivile Scemo (emozione prevalente: rabbia), motivato da un'osservazione fatta leggendo i risultati grezzi di un grafico, `andamento_Scrivile Scemo_top4.png`, dove sono mostrate le 4 emozioni prevalenti (riga per riga) della canzone studiata. Alcune righe (es. un verso con parole forti come sangue e lacrime) ricevono un punteggio di rabbia/paura/tristezza alto secondo il lessico, ma nel contesto della canzone il linguaggio è iperbolico — un limite noto dei metodi a conteggio di parole, che non colgono ironia o figure retoriche (vedi [Limiti](#limiti-dellanalisi)).

Per approfondire, il testo della canzone è stato ri-analizzato includendo nel conteggio di ogni riga anche le parole delle righe vicine (una finestra di contesto), con due ampiezze: ±1 riga e ±2 righe. Il confronto tra dato grezzo e le due versioni con contesto è stato fatto con:

- un grafico a linee che sovrappone le tre versioni riga per riga;
- un grafico a barre della differenza (contesto ±2 meno grezzo) per individuare i versi su cui il contesto incide di più;

In concreto, il punteggio di quella riga cambia includendo il contesto, nonostante l’emozione prevalente resti la rabbia. La distribuzione della rabbia cambia: alcune frasi che avevano punteggio 0, con contesto, raggiungono punteggio 3. Nei grafici di questa sezione l’asse orizzontale riporta il numero di riga e non il testo del verso»

Inoltre, per avere un ulteriore confronto, è stato utilizzato un modello Transformer, `irony-it`, per il riconoscimento dell'ironia, usato tramite la libreria `transformers`. È stato applicato al testo per capire se l'emozione trovata dal lessico (rabbia) è coerente con un tono ironico. Il risultato grafico mostra alcuni picchi di ironia (specialmente nella prima parte del testo), escludendola però da quel verso.

### 4. Confronto con un modello Transformer

Come verifica, le emozioni sono state stimate anche con pysentimiento (modelli Transformer già addestrati, uno per lingua), applicato a ogni canzone nel suo complesso invece che riga per riga (ma il modello ne legge solo l’inizio, vedi la nota sotto), con il modello della lingua della canzone. I modelli non hanno le stesse etichette: il modello italiano riconosce 4 emozioni (gioia, rabbia, tristezza, paura); il modello inglese ne riconosce 6 (gioia, rabbia, tristezza, paura, disgusto, sorpresa) più una categoria residua “others”; il modello spagnolo non è stato usato, perché nessuna canzone è stata analizzata come spagnola. Il confronto con NRC ha senso solo sulle emozioni in comune e, per ogni canzone, solo su quelle previste dal modello della sua lingua.

Con il modello Transformer l'emozione prevalente è rabbia in 12 canzoni su 20; con il lessico NRC è attesa in 13 canzoni su 20 e rabbia in 4 (tra cui Il sonno ed il furto (storia di un coinquilino), cfr ECCEZIONE in fase 2). Le etichette NRC attesa (13 canzoni) e fiducia (1 canzone) non hanno una controparte nel Transformer, che non le prevede: il confronto diretto tra i due metodi vale al massimo per le altre 6 canzoni (rabbia, gioia, disgusto). Tra queste 2 canzoni etichettate con rabbia corrispondono, le altre 2 no. Non corrispondono nemmeno la canzone etichettata con gioia (Me Want Marò Back, che col modello Transformer è stata classificata other) e quella con disgusto (Ringo Starr, classificata dal Transformer anger: il modello italiano non prevede il disgusto, quindi per questa canzone un riscontro era impossibile).

**Nota bene:** il modello non legge la canzone intera. I modelli di pysentimiento usati (italiano e inglese) elaborano al massimo circa 128 token per volta: il tokenizzatore dichiara 128 e, per il modello inglese, la configurazione ne ammette 130 (per quello italiano la configurazione indica 512, ma non è il limite effettivo). Lo script `prova_troncamento.py` (risultati in `fase_4/risultati_troncamento.txt`) lo verifica su tutte le canzoni: per ognuna le probabilità calcolate sul testo intero sono identiche a quelle calcolate sui soli primi 128 token (differenza massima 0,000). Tutte e 20 le canzoni superano i 128 token (da 166 token di *Rodger* a 634 di *Pula*, conteggiati senza i 2 token speciali), quindi per ognuna l'emozione del Transformer descrive solo la parte iniziale del testo: circa tre quarti di *Rodger* e circa un quinto di *Pula*. Il lessico NRC, invece, legge tutti i versi. Le canzoni sono state analizzate con il modello italiano, tranne *Me Want Marò Back* e *Django*, analizzate con quello inglese.

### 5. Anno di uscita e ascolti

Per avere i dati necessari al confronto si crea la tabella `canzoni_finale.csv`, con le colonne `titolo`, `emozione`, `data_uscita` e `ascolti`.

- **Anno di uscita.** Si interroga l'API di Genius: per ogni canzone si cerca "titolo + artista", si scartano i risultati di altri artisti (traduzioni, cover) e quelli con un titolo troppo diverso, e si legge la data di uscita del risultato migliore. Della data si **conserva solo l'anno**: per questo la colonna `data_uscita` contiene valori come `2017`. Il confronto dei titoli ignora maiuscole, accenti, punteggiatura e testo tra parentesi, con una piccola lista di eccezioni per un titolo scritto in modo diverso su Genius (Il sonno ed il furto (storia di un coinquilino)).
- **Ascolti.** Si scarica la pagina di **kworb.net** con le canzoni dell'artista e il numero totale di ascolti Spotify, e si associa a ogni canzone la riga con il titolo più simile. Se la stessa canzone compare più volte (versioni live, remix) si tiene la riga con più ascolti, cioè di norma la versione originale. Gli ascolti cambiano ogni giorno: i valori di questa tabella sono una fotografia scattata il **05/10/2026**.

### 6. Grafico interattivo

Il grafico finale (`grafico_interattivo.html`) è generato con la libreria **Plotly** e si apre in qualsiasi browser, anche senza internet. Mostra:

- **asse orizzontale:** gli anni, dal primo all'ultimo anno di uscita, compresi quelli senza canzoni;
- **asse verticale:** gli ascolti Spotify, in **scala logaritmica**;
- **colore del pallino:** l'emozione prevalente;
- **scheda al passaggio del mouse:** titolo, emozione, anno e ascolti esatti.

Si può zoomare trascinando un rettangolo, tornare alla vista iniziale con un doppio clic e nascondere un'emozione cliccandola nella legenda. Le canzoni dello stesso anno sono allargate un po' in orizzontale per non sovrapporsi: è solo un effetto grafico e nella scheda l'anno è sempre quello esatto.

**Come leggere la scala logaritmica.** Le canzoni più ascoltate hanno tra 75 e 171 milioni di ascolti, le meno ascoltate meno di 3 milioni. Su un asse normale le seconde sarebbero schiacciate in fondo e illeggibili. Nella scala logaritmica ogni tacca *moltiplica* invece di sommare: salire da 1 a 2 milioni occupa lo stesso spazio che da 100 a 200 milioni, perché in entrambi i casi gli ascolti raddoppiano. Quindi la distanza verticale tra due pallini indica *quante volte* uno è più ascoltato dell'altro (per esempio, *Ridere* ha circa 128 volte gli ascolti di *Pula*), non la differenza assoluta.

---

## Risultati

### Dati finali (`canzoni_finale.csv`)

Ascolti rilevati il 05/10/2026.

**Le 10 più ascoltate**

| Canzone | Emozione prevalente | Anno | Ascolti |
|---|---|---|---|
| Ridere | rabbia | 2020 | 171.188.119 |
| Pastello Bianco | attesa | 2020 | 169.837.369 |
| Giovani Wannabe | attesa | 2022 | 147.246.960 |
| Scrivile Scemo | rabbia | 2020 | 137.795.231 |
| Rubami la Notte | attesa | 2023 | 120.417.119 |
| Ricordi | attesa | 2022 | 114.677.234 |
| Ringo Starr | disgusto | 2020 | 107.140.657 |
| Scooby Doo | attesa | 2020 | 97.435.047 |
| Islanda | attesa | 2024 | 89.459.782 |
| La storia infinita | attesa | 2020 | 75.746.463 |

**Le 10 meno ascoltate**

| Canzone | Emozione prevalente | Anno | Ascolti |
|---|---|---|---|
| Me Want Marò Back | gioia | 2015 | 2.536.386 |
| 79 | attesa | 2017 | 2.267.225 |
| Sudowoodo | attesa | 2015 | 2.071.563 |
| Django | fiducia | 2015 | 1.773.425 |
| Il concorso musicale | attesa | 2017 | 1.699.785 |
| Gigi cinque ottavi | attesa | 2017 | 1.377.938 |
| In vento | attesa | 2014 | 1.357.143 |
| Pula | attesa | 2017 | 1.336.287 |
| Il sonno ed il furto (storia di un coinquilino) | rabbia | 2015 | 836.252 |
| Rodger | rabbia | 2015 | 824.220 |

**Nota bene:** Il sonno ed il furto (storia di un coinquilino) è un caso di parità tra due o più emozioni, dove viene scelta la prima in ordine di colonna (rabbia, attesa, disgusto, paura, gioia, tristezza, sorpresa, fiducia).

### Cosa si osserva

- **Un'emozione domina.** Attesa è l'emozione prevalente in 13 canzoni su 20 (7 delle più ascoltate e 6 delle meno ascoltate); rabbia in 4; gioia, fiducia e disgusto in una sola ciascuna. Le due emozioni principali compaiono in entrambi i gruppi, quindi con questi dati l'emozione prevalente non distingue le canzoni più ascoltate da quelle meno ascoltate.
- **L'anno di uscita separa nettamente i due gruppi.** Tutte le 10 più ascoltate sono uscite tra il 2020 e il 2024, mentre tutte le 10 meno ascoltate sono uscite tra il 2014 e il 2017.
- **Le scale sono molto diverse.** La più ascoltata (*Ridere*, circa 171 milioni) ha circa 208 volte gli ascolti della meno ascoltata (*Rodger*, circa 824 mila).

L’emozione quindi non sembra determinare la popolarità della canzone. La notorietà dei Pinguini Tattici Nucleari, legata anche alla loro partecipazione a Sanremo nel 2020, e la promozione di un singolo rispetto a un altro possono aver contribuito al numero di ascolti: sono fattori che in questo progetto non sono stati analizzati.

---

## Conclusioni

Risposte alle domande di ricerca, nei limiti del campione (20 canzoni scelte agli estremi, vedi [Limiti](#limiti-dellanalisi)):

- **Gli ascolti di una canzone dipendono dall'emozione che suscita?** Con questi dati non emerge una relazione tra emozione prevalente e ascolti.
- **Le canzoni più ascoltate hanno emozioni diverse da quelle meno ascoltate?** No: attesa è l'emozione prevalente in 7 delle più ascoltate e in 6 delle meno ascoltate, rabbia in 2 per gruppo; a separare i due gruppi è soprattutto l'anno di uscita.
- **Come cambia il punteggio di un verso se si considera anche il contesto delle righe vicine?** Nel caso studio di Scrivile Scemo il contesto cambia il punteggio di alcune righe (alcune passano da 0 a 3), ma l'emozione prevalente della canzone resta rabbia.
- **Il metodo a lessico e il modello Transformer danno risultati coerenti?** Confrontando i due metodi sono state riscontrate molte differenze nelle emozioni rilevate, tra quelle che entrambi analizzano. Il confronto va letto con cautela: il Transformer legge solo i primi 128 token di ogni canzone, il lessico NRC l'intero testo (vedi Limiti).

---

## Limiti dell'analisi

- **Campione piccolo e scelto agli estremi.** Le 20 canzoni sono le più e le meno ascoltate, non un campione casuale: i risultati descrivono questo gruppo e non si possono generalizzare a tutta la discografia.
- **Anno e ascolti sono intrecciati.** Le canzoni più vecchie e quelle più recenti sono finite in gruppi diversi: non si può attribuire la differenza di ascolti all'emozione, perché sono cambiati anche periodo di uscita, popolarità della band e altri fattori che qui non sono analizzati.
- **Lessico e traduzioni.** Le versioni italiana e spagnola del lessico NRC sono traduzioni automatiche dell'originale inglese: alcune possono essere sbagliate. Inoltre il metodo conta le parole e non ne coglie il contesto: ironia, metafore e sarcasmo possono ribaltare il senso di una frase (vedi il caso di Scrivile Scemo in 3.1). Gli stessi autori del lessico sconsigliano di trarre conclusioni su una singola frase dalle sole associazioni delle sue parole.
- **Squilibrio del lessico**: le emozioni non hanno lo stesso numero di parole nel NRC, quindi il predominio di attesa potrebbe essere in parte un artefatto del lessico.
- **Eccezioni di lingua.** Le eccezioni sono riconosciute tramite l’impronta del testo della riga: se Genius modifica un testo, o se la pulizia della fase 1 produce un risultato diverso, l’impronta non coincide e quella riga non viene corretta. In quel caso i punteggi possono differire leggermente da quelli riportati.
  - **Come funziona l'impronta (hash).** Un hash è un codice calcolato a partire da un testo con un algoritmo (qui SHA-256). Ha tre proprietà: lo stesso testo dà sempre lo stesso codice; se cambia anche un solo carattere, il codice cambia completamente; dal codice non si può ricavare il testo con un calcolo diretto. Esempio: il testo `ciao mondo` ha impronta `6c872dc1…ecd2`, mentre `ciao mondo!` (con un punto esclamativo in più) ha impronta `eea65ca3…bd4b`. Lo script calcola l'impronta di ogni riga di testo e controlla se è nell'elenco delle eccezioni: così riconosce le righe corrette a mano senza che i versi compaiano nel repository.
  - **Limiti dell'impronta.** (1) *Corrispondenza esatta:* basta una differenza minima di maiuscole, spazi o caratteri speciali perché l'impronta non coincida e la riga non venga riconosciuta; per questo l'analisi richiede testi identici a quelli usati qui. (2) *Non è una cifratura:* chi conosce già una canzone potrebbe provare a indovinare una riga e verificare se la sua impronta è nell'elenco; l'impronta impedisce di leggere i versi nel file, ma non è una protezione assoluta. (3) *Nessuna garanzia legale:* questa scelta riduce il rischio di riprodurre i testi nel repository, ma non è un parere giuridico sul diritto d'autore.
- **Un'emozione per canzone.** La scelta dell'emozione prevalente riassume ogni brano con una sola etichetta e nasconde le emozioni secondarie. Anche piccole differenze di punteggio possono cambiare l'etichetta, ed eventuali parità vengono risolte in modo arbitrario (vedi Metodo).
- **Contesto limitato.** L'analisi con finestra di contesto (±1/±2 righe) resta comunque un conteggio di parole, non una vera comprensione del testo: aiuta a "spalmare" il punteggio su più testo, ma non riconosce ironia o linguaggio figurato più di quanto non faccia il metodo riga per riga.
- **Modello dell'ironia.** `aequa-tech/irony-it` è stato valutato dai suoi autori sul test set di IronITA (tweet in italiano): su testi di canzoni lavora su un tipo di testo diverso da quello su cui è stato misurato, quindi i suoi risultati sull'ironia in Scrivile Scemo vanno letti con cautela.
- **Il Transformer legge solo l'inizio della canzone.** Il modello elabora circa 128 token per volta, quindi per ogni canzone considera solo la parte iniziale del testo, mentre il lessico NRC legge tutti i versi. I due metodi non confrontano le stesse porzioni di testo: parte delle differenze tra i loro risultati potrebbe dipendere da questo.
- **Etichette diverse per lingua.** I modelli Transformer di lingue diverse prevedono insiemi di emozioni diversi (4 per l’italiano, 6 più “others” per l’inglese): lo stesso brano può ricevere un’etichetta diversa a seconda della lingua scelta, e alcune emozioni NRC non possono mai coincidere. Per Me Want Marò Back il modello italiano darebbe gioia, la stessa etichetta di NRC, mentre quello inglese dà “others”. Questo caso mostra bene quanto il confronto dipenda dalla lingua scelta.
- **Date da Genius.** L'anno è quello registrato su Genius, che può non coincidere con la data di uscita ufficiale del singolo o dell'album (in questo caso sono risultate corrette da un'analisi manuale).
- **Ascolti.** Sono il totale Spotify riportato da kworb.net, fotografato in un giorno preciso (05/10/2026); non sono definitivi e cambiano ogni giorno.

---

## Risorse esterne e crediti

### Lessico NRC Emotion Lexicon (EmoLex), versioni italiana e spagnola

- **Cos'è:** lessico che associa le parole a 8 emozioni di base e a 2 polarità. Le versioni in altre lingue sono traduzioni automatiche dell'originale inglese.
- **Dove scaricarlo:** <http://saifmohammad.com/WebPages/NRC-Emotion-Lexicon.htm>
- **File usati:** `Italian-NRC-EmoLex.txt`; `Spanish-NRC-EmoLex.txt`
- **Dove metterli:** `progetto_università/fase_2/`
- **Uso:** gratuito per la ricerca. I file **non sono inclusi** in questo repository, in linea con i termini d'uso degli autori.

> Questo progetto usa il NRC Emotion Lexicon, creato da Saif Mohammad e Peter Turney al National Research Council Canada.

Citazione: Saif Mohammad e Peter Turney, *Crowdsourcing a Word-Emotion Association Lexicon*, Computational Intelligence, 29(3), 436-465, 2013.

### Modello Transformer per il confronto (pysentimiento)

Il modello per il confronto delle emozioni (`pysentimiento`) non è incluso: viene scaricato automaticamente da Hugging Face la prima volta che si esegue lo script di confronto, quindi la prima esecuzione richiede internet. Task: Emotion Classification; lingue usate: italiano e inglese. È stato utilizzato il task emotion di Pysentimiento, con i modelli specifici per italiano, inglese e spagnolo.

### Modello Transformer per l'ironia (aequa-tech/irony-it)

Il modello per il riconoscimento dell'ironia della fase 3.1 è `aequa-tech/irony-it`, un modello italiano (una versione di AlBERTo) addestrato per riconoscere l'ironia. Non è incluso: viene scaricato automaticamente da Hugging Face alla prima esecuzione, quindi serve internet. Pagina del modello: <https://huggingface.co/aequa-tech/irony-it>.

### Altre fonti

- **Genius** (<https://genius.com>): testi e date di uscita, tramite l'API ufficiale e un token personale.
- **kworb.net** (<https://kworb.net>): totale degli ascolti Spotify delle canzoni dell'artista.

---

## Librerie usate

Installabili tutte insieme con `python3 -m pip install -r requirements.txt`.

| Libreria | A cosa serve nel progetto |
|---|---|
| `lyricsgenius` | collega Python a Genius e scarica i testi delle canzoni (fase 1) |
| `python-dotenv` | legge il token di Genius dal file `.env` invece di scriverlo nel codice |
| `langdetect` | riconosce la lingua di ogni riga del testo (italiano, inglese, spagnolo) |
| `pandas` | gestisce le tabelle: legge e scrive i CSV e la tabella HTML di kworb |
| `pysentimiento` | modello Transformer già addestrato per stimare le emozioni, usato per il confronto |
| `matplotlib` | disegna i grafici della fase 3 (linee, barre) |
| `seaborn` | disegna la mappa di calore, appoggiandosi a matplotlib |
| `numpy` | calcoli numerici (barre affiancate; disposizione dei pallini nel grafico interattivo) |
| `transformers` | libreria di Hugging Face per usare modelli già addestrati: serve per il modello `aequa-tech/irony-it` (ironia, fase 3.1) |
| `torch` | motore che esegue il modello Transformer di pysentimiento e modello irony-it |
| `requests` | fa le richieste web: API di Genius (anni) e download della pagina di kworb (ascolti) |
| `lxml` | permette a pandas di leggere le tabelle HTML di kworb |
| `plotly` | crea il grafico interattivo e lo salva come file .html |

---

## Note legali

- I testi delle canzoni sono protetti da copyright e non sono inclusi nel repository: gli script li scaricano da Genius con un token personale.
- Il lessico NRC è usato secondo i termini degli autori (gratuito per la ricerca, con citazione) e non è ridistribuito.
- Il progetto ha finalità didattiche.