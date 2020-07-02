<?php
require_once('header.php')


?>

<h2> Principe </h2>

<p>
Le script permet de convertir des quiz <a href="https://doc.scenari.software/Opale/fr/">Opale</a> en des flashcards imprimables.
La référence des matières, thèmes est celle de <a href="https://www.faq2sciences.fr/">Faq2Sciences</a> (Unisciel).
</p>

<h2> Exemple </h2>
<img src="recto-flash-cards.png"
     alt="Recto d'une flashcard imprimable"
     width=500px
     height=500px>
<img src="verso-flash-cards.png"
     alt="Recto d'une flashcard imprimable"
     width=500px
     height=500px>

Une fois imprimée et ajustée selon les repères de coupe, le produit final devrait ressembler aux images ci-dessus.

<h2> Pré-requis </h2>

<ul>
    <li>Exportez une archive .scar de vos contenus selon <a href="https://gitlab.utc.fr/quachpas/cap_flashcards/-/wikis/Rechercher-des-questions-sur-Sc%C3%A9nari">ce guide</a>. Faites attention à bien inclure le réseau descendant. La procédure d'export est importante, les fichiers .quiz doivent se trouver à la racine de l'archive, et non pas enfouis dans des dossiers. Il est possible de réorganiser une archive .scar par vos propres moyens en renommant le fichier en .zip.</li>
    <li>Chargez l'archive .scar sur le site et envoyez la
          <form action="?" method="post" enctype="multipart/form-data">
               <label for="file">.scar Opale:</label>
               <input type="hidden" name="MAX_FILE_SIZE" value="262144000"/>
               <input type="file" id="file" name="file"/>
               <input type="submit" value="Envoyer" name="submit" id="submit"/>
          </form>
    </li>
    <li>Vous pourrez téléchargez une archive qui contient les fichiers out.tex, un fichier out par matière selon si la flashcard a été acceptée ou non, et le fichier out.pdf, qui contient toutes les flashcards acceptées.</li>
</ul>

<h2> Source </h2>
Le code source est disponible <a href="https://gitlab.utc.fr/quachpas/cap_flashcards">ici</a>
Ce convertisseur est basé sur le travail de Stéphane Poinsart (<a href="https://framagit.org/stephanep/amcexport">scenari2amc<a>)

<p>Ce service de conversion n'est pas sécurisé. Installez le code source sur en local si vous souhaitez l'utiliser à des fins confidentielles.</p>
<?php
require_once('footer.php')
?>
