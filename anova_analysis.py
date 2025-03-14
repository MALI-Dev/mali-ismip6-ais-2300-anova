import glob
import os
import shutil

from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
import xarray as xr

import statsmodels.api as sm
from statsmodels.formula.api import ols

interactions = 3

dataset_path = '/pscratch/sd/h/hoffman2/anova-results'
rhoi = 910.0
rhosw = 1028.0


file_list = sorted(glob.glob(os.path.join(dataset_path, '*nc')))
n_files = len(file_list)

year_list = np.arange(2016, 2301 + 1)
#year_list = np.arange(2050, 2051)
n_years = len(year_list)

q_list = [0] * n_files
m_list = [0] * n_files
e_list = [0] * n_files
h_list = [0] * n_files
slr_list = np.zeros((n_files, n_years)) * np.nan
valid_runs_per_year = np.zeros((n_years,))

for i, file_path in enumerate(file_list):
    run_name = os.path.basename(file_path).split('.')[0]
    print(run_name)
    q_list[i] = run_name.split('_')[0].split('-')[1]
    m_list[i] = run_name.split('_')[1].split('-')[1]
    e_list[i] = run_name.split('_')[2].split('-')[1]
    h_list[i] = run_name.split('_')[3].split('-')[1]
    ds = xr.open_dataset(file_path, decode_times=False, decode_cf=False)

    vaf = ds.volumeAboveFloatation.values
    inYrs  = ds.daysSinceStart.values / 365.
    assert len(vaf) <= slr_list.shape[1], \
           print(f'Error: len(vaf)={len(vaf)}; slr_list len={slr_list.shape[1]}',
              'yrs:', inYrs)
    slr_list[i, :len(vaf)] = -1.0 * (vaf - vaf[0]) / 3.62e14 * rhoi / rhosw


print('shape of slr_list', slr_list.shape)


var_q = np.zeros((n_years,)) * np.nan
var_m = np.zeros((n_years,)) * np.nan
var_e = np.zeros((n_years,)) * np.nan
var_h = np.zeros((n_years,)) * np.nan
var_qm = np.zeros((n_years,)) * np.nan
var_qe = np.zeros((n_years,)) * np.nan
var_qh = np.zeros((n_years,)) * np.nan
var_me = np.zeros((n_years,)) * np.nan
var_mh = np.zeros((n_years,)) * np.nan
var_eh = np.zeros((n_years,)) * np.nan
var_qme = np.zeros((n_years,)) * np.nan
var_qmh = np.zeros((n_years,)) * np.nan
var_qeh = np.zeros((n_years,)) * np.nan
var_meh = np.zeros((n_years,)) * np.nan
var_qmeh = np.zeros((n_years,)) * np.nan
var_res = np.zeros((n_years,)) * np.nan
var_all = np.zeros((n_years,)) * np.nan
r2 = np.zeros((n_years,)) * np.nan

for yr_idx, yr in enumerate(year_list):
    print(f'\n***** Year={yr} (ind={yr_idx}) *****\n')
    # get valid indices for this year
    # (not necessary when ensemble is complete)
    valid_run_ind = np.nonzero(np.logical_not(np.isnan(slr_list[:, yr_idx])))[0]
    n_valid = len(valid_run_ind)
    valid_runs_per_year[yr_idx] = n_valid
    if len(valid_run_ind) < 20:
        # give up if the number of valid runs has dwindled
        break
    slr_vals = slr_list[valid_run_ind, yr_idx]
    if slr_vals.sum() == 0.0:
        continue
    df = pd.DataFrame({'q': [q_list[i] for i in valid_run_ind],
                       'm': [m_list[i] for i in valid_run_ind],
                       'e': [e_list[i] for i in valid_run_ind],
                       'h': [h_list[i] for i in valid_run_ind],
                       'slr': slr_vals})
    print(df)
    if interactions == 1:
        model = ols("""slr ~ q + m + C(e) + C(h)""", data=df).fit()
    elif interactions == 2:
        model = ols("""slr ~ q + m + C(e) + C(h) +
                    q:m + q:C(e) + q:C(h) +
                    m:C(e) + m:C(h) +
                    C(e):C(h)""", data=df).fit()
    elif interactions == 3:
        model = ols("""slr ~ q + m + C(e) + C(h) +
                    q:m + q:C(e) + q:C(h) +
                    m:C(e) + m:C(h) +
                    C(e):C(h) +
                    q:m:C(e) + q:m:C(h) + q:C(e):C(h) +
                    m:C(e):C(h)""", data=df).fit()
    elif interactions == 4:
        model = ols("""slr ~ q + m + C(e) + C(h) +
                    q:m + q:C(e) + q:C(h) +
                    m:C(e) + m:C(h) +
                    C(e):C(h) +
                    q:m:C(e) + q:m:C(h) + q:C(e):C(h) +
                    m:C(e):C(h) +
                    m:C(e):C(h) +
                    q:m:C(e):C(h)""", data=df).fit()

    print(model.summary())
    r2[yr_idx] = model.rsquared

    anova_out = sm.stats.anova_lm(model, typ=2)
    print(anova_out)
    idx = 0
    var_q[yr_idx] = anova_out.sum_sq[idx] / (n_valid - 1)
    idx += 1
    var_m[yr_idx] = anova_out.sum_sq[idx] / (n_valid - 1)
    idx += 1
    var_e[yr_idx] = anova_out.sum_sq[idx] / (n_valid - 1)
    idx += 1
    var_h[yr_idx] = anova_out.sum_sq[idx] / (n_valid - 1)
    idx += 1
    if interactions >= 2:
       var_qm[yr_idx] = anova_out.sum_sq[idx] / (n_valid - 1)
       idx += 1
       var_qe[yr_idx] = anova_out.sum_sq[idx] / (n_valid - 1)
       idx += 1
       var_qh[yr_idx] = anova_out.sum_sq[idx] / (n_valid - 1)
       idx += 1
       var_me[yr_idx] = anova_out.sum_sq[idx] / (n_valid - 1)
       idx += 1
       var_mh[yr_idx] = anova_out.sum_sq[idx] / (n_valid - 1)
       idx += 1
       var_eh[yr_idx] = anova_out.sum_sq[idx] / (n_valid - 1)
       idx += 1
    if interactions >= 3:
       var_qme[yr_idx] = anova_out.sum_sq[idx] / (n_valid - 1)
       idx += 1
       var_qmh[yr_idx] = anova_out.sum_sq[idx] / (n_valid - 1)
       idx += 1
       var_qeh[yr_idx] = anova_out.sum_sq[idx] / (n_valid - 1)
       idx += 1
       var_meh[yr_idx] = anova_out.sum_sq[idx] / (n_valid - 1)
       idx += 1
    if interactions >= 4:
       var_qmeh[yr_idx] = anova_out.sum_sq[idx] / (n_valid - 1)
       idx += 1

    var_res[yr_idx] = anova_out.sum_sq[idx] / (n_valid-1)
    var_all[yr_idx] = np.std(slr_vals, ddof=1)**2  # TODO: not sure if ddof should be 0 or 1

#var_tot = var_m + var_e + var_h + var_me + var_mh + var_eh + var_qmeh + var_res
var_tot = var_m + var_q + var_e + var_h + var_res
if interactions >= 2:
    var_tot += var_qm + var_qe + var_qh + var_me + var_mh + var_eh
if interactions >= 3:
    var_tot += var_qme + var_qmh + var_qeh + var_meh
if interactions >= 4:
    var_tot += var_qmeh


# plot

fig = plt.figure(1, figsize=(10, 8), facecolor='w')
nrow = 2
ncol = 1

ax1 = fig.add_subplot(nrow, ncol, 1)
thk=2
thn=0.5
ls3='--'
ls4=':'
ax1.plot(year_list, np.sqrt(var_all), label='all', color='k', linewidth=thk, linestyle=':')
ax1.plot(year_list, np.sqrt(var_tot), label='total', color='k', linewidth=thk)
ax1.plot(year_list, np.sqrt(var_q), label='q', linewidth=thk)
ax1.plot(year_list, np.sqrt(var_m), label='m', linewidth=thk)
ax1.plot(year_list, np.sqrt(var_e), label='e', linewidth=thk)
ax1.plot(year_list, np.sqrt(var_h), label='h', linewidth=thk)
if interactions >= 2:
    ax1.plot(year_list, np.sqrt(var_qm), label='qm', linewidth=thn)
    ax1.plot(year_list, np.sqrt(var_qe), label='qe', linewidth=thn)
    ax1.plot(year_list, np.sqrt(var_qh), label='qh', linewidth=thn)
    ax1.plot(year_list, np.sqrt(var_me), label='me', linewidth=thn)
    ax1.plot(year_list, np.sqrt(var_mh), label='mh', linewidth=thn)
    ax1.plot(year_list, np.sqrt(var_eh), label='eh', linewidth=thn)
if interactions >= 3:
    ax1.plot(year_list, np.sqrt(var_qme), label='qme', linewidth=thn, linestyle=ls3)
    ax1.plot(year_list, np.sqrt(var_qmh), label='qmh', linewidth=thn, linestyle=ls3)
    ax1.plot(year_list, np.sqrt(var_qeh), label='qeh', linewidth=thn, linestyle=ls3)
    ax1.plot(year_list, np.sqrt(var_meh), label='meh', linewidth=thn, linestyle=ls3)
if interactions >= 4:
    ax1.plot(year_list, np.sqrt(var_qmeh), label='qmeh', linewidth=thn, linestyle=ls4)
ax1.plot(year_list, np.sqrt(var_res), label='residual', linewidth=thk, color='gray')
plt.legend(loc='center left')
plt.xlabel('Year')
plt.ylabel('sigma (m SLE)')

# fractional variance
ax2 = fig.add_subplot(nrow, ncol, 2)
stackdata = np.stack([var_q, var_m, var_e, var_h,
                      #var_qm, var_qe, var_qh,
                      #var_me, var_mh, var_eh,
                      #var_qmeh,
                      var_res])
stackdata = stackdata / stackdata.sum(axis=0) * 100.0
ax2.stackplot(year_list, stackdata, labels=('q', 'm', 'e', 'h',
                                            #'qm', 'qe', 'qh',
                                            #'me', 'mh', 'eh',
                                            #'qmeh',
                                            'residual'))
plt.legend()
plt.xlabel('Year')
plt.ylabel('percentage of variance')


plot_overview = False
if plot_overview:
    # overview of data
    fig = plt.figure(2, figsize=(8, 6), facecolor='w')
    nrow = 2
    ncol = 1

    ax = fig.add_subplot(nrow, ncol, 1)
    plt.bar(year_list, valid_runs_per_year, width=1.0)
    plt.xlabel('Year')
    plt.ylabel('Number of runs used')
    plt.ylim([0, 72])

    ax = fig.add_subplot(nrow, ncol, 2)
    plt.plot(year_list, r2)
    plt.xlabel('Year')
    plt.ylabel('OLS r^2')
    plt.ylim([0, 1])

plt.show()
