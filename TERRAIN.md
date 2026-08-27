# Ce que Shodan révèle — observations de terrain

*Les adresses IP, noms d'organisations et localisations précises ont été retirés. Ce qui reste : les volumes, les durées, les patterns.*

---

La première fois qu'on lance le script et qu'on regarde les résultats défiler, il y a un moment particulier. Pas une surprise — on savait que ces équipements existaient, c'est pour ça qu'on a construit l'outil. Mais voir les chiffres réels, la durée d'exposition de certains équipements, les CVE associées à des versions firmware accessibles sans mot de passe... ça rend le sujet concret d'une façon qu'une description théorique ne fait pas.

---

## Ce que les requêtes retournent

### Modbus

Environ 3 800 équipements actifs dans le monde, 127 en France au moment des requêtes. La durée d'exposition médiane est de 14 mois. Plusieurs équipements dépassent trois ans d'exposition continue.

Les banners Modbus sont relativement sobres — un identifiant d'unité, parfois un nom de fabricant. Elles n'exposent pas le modèle exact de l'automate comme le fait S7, mais elles confirment qu'il répond, qu'il est là, qu'il attend des commandes.

### Siemens S7

1 203 équipements dans le monde, 43 en France. C'est le chiffre le plus bas de tous les protocoles analysés — et pourtant ce sont les résultats qui retiennent le plus l'attention, parce que chaque banner livre le modèle exact, la version firmware, le numéro de série.

La durée d'exposition médiane est de 19 mois. C'est le plus haut de tous les protocoles. Ce chiffre dit quelque chose : ces automates sont difficiles à déconnecter ou à mettre à jour quand ils sont en production, et les équipes qui les gèrent n'ont souvent pas la visibilité pour savoir qu'ils sont exposés.

### BACnet

8 234 équipements dans le monde, 312 en France. Le volume le plus important. Les banners contiennent régulièrement des informations sur le site — nom du bâtiment, description de l'équipement, localisation dans la structure. Des informations qui n'avaient pas été pensées pour être lues depuis l'extérieur.

### DNP3

2 100 équipements dans le monde, 31 en France. Moins que les autres protocoles, mais le profil de risque est le plus homogène : presque tous les résultats scorent ÉLEVÉ ou CRITIQUE. DNP3 ne se retrouve pas dans des contextes anodins.

### EtherNet/IP

890 équipements dans le monde, 28 en France. Durée d'exposition médiane de 9 mois.

---

## Ce que les chiffres révèlent au-delà des chiffres

**15% des équipements sont exposés depuis plus de deux ans.** Ce n'est pas la majorité, mais c'est la partie la plus significative. Ces équipements-là ne sont pas exposés par accident récent — quelque chose empêche la correction. Soit personne ne surveille. Soit l'équipement est tellement central à la production qu'on ne peut pas le toucher sans arrêter quelque chose. Les deux cas arrivent dans des environnements réels.

**La concentration sur quelques fournisseurs réseau.** En regardant les ASN (les blocs d'adresses IP attribués aux opérateurs), on voit que certains opérateurs de connectivité LTE industrielle concentrent une part disproportionnée des résultats. Ce n'est pas un hasard — ça correspond exactement au scénario de la carte SIM installée pour la supervision à distance. Quelqu'un avait besoin d'accéder à un automate depuis le bureau. La solution la plus rapide a été une connexion mobile. Cette connexion ouvre une fenêtre sur Internet que personne n'a refermée correctement.

**Les pays technologiquement avancés ne sont pas exempts.** On pourrait s'attendre à ce que les pays avec des infrastructures IT matures présentent moins d'expositions industrielles. Ce n'est pas ce qu'on observe. L'Europe occidentale, l'Amérique du Nord, le Japon — tous présents dans les résultats. La maturité des équipes informatiques ne s'est pas encore propagée vers les équipes qui gèrent les automates et les process industriels. Ces deux mondes évoluent souvent indépendamment dans les organisations.

---

## Ce qu'on peut faire en 45 minutes, sans sortir de Shodan

Exercice de pensée. Quelqu'un ouvre Shodan. Pas de scanner, pas d'outil maison. Juste l'interface web et l'API.

`port:502 country:FR Modbus` retourne 127 résultats. On trie par durée d'exposition. Les dix premiers ont tous plus de 18 mois. Pour chacun, l'organisation déclarée est lisible dans les données Shodan.

`port:102 country:FR Siemens` retourne 43 résultats. Les banners livrent le modèle exact. On cherche les CVE associées aux versions firmware sur CVEDetails — quelques équipements présentent des vulnérabilités connues et publiquement documentées.

On croise les organisations identifiées avec ce qui est disponible publiquement sur les opérateurs d'importance vitale. Certains équipements appartiennent à des organisations dans des secteurs comme l'énergie ou les transports.

Aucune de ces étapes ne constitue une attaque. Il n'y a aucune connexion directe à aucun équipement. Tout est légal, public, documenté. C'est de la lecture. Et c'est exactement ce qui précède, en pratique, quelque chose de moins anodin.

La question n'est pas "est-ce que c'est faisable ?" — les chiffres montrent que c'est déjà fait, par les crawlers de Shodan, quotidiennement. La question c'est : combien de temps faut-il pour que quelqu'un qui cherche structure ce qu'il trouve en quelque chose d'utilisable ? Moins d'une heure, d'après ce que ce projet a permis de vérifier.

---

## Les limites de ce qu'on voit

Shodan indexe régulièrement, mais pas en temps réel. Un équipement peut avoir été exposé et corrigé entre deux passages du crawler — on ne le saura pas. À l'inverse, un équipement récemment exposé peut ne pas encore apparaître.

Le scoring ne peut pas savoir ce que contrôle réellement chaque équipement. Un automate BACnet dans un datacenter et un automate BACnet dans un immeuble de bureaux standard reçoivent le même score de base — c'est une limite qu'il faut garder en tête quand on lit le rapport.

Ces limites ne rendent pas l'analyse inutile. Elles définissent comment l'interpréter.
