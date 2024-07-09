#!/bin/sh
#
# Run doctests
#
if [ $# -eq 0 ] ; then
  echo "Usage: $0 {directory}"
  exit 1
fi

cd "$1" || exit 1
find . -maxdepth 1 -mindepth 1  -name '*.py' | (
  rc=0
  while read pyfile
  do
    if grep -q 'import doctest' "$pyfile" ; then
      echo "Testing $pyfile"
      ../pys python3 "$pyfile" || rc=1
    fi
  done
  exit $rc
)
