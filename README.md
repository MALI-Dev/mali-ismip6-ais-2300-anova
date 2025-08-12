This repository contains scripts and notes for setting up, running, and
analyzing an analysis of variance ensemble.

The ensemble was set up using compass:
* Create each set of 8 runs (exp2-5, 11-14) by adjusting melt and exponent files and ens. name in cfg and exponent in yaml.
* Generate set of 8 simulations using compass command:
```
/global/cfs/cdirs/fanssie/users/hoffman2/compass/ismip6_ais_2300_4kmDI_anova_ensemble_gpu/compass/landice/tests/ismip6_run/ismip6_ais_proj2300$ compass setup -n 94 -f ismip6_ais_proj2300_4km_nersc.cfg -w /pscratch/sd/h/hoffman2/ismip6_ais_2300_4kmDI_anova_ensemble_gpu/q05m50 -p /global/cfs/cdirs/fanssie/software/mali-develop-2024-10-14
```


# Files in this repository:

## Ensemble management:

* ismip6_ais_proj2300_4km_nersc.cfg - compass cfg file used in command above

* broadcast_file_to_ens_members.sh - helper script to copy a file to all
ensemble members in a subset if things weren't set up quite right

* update_namelist_in_ens_members.sh - helper script to update namelist for all
runs in an ensemble subset if things weren't set up quite right

* job_script_all.sh - example batch script to run up to 8 simulations bundled
together to make more effective use of queue

* submit_all_exps.sh - script to submit jobs for all runs in an ensemble subset.
Alternative workflow to job_script_all.sh 


## Post-processing:

* organize_anova_ensemble.py - copy global or regional stats files from all
simulations in ensemble and rename them with a naming convention for analysis

* anova_analysis.py - perform anova analysis and create anova plots.  Assumes
data has been organized using organize_anova_ensemble.py


## Archiving:

* archive_ensemble.sh - in progress

* process_output_for_archiving.py - in progress
