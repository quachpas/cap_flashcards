#!/bin/bash

xelatex -synctex=1 --interaction=batchmode --file-line-error --shell-escape out.tex
xelatex -synctex=1 --interaction=batchmode --file-line-error --shell-escape out.tex