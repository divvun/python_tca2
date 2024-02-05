#!/bin/bash

ANCHOR=bug3/anchor-nob-sme.txt
IN1=bug3/giella_no.docx_nob.sent
IN2=bug3/giella_sam.docx_sme.sent

/Users/bga001/Library/Caches/pypoetry/virtualenvs/python-tca2-vDuy0Iz_-py3.12/bin/tca2 \
    $ANCHOR \
    $IN1 \
    $IN2 > tca2.txt

java \
    -Xms512m \
    -Xmx1024m \
    -jar $GUTHOME/giellalt/CorpusTools/corpustools/tca2/dist/lib/alignment.jar \
    -cli-plain \
    -anchor=$ANCHOR \
    -in1=$IN1 \
    -in2=$IN2 2> compare.java.json 1> java.txt
