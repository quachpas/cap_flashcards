#!/bin/bash

/usr/bin/xelatex -synctex=1 --interaction=batchmode --file-line-error --shell-escape out.tex
/usr/bin/xelatex -synctex=1 --interaction=batchmode --file-line-error --shell-escape out.tex