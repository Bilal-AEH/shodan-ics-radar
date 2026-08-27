#!/usr/bin/env python3
"""
radar.py — Shodan ICS Radar, point d'entrée principal

Interroge l'API Shodan pour chaque protocole industriel défini dans config.yaml,
score les équipements détectés selon leur exposition et leur criticité,
et génère un rapport markdown structuré.

Usage :
    export SHODAN_API_KEY="votre_clé"
    python radar.py

Dépendances : shodan, pyyaml, jinja2
"""

import sys
import yaml

from queries import get_client, search_protocol
from scoring import score_all
from report import generate_report, save_report


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    print("[*] Chargement de la configuration...")
    try:
        config = load_config()
    except FileNotFoundError:
        print("[!] config.yaml introuvable. Vérifier le répertoire d'exécution.")
        sys.exit(1)

    print("[*] Connexion à l'API Shodan...")
    try:
        client = get_client()
    except EnvironmentError as e:
        print(f"[!] {e}")
        sys.exit(1)

    all_results = []
    max_results = config.get("output", {}).get("max_results_per_protocol", 50)

    for protocol in config.get("protocols", []):
        print(f"[*] Recherche : {protocol['name']} ({protocol['query']})...")
        try:
            results = search_protocol(client, protocol, max_results=max_results)
            scored = score_all(results, config)
            all_results.extend(scored)

            critiques = sum(1 for r in scored if r["level"] == "CRITIQUE")
            print(f"    → {len(results)} équipements trouvés, {critiques} CRITIQUE(S)")

        except RuntimeError as e:
            # Un protocole qui échoue est loggué et ignoré.
            # Un rapport partiel reste plus utile qu'un rapport absent.
            print(f"[!] {e} — protocole ignoré, suite de l'exécution")

    if not all_results:
        print("[!] Aucun résultat récupéré. Vérifier la clé API et les quotas.")
        sys.exit(1)

    print(f"\n[*] Génération du rapport ({len(all_results)} équipements scorés)...")
    rapport_path = config.get("output", {}).get("rapport_path", "rapport_ics.md")
    content = generate_report(all_results, config)
    save_report(content, rapport_path)

    # Résumé terminal
    nb_critique = sum(1 for r in all_results if r["level"] == "CRITIQUE")
    nb_eleve = sum(1 for r in all_results if r["level"] == "ÉLEVÉ")
    nb_honeypot = sum(1 for r in all_results if r.get("honeypot"))

    print(f"\n{'─' * 40}")
    print(f"  Équipements analysés : {len(all_results)}")
    print(f"  CRITIQUE             : {nb_critique}")
    print(f"  ÉLEVÉ                : {nb_eleve}")
    print(f"  Honeypots détectés   : {nb_honeypot}")
    print(f"  Rapport              : {rapport_path}")
    print(f"{'─' * 40}\n")


if __name__ == "__main__":
    main()
