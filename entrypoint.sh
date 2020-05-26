#!/bin/bash
set -eu
set -o pipefail

printf "\n----------------- Starting Url Headers GitHub Action! -----------------\n"
printf "urls: ${INPUT_URLS}\n"

# Tell the user files found immediately
printf "\n\nFound files in root of repository:\n"
ls

python /code/data/run.py

printf "Produced files:\n"
ls /code/data/

# Copy the contents to the GitHub workspace data folder
cp /code/data/*.json "${GITHUB_WORKSPACE}/data"
printf "Copied to workspace\n"
ls "${GITHUB_WORKSPACE}/data"
