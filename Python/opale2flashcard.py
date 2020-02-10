#!/usr/bin/python3
# encoding: utf-8
import sys
import os
import shutil
import unicodedata
import re
import argparse
import traceback
import xml.dom.minidom as minidom

from lxml import etree
from macpath import dirname

parser = argparse.ArgumentParser(description='Conversion from Opale (XML) to LaTeX (flashcard)')
parser.add_argument('sourcedir', help='XML files\' directory path - Path to root directory containing all XML files')
parser.add_argument('--a4paper', action='store_const', const='a4paper', default='10x8', help='Output format - (defaults to printing 10x8cm flashcards)')
args = parser.parse_args()
# args.sourcedir

# XML namespaces
namespace = {
    "sc" : "http://www.utc.fr/ics/scenari/v3/core",
    "op" : "utc.fr:ics/opale3",
    "sp" : "http://www.utc.fr/ics/scenari/v3/primitive",
}

licence_theme = {
    "integration" : "Intégration",
    #etc.
}

subject = {
    "#math" : "Mathématiques",
}

complexity_level = {
    '1' : "Connaître",
    '2' : "Changement de langage",
    '3' : "Comprendre, appliquer",
    '4' : "Analyser",
}

class Flashcard:
    def __init__(self, file, complexity_level, subject, education_level, licence_theme, question, choices, answer):
        self.file = file
        self.complexity_level = complexity_level
        self.subject = subject
        self.education_level = education_level
        self.licence_theme = licence_theme
        self.question = question
        self.choices = choices
        self.answer = answer

# print(namespace.keys())
# print(namespace.values())
                
# Parser settings
parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)

# Path validity check
if (not os.path.isdir(args.sourcedir)):
    sys.stderr.write('Error: '+args.sourcedir+' is not a directory.\n')
    sys.exit(1)

def remove_namespace(element):
    return etree.QName(element)

def fetch_data(element, expression, filename):
    for element in element.iterfind(expression, namespace):
        return element.text

def get_complexity_level(level):
    return complexity_level.get(level, "Invalid complexity level")

def get_licence_theme(theme_code):
    return licence_theme.get(theme_code, "Invalid theme code")

def get_subject(subject_code):
    return subject.get(subject_code, "Invalid subject code")

def write_output(file, complexity_level, subject, education_level, licence_theme, question, choices, answer):
    output = []
    # Output
    output.append('% Flashcard : ' + file + '\n')
    output.append('\cardfrontfooter{' + complexity_level + '}\n')
    output.append('\\begin{flashcard}[\cardfrontheader{' + subject + '}{' + education_level + '}{' + licence_theme + '}]{\n')
    output.append('\\vspace{\enoncevspace}\n')
    output.append(question + '\n')
    output.append('\\begin{enumerate}\n')
    for choice in range(len(choices)):
        output.append('\t\\item' + choices[choice] + '\n')
    output.append('\\end{enumerate}\n}\n')
    output.append('\\vspace*{\\stretch{1}}\n\\vspace{\\reponsevspace}\n')
    output.append(answer + '\n')
    output.append('\\vspace*{\\stretch{1}}\n\\end{flashcard}')
    
    return output
   
def write_outfile(output):
    # Directory and file output
    if os.path.isdir('output') is None:
        os.mkdir('output')
    if os.path.isfile('output/out.tex'):
        os.remove(os.path.join(os.getcwd(),'output/out.tex'))

    # Open outfile 
    outfile = open('output/out.tex', 'a', encoding = 'utf-8')

    # Write header
    header = open(os.path.join(os.getcwd(),'header.tex'),'r', encoding="utf-8")
    for line in header.readlines():
        outfile.write(line)
    outfile.write('\n\n')
    header.close

    # Write content
    outfile.write(''.join(output))

    # Write footer
    outfile.write('\n\n')
    footer = open(os.path.join(os.getcwd(),'footer.tex'),'r', encoding="utf-8")
    for line in footer.readlines():
        outfile.write(line)
    
    footer.close
    outfile.close     

def parse_files(args): # Copy all files in sourcedir/Prettified and prettify XML
    sourcedir = os.path.realpath(args.sourcedir)
    for file in os.listdir(sourcedir):
        workpath = os.path.join(sourcedir, file)
        if os.path.isfile(workpath) and file == '9493.quiz':
            # XML Tree
            tree = etree.parse(workpath, parser)
            root = tree.getroot()
            # Fetch data
            ## Type question : mcqSur, mcqMur
            if (remove_namespace(root[0]).localname == "mcqSur"):
                question_type = "mcqSur"
            print(question_type)
            ## Licence Theme and subject
            theme_code = fetch_data(root, ".//sp:themeLicence", file)
            splitted = theme_code.split('-')
            subject = get_subject(splitted[0])
            licence_theme = get_licence_theme(splitted[1])
            print(subject, licence_theme)
            ## Complexity level
            complexity_level = get_complexity_level(fetch_data(root, ".//sp:level", file))
            print(complexity_level)
            ## Education level
            education_level = fetch_data(root, ".//sp:educationLevel", file)
            print(education_level)
            ## Content
            ### Question
            question = "dummy question"
            choices = ["dummy choice 1", "dummy choice 2", "dummy choice 3"]
            fetch_data(root, ".//sc:textLeaf[@role='mathtex']", file) # Maths expressions
            ### Answer
            answer = "dummy dqzdzqdqz"

            # Write in output
            output = write_output(file, complexity_level, subject, education_level, licence_theme, question, choices, answer)
            write_outfile(output)


parse_files(args)

# root = etree.XML("<root>dataaaa<test>data</test><test2>data</test2></root>")
# print(root[1].tag)

# %%%%%%%%%%%%%%% TEMPLATE STANDARD %%%%%%%%%%%%%%%%

# \cardfrontfooter{Niveau de complexité}
# \begin{flashcard}[\cardfrontheader{Matière}{L0}{Thème}]{
# %%%%%%%%%%%%%%% ÉNONCÉ %%%%%%%%%%%%%%%%
# \vspace{\enoncevspace}
# \'Enoncé
# \begin{enumerate}
#     \item Réponse 1
#     \item Réponse 2
#     \item Réponse 3
# 	\item Réponse 4
# \end{enumerate}
# }
# %%%%%%%%%%%%%%% ÉNONCÉ %%%%%%%%%%%%%%%%
# \vspace*{\stretch{1}}
# %%%%%%%%%%%%%%% RÉPONSE %%%%%%%%%%%%%%%%
# \vspace{\reponsevspace}
# \lipsum[2]
# %%%%%%%%%%%%%%% RÉPONSE %%%%%%%%%%%%%%%%
# \vspace*{\stretch{1}}
# \end{flashcard}
# %%%%%%%%%%%%%%% TEMPLATE STANDARD %%%%%%%%%%%%%%%%