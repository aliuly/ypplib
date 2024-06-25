#!/bin/sh

#~ sh py -m ypp -h
#~ sh py -m ypp --unix -o output.txt -Dmayday=1st.may -Dj.s=error -Idata/snippets data/pp.yaml
#~ sh py -m ypp --unix -o output.txt -Idata/snippets --json data/demo2.yaml
#~ sh py -m ypp --unix -o output.txt -Idata/snippets  data/letest.yaml
#~ sh py -m ypp --unix -o output.txt -DSID=sys1 -Idata/snippets --json data/letest.yaml
#~ sh py -m ypp data/xx.yaml
#~ sh py -m ypp -o output.txt -Idata/snippets -DSID=tsv2 --json data/ts-v2.yaml
#~ sh py -m ypp --unix -o output.txt -DUSE_ACME -DSID=sys1 -Idata/snippets --json data/letest.yaml
sh py -m ypp -o output.txt -Idata/snippets -DUSE_ACME -DSID=tsv2 --json data/ts-v2.yaml

