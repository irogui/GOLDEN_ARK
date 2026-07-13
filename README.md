# GOLDEN ARK
*Plateforme web permettant la gestion d'une communauté ARK en complément d'un bot Discord.*

Lien: [https://golden-ark.emerald-prism.fr/](https://golden-ark.emerald-prism.fr/)

PS: Ceci n'est pas le vrai Repo mais une copie ne contenant aucune donnée sensible.

## Contexte
J'administre une communauté Discord autour du jeu ARK: Survival Evolved. Afin de faciliter la recherche d'informations et d'automatiser certaines tâches répétitives, j'ai développé en août 2024 un bot Discord nommé **IZARIX**.

À l'origine, ce bot permettait principalement aux joueurs d'obtenir rapidement des informations sur le jeu à l'aide de commandes Discord, comme l'emplacement des créatures, leurs variantes ou encore les recettes de fabrication d'un item.
*Exemple : /System_Call = Raptor - The Island*
Cette commande affiche une carte dans un salon indiquant les emplacements du Raptor sur la carte The Island.

Au fil du temps, j'ai amélioré le projet pour qu'il réponde aux besoins de la communauté. De nouvelles fonctionnalités ont été ajoutées, notamment un système de monnaie virtuelle appelée Gold, permettant aux joueurs de vendre des objets du jeu pour gagner de la monnaie, d'acheter des objets depuis une boutique, ainsi que de participer à plusieurs jeux de hasard (Pile ou Face, Chifoumi et une variante de Roulette russe) pour tenter d'en obtenir encore plus.

Cependant une limite importante est rapidement apparue: les interactions réalisées par des commandes Discord devenaient peu plus complexes, peu pratiques et parfois compliquées à comprendre pour certains joueurs. C'est dans ce contexte qu'est née l'idée de développer une application web venant compléter le bot Discord. Son objectif est d'offrir une interface plus intuitive avec un visuel assez beau ce que les joueurs achètent ou vendent, de centraliser les données dans une nouvelle base de données relationnelle (car avant les données étaient stockées avec des fichiers JSON) et de proposer de nouvelles fonctionnalités qui ne pourraient pas être implémentées sur Discord.

Par ailleurs c'est grâce aux acquis de ma 1er année en BUT Informatique que j'ai pu mener à bien ce projet.


## Objectifs
- Créer une BDD (base de données) centralisant toutes les informations concernant les joueurs, objets, évènements, etc...
- Proposer une boutique d'objets pour acheter et vendre ses items.
- Simplifier l'administration de la communauté via une interface admin.
- Compléter les fonctionnalités du bot Discord (informations sur les items ou créatures).


## Fonctionnalités

### Générales
- Connexion et renseignement sur les infos du joueur (Pseudo, nom du survivant dans le jeu, etc...)
- Vente d'items.
- Commandes d'items.
- Consultation du solde, du code de coffre fort (coffre dans le jeu permettant de recevoir ou envoyer des items pour qu'ils soient traités par un admin).

### Interface Admin
- Consultation des profils.
- Gestion des rôles(admin, membre, invité,...).
- Gestion des commandes et des reventes des membres (valider, annuler une commande).
- Gestion des items et de leurs caractéristiques.

### Boutique
- Catalogue.
- Fiches des items.
- Informations complémentaires sur les items.
- Achats.
- Commentaires et notes sur les items (en cours de dév)
- Affichage des différentes boutiques dans le jeu avec une carte et leur coordonnées (en cours de dev)
