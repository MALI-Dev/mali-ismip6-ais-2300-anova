import glob
import os
import shutil

from matplotlib import pyplot as plt
import numpy as np

plot_time_series = True

dataset_destination = '/pscratch/sd/h/hoffman2/anova-results'

runsets_base = '/pscratch/sd/h/hoffman2/ismip6_ais_2300_4kmDI_anova_ensemble_gpu'

ens_info = list()


exp_list = {'expAE02_04': {'esm': 'ccsm4', 'hydro': 'off'},
            'expAE03_04': {'esm': 'hadgem2', 'hydro': 'off'},
            'expAE04_04': {'esm': 'cesm2', 'hydro': 'off'},
            'expAE05_04': {'esm': 'ukesm1', 'hydro': 'off'},
            'expAE11_04': {'esm': 'ccsm4', 'hydro': 'on'},
            'expAE12_04': {'esm': 'hadgem2', 'hydro': 'on'},
            'expAE13_04': {'esm': 'cesm2', 'hydro': 'on'},
            'expAE14_04': {'esm': 'ukesm1', 'hydro': 'on'}}

for runset in sorted(glob.glob(os.path.join(runsets_base, 'q*m*'))):
    # get runset name
    runset_name = os.path.basename(runset)
    qval = runset_name[1:3]
    mval = runset_name[4:6]

    # process indiv. runs in this set
    for exp_name, exp_info in exp_list.items():
        esm = exp_info['esm']
        hydrofrac = exp_info['hydro']
        runpath = os.path.join(runset, 'landice', 'ismip6_run',
                               'ismip6_ais_proj2300', exp_name)
        with open(os.path.join(runpath, 'restart_timestamp'), 'r') as file:
            content = file.read()
        end_year = int(content.split('-')[0])
        std_name = f"q-{qval}_m-{mval}_e-{esm}_h-{hydrofrac}"
        print(f'Processing {std_name}')

        run_dict = {'name': std_name,
                    'q': qval,
                    'm': mval,
                    'e': esm,
                    'h': hydrofrac,
                    'path': runpath,
                    'end_year': end_year
                    }
        ens_info.append(run_dict)

        # copy globalStats to common location with naming convention
        gs_path = os.path.join(runpath, 'output', 'globalStats.nc')
        if os.path.isfile(gs_path):
            shutil.copyfile(gs_path,
                            os.path.join(dataset_destination,
                                         f'{std_name}.nc'))

# plot end year for all runs
fig_duration = plt.figure(99, figsize=(8, 8), facecolor='w')
nrow = 3
ncol = 1

final_time = np.zeros(len(ens_info))
for i, run in enumerate(ens_info):
    final_time[i] = run['end_year']

ax_yr_histo = fig_duration.add_subplot(nrow, ncol, 1)
plt.hist(final_time, bins=np.arange(final_time.min(), final_time.max() + 1))
plt.xlabel('final simulated year')
plt.ylabel('count')
plt.grid()

ax_yr_histo_cum = fig_duration.add_subplot(nrow, ncol, 2)
plt.hist(final_time, bins=np.arange(final_time.min(), final_time.max() + 1),
         cumulative=True)
plt.xlabel('final simulated year')
plt.ylabel('cumulative count')
plt.grid()

ax_yr_by_run = fig_duration.add_subplot(nrow, ncol, 3)
plt.bar(np.arange(len(ens_info)), final_time, width=0.9)
plt.ylim([2015, 2301])
plt.xlabel('run number')
plt.ylabel('final simulated year')
plt.grid(axis='y')

fig_duration.tight_layout()


if plot_time_series:
    for i, run in enumerate(ens_info):
        pass

plt.show()

