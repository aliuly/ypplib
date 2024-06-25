#!/bin/sh
#
# Run python using venv
#
set -euf
(set -o pipefail >/dev/null 2>&1) && set -o pipefail || :

mydir="$(dirname "$0")"
venv="$mydir/.venv"
sh "$mydir/setup.sh"
. "$venv"/bin/activate

exec python3 "$@"
