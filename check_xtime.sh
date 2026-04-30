
export ENSEMBLE_DIR="/pscratch/sd/h/hoffman2/ismip6_ais_2300_4kmDI_anova_ensemble_gpu/"

for exp_dir in $(find $ENSEMBLE_DIR -type d -wholename "*q05m50/**/*_04" | sort);do

    for file in $(find $exp_dir -type f -name "output_state_*.nc" | sort);do
        exp=$(basename exp_dir)
        if $(ncdump -v xtime $file | grep -q \@); then
            echo $file
        fi
    done
done
