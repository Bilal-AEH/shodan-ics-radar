"""
report.py — Génération du rapport markdown

Utilise Jinja2 pour séparer la logique de présentation du code Python.
Le template dans templates/rapport.md.j2 peut être modifié sans toucher
à ce fichier — utile pour adapter le format à différents destinataires.
"""

import os
from collections import Counter
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


def generate_report(all_results: list, config: dict) -> str:
    """
    Génère le rapport markdown à partir des résultats scorés.

    Calcule les statistiques globales nécessaires au résumé exécutif,
    puis délègue le rendu au template Jinja2.
    """
    total = len(all_results)
    critiques = [r for r in all_results if r["level"] == "CRITIQUE"]
    eleves = [r for r in all_results if r["level"] == "ÉLEVÉ"]
    honeypots = [r for r in all_results if r.get("honeypot")]

    # Top 10 pays par nombre d'équipements exposés
    countries = Counter(r["country"] for r in all_results)
    top_countries = countries.most_common(10)

    # Répartition par protocole
    protocols = Counter(r["protocol"] for r in all_results)

    context = {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "total": total,
        "critiques": critiques,
        "eleves": eleves,
        "honeypots": honeypots,
        "top_countries": top_countries,
        "protocols": dict(protocols),
        "all_results": all_results,
        "config": config,
    }

    env = Environment(
        loader=FileSystemLoader("templates"),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("rapport.md.j2")
    return template.render(**context)


def save_report(content: str, path: str) -> None:
    """Écrit le rapport sur disque. Crée le répertoire parent si nécessaire."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[✓] Rapport généré : {path}")
