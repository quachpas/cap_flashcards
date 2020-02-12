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
import time

from lxml import etree
from macpath import dirname
from itertools import zip_longest

parser = argparse.ArgumentParser(description='Conversion from Opale (XML) to LaTeX (flashcard)')
parser.add_argument('sourcedir', help='XML files\' directory path - Path to root directory containing all XML files. N.B. : Unzipping a .scar archive is the simplest workaround to have the .quiz files locally. To refer correctly to the "&" directory, you need to add an \ before. The path becomes "*/\&"')
parser.add_argument('--a4paper', action='store_const', const=True, default=False, help='Output format - (defaults to printing 10x8cm flashcards)')
parser.add_argument('--verbose', action='store_const', const=True, default=False, help='Force the output - Ignores transcripts errors')
parser.add_argument('--force', action='store_const', const=True, default=False, help='Verbose ouput - Details missing metadata errors')
parser.add_argument('--logs', action='store_const', const=True, default=False, help='Logs output - Outputs warning and errors in output/logs.txt instead of writing in the console')

# XML namespaces
namespace = {
    "sc" : "http://www.utc.fr/ics/scenari/v3/core",
    "op" : "utc.fr:ics/opale3",
    "sp" : "http://www.utc.fr/ics/scenari/v3/primitive",
}

licence_theme = {
    "integration" : "Intégration",
    "thermodyn" : "Thermodynamique",
    "thermochim" : "Thermochimie",
}

subject = {
    "#math" : "Mathématiques",
    "#phys" : "Physique",
    "#chim" : "Chimie",
}

complexity_level = {
    '1' : "Connaître",
    '2' : "Changement de langage",
    '3' : "Comprendre, appliquer",
    '4' : "Analyser",
}

roles_markup = {
    "emp" : ("\emph{", "}"),
    "exp" : ("$\^{", "}$"),
    "ind" : ("$_{", "}$"),
    "mathtex" : ("$", "$"),
}

tags_markup = {
    "textLeaf" : ("", ""),
    "inlineStyle" : ("", ""),
    "choiceLabel" : ("\item ", "\n"),
    "choiceExplanation" : ("", ""),
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
        self.err_flag = False
        self.err_message = ""

def remove_namespace(element):
    return etree.QName(element)

def fetch_data(element, expression):
    data = []
    output = ''
    for element in element.iterfind(expression, namespace):
        data.append(element.text)
    for x in data:
        output += x
    return output

def get_role_markup(role):
    return roles_markup.get(role, None)

def get_tag_markup(tag):
    return tags_markup.get(tag, None)

def get_complexity_level(level):
    return complexity_level.get(level, None)

def get_licence_theme(theme_code):
    return licence_theme.get(theme_code, None)

def get_subject(subject_code):
    return subject.get(subject_code, None)

def check_metadata(flashcard):
    if (flashcard.complexity_level is None or flashcard.complexity_level == "Missing Complexity Level"
            or flashcard.education_level is None or flashcard.education_level == "Missing Education Level"
            or flashcard.licence_theme is None or flashcard.licence_theme == "Missing Licence Theme"
            or flashcard.subject is None or flashcard.subject == "Missing Subject"):
        if (args.force == False):
            flashcard.err_flag = True
        if (args.verbose == True):
            flashcard.err_message = flashcard.file + ' was not written in out.tex.\n' + 'Metadata is missing :\n'
            if (flashcard.complexity_level is None or flashcard.complexity_level == "Missing Complexity Level"):
                flashcard.err_message += "\t- Missing Complexity Level\n"
            if (flashcard.education_level is None or flashcard.education_level == "Missing Education Level"):
                flashcard.err_message += "\t- Missing Education Level\n"
            if (flashcard.licence_theme is None or flashcard.licence_theme == "Missing Licence Theme"):
                flashcard.err_message += "\t- Missing Licence theme\n"
            if (flashcard.subject is None or flashcard.subject == "Missing Subject"):
                flashcard.err_message += "\t- Missing Subject\n"
            flashcard.err_message += "\n"
        else:
            flashcard.err_message = flashcard.file + " : Metadata is missing."

def write_logs(flashcard):
    logs = open('output/logs.txt', 'a', encoding = 'utf-8')

    logs.write(time.strftime("%m-%d-%Y @ %H:%M:%S\n", time.localtime()) + flashcard.err_message)

def write_output(flashcard):
    # Variables
    output = []

    # Check flashcard metadata
    check_metadata(flashcard)
    if (flashcard.err_flag == False):
        # Output
        output.append('% Flashcard : ' + flashcard.file + '\n')

        if (args.a4paper == False):
            output.append('\cardfrontfooter{' + flashcard.complexity_level + '}\n')

        output.append('\\begin{flashcard}[\cardfrontheader{' + flashcard.subject + '}{' + flashcard.education_level + '}{' + flashcard.licence_theme + '}]{\n')
        output.append('\\vspace{\enoncevspace}\n')
        output.append(flashcard.question + '\n')
        output.append('\\begin{enumerate}\n')
        for choice in range(len(flashcard.choices)):
            output.append('\t\\item ' + flashcard.choices[choice] + '\n')
        output.append('\\end{enumerate}\n}\n')
        output.append('\\vspace*{\\stretch{1}}\n\\vspace{\\reponsevspace}\n')
        output.append(flashcard.answer + '\n')
        output.append('\\vspace*{\\stretch{1}}\n\\end{flashcard}\n\n')
        
        return output
    else:
        return flashcard.err_message
   
def write_out_a4paper(flashcard_list):
    output_list = []
    footer = ['\cardfrontfooter{']
    question_count = 0 # Keeps track which question we're processing on a page [0-6]
    question_number = 0 # Keeps track of which question we're processing in flashcard_list [0-len(flashcard_list)]
    error_count = 0 # Tracking number of questions with missing metadata

    # Main Loop
    for fc in flashcard_list:
        check_metadata(fc)
        if (fc.err_flag == False):
            question_number += 1
            question_count += 1
            output_list.append(write_output(fc))
            
            if (question_count != 6 and len(flashcard_list) - question_number >= 1):
                # If len(flashcard_list) - question_number is between 6 and 1, then we're processing the last page of flashcards
                # The number of remaining flashcards will not be sufficient to do another loop
                # So we treat the last flashcards separately 
                footer.append(fc.complexity_level + '}\n{')
            elif (len(flashcard_list) - question_number == 0 ):
                footer.append(fc.complexity_level + '}\n')
            else:
                question_count = 0
                footer.append(fc.complexity_level + '}\n')
                output = ''.join(footer)
                for fc in output_list:
                    output += ''.join(fc)
                write_outfile(output)
                output = ''
                output_list = []
                footer = ['\cardfrontfooter{']
        # fc has a missing metadata error
        else:
            error_count += 1
            if (args.logs == False):
                print(fc.err_message)
            else:
                write_logs(fc)

    # Writing "\cardfrontfooter{.}{.}{.}{.}{.}{.}"
    output = ''.join(footer)

    # Adding the missing empty parameters to \cardfrontfooter
    for _ in range(0, 6 - question_count):
        output += '{}\n'

    # Writing output string
    for fc in output_list:
        output += ''.join(fc)
    
    write_outfile(output)

    return error_count

def write_outfile(output):
    # Open outfile 
    outfile = open('output/out.tex', 'a', encoding = 'utf-8')
    # Write content
    outfile.write(''.join(output))
    outfile.close     

def write_outfile_header():
    # Directory and file output
    if os.path.isdir('output') is None:
        os.mkdir('output')
    if os.path.isfile('output/out.tex'):
        os.remove(os.path.join(os.getcwd(),'output/out.tex'))

    # Open outfile 
    outfile = open('output/out.tex', 'a', encoding = 'utf-8')

    # Write header
    if (args.a4paper == True):
        header = open(os.path.join(os.getcwd(),'header_a4paper.tex'),'r', encoding="utf-8")
    else:
        header = open(os.path.join(os.getcwd(),'header_default.tex'),'r', encoding="utf-8")
    for line in header.readlines():
        outfile.write(line)
    outfile.write('\n\n')
    header.close

    outfile.close     

def write_outfile_footer():
    # Open outfile 
    outfile = open('output/out.tex', 'a', encoding = 'utf-8')

    # Write footer
    outfile.write('\n\n')
    footer = open(os.path.join(os.getcwd(),'footer.tex'),'r', encoding="utf-8")
    for line in footer.readlines():
        outfile.write(line)
    
    footer.close

def fetch_content(file, root):
    # Fetch data
    # variables 
    theme_code = None
    subject = None
    licence_theme = None
    complexity_level = None
    education_level = None
    ## Type question : mcqSur, mcqMur
    if (remove_namespace(root[0]).localname == "mcqSur"):
        question_type = "mcqSur"
    ## Licence Theme and subject
    theme_code = fetch_data(root, ".//sp:themeLicence")
    if (theme_code is not ''):
        splitted = theme_code.split('-')
        if (len(splitted) > 3):
            for x in range(0, len(splitted)-1, 2):
                if (len(splitted) - 1 - x == 2):
                    if (subject is None):
                        subject = get_subject(splitted[x])
                    else:
                        subject += get_subject(splitted[x])
                    
                    if (licence_theme is None):
                        licence_theme = get_licence_theme(splitted[x+1])
                    else:
                        licence_theme += get_licence_theme(splitted[x+1])    
                else:
                    if (subject is None):
                        subject = get_subject(splitted[x]) + '/'
                    else:
                        subject += get_subject(splitted[x]) + '/'
                    
                    if (licence_theme is None):
                        licence_theme = get_licence_theme(splitted[x+1]) + '/'
                    else:
                        licence_theme += get_licence_theme(splitted[x+1]) + '/'
        else:
            subject = get_subject(splitted[0])
            licence_theme = get_licence_theme(splitted[1])
    else:
        subject = None
        licence_theme = None
    ## Complexity level
    complexity_level = get_complexity_level(fetch_data(root, ".//sp:level"))
    ## Education level
    education_level = fetch_data(root, ".//sp:educationLevel")
    ## Content
    ### Question
    print(file)
    question = fetch_question(root)
    choices = fetch_choices(root)
    ### Answer
    answer = fetch_answer(root)

    # Create Flashcard instance
    flashcard = Flashcard(file, complexity_level, subject, education_level, licence_theme, question, choices, answer)
    return flashcard

def texfilter(text):
    text = text.replace('\\','\\textbackslash')
    text = text.replace('~','\\textasciitilde')
    text = text.replace('^','\\textasciicircum')
    text = text.replace('&','\\&')
    text = text.replace('%','\\%')
    text = text.replace('$','\\$')
    text = text.replace('#','\\#')
    text = text.replace('_','\\_')
    text = text.replace('{','\\{')
    text = text.replace('}','\\}')
    return text

def markup_content(element):
    output = []
    if (type(element) is not etree._Element):
        print("Error type")

    localname = remove_namespace(element).localname
    tag_markup = get_tag_markup(localname)
    output.append(tag_markup[0])

    if bool(element.attrib): # If there are attributes
        for key, value in zip(element.attrib.keys(), element.attrib.values()):
            if key == 'role':
                role_markup = get_role_markup(value)
    else:
        role_markup = ('', '')
    output.append(role_markup[0])
    if element.text is not None:
        output.append(element.text)
    output.append(role_markup[1])

    output.append(tag_markup[1])
    return ''.join(output)


def fetch_question(root):
    output = ''
    for element in root.iterfind(".//sc:question//sc:para", namespace):
        for text, child in zip_longest(element.xpath('text()'), element.getchildren()):
            if text is not None:
                output += texfilter(text)
            if child is not None:
                output += markup_content(child)
    return output

def fetch_choices(root):
    output = ''

    for element in root.iterfind(".//sc:choice", namespace):
        for text, child in zip_longest(element.xpath('text()'), element.getchildren()):
            if text is not None:
                # print(texfilter(text))
            if child is not None:
                # print(markup_content(child))

    return ["dummy choice 1", "dummy choice2", "dummy choice 2"]
    # fetch_data(root, ".//sc:textLeaf[@role='mathtex']") # Maths expressions

def fetch_answer(root):
    return "dummy answer"

def parse_files(args, question_count, err_count, parser): # Copy all files in sourcedir/Prettified and prettify XML
    sourcedir = os.path.realpath(args.sourcedir)
    flashcard_list = []

    for file in os.listdir(sourcedir):
        question_count += 1
        workpath = os.path.join(sourcedir, file)
        if os.path.isfile(workpath):
            # XML Tree
            tree = etree.parse(workpath, parser)
            root = tree.getroot()
            
            # Create Flashcard instance
            flashcard = fetch_content(file, root)

            # If --force option has been declared, put in dummy text
            if (args.force == True):
                if (flashcard.complexity_level is None):
                    flashcard.complexity_level = "Missing Complexity Level"
                if (flashcard.education_level is None):
                    flashcard.education_level = "Missing Education Level"
                if (flashcard.licence_theme is None):
                    flashcard.licence_theme = "Missing Licence Theme"
                if (flashcard.subject is None):
                    flashcard.subject = "Missing Subject"        
            
            # Write output string and write in outfile
            ## Default output format
            if (args.a4paper == False):
                output = write_output(flashcard)
                if (flashcard.err_flag == False or args.force == True):
                    write_outfile(output)
                    if (args.force == True):
                        
                        if (flashcard.err_message is not ''):    
                            print(flashcard.err_message)
                else:
                    err_count += 1
                    if (args.logs == False):
                        print(flashcard.err_message)
                    else:
                        write_logs(flashcard)
            ## a4paper output format
            else:
                output = ""
                # Make a list of every flashcard in sourcedir
                flashcard_list.append(flashcard)
    # Once finished reading all files in sourcedir, write output and write into outfile.
    if (args.a4paper == True):
        # Write flashcards
        err_count = write_out_a4paper(flashcard_list)

    return (question_count, err_count)

def opale_to_tex(args):
    # Path validity check
    if (not os.path.isdir(args.sourcedir)):
        sys.stderr.write('Error: '+args.sourcedir+' is not a directory.\n')
        sys.exit(1)

    # Parser settings
    parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)

    # Variables
    (question_count, err_count) = (0,0)
    write_outfile_header()
    (question_count, err_count) = parse_files(args, question_count, err_count, parser)
    write_outfile_footer()

    # Termination messages
    ## Check if --force has been declared
    if (args.force == True):
        print("WARNING : Option force has been declared. Transcription will process regardless of missing metadata.\n 'Missing [metadata_name]' will be added to fill in the flashcard.\n Error count is false.\n")
    ## Check if --logs has been declared
    if (args.logs == True):
        print("WARNING : Option logs has been declared. Errors messages will be written in output/logs.txt")
    ## Display number of errors / number of questions
    print(str(err_count) + '/' + str(question_count) + ' flashcards have missing metadata errors')
    ## Informations
    print("The .tex file out.tex has been created in ./output directory. Compiling it will produce a pdf file containing all flashcards in the specified source directory.")
                
args = parser.parse_args()
opale_to_tex(args)