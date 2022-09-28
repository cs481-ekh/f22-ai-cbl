#!/bin/bash
readonly MIN_PASSING_SCORE=0.00
readonly ERROR_MSG="Aborting commit. Your commit has a pylint score lower than ${MIN_PASSING_SCORE}"
echo "Starting a script to run pylint on python files."
#RCFILE=".scripts/.pylintrc"
# TODO: Update this before you run the script, or build some logic to define a list of PACKAGES
EXAMPLE_PACKAGES="knee_stress_predict"
PACKAGES="${1:-$EXAMPLE_PACKAGES}"

#for package in ${PACKAGES[@]}; do
#    echo "[$package]"
#    echo ">Running Pylint scan for $package python package"
#    # Lint all the python files;
#    # **/**/*.py catches every dir such as cmds, util, tests
##    pylint --rcfile=${RCFILE} ./${package}/**/**/*.py \; |
#    pylint ./${package}/**/**/*.py \; |
#        # Only get the number values
#        grep -oE "\-?[0-9]+\.[0-9]+" |
#        # Extract the score
#        awk 'NR==1 || NR % 4 == 0' |
#        # For score lines
#        while read line; do
#            echo ">Pylint score for $package is $line"
#            # If the line contains a score lower than MIN_PASSING_SCORE throw a problem.
#            if (($(echo "$line < ${MIN_PASSING_SCORE}" | bc -l))); then
#                # and print the error message
#                echo ">$ERROR_MSG" >&2
#                # and save the last_status as failure
#                last_status=1
#            else
#                echo ">Pylint score $line greater than min required score: ${MIN_PASSING_SCORE}; Success!"
#                last_status=0
#            fi
#            # Update the status if any pylint scan for a package fails
#            if [ $last_status -ne 0 ]; then
#                echo "FAILURE $toxfile: [$last_status]"
#                status=$last_status;
#            fi
#        done
#done

echo ">Running Pylint scan for XXX python package"
# **/**/*.py catches every dir such as cmds, util, tests
#pylint ./knee_stress_predict/**/*.py \; |
#    # Only get the number values
#    grep -oE "\-?[0-9]+\.[0-9]+" |
#    # Extract the score
#    awk 'NR==1 || NR % 4 == 0' |
#    # For score lines
#    while read line; do
#        echo ">Pylint score for XXX is $line"
#        # If the line contains a score lower than MIN_PASSING_SCORE throw a problem.
#        if (($(echo "$line < ${MIN_PASSING_SCORE}" | bc -l))); then
#            # and print the error message
#            echo ">$ERROR_MSG" >&2
#            # and save the last_status as failure
#            last_status=1
#        else
#            echo ">Pylint score $line greater than min required score: ${MIN_PASSING_SCORE}; Success!"
#            last_status=0
#        fi
#        # Update the status if any pylint scan for a package fails
#        if [ $last_status -ne 0 ]; then
#            echo "FAILURE $toxfile: [$last_status]"
#            status=$last_status;
#        fi
#    done

pylint ./knee_stress_predict/**/*.py \;
#grep "has been rated"
echo "Pylint Run Complete.  Final Status $status"
exit $status
