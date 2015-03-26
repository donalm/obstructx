#!/bin/zsh

bootstrap_script=${(%):-%N}
bindir=`dirname $bootstrap_script`
bindir_abs=`cd $bindir && pwd`
basedir=`dirname $bindir_abs`
scriptname=`basename $0`

export PYTHONPATH="$basedir/lib/python"


exec $bindir_abs/$scriptname.py $@
