#!/bin/bash

# Script to create a subset of model output for archiving purposes

# Location of ensemble model output
RUNDIR=/pscratch/sd/h/hoffman2/ismip6_ais_2300_4kmDI_anova_ensemble_gpu/q03m05; NAME=q03-m95

# Location where processed output should be placed
DEST_ROOT=/pscratch/sd/h/hoffman2/AIS_ANOVA_ARCHIVE_PROCESSING_20250214


DEST=$DEST_ROOT/$NAME

MESHVARS=latCell,lonCell,xCell,yCell,zCell,indexToCellID,latEdge,lonEdge,xEdge,yEdge,zEdge,indexToEdgeID,latVertex,lonVertex,xVertex,yVertex,zVertex,indexToVertexID,cellsOnEdge,nEdgesOnCell,nEdgesOnEdge,edgesOnCell,edgesOnEdge,weightsOnEdge,dvEdge,dcEdge,angleEdge,areaCell,areaTriangle,cellsOnCell,verticesOnCell,verticesOnEdge,edgesOnVertex,cellsOnVertex,kiteAreasOnVertex,meshDensity,layerThicknessFractions

mkdir -p $DEST
#cp $RUNDIR/*ensemble.cfg $DEST

# loop over runs
for dirpath in $RUNDIR/landice/ismip6_run/ismip6_ais_proj2300/exp*/ ; do
   RUN=`basename $dirpath`
   echo Processing $RUN
   mkdir $DEST/$RUN
   cp $dirpath/output/*Stats.nc $DEST/$RUN
   #ncrcat -d Time,,,10  $dirpath/output/output_*.nc $DEST/$RUN/output.nc
   #ncrcat -x -v $MESHVARS -d Time,,,10  $dirpath/output/output_*.nc $DEST/$RUN/output.nc
   # for branch runs, start 4 time levels in at year 2020 and then get every 10 years
   #ncrcat -x -v $MESHVARS,damage -d Time,4,,10  $dirpath/output/output_*.nc $DEST/$RUN/output.nc
   ncrcat  -v xtime,simulationStartTime,daysSinceStart,thickness,lowerSurface,xvelmean,yvelmean,cellMask -d Time,,,1  $dirpath/output/output_state*.nc $DEST/$RUN/output.nc
done

# create mesh var file using final output file
for fname in $dirpath/output/output_*.nc; do 
   ncks -v $MESHVARS $fname $DEST/mesh_vars.nc
   break
done
