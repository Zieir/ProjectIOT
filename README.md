# Robustesse dans les graphes
Vous trouverez le document de réponses en format pdf sous le nom "Rendu_Projet_Graphes.pdf".

---

## Structure du Projet

Le projet est organisé en plusieurs fichiers, chacun ayant un rôle bien défini :

### Display.py
Ce fichier regroupe les différentes fonctions d'affichage. On y trouve des sorties sur le terminal, mais aussi des visualisations en HTML interactif qui permettent de voir clairement les graphes, les chemins calculés et les différentes approches testées.

### Main.py
C'est le point d'entrée du projet. Il construit le graphe donné dans l'énoncé et lance le serveur d'affichage pour visualiser les résultats.

### GraphStruct.py
Ici on retrouve toute la structure de graphe. Ce fichier contient les fonctions qui permettent de manipuler le graphe et d'extraire les informations dont on a besoin pour les algorithmes. Il contient aussi des utilitaires pour charger des graphes depuis un fichier (Des exemples de format possible sont disponibles dans \code)

### Abstract.py
C'est le cœur du projet. On y trouve l'algorithme de parcours abstrait qui fonctionne même sur des graphes cycliques. Il contient aussi quelques fonctions de comparaison et une fonction du premier ordre qui optimise le chemin selon la fonction de comparaison qu'on lui passe en paramètres. Vers la fin, il y a une petite fonction de tests. L'algorithme de parcours est bien annoté avec la spécification logique qui permet de démontrer sa correction.

### NonAbstract.py
C'est un peu l'alpha du projet. On y garde l'ancienne version de l'algorithme, histoire de voir d'où on vient et comment ça a évolué.
