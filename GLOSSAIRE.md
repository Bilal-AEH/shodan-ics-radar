# Glossaire -- shodan-ics-radar

## Concepts generaux

**Shodan** -- Moteur de recherche pour equipements connectes a Internet (automates, cameras, routeurs). Indexe les services reseau, pas les pages web.

**API (Application Programming Interface)** -- Interface permettant a un programme d appeler les fonctions d un autre. Le script appelle l API Shodan pour automatiser les recherches.

**Port reseau** -- Point d entree d un service sur une machine. Port 502 = Modbus, port 102 = Siemens S7. Un port ouvert sans protection = acces possible pour un attaquant.

**Banniere (banner)** -- Reponse d un equipement a une connexion entrante. Contient modele, fabricant, version firmware. Shodan les collecte a grande echelle lors de ses scans.

**ICS (Industrial Control Systems)** -- Systemes contrôlant des processus industriels physiques : usines, centrales electriques, reseaux d eau. Une compromission peut avoir des consequences reelles (pannes, accidents).

**SCADA** -- Sous-type d ICS. Supervision et contrôle a distance d infrastructures critiques depuis une interface centrale.

**PLC / Automate programmable** -- Ordinateur industriel pour contrôler des machines. Ex : Siemens S7, Allen-Bradley. Conçus avant Internet -- securite reseau inexistante ou quasi nulle.

**Honeypot** -- Systeme-leurre pour attirer les attaquants. Ce script detecte les signatures Conpot dans les bannieres pour exclure les faux resultats des statistiques.

**Variable d environnement** -- Variable systeme jamais ecrite dans le code source. La cle Shodan est lue via SHODAN_API_KEY pour rester hors du depot Git.

## Protocoles scannes

**Modbus (port 502)** -- Protocole industriel cree en 1979. Aucune authentification, aucun chiffrement. Lit et ecrit des registres sur des automates a distance. Encore massivement deploye.

**Siemens S7 (port 102)** -- Protocole proprieaire Siemens pour S7-300/400/1200/1500. Expose modele exact et firmware sans auth. Vecteur utilise par Stuxnet pour saboter des centrifugeuses iraniennes.

**BACnet (port 47808)** -- Gestion technique du batiment : climatisation, chauffage, eclairage, contrôle d acces. Impact variable selon le site expose.

**DNP3 (port 20000)** -- Infrastructures critiques : distribution electrique, eau, gaz. Conçu pour fiabilite, pas pour la securite. Risque eleve si expose a Internet.

**EtherNet/IP (port 44818)** -- Protocole Allen-Bradley / Rockwell. Base sur Ethernet standard -- exposition accidentelle frequente.

## Scoring

**Score de risque (0-10)** -- Calcule a partir du protocole de base, duree d exposition estimee, presence SSL/TLS (rare sur ICS), signatures honeypot.

| Niveau   | Score  | Signification                    |
|----------|--------|----------------------------------|
| CRITIQUE | >= 8.0 | Intervention immediate           |
| ELEVE    | >= 6.0 | Priorite haute                   |
| MOYEN    | >= 4.0 | A surveiller                     |
| FAIBLE   | < 4.0  | Risque limite                    |

## Technique

**YAML** -- Format de configuration lisible par l humain. Utilise pour config.yaml (cle API, protocoles, seuils de scoring).

**Jinja2** -- Moteur de templates Python. Genere le rapport Markdown dynamiquement depuis templates/rapport.md.j2.

**Markdown** -- Format de mise en forme leger : # = titre, **gras**, - liste. Lisible en texte brut et rendu sur GitHub.
