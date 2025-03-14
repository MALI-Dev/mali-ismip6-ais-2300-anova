import glob
import os
import shutil

from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import xarray as xr

plot_time_series = True
rhoi = 910.0

#dataset_destination = '/pscratch/sd/h/hoffman2/anova-results'
dataset_destination = '/global/cfs/cdirs/fanssie/users/hoffman2/mali/ais2300-anova-results'

runsets_base = '/pscratch/sd/h/hoffman2/ismip6_ais_2300_4kmDI_anova_ensemble_gpu'

rgn = -1 # global stats
#rgn = 14 # FRIS
#rgn = 7 # Ross
#rgn = 9 # TG/PIG
rgn = 2 # Amery

if rgn >= 0:
    dataset_destination = os.path.join(dataset_destination, f'region{rgn}')
    if not os.path.exists(dataset_destination):
        os.mkdir(dataset_destination)

ens_info = list()

exp_list = {'expAE02_04': {'esm': 'ccsm4', 'hydro': 'off'},
            'expAE03_04': {'esm': 'hadgem2', 'hydro': 'off'},
            'expAE04_04': {'esm': 'cesm2', 'hydro': 'off'},
            'expAE05_04': {'esm': 'ukesm1', 'hydro': 'off'},
            'expAE11_04': {'esm': 'ccsm4', 'hydro': 'on'},
            'expAE12_04': {'esm': 'hadgem2', 'hydro': 'on'},
            'expAE13_04': {'esm': 'cesm2', 'hydro': 'on'},
            'expAE14_04': {'esm': 'ukesm1', 'hydro': 'on'}}

yr_list = np.arange(16, 302)

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
        print(f'Processing {std_name}: end year={end_year}')

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
        if rgn < 0:
            stat_path1 = os.path.join(runpath, 'output', 'globalStats.nc.cleaned')
            stat_path2 = os.path.join(runpath, 'output', 'globalStats.nc')
        else:
            stat_path1 = os.path.join(runpath, 'output', 'regionalStats.nc.cleaned')
            stat_path2 = os.path.join(runpath, 'output', 'regionalStats.nc')

        have_stat_file = False
        if os.path.isfile(stat_path1):
            stat_path = stat_path1
            have_stat_file = True
        elif os.path.isfile(stat_path2):
            stat_path = stat_path2
            have_stat_file = True
        else:
            print("  stats file not found: SKIPPING")
        if have_stat_file == True:
            ds = xr.open_dataset(stat_path, decode_times=False, decode_cf=False)
            years = ds.daysSinceStart.values / 365.0
            #inds = np.where(years == np.round(years))
            # find indices more carefully b/c of a case of two indices with the
            # same time in one of the files
            inds = list()
            for yr in yr_list:
                ind = np.where(years == yr)[-1]
                if len(ind) > 0:
                    inds.append(ind[0])
            days_even = ds.daysSinceStart[inds]
            ds_out = days_even.to_dataset(name = 'daysSinceStart')
            if rgn < 0:
                ds_out['volumeAboveFloatation'] = ds.volumeAboveFloatation[inds]
            else:
                ds_out['volumeAboveFloatation'] = ds.regionalVolumeAboveFloatation[inds, rgn]
            ds_out.to_netcdf(os.path.join(dataset_destination,
                                          f'{std_name}.nc'))

# plot end year for all runs
fig_duration = plt.figure(1, figsize=(8, 8), facecolor='w')
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
    fig_vaf = plt.figure(2, figsize=(14, 8), facecolor='w')

    qcols = {'03': 'r',
             '05': 'g',
             '10': 'b'}
    mcols = {'05': 'r',
             '50': 'g',
             '95': 'b'}
    ecols = {'ccsm4': 'r',
             'hadgem2': 'g',
             'cesm2': 'b',
             'ukesm1': 'k'}
    hcols = {'off': 'r',
             'on': 'b'}
    lw = 0.75
               
    nrow = 2
    ncol = 3

    ax_vaf = fig_vaf.add_subplot(nrow, ncol, 1)
    plt.title('all runs')
    ax_vafq = fig_vaf.add_subplot(nrow, ncol, 2)
    plt.title('sorted by q')
    ax_vafm = fig_vaf.add_subplot(nrow, ncol, 3)
    plt.title('sorted by m')
    ax_vafe = fig_vaf.add_subplot(nrow, ncol, 4)
    plt.title('sorted by e')
    ax_vafh = fig_vaf.add_subplot(nrow, ncol, 5)
    plt.title('sorted by h')

    for ax in fig_vaf.axes:
        ax.set_xlabel('Year')
        ax.set_ylabel('VAF (Gt)')

    for i, run in enumerate(ens_info):
        run_name = run['name']
        stat_path = os.path.join(dataset_destination, f'{run_name}.nc')
        if os.path.isfile(stat_path):
            ds = xr.open_dataset(stat_path, decode_times=False, decode_cf=False)
            yrs = ds.daysSinceStart.values / 365.0 + 2000.0
            vaf = ds.volumeAboveFloatation.values * 1.0e12 / rhoi
            ax_vaf.plot(yrs, vaf, '-', linewidth=lw)

            ax_vafq.plot(yrs, vaf, color=qcols[run['q']], linewidth=lw)
            ax_vafm.plot(yrs, vaf, color=mcols[run['m']], linewidth=lw)
            ax_vafe.plot(yrs, vaf, color=ecols[run['e']], linewidth=lw)
            ax_vafh.plot(yrs, vaf, color=hcols[run['h']], linewidth=lw)

    # create custom legends
    leg_el = []
    for key, val in qcols.items():
        leg_el.append(Line2D([0], [0], color=val, lw=4, label=key))
    ax_vafq.legend(handles=leg_el, loc='lower left')
    leg_el = []
    for key, val in mcols.items():
        leg_el.append(Line2D([0], [0], color=val, lw=4, label=key))
    ax_vafm.legend(handles=leg_el, loc='lower left')
    leg_el = []
    for key, val in ecols.items():
        leg_el.append(Line2D([0], [0], color=val, lw=4, label=key))
    ax_vafe.legend(handles=leg_el, loc='lower left')
    leg_el = []
    for key, val in hcols.items():
        leg_el.append(Line2D([0], [0], color=val, lw=4, label=key))
    ax_vafh.legend(handles=leg_el, loc='lower left')

    fig_vaf.tight_layout()



plt.show()

