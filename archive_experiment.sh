#!/bin/bash

readonly RED="\033[0;31m"
readonly NC="\033[0m"  # No Color

copy_input_files() {
  # input arguments
  local in_dir="$1"
  local out_dir="$2"

  # Find matching files
  local matches
  matches=$(find "$in_dir" -type f \( -name "namelist.landice" -o -name "streams.landice" -o -name "albany_input.yaml" \))

  if [[ -z "$matches" ]]; then
    echo -e "${RED}Error: No matching input files found in '$in_dir'.${NC}"
    exit 1
  fi

  echo "$matches" | while read -r file; do
    cp $file $out_dir
  done
}

copy_output_files() {
  # input arguments
  local in_dir="$1"
  local out_dir="$2"

  # Find matching files
  local matches
  matches=$(find "$in_dir/output" -type f -name "*Stats.nc")

  if [[ -z "$matches" ]]; then
    echo -e "${RED}Error: No matching input files found in '$in_dir'.${NC}"
    exit 1
  fi

  echo "$matches" | while read -r file; do
    cp $file $out_dir
  done
}

copy_restart_files() {
  # input arguments
  local in_dir="$1"
  local out_dir="$2"

  # Find matching files
  local matches
  matches=$(find -L "$in_dir" -type f -name "rst.*.nc" | sort -t '.' -k2)

  if [[ -z "$matches" ]]; then
    echo -e "${RED}Error: No matching restart files found in '$in_dir'.${NC}"
    exit 1
  fi

  # Filter files where the year is divisible by 15
  echo "$matches" | while read -r file; do
    year=$(echo "${file##*/}" | grep -oE '[0-9]{4}')
    if (( (year - 2015) % 15 == 0 )); then
      cp --preserve=links $file $out_dir
    fi
  done
}

validate_output_direcotry() {
    # input arguments
    local output_dir="$1"

    if [ ! -d $output_dir ]; then
        mkdir -p $output_dir
    fi

    if [ ! -d "${output_dir}/output" ]; then
        mkdir -p "${output_dir}/output"
    fi

    if [ ! -d "${output_dir}/input" ]; then
        mkdir -p "${output_dir}/input"
    fi
}

main() {
    local q="$1"
    local m="$2"
    local e="$3"
    
    if [ "$e" == "hist" ]; then
        expr_name="hist_04"
    else
        expr_name="expAE${e}_04/"
    fi

    input_dir="${ENSEMBLE_DIR}/q${q}m${m}/landice/ismip6_run/ismip6_ais_proj2300/${expr_name}"
    output_dir="${ARCHIVE_DIR}/q${q}m${m}/${expr_name}"

    # Make sure output directory (and all subdirs needed) exist
    validate_output_direcotry $output_dir

    # Check if the directory exists
    if [[ ! -d "$input_dir" ]]; then
      echo -e "${RED}Error: Directory '$input_dir' does not exist.${NC}"
      exit 1
    fi

    copy_input_files $input_dir "${output_dir}/input/"
    copy_output_files $input_dir "${output_dir}/output/"
    copy_restart_files $input_dir "${output_dir}/input/"

    python process_output_for_archiving.py -i "${input_dir}/output/" -o "${output_dir}/output/"
}

main "$@"
