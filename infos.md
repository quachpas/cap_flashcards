Micro-veille sur les flash cards : l'état de l'art du point de vue de l'esthétique
1h


tester la publication de flashcard avec LaTeX
en allant le plus loin possible : intégrer une image de fond (filigrane), des contenus riches (images, formules LaTeX, mise en forme...) + Logo Unisciel
 changement taille feuille 10x8cm pour imprimer directement. 
Format imprimeur : Rajout du cadre à l'impression.
Format : un énoncé et 5 réponses max. Métadonnées (thème de la question par ex.)
~6 à 12h


Transformation XML Scenari en flashcard LaTeX.
Point de départ : sript python d'export Scenari -> AMC (autre classe LaTeX de gestion des QCM)
https://framagit.org/stephanep/amcexport
30h


Filtrage (retirer les questions qui ne "passent pas bien". Trop longue ? métadonnée "niveau de complexité" trop haut.
- Conditions
    - Longueur de l'énoncé/réponse (présence de formule ?), ajustable jusqu'à \footnotesize (après, difficilement lisible)
    - Questions adaptés aux flashcards
        - Questions de cours
        - Exercices types solutionables de tête (dont les réponses sont vérifiables rapidement)
- Exclure
    - Questions non adaptés aux flashcards
        - Beaucoup de calculs/rédactions
    - Réponses à ressource (e.g. images)
    - Ressources difficilement illisibles
        - Implémentation : Tri manuel
10h à 15h


Automatiser : a partir de tous les fichers XML de la banque de question, avoir un moyen de générer l'ensemble des flash cards.
2h

