#!/bin/bash

export DB_URL="sqlite:///:memory:"

while : ; do

	pushd $(dirname $0)/..
	pipenv run pytest --ff --nf -x test/
	popd

	# If interactive shell, run in a loop
	test -t 0 && (echo Press [ENTER] to retest && read t) || break
done
