#!/bin/bash
readonly MIN_PASSING_SCORE=0.00
readonly ERROR_MSG="Aborting commit. Your commit has a pylint score lower than ${MIN_PASSING_SCORE}"
echo "Starting a script to run pylint on python files.";
echo ">Running Pylint scan for XXX python package";
SCORE=$(pylint ./knee_stress_predict/**/*.py | grep rated  | sed -n '$s/[^0-9]*\([0-9.]*\).*/\1/p')
echo $SCORE

if (($(echo "$SCORE < ${MIN_PASSING_SCORE}" | bc -l))); then
                # and print the error message
                echo ">$ERROR_MSG" >&2
                # and save the last_status as failure
                last_status=1
            else
                echo ">Pylint score $SCORE greater than min required score: ${MIN_PASSING_SCORE}; Success!"
                last_status=0
            fi
            # Update the status if any pylint scan for a package fails
            if [ $last_status -ne 0 ]; then
                echo "FAILURE $toxfile: [$last_status]"
                status=$last_status;
            fi

echo "Pylint Run Complete.  Final Status $status"
exit $status
