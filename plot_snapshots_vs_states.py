import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from generate_plots import Evaluation, configure_verbosity
from argparse import Namespace
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.rcParams['text.usetex'] = False
matplotlib.rcParams['font.size'] = 12
matplotlib.rcParams['figure.dpi'] = 300

args = Namespace()
args.ar = Path('../eurosp_data/workdir_tango_inference')
args.duration = 24*3600
args.step = 60
args.verbose = 0
args.exclude_dirs = [
    'cache',
    'tango_inference_control_50/dcmtk/dcmqrscp/0', # 1560.964364 DATA MISSING!!!
    'tango_inference_all_20/bftpd/bftpd/0/workdir/0', # 5220.813821 DATA MISSING!!!
    'tango_inference_control',
    'tango_inference_validate',
    'tango_inference_extend_on_groups_50',
    'tango_inference_dt_predict_50',
    'tango_inference_dt_extrapolate_50',
    'yajl', 'daap',
    '100'
]

args.exclude_runs = ['3', '4', '5']
args.include_targets = [
    'expat', 'exim', 'dcmtk', 'openssh',
    'openssl', 'dnsmasq', 'llhttp', 'rtsp',
    'sip', 'dtls',
    'lightftp', 'pureftpd', 'bftpd', 'proftpd'
    # 'daap', 'yajl',
]
args.mission = 'crosstesting'
configure_verbosity(args.verbose)

feval = Evaluation(args)

# Plotting part:
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import seaborn.objects as so
import numpy as np
from matplotlib.colors import Normalize

def calculate_reduction_ratio(row):
    if row['states'] == 0.0:
        if row['snapshots'] < row['batch_size'] :
            return 'N/A'
        else:
            return '0'
    else:
        r = round((1 - row['states'] / row['snapshots']) * 100, 2)
        st = round(row['states'], 0)
        sn = round(row['snapshots'], 0)
        return f"{st} ({r}%)"

def to_label(row):
    label = ''
    if row['type'] == 'inference' and row['validate'] == False:
        if row['extend_on_groups'] == False and \
                row['dt_predict'] == False and \
                row['dt_extrapolate'] == False:
            label += 'w/o opt'
        if row['extend_on_groups'] == True and \
                row['dt_predict'] == True and \
                row['dt_extrapolate'] == True :
            label += 'w/ opt'
    return label

cs = ['type', 'batch_size',
      'extend_on_groups', 'dt_predict', 'dt_extrapolate',
      'target', 'program', 'validate', 'time_step']
cs2 = ['type', 'batch_size',
      'extend_on_groups', 'dt_predict', 'dt_extrapolate',
      'target', 'program', 'validate']

def ploooooooot(tt, pathname):
    # add more columns for plotting
    fig, axes = plt.subplots(2, 2, sharex=True, sharey=True, layout='constrained')
    axes = axes.flatten()
    bs = [10, 20, 50, 100]
    for i, ax in enumerate(axes):
        tt_by_batch = tt[tt['batch_size'] == bs[i]]
        sns.barplot(data=tt_by_batch, y='target', x='snapshots',
                    ax=ax, color='darkblue', dodge=False)
        sns.barplot(data=tt_by_batch, y='target', x='states',
                    ax=ax, color='orange', dodge=False)
        # ax.plot(theoretical_ct_x, theoretical_ct_y)
        ax.grid(True)
        ax.set_title(f'Batch size: {bs[i]}')
        ax.set_xlabel('# of states (reduction ratio)')
        ax.set_xlim(0, 1500)

        # ax.set_yscale('log')
        # ax.set_ylim(0, 100)
        # ax.set_yticks([0, 25, 50, 75, 100], ['0', '25%', '50%', '75%', '100%'])
        ax.set_ylabel(None)

        for index, value in enumerate(tt_by_batch['snapshots']):
            label = calculate_reduction_ratio(tt_by_batch.iloc[index])
            ax.text(value, index, label, ha='left', va='center')

    print(f'Saving {pathname}')
    try:
        plt.savefig(f'{pathname}.png')
        plt.savefig(f'{pathname}.pdf')
    except ValueError as ex:
        print(ex)

# for i in feval.all_experiments:
    # print('Loaded', i)
df = feval.df_crosstest
df = df.groupby(cs).agg({'snapshots': 'mean', 'states': 'mean'}).reset_index()
tt = df.groupby(cs2).tail(1)

ploooooooot(tt, '../TangoFuzz-paper/media/reduction-ratio')
