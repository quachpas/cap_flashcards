- [Introduction](#introduction)
  - [SCENARIchain and Opale](#scenarichain-and-opale)
    - [What is SCENARIchain ?](#what-is-scenarichain-)
    - [What is Opale?](#what-is-opale)
    - [Documentation](#documentation)
  - [Why this script?](#why-this-script)
- [How to use the script?](#how-to-use-the-script)
  - [General instructions](#general-instructions)
- [Project state](#project-state)
  - [To do list](#to-do-list)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installing](#installing)
- [LaTeX](#latex)
  - [Definition of a flashcard](#definition-of-a-flashcard)
  - [Latex implementation of a flashcard](#latex-implementation-of-a-flashcard)
    - [Default output format (10x8cm)](#default-output-format-10x8cm)
    - [a4paper output format](#a4paper-output-format)
- [Script (Python)](#script-python)
  - [Source files integrity check](#source-files-integrity-check)
  - [Output settings](#output-settings)
  - [Rich content](#rich-content)
  - [Debugging tools](#debugging-tools)
  - [Running the tests](#running-the-tests)
- [Contributing](#contributing)
- [Author](#author)
- [License](#license)
- [Acknowledgments](#acknowledgments)
# Converting Opale XML to LaTeX flashcards <!-- omit in toc -->
## Introduction
>**If you are already familiar with the Scenari software suite, you can skip the following introduction.**

This project is backed by [*Unisciel*](http://www.unisciel.fr/), an online university creating and providing resources for secondary school pupils aged 15-18 (*lycée*), students, teachers and educational institutions.
### SCENARIchain and Opale
#### What is SCENARIchain ?
SCENARIchain refers to all Scenari software that involve structured collaborative writing.

For individual use, SCENARIchain can be deployed as a desktop application.
For collaborative use, SCENARIchain can be deployed as a server. 

#### What is Opale?
Opale is a publishing chain part of the software suite [Scenari](https://scenari.org/co/home.html). It is used to produce resources for academic training. These documents can be used for on-site, distance or blended learning. 

Opale can be used to:
- Design training modules, blending learning and evaluations activities into a single storyline.
- Produce from a single content multiple documents:
  - (web) Online course material,
  - (PDF) Printable booklet for learners
  - (HTML) Slideshows
  - (PDF) Training document
- Add rich multimedia content to the course: videos, sounds, images, diagrams, mathematical formulas (LaTeX, OpenDocument)
- Create [quizzes](quizz): multiple choice question (MCQ), multi choice question single answer, [categorise items](categorise), [order items](order), etc.
- Create accessible training materials in web format (HTML)
- Export content compatible with [SCORM](SCORM) (SCORM 1.2, or SCORM2004) standard to distribute them either via a Learning Management System (LMS), or a MOOC platform. Please refer to the [official website](https://scorm.com/) for more details.

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

<img src="LaTeX/models/flash-cards-01_Plan&#32;de&#32;travail&#32;1.jpg" width=400>
<img src="LaTeX/models/flash-cards-03_Plan&#32;de&#32;travail&#32;1.jpg" width=400>

## How to use the script?
### General instructions
The script works in collaboration with SCENARIchain.
You will need the following:
- Source files: the sources files **must be mcqSur or mcqMur quizzes** XML files, which you can download from your SCENARIchain server using the export option or export from your SCENARIchain desktop app. Find more details in the [Getting started](#getting-started) section.
- Licence theme file: as seen above, the flashcards each have a **subject** and a **theme**. As these are stored in the form of a code (#subj-them) in the source file, we need to produce a dictionary with all valid associations. This dictionary can be hard-coded in the script in the `opale_to_tex` function.
- Media resources: 
  - Compulsory resources are the subject logo (upper left) and university's logo (bottom right on the front). 
    > Both of these **must be** SVG files.
  - an icon and a logo are provided by default in [Python/output/images](./Python/output/images). 
> The script uses some tags that are present in Opale's document models **mcqSur** and **mcqMur**. Please find Opale's documentation [here](https://download.scenari.software/Opale@3.7/).

## Project state
- The script is a POC, therefore some functionalities may not function perfectly. Please use the debugging tools exhaustively to check the validity of the produced flashcards before printing.
### To do list
- Short tasks
  - A short text and a QR code are added automatically at the back of the flashcard. Add an option to disable it.
  - Image suppport is limited, as it's always put on the right side of the text. Better image support.
- Moderately long tasks
  - The icon is included in al flashcards. Implement a system to handle different icons according to which subject the flashcard has.
  - As of now, only one document is given "out.pdf" as the script's output. Categorised output will be added (sorted by subject for example).
- Long tasks
  - The QR code is static, a dynamic QR code generation according to the ressources found in the source file may be added in the future.
  - Write a configuration file template (YAML?) to implement:
    - custom short text on the back of the flashcard
    - custom subject/licence_theme dictionary
    - QR Code toggle
    - etc.
    - Expected behaviour:
      - Set default values to the script console options 
      - console options should override configuration file
## Getting Started
The root folder contains:
- [LICENSE](LICENSE), the license file.
- [README.md](README.md), this file.
- [themeLicence.xml](themeLicence.xml), an example XML file to produce the subject/licence dictionary.

There are two folders in this repository : LaTeX and Python. 

* The LaTeX folder is a playground for templating flashcards using the script. It contains basic examples and the models used for creating flashcards.
* The Python folder contains the script, two headers for two distinct ouput format and one footer. It also has some basic icons.

### Prerequisites

Install `python3` and `inkscape` ([Installation guide](https://wiki.inkscape.org/wiki/index.php/Installing_Inkscape)), these are required packages.

The following packages are optional : `latexmk` (necessary to use the `--compile` option).

### Installing

Clone the repository and set it as your current directory

```
git clone https://gitlab.utc.fr/quachpas/cap_flashcards/
cd  ./cap_flashcards
```
Download an archive from Scenari using the option 'export an archive' (_exporter une archive_).
Unzip it somewhere in the working directory. The `.scar` archive can be renamed to  `.zip` files.
Open a terminal and run the script.
> YOU NEED AN XML FILE WITH ALL LICENCE THEMES. There is one provided in the repository for simplicity's sake. Adjust as necessary.

```
python3 opale2flashcard.py ./path/to/questions/directory themeLicence.xml
```

The output will be in `./output/out.tex`.

## LaTeX
### Definition of a flashcard
A flashcard is made of different elements:  
1. Metadata : subject, education level, subject theme, complexity level.
2. Content : question, choices, solutions, answer (explanations).
3. Fixed elements : the subject icon and the university's logo.




### Latex implementation of a flashcard
> You will below an exhaustive explanation of the header files, so the reader can modify it afterwards if needed. In the following paragraphs, we will assume the reader has sufficient knowledge of LaTeX.

We use the [`flashcards` class](https://ctan.org/pkg/flashcards) for both output format. Follow the link to the class' CTAN page, and its documentation if you want to know more about the class itself. 

Options:
- The default option used is `avery5371`. 
- The `frame` option is used to reveal the flashcard's edge. This option is enabled in the a4paper output format. It reveals where to separate the flashcards after printing them.
- Add the `grid` option to reveal the **flashcard's content borders**. As specified in the class' documentation, there will be a uniform margin between the frame and the edge, defined by the length `\cardmargin`.

Graphics:
- Three colors are used that are part of unisciel's graphic charter
    ```latex
    \definecolor{uniscielblue}{RGB}{4,146,191}
    \definecolor{uniscielpink}{RGB}{231,33,90}
    \definecolor{uniscielgrey}{RGB}{103,104,104}
    % Bleu : #0492bf
    % Rose : #e7215a
    % Gris : #676868
    ```
- We use the package `fontspec` to set custom fonts:
    ```latex
    \usepackage{fontspec}
    %ITC Avant Garde Gothic 
    \setsansfont{ITC Avant Garde Gothic}[
        UprightFont={* Book},
        ItalicFont={* Book Oblique},
        BoldFont = {* Demi},
        BoldItalicFont = {* Demi Oblique}
    ]
    ```   
- The class' commands `\cardfrontstyle` and `\cardbackstyle` are used to set the content's font size and alignement behaviour.
    ```latex
    % --- FONT SIZE --- %
    \cardfrontstyle[\footnotesize\raggedright]{headings}
    \cardbackstyle[\footnotesize\raggedright]{plain}
    ```


#### Default output format (10x8cm)
We define the lengths of the class as such:
```latex
% --- CARD SIZE --- %
\def\pageheight{7.4cm}
\def\pagewidth{9.5cm}
\renewcommand{\cardpapermode}{portrait}
\renewcommand{\cardrows}{1}
\renewcommand{\cardcolumns}{1}
\setlength{\cardheight}{\pageheight}
\setlength{\cardwidth}{\pagewidth}
...
\setlength{\cardmargin}{3mm}
\setlength{\topoffset}{0mm}
\setlength{\oddoffset}{0mm}
\setlength{\evenoffset}{0mm}
```

The package `geometry` is used to define the output's format.
```latex
 \geometry{
    %showframe,
    papersize={10cm,8cm},
    marginparsep=0cm,
    footskip=0cm,
    hmargin=2mm,
    vmargin=2mm,
 }
```

The base of the flashcard template is written as such:
```latex
\begin{}
```
#### a4paper output format


## Script (Python)
### Source files integrity check
The script will check the integrity of the .quiz files. 
Only mcqSur and mcqMur question types are completely supported.
For other types, the behaviour is unpredictable. 
1. Missing content:
    The script will continue if a flashcard has missing content,
    whether that be the question, choices, solutions or answer. 
    The script will give a warning message. 
2. Missing metadata:
    The script will NOT output the flashcard if it has missing metadata.
    You can bypass this behaviour using the '--force' option.
    Be aware that it replace missing metadata with 'Missing METADATA_NAME'. 
3. Content size:
    Some flashcards have large content, these might overflow,
    and will be removed by default. 
    The criteria used to define that is a character count. 
    Q : Question, C : Choices, A : Answer
    Flashcards with an image in their question are flagged if :
        - Q + C > 700 or A > 1000
    Flashcards without are flagged if :
        - Q + C > 800 or A > 1000

### Output settings
The script will write in the './output/out.tex' file. 
The front is always output before the back of the flashcard. 
There are two output formats : 
- default, the page's dimensions are 10x8 cm. 
- a4paper, the output's format is an A4 page.
Every page contains 6 flashcards (10x8 cm). A grid outlines the borders. This is the preferred format for printing flashcards at home.

Some options can be used to filter the output (image_only, overflow_only, file_name [file_name])
Combining these options will join the results, duplicates might exist.
Using these options can help greatly in checking whether a flashcard is correctly transcripted.

### Rich content
Some flashcards contents can be quite rich. 
Below, we define which content is supported or not.
1. Question:
    - TWO images maximum. We consider that fitting two images on one flashcard
    is possible, but that would notably reduce the size and therefore make
    them indistinct. Image file format supported are pdf, png, jpeg, eps.
    If the script finds any occurences of "ci-contre" (see below), it will replace 
    them by "ci-contre". Use '--no_replace' to remove this behaviour.
    - Tables are supported within reason. 
    - MathLaTeX is supported.
2. Choices:
    - MathLaTeX is supported.
3. Answer:
    - MathLaTeX is supported.
    - Links are supported. They are removed by default. 
    This behaviour can be removed using the 'add_url' option.

### Debugging tools
Some options are available to help debug the code and/or check if the output
is correct. 
Logs will be in './output/logs.txt'. 
### Running the tests

The `--debug_mode` option should be enabled if you want to check the pdf output. It will let you associate the output to the original file name.

Given the following console output : 
```
python3 opale2flashcard.py faq2sciences/Physique-optigeom_2020-2-14/\&
opale2flashcard.py(9583.quiz): Metadata is missing.
opale2flashcard.py(9593.quiz): Metadata is missing.
opale2flashcard.py(9568.quiz): Image - Potentially overflowing content (Q, C, A): 445 100 1642
opale2flashcard.py(9721.quiz): Metadata is missing.
opale2flashcard.py(9541.quiz): No image - Potentially overflowing content (Q, C, A): 246 581 733
opale2flashcard.py(9569.quiz): Metadata is missing.
opale2flashcard.py(9620.quiz): Metadata is missing.
opale2flashcard.py(9540.quiz): WARNING ! This flashcard has an issue. There is nothing on the back.
opale2flashcard.py(9548.quiz): No image - Potentially overflowing content (Q, C, A): 255 624 831
opale2flashcard.py(9523.quiz): No image - Potentially overflowing content (Q, C, A): 215 133 1468
opale2flashcard.py(9612.quiz): Metadata is missing.
opale2flashcard.py(9592.quiz): Metadata is missing.
opale2flashcard.py(9572.quiz): Metadata is missing.
opale2flashcard.py(9608.quiz): Metadata is missing.
opale2flashcard.py(9624.quiz): No image - Potentially overflowing content (Q, C, A): 232 282 1348
opale2flashcard.py(9624.quiz): Metadata is missing.
opale2flashcard.py(9574.quiz): Metadata is missing.
opale2flashcard.py(9573.quiz): Metadata is missing.
opale2flashcard.py(9582.quiz): WARNING ! This flashcard has an issue. There is nothing on the back.
opale2flashcard.py(9582.quiz): Metadata is missing.
opale2flashcard.py(9588.quiz): Metadata is missing.
opale2flashcard.py(9558.quiz): No image - Potentially overflowing content (Q, C, A): 120 184 1185
opale2flashcard.py(9590.quiz): Image - Potentially overflowing content (Q, C, A): 414 68 1407
opale2flashcard.py(9590.quiz): Metadata is missing.
opale2flashcard.py(9504.quiz): Metadata is missing.
opale2flashcard.py(9616.quiz): No image - Potentially overflowing content (Q, C, A): 290 214 1541
opale2flashcard.py(9616.quiz): Metadata is missing.
opale2flashcard.py(9605.quiz): Metadata is missing.
opale2flashcard.py(9602.quiz): Metadata is missing.
opale2flashcard.py(9597.quiz): No image - Potentially overflowing content (Q, C, A): 984 461 1558
opale2flashcard.py(9597.quiz): Metadata is missing.
opale2flashcard.py(9580.quiz): Metadata is missing.
opale2flashcard.py(9560.quiz): No image - Potentially overflowing content (Q, C, A): 122 197 1118
opale2flashcard.py(9581.quiz): Metadata is missing.
opale2flashcard.py(9586.quiz): Metadata is missing.
opale2flashcard.py(9579.quiz): Metadata is missing.
opale2flashcard.py(9587.quiz): Metadata is missing.
opale2flashcard.py(9599.quiz): Metadata is missing.
opale2flashcard.py: 32/66 flashcards have missing metadata errors.
 These files will not be transcripted. Use option "--force" to ignore.

WARNING : We replaced every occurence of "ci-dessous" in the question by "ci-contre". If it was a mistake, please modify as necessary.
 Use option --no_replace to deactivate this feature.
Please make use of the "--overflow-only" option to check every flashcard for potential defects
opale2flashcard.py: The .tex file out.tex has been created in ./output directory. Compiling it will produce a pdf file containing all flashcards in the specified source directory.
 Use option '--compile' if you want to compile directly after. You must have latexmk installed.

```

Several issues seem to arise:
1. Some flashcards have missing metadata. These are listed, if you want to know which metadata is missing exactly, you can use the `--verbose` option to get more details.
2. Some flashcards have potentially overflowing content. The console outputs the len of the question, choices and answer in this order.
It also says whether the flashcard has an image in its question or not. You can use the `--overflow_only` option to compile and see the pdf output.
Using the `--image_only` option is also useful to check whether the images are sufficiently distinct.
3. One warning is given : 9540.quiz has no content on the back. This means that there are no explanations, only the solutions. If you want
to see the output pdf, and _only_ for this file. You can use the `--file_name FILE_NAME` option.

> Be warned that the output LaTeX document is not necessarily without syntax errors. If the source files are riddled with LaTeX Math mistakes, the document won't compile properly.

## Contributing

I'm open to any contributions. I am a complete beginner in regards to coding, and I am aware that my code has several design issues.
Some parts might need to be completely refactored. 

## Author

**Pascal Quach**, engineering student at _UTC (Université Technologique de Compiègne)_.

## License

This project is licensed under the GNU General Public License v3.0. - see the [LICENSE.md](LICENSE) file for details

## Acknowledgments

* Thanks to Stéphane Poinsart for helping me on this project. 
* [Inspiration Code](https://framagit.org/stephanep/amcexport)
* [Mixed content parsing inspiration code](https://stackoverflow.com/questions/24071072/iterate-over-both-text-and-elements-in-lxml-etree)

