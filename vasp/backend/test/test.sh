#!/bin/bash

export DB_URL="sqlite:///:memory:"

CODE=1

while : ; do

	pushd $(dirname $0)/..
	pipenv run pytest --ff --nf -x --cov=. test/
	CODE=$?
	popd

	# If interactive shell, run in a loop
	test -t 0 && (echo Press [ENTER] to retest && read t) || exit $CODE
done

exit $CODE
