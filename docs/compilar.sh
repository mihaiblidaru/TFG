#!/bin/bash

# Limpiar archivos auxiliares
./limpiar.sh

# Compilar
pdflatex main.tex
bibtex main
makeglossaries main
pdflatex main.tex
pdflatex main.tex
mv main.pdf "Trabajo_Fin_De_Grado.pdf"

# Limpiar archivos auxiliares
./limpiar.sh