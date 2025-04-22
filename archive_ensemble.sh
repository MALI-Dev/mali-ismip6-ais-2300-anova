#!/bin/bash
#SBATCH --qos=debug
#SBATCH --nodes=1
#SBATCH --constraint=cpu
#SBATCH --time=00:30:00

source $HOME/polaris/load_dev_polaris_0.6.0-alpha.1_pm-cpu_gnu_mpich.sh

export ENSEMBLE_DIR="/pscratch/sd/h/hoffman2/ismip6_ais_2300_4kmDI_anova_ensemble_gpu/"
export ARCHIVE_DIR="/pscratch/sd/a/anolan/ismip6_ais_anova_ensemble_archive"

srun parallel --jobs 4 ./archive_experiment.sh ::: 03 05 ::: 05 50 ::: "hist"

#srun parallel --jobs 4 ./archive_experiment.sh ::: 03 05 10 ::: 05 50 95 ::: "hist" 02 03 04 05 11 12 13 14
