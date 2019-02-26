#!/usr/bin/env bash

if [ "${debug}" == "1" ];
then
    set -x
fi

mkdir -p wc_out || ${AGAVE_JOB_CALLBACK_FAILURE}

if [ -f "${input}" ];
then
    wc "${input}" > wc_out/output.txt
else
    echo "${input} wasn't able to be read" && \
    ${AGAVE_JOB_CALLBACK_FAILURE}
fi

# Cleanup
rm "$SEQ1"

if [ "${debug}" == "1" ];
then
    set +x
fi

# Implementation Notes
#
# Inputs: 'input'
#
# The variable ${input} is replaced with the actual name of 
# the input file as specified by the application descripton
# when this template is used as the basis for writing out the
# command file that's to be executed on the host system
#
# This template script is written with the assumption that
# as part of the Agave job life cycle, the file(s) referenced by
# inputs in the application and job description will be staged 
# into place in the job's working directory before the command
# file is executed or sent to the batch scheduler
#
# Parameters: 'debug'
#
# The same replacement logic applies to variables specified as
# part of the parameters portion of the application and job
# definition. Values passed in at run time are valiated as per
# the rules and constraints define in the application 
# definition. 
#
# Defensive programming: ${AGAVE_JOB_CALLBACK_FAILURE}
#
# Agave supports callbacks that can be embedded in a script
# that can explictly inform the platform of errors or progress 
# in the case of long-running tasks. In this template, the 
# AGAVE_JOB_CALLBACK_FAILURE will get subbed out into a curl
# command that will make a special informative http request
# in the event of a catastrophic error. Some people like to
# embed this as part of a general bash error handler!