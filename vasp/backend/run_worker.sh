#!/bin/bash
#export INIT_DRAMATIQ=1

dramatiq merchant_vasp -p 2 -t 2 --verbose  "$@"
