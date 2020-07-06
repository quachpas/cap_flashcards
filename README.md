# Converting Opale Quizzes (XML) to LaTeX flashcards
## Introduction
>**If you are already familiar with the Scenari software suite, you can skip the following introduction.**

This project is backed by [*Unisciel*](http://www.unisciel.fr/), an online university creating and providing resources for secondary school pupils aged 15-18 (*lycée*), students, teachers and educational institutions.
### SCENARIchain and Opale
#### What is SCENARIchain ?
SCENARIchain refers to all Scenari software that involve structured collaborative writing.

For individual use, SCENARIchain can be deployed as a desktop application.
For collaborative use, SCENARIchain can be deployed as a server. 

#### What is Opale?
Opale is a publishing chain part of the [Scenari](https://scenari.org/co/home.html) software suite. It is used to produce resources for academic training. These documents can be used for on-site, distance or blended learning. 

Opale can be used to:
- Design training modules, blending learning and evaluations activities into a single storyline.
- Produce from a single content multiple documents:
  - (web) Online course material,
  - (PDF) Printable booklet for learners
  - (HTML) Slideshows
  - (PDF) Training document
- Add rich multimedia content to the course: videos, sounds, images, diagrams, mathematical formulas (LaTeX, OpenDocument)
- Create [quizzes][quizz]: multiple choice question (MCQ), multi choice question single answer, [categorise items][categorise], [order items][order], etc.
- Create accessible training materials in web format (HTML)
- Export content compatible with [SCORM][SCORM] (SCORM 1.2, or SCORM2004) standard to distribute them either via a Learning Management System (LMS), or a MOOC platform. Please refer to the [official website](https://scorm.com/) for more details.

[SCORM]: https://trac.scenari.org/opale/wiki/scorm
[quizz]: https://moodle.utc.fr/file.php/1330/cometes-modules/cometes-module-3-advanced/cometes-module-3-parcours/co/0551_exercices_interactifs.html
[categorise]: https://moodle.utc.fr/file.php/1330/cometes-modules/cometes-module-3-advanced/cometes-module-3-parcours/co/0551a_categorisation.html
[order]: https://moodle.utc.fr/file.php/1330/cometes-modules/cometes-module-3-advanced/cometes-module-3-parcours/co/guide_advanced.html

You will find below some examples of content produced using the Opale module in different format.

From left to right: web material, web slideshow, PDF OpenDocument, web publication using [Emeraude](https://download.scenari.software/Emeraude@1.3.0.07/). 

[![Opale web](https://doc.scenari.software/Opale@3.8/fr/res/OpaleAurora.png)](https://example.scenari.software/Opale@3.8/auroraW)
[![Slideshow web](https://doc.scenari.software/Opale@3.8/fr/res/OpalePres.png) ](https://example.scenari.software/Opale@3.8/auroraD)
[![PDF (OpenDocument)](https://doc.scenari.software/Opale@3.8/fr/res/OpaleOdt.png)](https://example.scenari.software/Opale@3.8/paperLight)
[![Emeraude tutorial web](https://doc.scenari.software/Opale@3.8/fr/res/OpaleAurora.png)](https://example.scenari.software/Opale@3.8/auroraAW)


#### Documentation
[SCENARIchain documentation (English)](https://doc.scenari.software/SCENARIchain@5.0/en/)

[SCENARIchain documentation (French)](https://doc.scenari.software/SCENARIchain@5.0/fr/)

[Opale documentation (English)](https://doc.scenari.software/Opale@3.8/en/)

[Opale documentation (French)](https://doc.scenari.software/Opale@3.8/fr/)
### Why this script?
The aim of this script is to produce printable flashcards to be used as learning support material for undergraduate students mainly. The format used is 10x8cm. You can find an example file [here](./LaTeX/flashcard_1x1.pdf).

It can also be used to produce printable flashcards at home for students' personal use. (A4 paper format). Please refer to the example [file](./LaTeX/flashcard_2x3.pdf) given in the LaTeX folder for more details.

Find below the front and the back of a flashcard. 

**Please note that the examples are models that were produced at the beginning of the project as a first design of the flashcard and are OUTDATED. Some additional changes have been made since, including adding correct answers checkboxes on the back of the flashcard. Some other changes may or may not be made in the future.**

<img src="LaTeX/models/recto-flash-cards.png" width=400>
<img src="LaTeX/models/verso-flash-cards.png" width=400>

## Getting Started
The root folder contains:
- [LICENSE](LICENSE), the license file.
- [README.md](README.md), this file.

There are three folders in this repository : Example files, LaTeX and Python. 

* The LaTeX folder is a playground for templating flashcards using the script. It contains basic examples and the models used for creating flashcards.
* The Python folder contains the script, two headers for two distinct ouput format and one footer. It also has some basic icons.
* The Example files folder contains `themeLicence.xml`, `9047.quiz`, and `8983.quiz` and folders leading to the image resource used by `9047.quiz`. 
* The Web folder contains all elements necessary to deploy a front to this script.

### Prerequisites
The script has only been tested on a linux system so far (Ubuntu 18.04.4 LTS). If all dependencies are installed, it should probably work seamlessly. You might need to tweak a few settings for `inkscape` to work properly.

**TeX Live 2019 has been used to compile all documents**. Please check that you have all necessary latex packages installed. You can find an exhaustive list in the wiki.

The script calls that tool **twice** and it can take up to a few minutes to produce a complete pdf of a few hundreds flashcards.

#### Linux systems
Install `python3` if needed and `inkscape` 0.92 ([Installation guide](https://wiki.inkscape.org/wiki/index.php/Installing_Inkscape#Installing_on_Linux)), these are required packages.

I use `xelatex`to compile my `.tex` files.

You may need to update your packages.

```bash
apt update
apt install libcanberra-gtk-module libcanberra-gtk3-module
add-apt-repository ppa:inkscape.dev/stable-0.92
apt update
apt install inkscape
apt install latexmk
apt install texlive-xetex
```

#### Windows
Install `python3` ([Installation guide](https://docs.python.org/3/using/windows.html)) and `inkscape` ([Installation guide](https://wiki.inkscape.org/wiki/index.php/Installing_Inkscape#Installing_on_a_Windows_system)).

> It hasn't been tested yet. 

#### macOS
MacOS comes with Python 2.7 pre-installed. Since this script has been tested on Python 3, please update your version of Python if it's already not up-to-date. You can find an installation guide here : [MacPython](https://docs.python.org/3/using/mac.html).

Inkscape is used to include `.svg` files. Here is an installation guide, and a faq : [installation guide and faq](https://wiki.inkscape.org/wiki/index.php/Installing_Inkscape#Installing_on_a_Mac).

> It hasn't been tested yet.

### Installing and first test run

Clone the repository where you want it to be and set it as your current working directory.

```
git clone https://gitlab.utc.fr/quachpas/cap_flashcards/
cd  ./cap_flashcards
```

At this point, if you want to run the script, you need source files. There is a sample provided in the folder [Example files](/Example-files/).

Open a terminal and run the script.
> You need an XML file describing all themes. There is one provided in the repository for example's sake. Please adjust as necessary. 

```
python3 ./Python/opale2flashcard.py ./Examples-files ./Examples-files/themeLicence.xml
```

The output will be found in your **current directory**, that is from where you launch the script.

## How to use the script?
### General instructions
The script works in collaboration with SCENARIchain.
You will need the following:
- Source files: the sources files **must be mcqSur or mcqMur quizzes** XML files, which you can download from your SCENARIchain server using the export option or export from your SCENARIchain desktop app. Find more details in the [Getting started](#getting-started) section.
- Licence theme file: as seen above, the flashcards each have a **subject** and a **theme**. As these are stored in the form of a code (#subj-them) in the source file, we need to produce a dictionary with all valid associations. This dictionary can be hard-coded in the script in the `opale_to_tex` function.
- Media resources: 
  - Assets for different subjects are provided.

> The script uses Opale's document models **mcqSur** and **mcqMur**. Please find Opale's documentation [here](https://download.scenari.software/Opale@3.7/).

**You will find more details on how to obtain a scar archive in the wiki. This particular page is written in French.**

## Web

The web part has been tested using php7.4-fpm + nginx on Ubuntu 20.04 LTS server.

Script dependencies :
```
add-apt-repository ppa:inkscape.dev/stable-0.92
apt update
apt install inkscape
apt install texlive-xetex
apt install python3
apt install python3-pip
pip3 install lxml
pip3 install Pillow
pip3 install qrcode
```

> Inkscape will try to create /var/www/.config/inkscape, so the user running the webserver needs the appropriate permissions on this folder.

How to install :
1. Move everything in the Web folder to your webserver root folder. 
2. Give appropriate ownerhships/permissions recursively to the user.

## TeX Live and Inkscape

Using another TeX Live version other than 2019 might create issues. Using inkscape 0.92 is also on purpose, since the `svg` package given with TeX Live 2019 does not recognises the newer version of inkscape. Upgrading to TeX Live 2020 and inkscape 1.0 is undefined behaviour, do so at your own risk.

## Contributing

I'm open to any contributions. I am a complete beginner in regards to coding, and I am aware that my code has several issues.
Some parts might need to be completely refactored.

## Author

**Pascal Quach**, engineering student at _UTC (Université Technologique de Compiègne)_.

## License

This project is licensed under the GNU General Public License v3.0. - see the [LICENSE.md](LICENSE) file for details

## Acknowledgments

* Thanks to Stéphane Poinsart for helping me on this project. 
* [Inspiration Code](https://framagit.org/stephanep/amcexport)
* [Mixed content parsing inspiration code](https://stackoverflow.com/questions/24071072/iterate-over-both-text-and-elements-in-lxml-etree)

