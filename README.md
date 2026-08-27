# Shodan ICS Radar

Il y a un moteur de recherche qui indexe les objets connectés à Internet. Pas les sites web — les objets. Les caméras, les routeurs, les serveurs industriels. Il s'appelle Shodan, et une recherche simple sur le port 502 retourne des milliers d'automates programmables exposés en ligne. Des automates qui pilotent des process physiques réels. Avec un protocole qui date de 1979, sans authentification.

Ce n'est pas une faille qu'on découvre. C'est quelque chose qui est là, visible, indexé, accessible à quiconque ouvre un navigateur. Ce qui m'a intrigué, ce n'est pas la technique — c'est la question que ça pose : comment est-ce qu'on se retrouve dans cette situation ? Et qu'est-ce qu'on fait avec cette information ?

Ce projet est la réponse que j'ai construite.

---

## Ce que fait le script

Il interroge l'API Shodan sur cinq protocoles industriels, récupère les métadonnées des équipements qui répondent, calcule un score de risque pour chacun, et génère un rapport structuré. Rien de plus — aucune connexion directe aux équipements, aucune interaction avec les systèmes identifiés. Tout ce que le script contacte, c'est l'API Shodan.

La distinction est importante. Shodan indexe ce qui est déjà visible depuis Internet. Observer ce que Shodan a vu, ce n'est pas scanner — c'est lire ce qui est public.

---

## Les fichiers

| Fichier | Ce qu'il fait |
|---|---|
| [`radar.py`](./radar.py) | Point d'entrée — lance l'analyse et orchestre les modules |
| [`queries.py`](./queries.py) | Envoie les requêtes à l'API Shodan, structure les résultats |
| [`scoring.py`](./scoring.py) | Calcule le score de risque de chaque équipement |
| [`report.py`](./report.py) | Génère le rapport markdown depuis les résultats scorés |
| [`config.yaml`](./config.yaml) | Protocoles ciblés, seuils, paramètres |
| [`PROTOCOLES.md`](./PROTOCOLES.md) | Ce que j'ai compris sur ces protocoles — et ce qu'ils exposent |
| [`TERRAIN.md`](./TERRAIN.md) | Ce que les résultats Shodan révèlent concrètement |

---

## Lancer l'analyse

```bash
pip install shodan pyyaml jinja2
export SHODAN_API_KEY="votre_clé"
python radar.py
```

Le rapport est généré dans `rapport_ics.md`.

---

## Les protocoles ciblés

| Protocole | Port | Pourquoi il est là |
|---|---|---|
| Modbus | 502 | Le plus répandu, le plus ancien, zéro authentification |
| Siemens S7 | 102 | Expose le modèle exact de l'automate sans mot de passe |
| BACnet | 47808 | Gestion de bâtiments — expose des métadonnées sur le site |
| DNP3 | 20000 | Électricité, eau, gaz — le niveau de criticité le plus élevé |
| EtherNet/IP | 44818 | Lignes de production Allen-Bradley / Rockwell |

---

## Comment le score est construit

Deux choses entrent en compte : le type de protocole (certains contrôlent des choses plus critiques que d'autres) et la durée d'exposition (un équipement visible depuis 18 mois a eu 18 mois pour être trouvé par quelqu'un d'autre). S'ajoutent des ajustements si des CVE sont référencées, si un certificat SSL est détecté, ou si la banner ressemble à un honeypot.

Le score final va de 0 à 10. Quatre niveaux : FAIBLE, MOYEN, ÉLEVÉ, CRITIQUE. Chaque facteur est détaillé dans le rapport — un score sans explication ne sert à rien.

---

| | |
|---|---|
| Langage | Python 3.11 |
| API | Shodan (plan académique) |
| Dépendances | `shodan` · `pyyaml` · `jinja2` |
