# Converting Opale XML to LaTeX flashcards

## Project state
- The script is a POC. Dictionaries for the xml namespaces and metadata are hard-coded and not fetched dynamically.
- It has not yet been tested on a large question bank. 

## Definition of a flashcard
Many elements make up a flashcard:  
1. Metadata : subject, education level, subject theme, complexity level;
2. Content : question, choices, solutions, answer (explanations);
3. Fixed elements : the subject icon and unisciel's logo. 

## Source files integrity check
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

## Output settings
The script will write in the './output/out.tex' file. 
The front is always output before the back of the flashcard. 
There are two output formats : 
- default, the page's dimensions are 10x8 cm. 
- a4paper, the output's format is an A4 page.
Every page contains 6 flashcards (10x8 cm). A grid outlines the borders. This is the preferred format for printing flashcards at home.

Some options can be used to filter the output (image_only, overflow_only, file_name [file_name])
Combining these options will join the results, duplicates might exist.
Using these options can help greatly in checking whether a flashcard is correctly transcripted.

## Rich content
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

## Debugging tools
Some options are available to help debug the code and/or check if the output
is correct. 
Logs will be in './output/logs.txt'. 

## Getting Started

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
Download an archive containing MCQ from Scenari using the option 'export an archive' (_exporter une archive_)
Unzip it somewhere in the working directory. .scar archive can be renamed to .zip files.
Open a terminal and run the script.

```
python3 opale2flashcard.py ./path/to/questions/directory
```

The output will be in ./output/out.tex

## Running the tests

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

Several issues seem to arise :
    1. Some flashcards have missing metadata. These are listed, if you want to know which metadata is missing exactly, you can use the `--verbose` option.
    2. Some flashcards have potentially overflowing content. The console outputs the len of the question, choices and answer in this order.
        It also says whether the flashcard has an image in its question or not. You can use the `--overflow_only` option to compile and see the pdf output.
        Using the `--image_only` option is also useful to check whether the images are sufficiently distinct.
    3. One warning is given : 9540.quiz has no content on the back. This means that there are no explanations, only the solutions. If you want
        to see the output pdf, and _only_ for this file. You can use the `--file_name FILE_NAME` option.

## Contributing

I'm open to any contributions. I am a complete beginner in regards to coding, and I am aware that my code has several design issues.
Some parts might need to be rewritten completely. 

## Author

**Pascal Quach**, engineering student at _UTC (Université Technologique de Compiègne)_.

## License

This project is licensed under the GNU General Public License v3.0. - see the [LICENSE.md](LICENSE) file for details

## Acknowledgments

* Thanks to Stéphane Poinsart for helping me on this project. 
* [Inspiration Code](https://framagit.org/stephanep/amcexport)
* [Mixed content parsing inspiration code](https://stackoverflow.com/questions/24071072/iterate-over-both-text-and-elements-in-lxml-etree)

