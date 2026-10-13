"""
SCRIPT USA-E-GETTA: crea fase_2/eccezioni_lingua_hash.csv
==========================================================

Cosa fa:
- legge fase_2/eccezioni_lingua.csv (colonne: testo, lingua), che contiene
  righe di testo delle canzoni e quindi NON sta nel repository
- per ogni riga calcola la sua "impronta" (hash SHA-256)
- salva in fase_2/eccezioni_lingua_hash.csv solo impronta e lingua
  (colonne: hash, lingua): questo file NON contiene versi e puo' stare
  nel repository

Va lanciato una sola volta, dalla cartella principale del progetto.
"""

import csv        # legge e scrive i file CSV
import hashlib    # libreria standard di Python per calcolare le impronte (hash)
import os         # costruisce i percorsi dei file

# Cartella dove si trova questo script, cioe' la cartella principale del progetto.
CARTELLA_PRINCIPALE = os.path.dirname(os.path.abspath(__file__))

# File di input (con i versi) e di output (solo impronte).
PERCORSO_INPUT = os.path.join(CARTELLA_PRINCIPALE, "fase_2", "eccezioni_lingua.csv")
PERCORSO_OUTPUT = os.path.join(CARTELLA_PRINCIPALE, "fase_2", "eccezioni_lingua_hash.csv")


def calcola_impronta(testo):
    """
    Trasforma una riga di testo nella sua impronta SHA-256.

    Passaggi:
    - testo.encode("utf-8") trasforma il testo in "byte", cioe' numeri:
      l'algoritmo di hash lavora sui byte, non sulle lettere
    - hashlib.sha256(...) calcola l'impronta
    - .hexdigest() la restituisce come testo di 64 caratteri
      (cifre e lettere da a a f)

    Lo stesso testo da' sempre la stessa impronta; se cambia anche una
    sola lettera, l'impronta cambia completamente.
    """
    return hashlib.sha256(testo.encode("utf-8")).hexdigest()


def main():
    impronte = {}   # dizionario {impronta: lingua}

    with open(PERCORSO_INPUT, "r", encoding="utf-8", newline="") as file:
        # DictReader usa la prima riga ("testo,lingua") come nomi delle colonne.
        for riga in csv.DictReader(file):
            impronta = calcola_impronta(riga["testo"])
            impronte[impronta] = riga["lingua"]

    with open(PERCORSO_OUTPUT, "w", encoding="utf-8", newline="") as file_csv:
        scrittore = csv.writer(file_csv)
        scrittore.writerow(["hash", "lingua"])
        for impronta, lingua in impronte.items():
            scrittore.writerow([impronta, lingua])

    print(f"Fatto: {len(impronte)} impronte salvate in {PERCORSO_OUTPUT}")


if __name__ == "__main__":
    main()