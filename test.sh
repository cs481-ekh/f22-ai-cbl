#!/bin/bash
readonly MIN_PASSING_SCORE=0.00
readonly ERROR_MSG="Aborting commit. Your commit has a pylint score lower than ${MIN_PASSING_SCORE}"
echo "Starting a script to run pylint on python files.";
echo ">Running Pylint scan for XXX python package";
pylint ./knee_stress_predict/**/*.py
grep '$s/[^0-9]*\([0-9.]*\).*/\1/p'

echo "Pylint Run Complete.  Final Status $status"
exit $status
