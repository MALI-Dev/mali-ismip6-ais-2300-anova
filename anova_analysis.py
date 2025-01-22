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
var_qmeh = np.zeros((n_years,)) * np.nan
var_res = np.zeros((n_years,)) * np.nan
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
    #model = ols("""slr ~ C(q) + C(m) + C(e) + C(h) +
    #           C(q):C(m) + C(q):C(e) + C(q):C(h) +
    #           C(m):C(e) + C(m):C(h) +
    #           C(e):C(h) +
    #           C(q):C(m):C(e):C(h)""", data=df).fit()
    model = ols("""slr ~ C(q) + C(m) + C(e) + C(h)""", data=df).fit()
    #model = ols("""slr ~ C(m) + C(e) + C(h) +
    #           C(m):C(e) + C(m):C(h) + C(e):C(h) +
    #           C(m):C(e):C(h)""", data=df).fit()

    print(model)

    anova_out = sm.stats.anova_lm(model, typ=2)
    print(anova_out)
    idx = 0
    var_q[yr_idx] = anova_out.sum_sq[idx] / n_valid
    idx += 1
    var_m[yr_idx] = anova_out.sum_sq[idx] / n_valid
    idx += 1
    var_e[yr_idx] = anova_out.sum_sq[idx] / n_valid
    idx += 1
    var_h[yr_idx] = anova_out.sum_sq[idx] / n_valid
    idx += 1
#    var_qm[yr_idx] = anova_out.sum_sq[idx] / n_valid
#    idx += 1
#    var_qe[yr_idx] = anova_out.sum_sq[idx] / n_valid
#    idx += 1
#    var_qh[yr_idx] = anova_out.sum_sq[idx] / n_valid
#    idx += 1
#    var_me[yr_idx] = anova_out.sum_sq[idx] / n_valid
#    idx += 1
#    var_mh[yr_idx] = anova_out.sum_sq[idx] / n_valid
#    idx += 1
#    var_eh[yr_idx] = anova_out.sum_sq[idx] / n_valid
#    idx += 1
#    var_qmeh[yr_idx] = anova_out.sum_sq[idx] / n_valid
#    idx += 1
    var_res[yr_idx] = anova_out.sum_sq[idx] / n_valid

#var_all = var_m + var_e + var_h + var_me + var_mh + var_eh + var_qmeh + var_res
var_all = var_m + var_e + var_h + var_res

# plot

fig = plt.figure(1, figsize=(10, 8), facecolor='w')
nrow = 2
ncol = 1

ax1 = fig.add_subplot(nrow, ncol, 1)
thk=2
thn=0.5
ax1.plot(year_list, np.sqrt(var_all), label='all', color='k', linewidth=thk)
ax1.plot(year_list, np.sqrt(var_q), label='q', linewidth=thk)
ax1.plot(year_list, np.sqrt(var_m), label='m', linewidth=thk)
ax1.plot(year_list, np.sqrt(var_e), label='e', linewidth=thk)
ax1.plot(year_list, np.sqrt(var_h), label='h', linewidth=thk)
#ax1.plot(year_list, np.sqrt(var_qm), label='qm', linewidth=thn)
#ax1.plot(year_list, np.sqrt(var_qe), label='qe', linewidth=thn)
#ax1.plot(year_list, np.sqrt(var_qh), label='qh', linewidth=thn)
#ax1.plot(year_list, np.sqrt(var_me), label='me', linewidth=thn)
#ax1.plot(year_list, np.sqrt(var_mh), label='mh', linewidth=thn)
#ax1.plot(year_list, np.sqrt(var_eh), label='eh', linewidth=thn)
#ax1.plot(year_list, np.sqrt(var_qmeh), label='qmeh', linewidth=thn)
ax1.plot(year_list, np.sqrt(var_res), label='residual', linewidth=thn)
plt.legend()
plt.xlabel('Year')
plt.ylabel('sigma (m SLE)')

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


fig = plt.figure(2, figsize=(8, 6), facecolor='w')
nrow = 1
ncol = 1

ax = fig.add_subplot(111)
plt.bar(year_list, valid_runs_per_year, width=0.9)
plt.xlabel('Year')
plt.ylabel('Number of runs used')
plt.ylim([0, 72])

plt.show()
