#!/bin/bash

ANCHOR=bug3/anchor-nob-sme.txt
IN1=bug3/samediggi-article-42.html_nob.sent
IN2=bug3/samediggi-article-42.html_sme.sent

tca2 \
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
