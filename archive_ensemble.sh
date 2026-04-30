#!/bin/bash
#SBATCH --qos=regular
#SBATCH --nodes=5
#SBATCH --ntasks-per-node=16
#SBATCH --cpus-per-task=8
#SBATCH --account=m4288
#SBATCH --constraint=cpu
#SBATCH --time=01:15:00

source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh

export ENSEMBLE_DIR="/pscratch/sd/h/hoffman2/ismip6_ais_2300_4kmDI_anova_ensemble_gpu/"
export ARCHIVE_DIR="/pscratch/sd/a/anolan/ismip6_ais_anova_ensemble_archive"

main(){

    # copy the forcing and meshes to top level dir
    archive_meshes_and_forcing

    # extract subset of mesh varibales from initial condition file
    extract_mesh_vars

    # archive the experiment dirs in parallel
    # ref: https://www.docs.arc.vt.edu/usage/parallel.html
    parallel -j $SLURM_NTASKS srun --nodes=1 --ntasks=1 --cpus-per-task=8 \
        ./archive_experiment.sh ::: 03 05 10 ::: 05 50 95 ::: "hist" 02 03 04 05 11 12 13 14
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

extract_mesh_vars(){

    mesh_vars=(
        latCell lonCell xCell yCell zCell indexToCellID
        latEdge lonEdge xEdge yEdge zEdge indexToEdgeID
        latVertex lonVertex xVertex yVertex zVertex indexToVertexID
        cellsOnEdge nEdgesOnCell nEdgesOnEdge edgesOnCell edgesOnEdge
        weightsOnEdge dvEdge dcEdge angleEdge areaCell areaTriangle
        cellsOnCell verticesOnCell verticesOnEdge
        edgesOnVertex cellsOnVertex kiteAreasOnVertex
    )

    mesh_vars_string="${mesh_vars[@]}"

    ncks -O -C -v "${mesh_vars_string//${IFS:0:1}/,}" \
         -o "${ARCHIVE_DIR}/mesh/mesh_vars.nc" \
         "${ARCHIVE_DIR}/mesh/AIS_4to20km_r01_20220907_m3_05perc_seafloor_mu.nc"
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
