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
        - Implémentation : Détection d'un énoncé/une réponse "longue" (critères à définir), puis ajustement manuel de la part de l'utilisateur à l'aide du rendu https://wiki.qt.io/Handling_PDF#Calling_an_external_viewer_application 
    - Questions adaptés aux flashcards
        - Questions de cours (explications au dos)
        - Exercices types solutionables de tête (dont les réponses sont vérifiables rapidement)
- Exclure
    - Questions non adaptés aux flashcards
        - Beaucoup de calculs/rédactions
        - QCM de cours ? Utilité à débattre, sur une flashcard, il vaudrait mieux poser reformuler l'énoncé pour poser une questin de cours. 
    - Réponses à ressource (e.g. images). Pour l'instant, le format flashcards n'est pas adapté pour contenir des ressources. L'utilisation du QR code amenant vers du contenu additionnel serait utile ! 
    - Ressources difficilement illisibles
        - Implémentation : Tri manuel. On distingue les questions contenant des images dans l'énoncé, pour pouvoir vérifier la lisibilité manuellement. https://wiki.qt.io/Handling_PDF#Calling_an_external_viewer_application
10h à 15h


Automatiser : a partir de tous les fichers XML de la banque de question, avoir un moyen de générer l'ensemble des flash cards.
2h

