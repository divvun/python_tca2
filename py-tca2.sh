#!/bin/bash
# tca2 \
#     data/anchor-nob-fkv.txt \
#     data/kommisjonen_21.08.2020_nob.txt_nob.sent \
#     data/kommisjonen_21.08.2020_fkv.txt_fkv.sent

java \
    -Xms512m \
    -Xmx1024m \
    -jar /Users/bga001/repos/giellalt/CorpusTools/corpustools/tca2/dist/lib/alignment.jar \
    -cli-plain \
    -anchor=data/anchor-nob-fkv.txt \
    -in1=data/kommisjonen_21.08.2020_nob.txt_nob.sent \
    -in2=data/kommisjonen_21.08.2020_fkv.txt_fkv.sent