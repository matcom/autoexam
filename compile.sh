#! /bin/bash

cd generated/$1/
for f in *.tex ; do echo "Processing $f" ; pdflatex "$f" ; done
mkdir pdf
mv *.pdf pdf/
rm *.aux
mkdir src/
mv *.tex src/
mv *.png src/
mkdir log
mv *.log log/
