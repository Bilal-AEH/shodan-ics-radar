"""
queries.py — Interrogation de l'API Shodan

Ce module est la seule partie du projet qui communique avec l'extérieur.
Il contacte uniquement l'API Shodan — pas les équipements identifiés.
Tout ce qu'il retourne est ce que Shodan a déjà indexé publiquement.
"""

import shodan
import os
from datetime import datetime, timezone


def get_client() -> shodan.Shodan:
    """
    Instancie le client Shodan depuis la variable d'environnement.

    Lève une exception explicite si la clé est absente — mieux qu'une
    erreur d'authentification cryptique plusieurs appels plus tard.
    """
    api_key = os.getenv("SHODAN_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Variable SHODAN_API_KEY non définie.\n"
            "Exécuter : export SHODAN_API_KEY='votre_clé'"
        )
    return shodan.Shodan(api_key)


def search_protocol(client: shodan.Shodan, protocol_config: dict, max_results: int = 50) -> list:
    """
    Interroge Shodan pour un protocole industriel donné.

    Utilise search_cursor (générateur) plutôt que search (liste complète) :
    on arrête dès que max_results est atteint, sans payer de crédits API
    pour des résultats qu'on ne lirait pas.

    Paramètres
    ----------
    client          : instance shodan.Shodan authentifiée
    protocol_config : section d'un protocole depuis config.yaml
    max_results     : nombre maximum de résultats à récupérer

    Retour
    ------
    list[dict] : équipements avec métadonnées Shodan + durée d'exposition calculée
    """
    results = []

    try:
        cursor = client.search_cursor(protocol_config["query"])

        for result in cursor:
            if len(results) >= max_results:
                break

            # Calcul de la durée d'exposition depuis la première vue Shodan
            exposure_days = None
            timestamp = result.get("timestamp")
            if timestamp:
                try:
                    first_seen = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    exposure_days = (datetime.now(tz=timezone.utc) - first_seen).days
                except ValueError:
                    pass  # Date malformée — on continue sans ce champ

            equipment = {
                "ip": result.get("ip_str", "N/A"),
                "port": result.get("port"),
                "country": result.get("location", {}).get("country_name", "Inconnu"),
                "country_code": result.get("location", {}).get("country_code", "??"),
                "org": result.get("org", "Organisation inconnue"),
                "isp": result.get("isp", "ISP inconnu"),
                "banner": result.get("data", ""),
                "timestamp": timestamp,
                "exposure_days": exposure_days,
                "ssl": "ssl" in result,
                "protocol": protocol_config["name"],
                "risk_base": protocol_config["risk_base"],
                "hostnames": result.get("hostnames", []),
                # CVE référencées directement par Shodan dans ses résultats
                "vulns": list(result.get("vulns", {}).keys()),
            }

            results.append(equipment)

    except shodan.APIError as e:
        raise RuntimeError(f"Erreur Shodan sur '{protocol_config['name']}': {e}")

    return results
