# Les protocoles — ce que j'ai compris

Quand on parle de cybersécurité industrielle, on parle souvent de "systèmes critiques" sans vraiment expliquer ce que ça veut dire. Voilà ce que j'ai compris en creusant le sujet.

---

## Le contexte qui change tout

Un automate industriel ne ressemble pas à un serveur web. Il ne gère pas de sessions, il n'a pas d'interface de connexion, il n'envoie pas de cookies. Il fait une chose : communiquer avec d'autres équipements sur un réseau pour piloter un process physique. Une vanne. Un moteur. Un capteur de pression.

Ces systèmes ont été conçus pour fonctionner dans des réseaux fermés, physiquement isolés du reste du monde. Cette isolation — l'*air gap* — était leur seule protection. Personne n'avait prévu qu'un jour il faudrait accéder à ces automates depuis un bureau à 300 km, ou les intégrer aux logiciels de gestion de l'entreprise. Mais ça s'est passé quand même, progressivement, souvent sans que les équipes qui gèrent les machines et les équipes qui gèrent le réseau se parlent vraiment.

Ce qui reste, c'est une génération entière d'équipements qui n'ont aucun mécanisme de sécurité — parce qu'ils n'en avaient jamais eu besoin — et qui se retrouvent désormais accessibles depuis Internet.

---

## Modbus — Port 502

Modbus existe depuis 1979. C'est l'un des protocoles industriels les plus déployés au monde, et sa conception n'a pratiquement pas changé depuis sa création.

Il n'y a pas d'authentification. Pas de chiffrement. Pas de vérification de l'origine des commandes. N'importe qui qui connaît la structure d'une trame Modbus peut envoyer des commandes à un automate — lire des registres, écrire des valeurs. Le protocole ne fait pas la différence entre un opérateur légitime et quelqu'un qui enverrait les mêmes octets depuis l'autre bout du monde.

Ce qui est exposé sur le port 502, c'est ça : un accès direct à des registres qui correspondent à des grandeurs physiques réelles. Des températures, des pressions, des positions de vannes. Selon l'équipement, lire ces valeurs donne une image précise de ce qui se passe dans l'installation. Les modifier, c'est agir sur l'installation.

Shodan indexe environ 3 800 équipements actifs sur ce port.

---

## Siemens S7 — Port 102

Le protocole S7 est propriétaire Siemens, conçu pour les automates de la gamme S7. Ce qui le distingue des autres, c'est ce qu'il révèle sans qu'on lui demande.

Quand Shodan se connecte à un automate S7, il reçoit en réponse le modèle exact de l'équipement, sa référence matérielle, son numéro de série, la version de son firmware. Tout ça sans la moindre authentification. C'est la banner — la réponse que l'automate envoie naturellement quand quelqu'un initie une connexion.

Pour quelqu'un qui cherche, c'est un point de départ très précis. La référence du firmware, croisée avec les bases de CVE publiques, donne la liste des vulnérabilités connues sur cet équipement exact. Des bibliothèques open source comme Snap7 permettent de communiquer avec ces automates de façon programmatique, et leur documentation est publique.

Stuxnet — le cyberweapon découvert en 2010 qui ciblait le programme nucléaire iranien — fonctionnait exactement sur cette surface. Il lisait les valeurs de rotation des centrifugeuses S7, les modifiait, et renvoyait de fausses données aux opérateurs pour masquer ce qu'il faisait. Ce n'est pas de l'histoire ancienne : les automates S7 exposés aujourd'hui sur Shodan présentent la même architecture.

Shodan indexe environ 1 200 équipements actifs sur ce port. La durée d'exposition médiane observée est de 19 mois — la plus longue de tous les protocoles analysés.

---

## BACnet — Port 47808

BACnet s'occupe des bâtiments. Climatisation, chauffage, contrôle d'accès, ascenseurs, détection incendie. Ce qu'on appelle la GTB — Gestion Technique du Bâtiment.

Ce protocole a une particularité : il expose par défaut des métadonnées descriptives sur le site. Le nom de l'équipement, sa description, sa localisation. Ces champs font partie de la spécification — ce n'est pas un bug, c'est ainsi que BACnet est conçu. Dans un réseau interne, c'est pratique pour retrouver un équipement. Sur Internet, ça donne à quelqu'un qui cherche une idée précise de ce qu'il a en face, et parfois de l'endroit où c'est installé.

Ce qui rend BACnet intéressant à analyser, c'est la variété des déploiements. Un automate BACnet qui gère la ventilation d'un entrepôt logistique, c'est une chose. Un automate qui gère le contrôle d'accès ou le refroidissement d'un datacenter, c'en est une autre. L'outil ne peut pas distinguer les deux depuis Shodan — c'est une limite réelle du scoring.

Shodan indexe environ 8 200 équipements sur ce port. C'est le volume le plus important de tous les protocoles analysés.

---

## DNP3 — Port 20000

DNP3 a été développé pour les télécommunications entre sous-stations électriques. C'est le protocole des réseaux de distribution — électricité, eau, gaz. Quand on parle d'"infrastructures critiques", les systèmes DNP3 sont souvent ce qu'on a en tête.

Un équipement DNP3 exposé sur Internet est rarement un équipement de bureau. Statistiquement, c'est une sous-station, une station de pompage, un point de contrôle d'un réseau de distribution. Ce que ces systèmes gèrent a des conséquences directes sur des populations.

Il suffit de regarder ce qui s'est passé en Ukraine en 2015 et 2016 : deux coupures de courant coordonnées, qui impliquaient notamment la compromission de systèmes SCADA de distribution électrique utilisant des protocoles comparables. Ces événements sont documentés, analysés, publics. Ce n'est pas un scénario théorique.

Shodan indexe environ 2 100 équipements sur ce port. Volume plus faible que BACnet ou Modbus — mais presque tous les résultats scorent ÉLEVÉ ou CRITIQUE.

---

## EtherNet/IP — Port 44818

Protocole Allen-Bradley (Rockwell Automation). Lignes de production, process manufacturing, automation industrielle. Moins connu que Modbus ou S7, mais présent dans des environnements où les automates contrôlent des process en continu.

---

## Ce que tout ça a en commun

Ces protocoles n'ont pas été mal conçus. Ils ont été conçus pour un contexte précis — des réseaux fermés, des équipements qui ne parlent qu'à d'autres équipements du même site — et ils fonctionnent très bien dans ce contexte. Le problème, c'est que ce contexte a changé.

La supervision à distance est devenue une nécessité opérationnelle. L'intégration des données de production avec les systèmes d'information de l'entreprise aussi. Ces besoins ont créé des chemins réseau qui n'existaient pas avant — et qui n'ont pas toujours été sécurisés correctement, parfois parce que personne ne mesurait vraiment ce que ça ouvrait.

Ce n'est pas une question de négligence. C'est une question de deux mondes qui se sont rejoints plus vite que les pratiques n'ont évolué.
