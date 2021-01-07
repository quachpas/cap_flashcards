#! /bin/bash
#
# Compile every scar file in a directory
#

if [ $# -ne 2 ]; then
	echo "Usage: $0 <input dir> <output dir>" >&2
	echo "  input dir: directory containing scar files with xml Scenari quiz" >&2
	echo "  output dir: directory that will have every pdf" >&2
	exit
fi

INDIR=$1
OUTDIR=$2

if [ ! -d $INDIR ] ; then
	echo "Input dir '$INDIR' is not a directory" >&2
	exit
fi
if [ ! -d $OUTDIR ] ; then
	echo "Output dir '$OUTDIR' is not a directory" >&2
	exit
fi

TMPDIR=$(mktemp -d)
UNZIPDIR="$TMPDIR/unzip"


for scarfile in "$INDIR"/*.scar ; do
	unzip $scarfile -d $UNZIPDIR
	content=$(basename "$scarfile" .scar)
	python3  ./Python/opale2flashcard.py $UNZIPDIR ./Example-files/themeLicence.xml --compile
	mv ./Python/output/out.pdf "$OUTDIR/$content-print.pdf"
	python3  ./Python/opale2flashcard.py $UNZIPDIR ./Example-files/themeLicence.xml --a4paper --compile
	mv ./Python/output/out.pdf "$OUTDIR/$content-a4.pdf"
	[[ "$UNZIPDIR" == /tmp/* ]] && rm -R "$UNZIPDIR"
done

[[ "$TMPDIR" == /tmp/* ]] && rm -R "$TMPDIR"

