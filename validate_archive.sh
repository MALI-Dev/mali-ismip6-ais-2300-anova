#!/bin/bash

export ARCHIVE_DIR="/pscratch/sd/a/anolan/ismip6_ais_anova_ensemble_archive"

readonly RED="\033[0;31m"
readonly NC="\033[0m"  # No Color

count_files() {
    find . -name $1 -exec du -sh {} \; | grep $2 | wc -l
}

check_file_counts() {

    if [[ $(count_files $1 "exp") != 72 ]]; then
        echo -e "${RED}Error: Incorrect numer of '$1' files found in experiment dirs.${NC}"
    fi

    if [[ $(count_files $1 "hist") != 9 ]]; then
        echo -e "${RED}Error: Incorrect numer of '$1' files found in historical dirs.${NC}"
    fi

}

pushd $ARCHIVE_DIR

check_file_counts "namelist.landice"
check_file_counts "streams.landice"
check_file_counts "albany_input.yaml"
check_file_counts "flux.nc"
check_file_counts "state.nc"

popd
