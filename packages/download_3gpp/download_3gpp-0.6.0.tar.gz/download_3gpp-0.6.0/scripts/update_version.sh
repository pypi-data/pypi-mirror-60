#!/bin/bash

BASH_RELEASE_PATTERN=^[0-9]+\.[0-9]+\.[0-9]+$
BASH_DRYRUN_PATTERN=-dryrun[0-9]*$
SED_DRYRUN_PATTERN=s/^\([0-9]+\.[0-9]+\.[0-9]+\)\(.*\)$/\\1.${CI_PIPELINE_ID}/

# Put the release tag in the VERSION file if this is a release pipeline.
# For a dryrun release tag use the Python PEP-440 development release pattern and extract the
# semantic version plus the pipeline number for the VERSION file.
# Otherwise use the Python PEP-440 development release pattern and use "0.0.0" with the
# pipeline number for unique identification.
# https://www.python.org/dev/peps/pep-0440/

if [[ ${CI_COMMIT_REF_NAME} =~ ${BASH_RELEASE_PATTERN} ]]; then
  echo "${CI_COMMIT_REF_NAME}";
elif [[ ${CI_COMMIT_REF_NAME} =~ ${BASH_DRYRUN_PATTERN} ]]; then
  echo "${CI_COMMIT_REF_NAME}" | sed -r ${SED_DRYRUN_PATTERN};
else
  echo "0.0.0.${CI_PIPELINE_ID}";
fi
