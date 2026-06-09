#!/usr/bin/env python3
"""
Diagnostic de l'ecran "Claude Code Usage".

Le moniteur masque les erreurs de recuperation des donnees Claude (elles sont
juste loguees en warning, et l'ecran affiche 0 / vide). Ce script reproduit
l'appel et affiche TOUT : chemin des identifiants, validite du token, et la
reponse brute de l'API. A lancer depuis le dossier du projet :

    python windows\\check-claude.py
"""

import json
import os
from datetime import datetime
from pathlib import Path

CREDENTIALS_PATH = Path(
    os.environ.get("CLAUDE_CREDENTIALS", Path.home() / ".claude" / ".credentials.json")
)
USAGE_API_URL = "https://api.anthropic.com/api/oauth/usage"


def main() -> int:
    print("=" * 60)
    print(" Diagnostic ecran Claude Code Usage")
    print("=" * 60)
    print(f"Chemin des identifiants : {CREDENTIALS_PATH}")
    print(f"  variable CLAUDE_CREDENTIALS : {os.environ.get('CLAUDE_CREDENTIALS', '(non definie)')}")
    print(f"  le fichier existe ?         : {CREDENTIALS_PATH.exists()}")

    if not CREDENTIALS_PATH.exists():
        print("\n[X] Fichier d'identifiants INTROUVABLE.")
        print("    -> Etes-vous connecte a Claude Code sur CE PC Windows ?")
        print("       Installez Claude Code et lancez `claude` pour vous connecter,")
        print("       ce qui creera le fichier .credentials.json.")
        print("    -> Sinon, definissez la variable CLAUDE_CREDENTIALS vers le bon fichier.")
        return 1

    # Lecture du token
    try:
        creds = json.loads(CREDENTIALS_PATH.read_text(encoding="utf-8"))
        oauth = creds["claudeAiOauth"]
        token = oauth["accessToken"]
        print(f"\n[OK] accessToken trouve (longueur {len(token)}).")
        exp = oauth.get("expiresAt")
        if exp:
            # expiresAt est en millisecondes
            exp_dt = datetime.fromtimestamp(exp / 1000)
            now = datetime.now()
            etat = "EXPIRE" if exp_dt < now else "valide"
            print(f"     expiration : {exp_dt}  ({etat}, maintenant {now})")
            if exp_dt < now:
                print("     -> Le token est EXPIRE. Lancez `claude` sur ce PC pour le rafraichir.")
    except Exception as e:
        print(f"\n[X] Impossible de lire le token : {e}")
        print("    Structure attendue : claudeAiOauth.accessToken")
        return 1

    # Appel API
    try:
        import requests
    except ImportError:
        print("\n[X] Module 'requests' manquant. Lancez d'abord windows\\install-deps.bat")
        return 1

    print(f"\nAppel : GET {USAGE_API_URL}")
    try:
        resp = requests.get(
            USAGE_API_URL,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        print(f"  Reponse HTTP : {resp.status_code}")
        body = resp.text
        print("  Corps :")
        print("  " + (body[:2000] if body else "(vide)"))
        resp.raise_for_status()
        print("\n[OK] L'API renvoie des donnees. L'ecran Claude devrait s'afficher.")
        return 0
    except Exception as e:
        print(f"\n[X] Echec de l'appel API : {e}")
        print("    - HTTP 401  -> token invalide/expire : relancez `claude` pour vous reconnecter.")
        print("    - timeout / erreur reseau -> verifiez la connexion / un proxy / pare-feu.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
