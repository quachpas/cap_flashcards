<?php
$path_to_script_folder = "/opt/cap_flashcards/";
$path_to_theme_file = "/opt/cap_flashcards/Example-files/themeLicence.xml";
$path_to_compile_script = "/opt/cap_flashcards/compile.sh";

const FILES_EXTENSIONS = ['scar'];
function error($text)
{
	require_once("header.php");
	echo ($text);
	require_once("footer.php");
	exit(1);
}
// look in a directory recursively to find a file that contains "$filename"
function findfile($dir, $filename)
{
	$iterator = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($dir), RecursiveIteratorIterator::SELF_FIRST);

	foreach ($iterator as $path) {
		if (!$path->isDir()) {
			$pathstr = $path->__toString();
			if (strpos($pathstr, $filename) !== false) {
				return ($pathstr);
			}
		}
	}
	return false;
}

function printlogs($cmdout)
{
	if (!count($cmdout) || !trim($cmdout[0]))
		return;
	echo '<pre class="logs">';
	foreach ($cmdout as $cmdoutline)
		echo $cmdoutline . "\n";
	echo "</pre>";
}

if (!empty($_FILES)) {
	$legalSize = 262144000;
	$legalExtensions = array_map("strtolower", FILES_EXTENSIONS);

	$id = bin2hex(random_bytes(16));
	$actualName = $_FILES['file']['tmp_name'];
	$actualSize = $_FILES['file']['size'];
	$extension = strtolower(pathinfo($_FILES['file']['name'], PATHINFO_EXTENSION));

	$pathroot = '/tmp/upload/' . $id . '/';
	$pathin = $pathroot . 'in/';
	$pathfinal = __DIR__ . '/upload/' . $id . '/';
	$filein = $pathroot . "scenari.scar";
	$fileout = $pathroot . "latex.zip";

	// No empty file
	if (empty($actualName) || $actualSize <= 0)
		error("Erreur interne : le fichier n'existe pas, ou le fichier est vide.");

	// Check if the name is not already used
	if (file_exists($filein))
		error("Erreur interne : le nom a déjà été utilisé.");

	// Size checks
	if ($actualSize > $legalSize)
		error("Erreur interne : le fichier est trop volumineux");

	// Allowed extension 
	if (!in_array($extension, $legalExtensions))
		error("Erreur interne : Seuls les fichiers .scar sont valides");

	// Create file
	if (!file_exists($pathroot)) {
		mkdir($pathroot, 0700, true);
	}
	if (!file_exists($pathin)); {
		mkdir($pathin, 0700, true);
	}
	if (!file_exists($pathfinal)) {
		mkdir($pathfinal, 0700, true);
	}

	// Moving file
	if (!move_uploaded_file($actualName, $filein)) {
		error("Erreur interne : le fichier envoyé n'a pas pu être chargé correctement.");
	}

	// unzip the uploaded file
	$zip = new ZipArchive;
	$res = $zip->open($filein);
	if ($res === TRUE) {
		$zip->extractTo($pathin);
		$zip->close();
	} else {
		error("Erreur interne : le fichier envoyé n'a pas pu être dézippé.");
	}

	echo "Fichier accepté... Traitement en cours...</br>";
	chdir($path_to_script_folder . "Python/");
	exec("python3 opale2flashcard.py $pathin $path_to_theme_file --output " . $id . " 2>&1", $cmdout_python, $errcode);
	
	if ($errcode === 0 && file_exists('output/' . $id . '/out.tex')) {
		echo "<br><b>Conversion terminée !</b><br>";
		printlogs($cmdout_python);
	} else {
		printlogs($cmdout_python);
		error("<br><b>Erreur lors de la conversion !</b><br>");
	}

	chdir("./output/" . $id . "/");
	exec("sh $path_to_compile_script 2>&1", $cmdout_compile, $errcode_compile);

	exec("zip -r latex.zip . 2>&1", $cmdout_zip, $errcode);

	printlogs($cmdout_compile);

	if ($errcode === 0 && file_exists('latex.zip')) {
		rename('latex.zip', $pathfinal . 'latex.zip');
		echo "<p><a href=\"./upload/$id/latex.zip\">Téléchargez vos fichiers LaTeX et le fichier pdf</a></p>";
		echo "<p><b>Attention, si le nombre de flashcards est important, la prévisualisation peut prendre du temps ... Jusqu'à 10~15 min pour 300+ flashcards.</b></p>";
	} else {
		echo '<pre>';
		printlogs($cmdout_zip);
		error("Erreur interne : la production du fichier zip des fichiers tex a échouée");
		echo '</pre>';
	}

	if ($errcode_compile === 0 && file_exists('out.pdf')) {
		rename('out.pdf', $pathfinal . 'out.pdf');
		echo "<h2>Prévisualisation</h2><p><br><iframe width=\"800\" height=\"900\" src=\"./upload/$id/out.pdf\"><a href=\"./upload/$id/out.pdf\">Lien de prévisualisation PDF</a></iframe></p>";
	} else {
		error("Erreur interne : la prévisualisation a échoué ");
	}
}
require_once('header.php');

?>

<h2> Principe </h2>

<p>
	Le script permet de convertir des quiz <a href="https://doc.scenari.software/Opale/fr/">Opale</a> en des flashcards imprimables.
	La référence des matières, thèmes est celle de <a href="https://www.faq2sciences.fr/">Faq2Sciences</a> (Unisciel).
</p>

<h2> Exemple </h2>
<img src="recto-flash-cards.png" alt="Recto d'une flashcard imprimable" width=auto height=500px>
<img src="verso-flash-cards.png" alt="Recto d'une flashcard imprimable" width=auto height=500px>
</br>
Une fois imprimée et ajustée selon les repères de coupe, le produit final devrait ressembler aux images ci-dessus.

<h2> Pré-requis </h2>

<ul>
	<li>Exportez une archive .scar de vos contenus selon <a href="https://gitlab.utc.fr/quachpas/cap_flashcards/-/wikis/Rechercher-des-questions-sur-Sc%C3%A9nari">ce guide</a>. Faites attention à bien inclure le réseau descendant.</li>
	<li>Chargez l'archive .scar sur le site et cliquez sur envoyez. Attention, si le nombre de flashcards est important, le compilation peut prendre du temps !
		<form action="?" method="post" enctype="multipart/form-data">
			<label for="file">.scar Opale:</label>
			<input type="hidden" name="MAX_FILE_SIZE" value="262144000" />
			<input type="file" id="file" name="file" />
			<input type="submit" value="Envoyer" name="submit" id="submit" />
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