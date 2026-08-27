"""
scoring.py — Calcul du score de risque composite

Le score (0–10) combine deux dimensions principales :
- Risque intrinsèque du protocole (défini dans config.yaml)
- Durée d'exposition sur Internet (calculée depuis le timestamp Shodan)

Et trois ajustements :
- SSL/TLS détecté → réduction (tentative de protection)
- Signatures honeypot → réduction (équipement probablement factice)
- CVE référencées → augmentation (vulnérabilités connues et publiques)

Chaque facteur est retourné dans le résultat final pour que le rapport
puisse expliquer le score — une note sans justification n'a pas de valeur
opérationnelle pour l'équipe qui reçoit le rapport.
"""

import re


# Signatures connues de honeypots industriels.
# Conpot est le plus répandu : il émule des équipements Modbus, S7 et BACnet
# pour attirer les attaquants et les observer. Les identifier réduit les
# faux positifs — on préfère sous-évaluer le risque d'un honeypot que
# surévaluer le risque d'un équipement réel.
HONEYPOT_SIGNATURES = [
    r"conpot",
    r"ICS/SCADA Honeypot",
    r"HoneyD",
    r"OpenPLC.*test",
]

# Compilation une seule fois au chargement du module — pas à chaque appel
HONEYPOT_PATTERNS = [re.compile(sig, re.IGNORECASE) for sig in HONEYPOT_SIGNATURES]


def is_honeypot(banner: str) -> bool:
    """Détecte les honeypots industriels à partir de leur banner protocolaire."""
    return any(pattern.search(banner) for pattern in HONEYPOT_PATTERNS)


def calculate_risk(equipment: dict, config: dict) -> dict:
    """
    Calcule le score de risque pour un équipement et retourne un dict enrichi.

    Le score part du risque intrinsèque du protocole, puis est ajusté
    selon les facteurs détaillés en en-tête de module.
    Score final borné entre 0 et 10.
    """
    score_cfg = config.get("scoring", {})
    base_score = float(equipment.get("risk_base", 5))

    # Bonus d'exposition : progressif jusqu'à +2 points, normalisé sur 365 jours.
    # Au-delà d'un an, le risque d'avoir été découvert ne croît plus de façon
    # significativement linéaire — on plafonne la normalisation.
    exposure_days = equipment.get("exposure_days")
    exposure_bonus = 0.0
    if exposure_days is not None:
        weight = score_cfg.get("exposure_weight", 0.3)
        normalized = min(exposure_days / 365.0, 1.0)
        exposure_bonus = normalized * 2.0 * weight

    # Réduction SSL : l'équipement expose au moins un certificat.
    # Rare sur les ICS, mais signale une tentative de sécurisation.
    ssl_discount = score_cfg.get("ssl_discount", 1.5) if equipment.get("ssl") else 0.0

    # Réduction honeypot : probable leurre, pas un équipement de production réel.
    banner = equipment.get("banner", "")
    honeypot = is_honeypot(banner)
    honeypot_discount = score_cfg.get("honeypot_discount", 3.0) if honeypot else 0.0

    # Bonus CVE : chaque CVE connue référencée par Shodan ajoute 0.3 point.
    # Plafonné à +1.5 — une liste de CVE ne change pas la nature du risque,
    # elle l'aggrave marginalement.
    cve_bonus = min(len(equipment.get("vulns", [])) * 0.3, 1.5)

    raw = base_score + exposure_bonus + cve_bonus - ssl_discount - honeypot_discount
    final_score = round(max(0.0, min(10.0, raw)), 1)

    # Niveau qualitatif dérivé des seuils définis dans config.yaml
    thresholds = score_cfg.get("thresholds", {})
    if final_score >= thresholds.get("critique", 8.0):
        level = "CRITIQUE"
    elif final_score >= thresholds.get("eleve", 6.0):
        level = "ÉLEVÉ"
    elif final_score >= thresholds.get("moyen", 4.0):
        level = "MOYEN"
    else:
        level = "FAIBLE"

    return {
        **equipment,
        "score": final_score,
        "level": level,
        "honeypot": honeypot,
        # Facteurs détaillés — présents dans le rapport pour expliquer le score
        "exposure_bonus": round(exposure_bonus, 2),
        "ssl_discount": round(ssl_discount, 2),
        "honeypot_discount": round(honeypot_discount, 2),
        "cve_bonus": round(cve_bonus, 2),
    }


def score_all(results: list, config: dict) -> list:
    """
    Applique calculate_risk à tous les équipements.
    Retourne la liste triée par score décroissant.
    Les honeypots sont conservés — marqués dans le rapport, pas supprimés.
    """
    scored = [calculate_risk(eq, config) for eq in results]
    return sorted(scored, key=lambda x: x["score"], reverse=True)
