#!/bin/bash

readonly RED="\033[0;31m"
readonly NC="\033[0m"  # No Color

copy_input_files() {
  # input arguments
  local dir="$1"

  # Find matching files
  local matches
  matches=$(find "$dir" -type f \( -name "namelist.landice" -o -name "streams.landice" -o -name "albany_input.yaml" \))

  if [[ -z "$matches" ]]; then
    echo -e "${RED}Error: No matching input files found in '$dir'.${NC}"
    exit 1
  fi

  echo "$matches" | while read -r file; do
    echo $file
  done
}

copy_output_files() {
  # input arguments
  local dir="$1"

  # Find matching files
  local matches
  matches=$(find "$dir/output" -type f -name "*Stats.nc")

  if [[ -z "$matches" ]]; then
    echo -e "${RED}Error: No matching input files found in '$dir'.${NC}"
    exit 1
  fi

  echo "$matches" | while read -r file; do
    echo $file
  done
}

copy_restart_files() {
  # input arguments
  local dir="$1"

  # Find matching files
  local matches
  matches=$(find "$dir" -type f -name "rst.*.nc" | sort -t '.' -k2)

  if [[ -z "$matches" ]]; then
    echo -e "${RED}Error: No matching restart files found in '$dir'.${NC}"
    exit 1
  fi

  # Filter files where the year is divisible by 15
  echo "$matches" | while read -r file; do
    year=$(echo "${file##*/}" | grep -oE '[0-9]{4}')
    if (( (year - 2015) % 15 == 0 )); then
      echo "$file"
    fi
  done
}

main() {
    # input arguments
    local input_dir="$1"
    local output_dir="$2"

    # Check if a directory was provided
    if [[ -z "$input_dir" ]]; then
      echo -e "${RED}Error: No directory provided.${NC}"
      echo "Usage: find_div15_rst_files /path/to/directory"
      exit 1
    fi

    # Check if the directory exists
    if [[ ! -d "$input_dir" ]]; then
      echo -e "${RED}Error: Directory '$input_dir' does not exist.${NC}"
      exit 1
    fi

    copy_input_files "dumb"
    copy_output_files $input_dir
    copy_restart_files $input_dir
}

main "$@"
