#!/bin/sh
#
# Generate test cases
#
set -euf
(set -o pipefail >/dev/null 2>&1) && set -o pipefail || :

mydir=$(dirname $(readlink -f "$0"))
export PYTHONPATH="$mydir/.."
ypp_cmd="$mydir/../py -m ypp"
test_cmd="$mydir/../py test-ypp.py"

(
  echo "Generating test credentials"
  cd $mydir/..
  $ypp_cmd <<-'_EOF_'
	$<pwgen:linux:24:md5>
	#keygen linux:priv:2048
	_EOF_
  tar zcvf "$mydir/demokeys.tgz" keys secrets.yaml
)

(
  sed -e 's/#.*$//' | (while read testcase args
  do
    testcase=$(echo "$testcase" | tr -d :)
    ([ -z "$testcase" ] || [ -z "$args" ]) && continue
    echo "$testcase|$args"
    ( set -x ; $test_cmd run $args > "$mydir/$testcase.json" )
  done)
) <<-'_EOF_'
	# Test cases

	# Basic command line test
	z00cli1:	-h

	# Test if Windows or Unix files are created
	z00empty1:	--windows --output output.txt data/empty.yaml
	z00empty2:	--unix --output output.txt data/empty.yaml


	# Basic
	z00pp1:		--json=2 -Idata/snippets data/pp.yaml
	z00pp2:		-Dmayday=1st.may -Dj.s=error -Idata/snippets --json=2 data/pp.yaml
	z00data:	data/xx.yaml

	# myotc test files
	z00demo20:	-Idata/snippets --json=2 data/demo2.yaml

	z00letest1:	-Idata/snippets --json=2 data/letest.yaml
	z00letest2:	-DSID=sys1 -Idata/snippets --json=2 data/letest.yaml
	z00letest3: 	-DUSE_ACME -DSID=sys1 -Idata/snippets --json=2 data/letest.yaml

	z00tsv21:	-Idata/snippets -DUSE_ACME --json=2 data/ts-v2.yaml
	z00tsv22: 	-Idata/snippets -DSID=tsv2 --json=2 data/ts-v2.yaml
	z00tsv23:	-Idata/snippets -DUSE_ACME -DSID=tsv2 --json=2 data/ts-v2.yaml

	_EOF_
