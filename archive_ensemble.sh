#!/bin/bash
#SBATCH --qos=debug
#SBATCH --nodes=1
#SBATCH --constraint=cpu
#SBATCH --time=00:30:00

source $HOME/polaris/load_dev_polaris_0.6.0-alpha.1_pm-cpu_gnu_mpich.sh

export ENSEMBLE_DIR="/pscratch/sd/h/hoffman2/ismip6_ais_2300_4kmDI_anova_ensemble_gpu/"
export ARCHIVE_DIR="/pscratch/sd/a/anolan/ismip6_ais_anova_ensemble_archive"

main(){

    # copy the forcing and meshes to top level dir
    archive_meshes_and_forcing
    # archive the experiment dirs in parallel
    srun parallel --jobs 4 ./archive_experiment.sh ::: 03 05 10 ::: 05 50 95 ::: "hist" 02 03 04 05 11 12 13 14
}

unique_files(){
    # ref: https://stackoverflow.com/a/54577081
    # start with a sort -r, so that exp 11-15 are always used
    while read data; do sort -r | sort -k1,1 -u | cut -f 2-; done;
}

find_validate_copy(){
    # ref: https://stackoverflow.com/a/54577081
    local matches=($(find $ENSEMBLE_DIR -name $1 -printf '%f\t%p\n' | unique_files))

    # Make sure the right number of matches occurs
    if [ ${#matches[@]} -ne $2 ]; then
        echo -e "Error: Expected to find $2 files, but found ${#matches[@]}"
        exit 1
    fi

    # copy over to archive dir
    printf "%s\n" "${matches[@]}" | xargs -I {} cp {} $3
}

archive_meshes_and_forcing(){
    local mesh_dir="${ARCHIVE_DIR}/mesh/"
    local forcing_dir="${ARCHIVE_DIR}/forcing/"

    for dir in $mesh_dir $forcing_dir; do
        if [ ! -d $dir ]; then
            mkdir $dir
        fi
    done

    # three initial conditions (one per q value)
    find_validate_copy "relaxed_10yrs_4km.nc" 1 $mesh_dir
    find_validate_copy "AIS_4to20km*seafloor_mu.nc" 2 $mesh_dir

    # three ISMIP6 param files (one per m value)
    find_validate_copy 'basin_and_coeff*.nc' 3 $forcing_dir

    ## five TF files (one per climate model and obs.)
    find_validate_copy '*TF*.nc' 5 $forcing_dir

    ## five SMB files (one per climate model and obs.)
    find_validate_copy '*smb*.nc' 5 $forcing_dir

    ## four hydro mask files (one per climate model)
    find_validate_copy '*ice_shelf_collapse_mask*.nc' 4 $forcing_dir

    ##one region input mask
    find_validate_copy 'AIS_4to20km_r01_20220907.regionMask_ismip6.nc' 1 $mesh_dir

    ## one graph file
    find_validate_copy 'graph.info' 1 $mesh_dir
}

main
