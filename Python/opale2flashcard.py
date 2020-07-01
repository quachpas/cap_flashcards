#!/usr/bin/python3
# encoding: utf-8
import sys
import os, glob
import shutil
import unicodedata
import re
from PIL import Image
import argparse
from argparse import RawDescriptionHelpFormatter
import traceback
import xml.dom.minidom as minidom
import time
import timeit

from lxml import etree
from itertools import zip_longest

parser = argparse.ArgumentParser(description="""
=== Conversion from mcqMur/mcqSur (Opale-XML) to LaTeX (flashcard class) ===

--- Definition of a flashcard ---
Many elements make up a flashcard:
    1. Metadata : subject, education level, subject theme, complexity level.
    2. Content : question, choices, solutions, answer (explanations)
    3. Fixed elements : the subject icon and unisciel's logo. 

--- Source files integrity check ---
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
    Be aware that it replace missing metadata with 'Missing [metadata_name]'. 
3. Content size:
    Some flashcards have large content, these might overflow,
    and will be removed by default. 
    The criteria used to define that is a character count. 
    Q : Question, C : Choices, A : Answer
--- Output settings ---
The script will write in the './output/out.tex' file. 
The front is always output before the back of the flashcard. 
There are two output formats : 
    - default, the page's dimensions are 10x8 cm. 
    - a4paper, the output's format is an A4 page.
    Every page contains 6 flashcards (10x8 cm).
    A grid outlines the borders. 
    This is the preferred format for printing at home.
Some options can be used to filter the output (image_only, overflow_only, file_name [file_name])
Combining these options will join the results, duplicates might exist.
Using these options can help greatly in checking whether a flashcard is correctly transcripted.

--- Rich content ---
Some flashcards contents can be quite rich. 
Below, we define which content is supported or not.
1. Question:
    - ONE image maximum. We consider that fitting two images on one flashcard
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

--- Debugging tools ---
Some options are available to help debug the code and/or check if the output
is correct. 
Logs will be in './output/logs.txt'.

--- How to use ---
After cloning the repository, you should download a .scar archive from Scenari
and unzip it directly in the same directory (rename it to '*.zip').
Pass in the path to the directory containing the .quiz files to the script.
If you have xelatex installed, you can use the '--compile' option to directly
compile the pdf. 
""", formatter_class=RawDescriptionHelpFormatter)

parser.add_argument('sourcedir', help = """
XML files\' directory path - Path to root directory containing all XML files. 
N.B. : Unzipping a .scar archive is the simplest workaround to have the .quiz files locally. 
To refer correctly to the "000&" directory, you need to add an \ before. The path becomes "*/\&.
Example : python3 opale2flashcard.py faq2sciences/Physique-thermo_2020-2-11/\&
""")
parser.add_argument('themefile', help = """
Themes list file path - Path to an xml file containing all theme codes.
""")
parser.add_argument('--a4paper', action = 'store_true', help  ="""
Output format - (defaults to printing 10x8cm flashcards)
""")
parser.add_argument('--noclean', action = 'store_true', help  ="""
Clean output folder - Cleanse by default
""")
parser.add_argument('--force', action = 'store_true', help = """
Force the output - Ignores transcripts errors
""")
parser.add_argument('--compile', action = 'store_true', help = """
Compile output tex file - Automatically compiles out.tex file after the script and cleans the auxiliary files. Minimal console output.
""")
parser.add_argument('--verbose', action = 'store_true', help = """
Verbose ouput - Details missing metadata errors
""")
parser.add_argument('--logs', action = 'store_true', help = """
Logs output - Outputs warning and errors in output/logs.txt instead of writing in the console
""")
parser.add_argument('--debug_mode', action = 'store_true', help = """
Debug mode - Combined with file_name, prints out fetching contents. Solely use for debugging the script.
""")
parser.add_argument('--file_name', action = 'store', help = """
Debugging tool - Outputs only one file.
""")
parser.add_argument('--image_only', action = 'store_true', help = """
Debugging tool - Outputs only files with images. 
""")
parser.add_argument('--overflow_only', action = 'store_true', help = """
Debugging tool - Outputs only files with potential overflowing content.  
""")
parser.add_argument('--non_relevant_only', action = 'store_true', help = """
Debugging tool - Outputs only files with content flagged non-relevant.
""")
parser.add_argument('--no_replace', action = 'store_true', help = """
Question with image - Stops replacing "ci-dessous" with "ci-contre" for files with images in the question.  
""")
parser.add_argument('--add_url', action = 'store_true', help = """
Links to material - Adds urls to flashcards. Script won't output any links by default.
""")
# XML namespaces
namespace = {
    "sm" : "http://www.utc.fr/ics/scenari/v3/modeling",
    "sc" : "http://www.utc.fr/ics/scenari/v3/core",
    "op" : "utc.fr:ics/opale3",
    "sp" : "http://www.utc.fr/ics/scenari/v3/primitive",
    "xml" : "http://www.w3.org/XML/1998/namespace",
}

complexity_level = {
    '1' : "Connaître",
    '2' : "Changement de langage",
    '3' : "Comprendre, appliquer",
    '4' : "Analyser",
}

roles_markup = {
    "emp" : ("\emph{", "}"),
    "exp" : ("$^{", "}$"),
    "ind" : ("$_{", "}$"),
    "mathtex" : ("$", "$"),
    "url" : ("}", "{"),
}

tags_markup = {
    "textLeaf" : None,
    "inlineStyle" : None,
    "choiceLabel" : ("\item ", "\n"),
    "choiceExplanation" : None,
    "txt" : None,
    "para" : None,
    "phrase" : ("\href{", "}"),
}

class Flashcard:
    def __init__(self, file, question_type, complexity_level, subject, education_level, licence_theme, question, image, image_square, image_rectangular, choices, answer, solution_list, choice_number,subject_length, licence_theme_length, question_length, choices_length, answer_length):
        self.file = file
        self.question_type = question_type
        self.complexity_level = complexity_level
        self.subject = subject
        self.education_level = education_level
        self.licence_theme = licence_theme
        self.question = question
        self.image = image
        self.image_square = image_square
        self.image_rectangular = image_rectangular
        self.choices = choices
        self.answer = answer
        self.solution_list = solution_list
        self.choice_number = choice_number
        self.overflow_flag = False
        self.err_flag = False
        self.err_message = ""
        self.relevant = True
        self.subject_length = subject_length
        self.licence_theme_length = licence_theme_length
        self.question_length = question_length
        self.choices_length = choices_length
        self.answer_length = answer_length

def remove_namespace(element):
    return etree.QName(element)

def literal_QName(ns, tag):
    return '{' + namespace.get(ns) + '}' + tag

def fetch_data(file, element, expression):
    data = []
    output = ''
    for element in element.iterfind(expression, namespace):
        data.append(element.text)
    for x in data:
        output += x
    if (output == ''):
        return None
    return output

def get_role_markup(role):
    return roles_markup.get(role, None)

def get_tag_markup(tag):
    return tags_markup.get(tag, None)

def get_complexity_level(level):
    return complexity_level.get(level, None)

def get_subject_and_themes(filename, parser):
    licence_theme = {}
    subject = {}

    # Theme file 
    themefile = os.path.join(os.path.dirname(os.path.realpath(filename)), os.path.basename(filename))
    # File check
    if (themefile is None or os.path.isfile(themefile) is False):
        write_logs(
            "Themes list file does not exist (" + filename + ")",
            "Themes list file does not exist (" + filename + ")"
        )
        return None 
    
    # Parsing theme file

    themetree = etree.parse(themefile, parser)
    if (themetree is None):
        write_logs(
            "Cannot parse themefile using etree (" + filename + ")",
            "Cannot parse themefile using etree (" + filename + ")",
        )
        return None
    
    for theme in themetree.findall(".//sm:option", namespace):
        code = theme.get("key")
        name = theme.get("name")
        splitted_code = code.split("-")
        theme = cleantheme(name)
        # Subject
        if (splitted_code[1] == ''):
            subject.update({splitted_code[0] : theme})
        # Licence Theme
        else:
            licence_theme.update({splitted_code[1] : theme})
    return licence_theme, subject

def cleantheme(text):
    text=''.join((c for c in unicodedata.normalize('NFKC', text)))
    text=''.join(e for e in text if (e.isalnum() or ord(e)==ord(' ') or e in ['-', ',', '(', ')']))
    return text.strip()

def calc_vspace_parameters(flashcard):
    if (flashcard.image is not None):
        vspace_question = 0.10
        vspace_answer = 0.10
    else:
        vspace_question = 0.15
        vspace_answer = 0.10

    return (vspace_question, vspace_answer)


def get_licence_theme(licence_theme_dict, theme_code):
    if (licence_theme_dict.get(theme_code, None) is not None):
        return licence_theme_dict.get(theme_code, None)
    else:
        return ''

def get_subject(subject_dict, subject_code):
    if (subject_dict.get(subject_code, None) is not None):
        return subject_dict.get(subject_code, None)
    else:
        return ''

def get_output_directory():
    if (os.path.basename(os.getcwd()) == 'cap_flashcards'):
        return os.path.join(os.getcwd(), 'Python/output')
    elif (os.path.basename(os.getcwd()) == 'Python'):
        return os.path.join(os.getcwd(), 'output')
    else:
        write_logs(
            "Current working directory is neither cap_flashcards nor Python",
            "Current working directory is neither cap_flashcards nor Python"
        )
        return None

def get_headers_directory():
    if (os.path.basename(os.getcwd()) == 'cap_flashcards'):
        return os.path.join(os.getcwd(), 'Python')
    elif (os.path.basename(os.getcwd()) == 'Python'):
        return os.getcwd()
    else:
        write_logs(
            "Current working directory is neither cap_flashcards nor Python",
            "Current working directory is neither cap_flashcards nor Python"
        )
        return None

def check_metadata(flashcard):
    if (flashcard.complexity_level is None or flashcard.complexity_level == "Missing Complexity Level" 
            # or flashcard.education_level is None or flashcard.education_level == "Missing Education Level" 
            or flashcard.licence_theme is None or flashcard.licence_theme == "Missing Licence Theme"
            or flashcard.subject is None or flashcard.subject == "Missing Subject"):
        if (args.force == False):
            flashcard.err_flag = True
        if (args.verbose == True):
            flashcard.err_message += 'opale2flashcard.py: ' + flashcard.file + ' was not written in out.tex.\n' + 'Metadata is missing :'
            if (flashcard.complexity_level is None or flashcard.complexity_level == "Missing Complexity Level"):
                flashcard.err_message += "\t- Missing Complexity Level\n"
            # if (flashcard.education_level is None or flashcard.education_level == "Missing Education Level"):
            #     flashcard.err_message += "\t- Missing Education Level\n"
            if (flashcard.licence_theme is None or flashcard.licence_theme == "Missing Licence Theme"):
                flashcard.err_message += "\t- Missing Licence theme\n"
            if (flashcard.subject is None or flashcard.subject == "Missing Subject"):
                flashcard.err_message += "\t- Missing Subject\n"
        else:
            if (flashcard.err_message != ''):
                flashcard.err_message += '\nopale2flashcard.py(' + flashcard.file + "): Metadata is missing.\n"    
            flashcard.err_message += 'opale2flashcard.py(' + flashcard.file + "): Metadata is missing."

def check_generator(file, generator, expression):
    try:
        next(generator)
        return True
    except StopIteration:
        write_logs(
            None,
            'opale2flashcard.py(' + file + "): Missing question content. Tried looking for " + expression
        )
        return False

def check_overflow(flashcard):
    if (flashcard.image is None):
        if (
                flashcard.question_length + flashcard.choices_length > 530
                or flashcard.answer_length > 630
        ):
            flashcard.overflow_flag = True
            flashcard.err_message += 'opale2flashcard.py(' + flashcard.file +  '): No image - Potentially overflowing content (Q, C, A): ' + str(flashcard.question_length) + ' ' + str(flashcard.choices_length) + ' ' + str(flashcard.answer_length) + " "
    else:
        if (flashcard.image_square is True and flashcard.question_length + flashcard.choices_length > 240 or flashcard.image_rectangular is True and flashcard.question_length + flashcard.choices_length > 385 and flashcard.choices_length > 60 or flashcard.answer_length > 780):
            flashcard.overflow_flag = True
            flashcard.err_message += 'opale2flashcard.py(' + flashcard.file +  '): Image - Potentially overflowing content (Q, C, A): ' + str(flashcard.question_length) + ' ' + str(flashcard.choices_length) + ' ' + str(flashcard.answer_length) + " "
        if (flashcard.image.count("includegraphics") >= 2):
            flashcard.overflow_flag = True
            write_logs(
                'opale2flashcard.py(' + flashcard.file + '): WARNING ! There are at least two images in the question. Content might overflow',
                'opale2flashcard.py(' + flashcard.file + '): WARNING ! There are at least two images in the question. Content might overflow', 
            )
        if (flashcard.question.count("tabular") >= 1):
            flashcard.overflow_flag = True
            write_logs(
                'opale2flashcard.py(' + flashcard.file + '): WARNING ! There is at least one table in the question. Content might overflow',
                'opale2flashcard.py(' + flashcard.file + '): WARNING ! There is at least one table in the question. Content might overflow', 
            )
    if (args.debug_mode == True):
        print('opale2flashcard.py(' + flashcard.file +  ')(Debug): Image - Length (Q, C, A): ' + str(flashcard.question_length) + ' ' + str(flashcard.choices_length) + ' ' + str(flashcard.answer_length) + " ")

def check_content(flashcard):
    # Check irrelevant content in flashcard
    # Remove flashcard if not pertinent
    if ('http://' in flashcard.answer or 'https://' in flashcard.answer):
        flashcard.relevant = False
        flashcard.err_message += 'opale2flashcard.py(' + flashcard.file + "): Answer contains an URL."
    
    if (not flashcard.choices):
        flashcard.err_flag = True
        flashcard.err_message += 'opale2flashcard.py(' + flashcard.file + "): Flashcard does not have any choices."


def check_output(output, err_count):
    if (args.file_name is True and output.count("\\begin{flashcard}") != 1):
        write_logs(
            'opale2flashcard.py (--file_name) DANGER ! More than one flashcard.',
            'opale2flashcard.py (--file_name) DANGER ! Specified option "--file_name" did not work as expected. More than one flashcard in output file.',
        )
    if (args.image_only is True and output.count("\includegraphics[") < output.count("\\begin{flashcard}")):
        write_logs(
            'opale2flashcard.py (--file_name) DANGER ! Less images than expected.',
            'opale2flashcard.py (--file_name) DANGER ! Specified option "--image_only" did not work as expected. There are less images than flashcards.',
        )
    if (args.overflow_only is True and err_count != output.count("\\begin{flashcard}")):
        write_logs(
            'opale2flashcard.py (--file_name) DANGER ! Non-expected flashcards.',
            'opale2flashcard.py (--file_name) DANGER ! Specified option "--overflow_only" did not work as expected. The error_count does not coincide with the number of flashcards',
        )
    if (args.non_relevant_only is True and err_count != output.count("\\begin{flashcard}")):
        write_logs(
            'opale2flashcard.py (--file_name) DANGER ! Non-expected flashcards.',
            'opale2flashcard.py (--file_name) DANGER ! Specified option "--non_relevant_only" did not work as expected. The error_count does not coincide with the number of flashcards',
        )

def write_logs(err_message, verb_err_message):
    if (args.logs == False):
        if (args.verbose == True and verb_err_message is not None):
            print(verb_err_message)
        elif (err_message is not None):
            print(err_message)
    else:
        # Get output directory
        output_dir = get_output_directory()
        logsfile_path = os.path.join(output_dir, 'logs.txt')
        logs = open(logsfile_path, 'a', encoding = 'utf-8')
        if (args.verbose == True and verb_err_message is not None):
            logs.write(time.strftime('opale2flashcard.py:' + "%m-%d-%Y @ %H:%M:%S - ", time.localtime()) + verb_err_message + '\n')
        elif (err_message is not None):
            logs.write(time.strftime('opale2flashcard.py:' + "%m-%d-%Y @ %H:%M:%S - ", time.localtime()) + err_message + '\n')

def write_solution(question_type, solution_list, choice_number, question_count):
    output = ''
    if (question_count is not None and args.a4paper == True):
        (x_shift_1, x_shift_2, y_shift_1, y_shift_2) = solution_positions_a4paper(question_count)
    elif (args.a4paper == False):
        (x_shift_1, x_shift_2, y_shift_1, y_shift_2) = ('-0.25cm', '2.75cm', '2.25cm', '2.25cm')

    
    choice_number += 1

    output += "\\begin{tikzpicture}[remember picture, overlay]\n"
    output += "\\node [align=left, opacity=1] at ([xshift=" + x_shift_1 + ", yshift=" + y_shift_1 + "]current page.center) {\n"
    if (question_type == 'mcqMur'):
        output += "\\color{white}\n\\normalsize\\textsf{\\textit{Réponses}}\n};\n"
    if (question_type == 'mcqSur'):
        output += "\\color{white}\n\\normalsize\\textsf{\\textit{Réponse}}\n};\n"
    output += "\\node [align=left, opacity=1] at ([xshift=" + x_shift_2 + ", yshift=" + y_shift_2 + "]current page.center) {\n"

    for choice in range(1, choice_number):
        if (choice % 4 == 1):
            output += "\color{white}\n$"
        
        output += str(choice) + ':'
        if (choice in solution_list):
            output += '\\boxtimes'
        else:
            output += '\\square'
        if (choice % 4 == 0):
            output += "$"
            if (choice_number -1 > 4):
                output += "\\\\\n"
        else:
            output += "\\qquad"
        
    if ( (choice_number - 1) % 4 != 0):
        output += '$'      
        
    output += "};\n\\end{tikzpicture}\n"

    return output

def solution_positions_a4paper(question_count):
    #               1 2       2 1
    # QUESTIONS     3 4   =>  4 3      ANSWERS
    #               5 6       6 5
    # Positions are "reversed"
    if (question_count % 2 == 1):
        # Right side
        x_shift_1 = '3.1cm'
        x_shift_2 = '6.6cm'
    else :
        # Left side 
        x_shift_1 = '-7cm'
        x_shift_2 = '-3.5cm'

    if (question_count <= 2):
        # Upper
        y_shift_1 = '13.05cm'
        y_shift_2 = '13.06cm'
    elif (question_count <= 4):
        # Middle
        y_shift_1 = '5.05cm'
        y_shift_2 = '5.06cm'
    else:
        # Lower
        y_shift_1 = '-2.97cm'
        y_shift_2 = '-2.96cm'
    
    return (x_shift_1, x_shift_2, y_shift_1, y_shift_2)

def fetch_content(file, root, licence_theme_dict, subject_dict):
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
    if (remove_namespace(root[0]).localname == "mcqMur"):
        question_type = "mcqMur"
    ## Licence Theme and subject
    theme_code = fetch_data(file, root, ".//sp:themeLicence")
    if (theme_code is not None and theme_code != ''):
        
        splitted = theme_code.split('-')
        # Case where there are multiple licenceTheme
        # We just concatenate them with the delimiter '/' for subjects and '\n' for themes
        # The probability that there is more than two themes is low.
        if (len(splitted) > 3):
            for x in range(0, len(splitted)-1, 2):
                # One theme
                if (len(splitted) - 1 - x == 2):
                    # If subjects or licence_theme have not been initialised
                    if (subject is None):
                        subject = get_subject(subject_dict, splitted[x])
                    else:
                        if (subject != get_subject(subject_dict, splitted[x])):
                            subject += '/' + get_subject(subject_dict, splitted[x])
                    if (licence_theme is None):
                        licence_theme = get_licence_theme(licence_theme_dict, splitted[x+1])
                    else:
                        if (licence_theme != get_licence_theme(licence_theme_dict, splitted[x+1])):
                            licence_theme += '\\\\' + get_licence_theme(licence_theme_dict, splitted[x+1])    
                # Two themes
                else:
                    # If subjects or licence_theme have not been initialised
                    if (subject is None):
                        subject = get_subject(subject_dict, splitted[x])
                    else:
                        if (subject != get_subject(subject_dict, splitted[x])):
                            subject += '/' + get_subject(subject_dict, splitted[x])
                    
                    if (licence_theme is None):
                        licence_theme = get_licence_theme(licence_theme_dict, splitted[x+1])
                    else:
                        if (licence_theme != get_licence_theme(licence_theme_dict, splitted[x+1])):
                            licence_theme += '\\\\' + get_licence_theme(licence_theme_dict, splitted[x+1])
        # Single licenceTheme
        else:
            subject = get_subject(subject_dict, splitted[0])
            licence_theme = get_licence_theme(licence_theme_dict, splitted[1])
        
    else:
        subject = None
        licence_theme = None

    ## Complexity level
    complexity_level = get_complexity_level(fetch_data(file, root, ".//sp:level"))
    ## Education level
    education_level = fetch_data(file, root, ".//sp:educationLevel")
    ## Content
    ### Question

    (question, question_length, image, square, rectangular) = fetch_question(file, root)
    (choices, choices_length) = fetch_choices(file, root)
    ### Answer
    (answer, answer_length) = fetch_answer(file, root)
    (solution_list, choice_number) = fetch_solution(file, root, question_type)

    # Create Flashcard instance
    
    if (subject == None):
        subject = ''
        subject_length = 0
    else:
        subject_length = len(subject)
    if (licence_theme == None):
        licence_theme_length = 0
    else:
        licence_theme_length = len(licence_theme)
    
    flashcard = Flashcard(file, question_type, complexity_level, subject, education_level, licence_theme, question, image, square, rectangular, choices, answer, solution_list, choice_number, subject_length, licence_theme_length, question_length, choices_length, answer_length)

    return flashcard

def output_cleanup(output):
    # Delete control characters like \n \t \r
    translator = str.maketrans('\n\t\r', '   ')
    if (type(output) == list):
        for index in range(len(output)):
            if ('\n' or '\t' or '\r' in output[index]):
                output[index] = output[index].translate(translator)
            if (type(output[index]) == str):
                output[index] = output[index].translate(translator)
            elif (type(output[index]) == list):
                output[index] = ''.join(output_cleanup(output[index]))
    if (type(output) == str):
        output = output.translate(translator)
    return output

def texfilter(text):
    # text = text.replace('~','\\textasciitilde')
    # text = text.replace('^','\\textasciicircum')
    text = text.replace('&','\\&')
    text = text.replace('%','\\%')
    text = text.replace('ˉ', '$^{-}$')
    # text = text.replace('$','\\$')
    text = text.replace('#','\\#')
    # text = text.replace('_','\\_')
    # text = output_cleanup(text)
    return text

def markup_content(file, element):
    output = []
    url = None
    text = None
    if (type(element) is not etree._Element):
        print("Error type")

    localname = remove_namespace(element).localname

    if (localname == 'phrase' and args.add_url is not True):
        tag_markup = None
    else:
        tag_markup = get_tag_markup(localname)
        
    if (tag_markup is not None):
        output.append(tag_markup[0])

    # Check if there are attributes that are different from xml:space="preserve"
    if bool(element.attrib and element.attrib.keys()[0] != literal_QName('xml', 'space')):
        for key, value in zip(element.attrib.keys(), element.attrib.values()):
            if (key == 'role' and value != ""):
                role_markup = get_role_markup(value)
                # Special case for urls
                if (value == 'url' and args.add_url is not True):
                    role_markup = None
                elif (value == 'url'):
                    for url in element.iterfind(".//sp:url", namespace):
                        url = texfilter(url.text)
                    text = element.xpath('text()')
                    text = output_cleanup(text[0])
                # element.text = texfilter(element.text)
            else:
                role_markup = None        
    else:
        role_markup = None

    if url is not None:
        output.append(url)
    if (role_markup is not None):
        output.append(role_markup[0])
    if url is None:
        if element.text is not None:
            output.append(element.text)
    if (role_markup is not None):
        output.append(role_markup[1])
    if text is not None:
        output.append(text)
    if (tag_markup is not None):
        output.append(tag_markup[1])
    
    output = output_cleanup(output)
    return ''.join(output)

def tail_gen(file, node, url):
    yield node
    
    for child in node:
        if (args.add_url == True and child.attrib and child.attrib.keys()[0] == 'role' and child.attrib.values()[0] == 'url'):
            # Don't strip the tail from the phrase node whose role is url.
            url = True
        yield from tail_gen(file, child, url)
    
    if node.tail is not None:
        if (args.add_url == True):
            if (url is not True):
                tail = node.tail.strip()
            elif (remove_namespace(node).localname == 'urlM'):
                tail = None
                url = False
            else:
                tail = node.tail.strip()
        else:
            if (remove_namespace(node).localname == 'phrase'):
                tail = node.tail
            else:
                tail = node.tail
    else:
        tail = None
    
    if tail is not None:
        yield tail

def mixed_content_parsing(file, node):
    output = ''
    gen = tail_gen(file, node, False)
    for element in gen:
        if (type(element) != str):
            if (remove_namespace(element).localname == 'url'):
                continue
        if ((type(element) == etree._Element)):
            if (element.text != ' '):
                output += markup_content(file, element)
            if (args.file_name == file and args.debug_mode is True):
                print("MIXED CONTENT PARSING ->" + output + '/')
        elif (element):
            output += texfilter(element)
            if (args.file_name == file and args.debug_mode is True):
                print("MIXED CONTENT PARSING ->" + output + '/')                


    return output

def fetch_question(file, root):
    output = ''
    text_length = 0
    square = False
    rectangular = False
    image = "\hfill\n\\begin{minipage}[t]{0.4\linewidth}\n\strut\\vspace*{-\\baselineskip}\\newline\n"
    path_to_image = ''
    # Questions can have rich content (images, etc.), so we examine every children
    check_generator(file , root.iterfind(".//sc:question/op:res", namespace), './/sc:question/op:res')
    for element in root.iterfind(".//sc:question/op:res", namespace):
        for section in element.getchildren():
            # Section is a text paragraph
            if (remove_namespace(section).localname == 'txt'):
                for child in section.find('op:txt', namespace):
                    # Text
                    if (remove_namespace(child).localname == 'para'):
                        output += mixed_content_parsing(file, child)
                        text_length += len(mixed_content_parsing(file, child))
                        output += '\n'

                    # Table 
                    if (remove_namespace(child).localname == 'table'):
                        output += "\n\\begin{center}\n\\tabcolsep=0.11cm\n\\begin{tabular}{"
                        for column in child.iterfind(".//sc:column", namespace):
                            output += '| c '
                        output += '|}\n'
                        for row in child.iterfind(".//sc:row", namespace):
                            output += '\hline\n'
                            for cell in row.iterfind(".//sc:cell", namespace):
                                for content in cell.iter():
                                    if (content.text is not None and not str.isspace(content.text)):
                                        output += markup_content(file, content) + '&'
                            output = output[:-1] # Remove the additional &
                            output += '\\\\\n'
                        output += '\hline\n'
                        output += "\n\\end{tabular}\n\\end{center}\n"

            # Section is a ressource
            if (remove_namespace(section).localname == 'res'):
                for root, dirs, files in os.walk(args.sourcedir):
                    for name in files:
                        if(name == section.attrib.values()[0].split("/")[-1]):
                            path_to_image = os.path.abspath(os.path.join(root, name))
                if (not path_to_image.endswith('.gif')):
                    image += "\\includegraphics[max size={\\textwidth}{0.4\\textheight}, center, keepaspectratio]{" + path_to_image + "}\n"
                else:
                    write_logs(
                        file + ' > Found a .gif ressource/image. Not supported',
                        file + ' > Found a .gif ressource/image. Not supported'
                    )

    # unchanged -> no image
    if (image == "\\hfill\n\\begin{minipage}[t]{0.4\linewidth}\n\\strut\\vspace*{-\\baselineskip}\\newline\n"):
        image = None
    elif (image is not None):
        image += '\n\\end{minipage}'
        if (args.no_replace == False):
            output = output.replace("ci-dessous", "ci-contre")
        # print(path_to_image)
        (width, height) = Image.open(path_to_image).size
        if (width / height > 0.825):
            square = False
            rectangular = True
        else:
            square = True
            rectangular = False

    if (args.debug_mode is True and args.file_name == file):
        print('QUESTION\n' + output)

    return (output, text_length, image, square, rectangular)

def fetch_choices(file, root):
    output_arr = []
    output = ''
    text_length = 0
    # Choice is text-only
    check_generator(file, root.iterfind(".//sc:choice//sc:choiceLabel", namespace), './/sc:choice//sc:choiceLabel')
    i = 1
    for element in root.iterfind(".//sc:choice//sc:choiceLabel//op:txt", namespace):
        output += '\\item [' + str(i) + '.]'
        for child in element.getchildren():
            output += mixed_content_parsing(file, child)
            text_length += len(mixed_content_parsing(file, child))
        if(output == '\\item [' + str(i) + '.]'):
            output = ''
        else:
            output += '\n'
            output_arr.append(output)
            output = ''
            i += 1
    
    if (args.file_name == file and args.debug_mode is True):
        print('CHOICES\n' + ''.join(output_arr))
    return (output_arr, text_length)

def fetch_answer(file, root):
    output = ''
    text_length = 0
    number_list = []
    number_counter = 0
    choice_number = 0

    # Explanations for each choices
    choice_explanation_bool = check_generator(file, root.iterfind(".//sc:choice//sc:choiceExplanation//op:txt", namespace), './/sc:choice//sc:choiceExplanation//op:txt')
    if (choice_explanation_bool == True):
        output += '\\begin{enumerate}\n'
        # Associate each explanation to a choice number
        for choice in root.iterfind(".//sc:choice//", namespace):
            if (remove_namespace(choice.tag).localname == 'choiceLabel'):
                choice_number += 1
            if (remove_namespace(choice.tag).localname == 'choiceExplanation'):
                number_list.append(choice_number)
    for element in root.iterfind(".//sc:choice//sc:choiceExplanation/op:txt", namespace):
        text = ''
        for e in element.iter():
            # Find text
            if e.text is not None:
                text += e.text
        
        # If text
        if (text != ''):
            output += '\\item [' + str(number_list[number_counter]) +'.]'
        for child in element.getchildren():
            choice_explanation = mixed_content_parsing(file, child)
            text_length += len(mixed_content_parsing(file, child))
            # op:txt can exist if there is a comment
            if (choice_explanation != ''):
                output += choice_explanation
                output += '\n'
        number_counter += 1
        
    if (check_generator(file, root.iterfind(".//sc:choice//sc:choiceExplanation//op:txt", namespace), './/sc:choice//sc:choiceExplanation//op:txt') == True):
        output += '\\end{enumerate}\n'

    # Global Explanation
    global_explanation_bool = check_generator(file , root.iterfind(".//sc:globalExplanation//op:txt", namespace), './/sc:globalExplanation//op:txt')
    for element in root.iterfind(".//sc:globalExplanation//op:txt", namespace):
        for child in element.getchildren():
            output += mixed_content_parsing(file, child)
            text_length += len(mixed_content_parsing(file, child))
            output += '\n\n'

    if (choice_explanation_bool and global_explanation_bool):
        write_logs(
            None,
            'opale2flashcard.py(' + file + '): WARNING ! Both choice explanations and global explanation exist,\n the content on the back of the flashcard might overflow.\n Please manually check the corresponding flashcard using the option "--debug_mode"'
        )
    if (not choice_explanation_bool and not global_explanation_bool):
        if (args.file_name is not None):
            if (args.file_name == file):
                write_logs(
                    'opale2flashcard.py(' + file + '): WARNING ! This flashcard has an issue. There is nothing on the back.',
                    'opale2flashcard.py(' + file + '): WARNING ! Both choice explanations and global explanations are empty.'
                )
        else:
            write_logs(
                'opale2flashcard.py(' + file + '): WARNING ! This flashcard has an issue. There is nothing on the back.',
                'opale2flashcard.py(' + file + '): WARNING ! Both choice explanations and global explanations are empty.'
            )
    if (args.file_name == file and args.debug_mode is True):
        print('ANSWER\n' + output)
    output = texfilter(output)
    #output = output_cleanup(output)
    
    return (output, text_length)

def fetch_solution(file, root, question_type):
    solution_list = []
    choice_number = 0 

    if (question_type == 'mcqMur'):
        for choice in root.findall(".//sc:choice", namespace):
            choice_number += 1
            if (choice.attrib.values()[0] == 'checked'):
                solution_list.append(choice_number)
    
    if (question_type == 'mcqSur'):
        for choice in root.findall(".//sc:choice", namespace):
            choice_number += 1

        for solution in root.iterfind(".//sc:solution", namespace):
            solution_list = [int(i) for i in solution.attrib.values()]

    if (not solution_list):
        write_logs(
            'opale2flashcard.py(' + file + '): WARNING ! This flashcard has an issue. No solutions found.',
            'opale2flashcard.py(' + file + '): WARNING ! The solution_list is empty. Question type was : ' + question_type + '.'
        )


    return (solution_list, choice_number)


def process_error(flashcard):
    if (args.file_name is not None or args.image_only is True or args.overflow_only is True or args.non_relevant_only is True):
        if (args.file_name == flashcard.file and args.file_name is not None):
            write_logs(
                flashcard.err_message,
                flashcard.err_message
            )
        else:
            if (flashcard.image is not None and args.image_only is True):
                write_logs(
                    flashcard.err_message,
                    flashcard.err_message
                ) 
            if (flashcard.overflow_flag is True and args.overflow_only is True):
                write_logs(
                    flashcard.err_message,
                    flashcard.err_message
                )
            if (flashcard.relevant is False and args.non_relevant_only is True):
                write_logs(
                    flashcard.err_message,
                    flashcard.err_message
                )
    # Else, just process the error message
    else:
        write_logs(
            flashcard.err_message,
            flashcard.err_message
        ) 
def process_write_outfile(flashcard, output):
    # If any output options have been declared
    if (args.file_name is not None or args.image_only is True or args.overflow_only is True or args.non_relevant_only is True):
        # Treat each `option`
        if (args.file_name == flashcard.file and args.file_name is not None):
            write_outfile(output, flashcard.subject.lower())
            write_outfile(output, None)
        if (flashcard.image is not None and args.image_only is True):
            write_outfile(output, flashcard.subject.lower())
            write_outfile(output, None)
        if (flashcard.overflow_flag is True and args.overflow_only is True):
            write_outfile(output, flashcard.subject.lower())
            write_outfile(output, None)
        if (flashcard.relevant is False and args.non_relevant_only is True):
            write_outfile(output, flashcard.subject.lower())
            write_outfile(output, None)
    # Else, just write the output if the flashcard is valid, or force option has been set
    elif (flashcard.err_flag is False and flashcard.overflow_flag is False and flashcard.relevant is True or args.force == True):
        write_outfile(output, flashcard.subject.lower())
        write_outfile(output, None)
    else:
        rejected = flashcard.subject.lower() + '-rejected'
        write_outfile(output, rejected)
        write_outfile(output, 'rejected')

def write_output(flashcard, question_count):
    # Variables
    output = []
    (vspace_question, vspace_answer) = calc_vspace_parameters(flashcard)
    
    # Output
    output.append('% Flashcard : ' + flashcard.file + '/' + flashcard.question_type + '\n')
    output.append('% (Q, C, A) : ' + str(flashcard.question_length) + ', ' + str(flashcard.choices_length) + ', ' + str(flashcard.answer_length) + '\n')

    output.append('\\cardbackground\n{' + flashcard.complexity_level + '}\n{' + flashcard.subject + '}\n{' + flashcard.licence_theme + '}\n{' + 'qrcode}\n')
    # TODO : Qrcode ici, hardcoded. HARDCODED

    output.append('\\begin{flashcard}[]{\n\\color{black}\n')
    output.append('\\vspace{' + str(vspace_question) + '\\textheight}\n\\RaggedRight\n')

    # Question + Choices
    if (flashcard.image is not None):
        output.append('\\begin{minipage}[t]{0.55\\linewidth}\n')
    output.append(flashcard.question + '\n')
    
    # Image is square, 1x2 grid
    if (flashcard.image_rectangular is False):
        output.append('\\begin{enumerate}\n')
        for choice in flashcard.choices:
            output.append(choice)
        output.append('\\end{enumerate}\n')

    if (flashcard.image is not None):
        output.append('\\end{minipage}\n')
        output.append(flashcard.image + '\n')

    # Image is rectangular, 2x2 grid
    if (flashcard.image_rectangular is True):
        if (len(flashcard.choices) % 2 == 0):
            minipage_length = str(0.90/(len(flashcard.choices)//2))
        else:
            minipage_length = str(0.90/(len(flashcard.choices)//2+1))
        output.append('\\begin{minipage}[l]{' + minipage_length + '\\linewidth}\n\\begin{enumerate}\n')
        i = 0
        for choice in flashcard.choices:
            if (i % 2 == 0 and i != 0):
                output.append('\\end{enumerate}\n\\end{minipage}\n\\hfill\n')
                output.append('\\begin{minipage}[l]{' + minipage_length + '\\linewidth}\n\\begin{enumerate}\n')
            output.append(choice)
            i += 1
        output.append('\\end{enumerate}\n\\end{minipage}\n\\hfill\n')

    output.append('}\n')
    output.append('\\vspace*{\\stretch{1}}\n\\color{white}\n')
    # Answer/Solution
    output.append(write_solution(flashcard.question_type, flashcard.solution_list, flashcard.choice_number, question_count))
    output.append('\\vspace{' + str(vspace_answer) + '\\textheight}\n\\RaggedRight\n')
    
    output.append(flashcard.answer + '\n')
    output.append('\\vspace*{\\stretch{1}}\n\\end{flashcard}\n\n')
    
    return output
   
def write_out_a4paper(flashcard_list):
    output_list = []
    footer = ['\\cardfrontfooter']
    question_count = 0 # Keeps track which question we're processing on a page [0-6]
    question_number = 0 # Keeps track of which question we're processing in flashcard_list [0-len(flashcard_list)]
    error_count = 0 # Tracking number of questions with missing metadata

    # Main Loop
    for fc in flashcard_list:
        question_number += 1
        question_count += 1
        output_list.append(write_output(fc, question_count))
        if (question_count != 6 and len(flashcard_list) - question_number >= 1):
            # If len(flashcard_list) - question_number is between 6 and 1, then we're processing the last page of flashcards
            # The number of remaining flashcards will not be sufficient to do another loop
            # So we treat the last flashcard separately 
            footer.append('{' + fc.complexity_level + '}\n')
        elif (len(flashcard_list) - question_number == 0 ):
            footer.append(fc.complexity_level + '}\n')
        else:
            question_count = 0
            footer.append('{' + fc.complexity_level + '}\n')
            output = ''.join(footer)
            for fc in output_list:
                output += ''.join(fc)
            write_outfile(output, fc.subject.lower())
            output = ''
            output_list = []
            footer = ['\cardfrontfooter']

    # Writing "\cardfrontfooter{.}{.}{.}{.}{.}{.}"
    output = ''.join(footer)

    # Adding the missing empty parameters to \cardfrontfooter
    for _ in range(0, 6 - question_count):
        output += '{}\n'

    # Writing output string
    for fc in output_list:
        output += ''.join(fc)
    
    write_outfile(output, fc.subject.lower())

    return error_count

def write_outfile(output, subject):
    # Get output directory
    output_dir = get_output_directory()
    if (subject is not None and subject != ''):
        outfile_path = os.path.join(output_dir, 'out-' + subject.lower() + '.tex')
    else:
        outfile_path = os.path.join(output_dir, 'out.tex')
    # Open outfile
    outfile = open(outfile_path, 'a', encoding = 'utf-8')
    # Write content
    outfile.write(''.join(output))
    outfile.close

def write_outfile_header(subject_set):
    # Get output directory
    output_dir = get_output_directory()
    if ('' in subject_set):
        subject_set.remove('')
    for subject in subject_set:
        outfile_path = os.path.join(output_dir, 'out-' + subject.lower() + '.tex')
        
        write_header(output_dir, outfile_path)    

    outfile_path = os.path.join(output_dir, 'out.tex')
    write_header(output_dir, outfile_path)  

def write_header(output_dir, outfile_path):
    # Get headers' directory
    headers_dir = get_headers_directory()
    header_default_path = os.path.join(headers_dir, 'header_default.tex')
    header_a4paper_path = os.path.join(headers_dir, 'header_a4paper.tex')

    # Directory and file output
    if os.path.isdir(output_dir) is None:
        os.mkdir(output_dir)
    if os.path.isfile(outfile_path):
        os.remove(outfile_path)

    # Open outfile 
    outfile = open(outfile_path, 'a', encoding = 'utf-8')

    # Write header
    if (args.a4paper == True):
        header = open(header_a4paper_path,'r', encoding="utf-8")
    else:
        header = open(header_default_path,'r', encoding="utf-8")
    for line in header.readlines():
        if ('% Graphicspath' not in line):
            outfile.write(line)
        else:
            outfile.write('\graphicspath{{' + output_dir + '/images/' + '}' + '}\n')
    outfile.write('\n\n')
    header.close

    outfile.close 

def write_outfile_footer(subject_set):
    # Get output directory
    output_dir = get_output_directory()
    if ('' in subject_set):
        subject_set.remove('')
    for subject in subject_set:
        outfile_path = os.path.join(output_dir, 'out-' + subject.lower() + '.tex')

        write_footer(output_dir, outfile_path)

    outfile_path = os.path.join(output_dir, 'out.tex')
    write_footer(output_dir, outfile_path)

def write_footer(output_dir, outfile_path):
    # Get headers' directory
    headers_dir = get_headers_directory()
    footer_path = os.path.join(headers_dir, 'footer.tex')
    
    # Open outfile 
    outfile = open(outfile_path, 'a', encoding = 'utf-8')

    # Write footer
    outfile.write('\n\n')
    footer = open(footer_path,'r', encoding="utf-8")
    for line in footer.readlines():
        outfile.write(line)
    
    footer.close

def write_background_parameter(flashcard):
    backgroundparam = ['\\backgroundparam\n{' + flashcard.subject.lower() + '}\n{' + flashcard.subject.lower() + '-front-header}\n{' + flashcard.subject.lower() + '-front-footer}\n{' + flashcard.subject.lower() + '-back-background}\n{' + flashcard.subject.lower() + '-back-header}\n{' + flashcard.subject.lower() + '-back-footer}\n{front-university-logo}\n{back-university-logo}\n']
    write_outfile(backgroundparam, flashcard.subject.lower())
    write_outfile(backgroundparam, None)

def write_flashcards(flashcard_list):
# Write output string and write in outfile
## Default output format
    output = []
    if (args.a4paper == False):
        question_count = 0
        for flashcard in flashcard_list:
            # Background parameters
            if (args.force is True
            or ((flashcard.overflow_flag is False and flashcard.err_flag is False) and 
                (question_count == 0 or flashcard_list[question_count-1].subject.lower() != flashcard_list[question_count].subject.lower()))):
                write_background_parameter(flashcard)
            # Create a standard output only if the flashcard's errors flags are not set (or force option has been set)
            # OR if any debug "only-options" are used
            if ((flashcard.err_flag is False and flashcard.overflow_flag is False and flashcard.relevant is True) 
            or (args.image_only is True or args.overflow_only is True or args.non_relevant_only is True)
            or args.force is True):
                for out in write_output(flashcard, None):
                    output.append(out)
            
            # Write in the outfile only the valid files
            process_write_outfile(flashcard, output)
            output = []
            question_count += 1

def sort_flashcards_by_subject(flashcard_list, subject_set):
    sorted_list = []
    subject = ''
    for subject in subject_set:
        for fc in flashcard_list:
            if (fc.subject == subject):
                sorted_list.append(fc)    
        
    return sorted_list

def parse_files(args, question_count, err_count, parser, licence_theme, subject): # Copy all files in sourcedir/Prettified and prettify XML
    sourcedir = os.path.abspath(args.sourcedir)
    subject_list = []
    flashcard_list = []

    for file in os.listdir(sourcedir):
        # Ignore all files which are not .quiz
        if (file.endswith(".quiz") is False):
            continue
        # File name option
        if (args.file_name is not None and file != args.file_name):
            continue

        workpath = os.path.join(sourcedir, file)
        if os.path.isfile(workpath):
            # XML Tree
            tree = etree.parse(workpath, parser)
            root = tree.getroot()
            
            # Create Flashcard instance
            flashcard = fetch_content(file, root, licence_theme, subject)
            subject_list.append(flashcard.subject)
            
            # Check overflow
            check_overflow(flashcard)
                        
            # Check metadata
            check_metadata(flashcard)

            # Check non-pertinent content (URLs)
            check_content(flashcard)
            
            # Process errors, ignore flashcards not concerned
            if (args.image_only is True and flashcard.image is None):
                continue
            elif (args.overflow_only is True and flashcard.overflow_flag is False):
                continue
            elif (args.non_relevant_only is True and flashcard.relevant is True):
                continue

            # If --force option has been declared, put in dummy text to avoid compilation errors
            if (args.force == True):
                if (flashcard.complexity_level is None):
                    flashcard.complexity_level = "Missing Complexity Level"
                if (flashcard.licence_theme is None):
                    flashcard.licence_theme = "Missing Licence Theme"
                if (flashcard.subject is None):
                    flashcard.subject = "Missing Subject"        
            
            # Error procedure
            if (flashcard.err_flag is True or flashcard.overflow_flag is True or flashcard.relevant is False):
                err_count += 1
                process_error(flashcard) 
            
            # If a flashcard has been forcibly output, and its error message is not null
            if (args.force == True and flashcard.err_message != ''):
                err_count += 1
                process_error(flashcard)

            # Make a list of every flashcard in sourcedir
            flashcard_list.append(flashcard)
        
        question_count += 1

    return (flashcard_list, subject_list, question_count, err_count)

def compile_tex(args):
    if (args.compile == True):
        
        os.chdir(get_output_directory())
        os.system("xelatex --synctex=1 --interaction=batchmode --file-line-error --shell-escape out.tex")
        os.system("xelatex --synctex=1 --interaction=batchmode --file-line-error --shell-escape out.tex")

def clean_tex(args):
        
    for filename in glob.glob(os.path.join(get_output_directory(), "out*")):
        os.remove(filename)

def opale_to_tex(args):
    # Path validity check
    if (not os.path.isdir(args.sourcedir)):
        sys.stderr.write('Error source directory: ' + args.sourcedir + ' is not a directory or does not exist.\n')
        sys.exit(1)
    if (not os.path.isfile(args.themefile)):    
        sys.stderr.write('Error themefile: ' + args.themefile +' is not a file or does not exist.\n')
        sys.exit(1)
    if (args.file_name is not None):
        if (not os.path.isfile(os.path.realpath(args.sourcedir + "/" + args.file_name))):
            sys.stderr.write('Error: ' + args.file_name +' is not a file or does not exist.\n')
            sys.exit(1)
    
    # Parser settings
    parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
    # Theme tree

    # clean output directory
    if (args.noclean is False):
        clean_tex(args)
    
    # Comment this line if you want to use a hard-coded dictionary
    (licence_theme, subject) = get_subject_and_themes(args.themefile, parser)
    # Example hard-coded dictionary
    # licence_theme = {
    #     'strucmat': 'Structure de la matière',
    #     'them': 'Complete theme'
    # }
    # subject = {
    #     '#subj': 'Subject',
    #     '#math': 'Mathematics'
    # }

    # Variables
    (question_count, err_count) = (0,0)
    
    (flashcard_list, subject_list, question_count, err_count) = parse_files(args, question_count, err_count, parser, licence_theme, subject)
    
    sorted_list = sort_flashcards_by_subject(flashcard_list, set(subject_list))
    write_outfile_header(set(subject_list))
    write_flashcards(sorted_list)
    write_outfile_footer(set(subject_list))

    # Check out.tex


    # Compile out.tex if option --compile has been declared
    compile_tex(args)

    # Termination message
    ## Check if --force has been declared
    if (args.force == True):
        print("WARNING : Option force has been declared. Transcription will process regardless of missing metadata.\n 'Missing [metadata_name]' will be added to fill in the flashcard.\n Error count may be wrong.\n")
    ## Check if --logs has been declared
    if (args.logs == True):
        print("WARNING : Option logs has been declared. Errors messages will be written in output/logs.txt")
    ## Check if --debug_mode has been declared
    if (args.debug_mode == True):
        print("WARNING : Mode debug has been declared. The filename will be written next to the theme level.")
    if (args.overflow_only == True):
        print("WARNING : Only potentially overflowing cards have been written in out.tex")
    ## Display number of errors / number of questions
    print('opale2flashcard.py: ' +str(err_count) + '/' + str(question_count) + ' flashcards errors, either metadata or overflowing content.\n These files will not be transcripted. Use option "--force" to ignore.\n')

    ## Informations
    if (args.no_replace == False):
        print('WARNING : We replaced every occurence of "ci-dessous" in the question by "ci-contre". If it was a mistake, please modify as necessary.\n Use option "--no_replace" to deactivate this feature.')
    print('Please make use of the "--XXX-only" options to check every flashcard for potential defects')

    if (args.compile == False):
        print("opale2flashcard.py: The .tex file out.tex has been created in ./output directory. Compiling it will produce a pdf file containing all flashcards in the specified source directory.\n Use option '--compile' if you want to compile directly after. You must have xelatex installed.")
    else:
        print("The .tex file has been compiled. The output pdf is in ./output directory. Please refer to output.log for eventual compilation errors.")

start_time = time.time()                
args = parser.parse_args()
opale_to_tex(args)
print("The script took {0:0.3f} seconds to complete.".format(time.time() - start_time))
