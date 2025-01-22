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

for i, file_path in enumerate(file_list):
    run_name = os.path.basename(file_path).split('.')[0]
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
var_me = np.zeros((n_years,)) * np.nan
var_mh = np.zeros((n_years,)) * np.nan
var_eh = np.zeros((n_years,)) * np.nan
var_meh = np.zeros((n_years,)) * np.nan
var_res = np.zeros((n_years,)) * np.nan
for yr_idx, yr in enumerate(year_list):
    print(f'\n***** Year={yr} (ind={yr_idx}) *****\n')
    # get valid indices for this year
    # (not necessary when ensemble is complete)
    valid_run_ind = np.nonzero(np.logical_not(np.isnan(slr_list[:, yr_idx])))[0]
    n_valid = len(valid_run_ind)
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
    i#print(df)
    #model = ols("""slr ~ C(q) + C(m) + C(e) + C(h) +
    #           C(q):C(m) + C(q):C(e) + C(q):C(h) +
    #           C(m):C(e) + C(m):C(h) + C(e):C(h) +
    #           C(q):C(m):C(e):C(h)""", data=df).fit()
    model = ols("""slr ~ C(m) + C(e) + C(h) +
               C(m):C(e) + C(m):C(h) + C(e):C(h) +
               C(m):C(e):C(h)""", data=df).fit()


    anova_out = sm.stats.anova_lm(model, typ=2)
    print(anova_out)
    var_m[yr_idx] = anova_out.sum_sq[0] / n_valid
    var_e[yr_idx] = anova_out.sum_sq[1] / n_valid
    var_h[yr_idx] = anova_out.sum_sq[2] / n_valid
    var_me[yr_idx] = anova_out.sum_sq[3] / n_valid
    var_mh[yr_idx] = anova_out.sum_sq[4] / n_valid
    var_eh[yr_idx] = anova_out.sum_sq[5] / n_valid
    var_meh[yr_idx] = anova_out.sum_sq[6] / n_valid
    var_res[yr_idx] = anova_out.sum_sq[7] / n_valid

var_all = var_m + var_e + var_h + var_me + var_mh + var_eh + var_meh + var_res

# plot

fig = plt.figure(1, figsize=(10, 8), facecolor='w')
nrow = 2
ncol = 1

ax1 = fig.add_subplot(nrow, ncol, 1)
thk=2
thn=0.5
ax1.plot(year_list, np.sqrt(var_all), label='all', color='k', linewidth=thk)
ax1.plot(year_list, np.sqrt(var_m), label='m', linewidth=thk)
ax1.plot(year_list, np.sqrt(var_e), label='e', linewidth=thk)
ax1.plot(year_list, np.sqrt(var_h), label='h', linewidth=thk)
ax1.plot(year_list, np.sqrt(var_me), label='me', linewidth=thn)
ax1.plot(year_list, np.sqrt(var_mh), label='mh', linewidth=thn)
ax1.plot(year_list, np.sqrt(var_eh), label='eh', linewidth=thn)
ax1.plot(year_list, np.sqrt(var_meh), label='meh', linewidth=thn)
ax1.plot(year_list, np.sqrt(var_res), label='residual', linewidth=thn)
plt.legend()
plt.xlabel('Year')
plt.ylabel('sigma (m SLE)')

ax2 = fig.add_subplot(nrow, ncol, 2)
stackdata = np.stack([var_m, var_e, var_h, var_me, var_mh, var_eh, var_meh, var_res])
stackdata = stackdata / stackdata.sum(axis=0) * 100.0
ax2.stackplot(year_list, stackdata, labels=('m', 'e', 'h', 'me', 'mh', 'eh', 'meh', 'residual'))
plt.legend()
plt.xlabel('Year')
plt.ylabel('percentage of variance')


plt.show()
