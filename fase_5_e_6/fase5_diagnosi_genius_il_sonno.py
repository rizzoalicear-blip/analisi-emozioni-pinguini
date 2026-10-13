"""
diagnosi_genius.py - mostra COSA risponde Genius quando cerchi UNA canzone.

A COSA SERVE
  Quando anni_genius.py dice "NON TROVATA" per una canzone, questo script ti fa vedere
  con i tuoi occhi i risultati che Genius restituisce, così capiamo dove sta il problema:
    - Genius non restituisce proprio quella canzone nella ricerca?
    - La restituisce, ma con un artista scritto in modo diverso?
    - La restituisce, ma senza data di uscita?

COME SI USA
  1. Lancia lo script: ti chiede il titolo della canzone.
  2. Scrivilo come sta in emozioni_per_canzone.csv e premi Invio.
  3. Copia e incolla qui in chat tutto quello che stampa.

NON MODIFICA NESSUN FILE: legge soltanto.

FILE NECESSARI: il .env con il token (GENIUS_ACCESS_TOKEN oppure GENIUS_TOKEN)
LIBRERIE: pip install requests python-dotenv
"""

import os
import re
import time
from difflib import SequenceMatcher

import requests
from dotenv import load_dotenv

ARTISTA = "Pinguini Tattici Nucleari"
URL_RICERCA = "https://api.genius.com/search"
URL_CANZONE = "https://api.genius.com/songs/{}"
PAUSA = 1.0   # secondi tra una richiesta e l'altra


def chiedi(url, headers, parametri=None):
    """Fa una richiesta a Genius e restituisce la parte 'response' del JSON."""
    risposta = requests.get(url, headers=headers, params=parametri, timeout=15)
    if risposta.status_code == 401:
        raise SystemExit("Genius ha rifiutato il token (errore 401): controlla il .env")
    risposta.raise_for_status()
    return risposta.json()["response"]


def main():
    load_dotenv()
    token = os.getenv("GENIUS_ACCESS_TOKEN") or os.getenv("GENIUS_TOKEN")
    if not token:
        raise SystemExit("Token non trovato nel .env")
    headers = {"Authorization": f"Bearer {token}"}

    titolo = input("Titolo della canzone (come nel tuo file): ").strip()
    senza_parentesi = re.sub(r"\(.*?\)", "", titolo).strip()

    # Proviamo tre modi diversi di fare la ricerca e vediamo cosa cambia
    ricerche = [
        f"{titolo} {ARTISTA}",            # titolo completo + artista
        f"{senza_parentesi} {ARTISTA}",   # titolo senza parentesi + artista
        titolo,                           # solo il titolo
    ]

    id_gia_visti = set()
    for query in ricerche:
        print("\n" + "=" * 70)
        print(f"RICERCA: {query!r}")
        print("=" * 70)
        hits = chiedi(URL_RICERCA, headers, {"q": query})["hits"]
        if not hits:
            print("  (Genius non ha restituito nessun risultato)")
        for numero, hit in enumerate(hits, start=1):
            canzone = hit["result"]
            print(f"  {numero}. titolo: {canzone['title']!r}")
            print(f"     artista: {canzone['primary_artist']['name']!r}   id: {canzone['id']}")
            print(f"     data nel risultato di ricerca: {canzone.get('release_date_components')}")

            # Per i risultati dell'artista giusto e con titolo simile al nostro,
            # chiediamo anche la "scheda" completa per vedere se lì c'è la data
            artista_ok = ARTISTA.lower() in canzone["primary_artist"]["name"].lower()
            simile = SequenceMatcher(None, titolo.lower(), canzone["title"].lower()).ratio() >= 0.5
            if artista_ok and simile and canzone["id"] not in id_gia_visti:
                id_gia_visti.add(canzone["id"])
                time.sleep(PAUSA)
                scheda = chiedi(URL_CANZONE.format(canzone["id"]), headers)["song"]
                print(f"     >> SCHEDA COMPLETA: release_date_components = "
                      f"{scheda.get('release_date_components')}")
                print(f"     >> SCHEDA COMPLETA: release_date            = {scheda.get('release_date')!r}")
                print(f"     >> SCHEDA COMPLETA: album                   = "
                      f"{(scheda.get('album') or {}).get('name')!r}")
        time.sleep(PAUSA)


if __name__ == "__main__":
    main()