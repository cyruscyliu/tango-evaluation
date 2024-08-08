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
args.ar = Path('public')
args.duration = 24*3600
args.step = 60
args.verbose = 0
args.exclude_dirs = [
    'cache',
    'tango_inference_control_50/dcmtk/dcmqrscp/0', # 1560.964364 DATA MISSING!!!
    'tango_inference_all_20/bftpd/bftpd/0/workdir/0', # 5220.813821 DATA MISSING!!!
    'tango_inference_control_100/lightftp/lightftp/0', # 3900.586574 DATA MISSING!!!'
    'tango_inference_all',
    'tango_inference_validate',
    'tango_inference_extend_on_groups_50',
    'tango_inference_dt_predict_50',
    'tango_inference_dt_extrapolate_50',
    'daapd',
]

args.exclude_runs = ['3', '4']
args.include_targets = [
    'expat', 'exim', 'dcmtk', 'openssh',
    'openssl', 'dnsmasq', 'llhttp', 'live555',
    'kamailio', 'tinydtls', 'lightftp', 'pureftpd',
    'bftpd', 'proftpd', 'yajl'
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
        return 0, '0'
    else:
        r = round((1 - row['states'] / row['snapshots']) * 100, 2)
        st = round(row['states'], 0)
        sn = round(row['snapshots'], 0)
        return r, f"{st} ({r:0.2f}%)"

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

targets = [
    'bftpd', 'dcmtk', 'dnsmasq', 'exim',
    'expat', 'kamailio', 'lightftp', 'live555',
    'llhttp', 'openssh', 'openssl', 'proftpd',
    'pureftpd', 'tinydtls', 'yajl'
]

def ploooooooot(tt, pathname):
    # add more columns for plotting
    fig, axes = plt.subplots(2, 2, sharex=True, sharey=True, layout='constrained')
    axes = axes.flatten()
    bs = [10, 20, 50, 100]
    for i, ax in enumerate(axes):
        tt_by_batch = tt[tt['batch_size'] == bs[i]]
        sns.barplot(data=tt_by_batch, y='target', x='snapshots',
                    ax=ax, color='darkblue', dodge=False, gap=0.1)
        sns.barplot(data=tt_by_batch, y='target', x='states',
                    ax=ax, color='orange', dodge=False, gap=0.1)
        # ax.plot(theoretical_ct_x, theoretical_ct_y)
        ax.tick_params(axis='y', labelsize=10)
        ax.set_title(f'Batch size: {bs[i]}')
        ax.set_xlabel(None)
        ax.set_xlim(0, 1500)

        # ax.set_yscale('log')
        # ax.set_ylim(0, 100)
        # ax.set_yticks([0, 25, 50, 75, 100], ['0', '25%', '50%', '75%', '100%'])
        ax.set_ylabel(None)

        s = []
        for _, row in tt_by_batch.iterrows():
            value = row['snapshots']
            target = row['target']
            r, label = calculate_reduction_ratio(row)
            s.append(r)
            index = targets.index(target)
            ax.text(1500, index, label, ha='right', va='center', fontsize=10)
        print(f"average r={np.mean(s)}")

    print(f'Saving {pathname}')
    try:
        plt.savefig(f'{pathname}.png')
        plt.savefig(f'{pathname}.pdf')
    except ValueError as ex:
        print(ex)

# for i in feval.all_experiments:
    # print('Loaded', i)
df = feval.df_crosstest
# remove the rows where the snapshot is less than batch_size
# no cross-testing is executed then no validation is performed
df = df.loc[df['snapshots'] >= df.index.get_level_values('batch_size')]

df = df.groupby(cs).agg({'snapshots': 'mean', 'states': 'mean'}).reset_index()
tt = df.groupby(cs2).tail(1)

ploooooooot(tt, '../TangoFuzz-paper/media/reduction-ratio')
