#!/usr/bin/python3
# encoding: utf-8
import sys
import os
import shutil
import unicodedata
import re
import argparse
import traceback

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
# print(namespace.keys())
# print(namespace.values())

# Parser settings
parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)

# Path validity check
if (not os.path.isdir(args.sourcedir)):
    sys.stderr.write('Error: '+args.sourcedir+' is not a directory.\n')
    sys.exit(1)

# Get absolute path
sourcedir = os.path.realpath(args.sourcedir)
for files in os.walk(sourcedir, topdown = False):
    for file_name in files:
        print(file_name)



# root = etree.XML("<root>dataaaa<test>data</test><test2>data</test2></root>")
# print(root[1].tag)