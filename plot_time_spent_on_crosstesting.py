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
args.verbose = 1
args.exclude_dirs = [
    'cache',
    'tango_inference_control_50/dcmtk/dcmqrscp/0', # 1560.964364 DATA MISSING!!!
    'tango_inference_all_20/bftpd/bftpd/0/workdir/0', # 5220.813821 DATA MISSING!!!
    'tango_inference_control_100/lightftp/lightftp/0', # 3900.586574 DATA MISSING!!!'
    'tango_inference_validate',
    'tango_inference_extend_on_groups_50',
    'tango_inference_dt_predict_50',
    'tango_inference_dt_extrapolate_50',
    'yajl', 'daap',
]

args.exclude_runs = ['3', '4']
args.include_targets = [
    'expat', 'exim', 'dcmtk', 'openssh',
    'openssl', 'dnsmasq', 'llhttp', 'rtsp',
    'sip', 'dtls',
    'lightftp', 'pureftpd', 'bftpd', 'proftpd'
    # 'daap', 'yajl',
]
args.mission = "crosstesting"
configure_verbosity(args.verbose)

feval = Evaluation(args)

# Plotting part:
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import seaborn.objects as so
import numpy as np
from matplotlib.colors import Normalize

def calculate_percentage(row):
    if row['time_elapsed'] == 0.0: # first row
        return np.nan
    else:
        return row['time_crosstest'] / row['time_elapsed'] * 100

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
      'validate', 'time_step']

def ploooooooot(tt, pathname, show_snapshots=True):
    # add more columns for plotting
    tt['label'] = tt.apply(to_label, axis=1)

    fig, axes = plt.subplots(2, 2, sharex=True, sharey=True, layout='constrained')
    axes = axes.flatten()
    bs = [10, 20, 50, 100]
    for i, ax in enumerate(axes):
        tt_by_batch = tt[tt['batch_size'] == bs[i]]
        g = sns.lineplot(
            data=tt_by_batch, x='time_step', y='percentage', hue='label',
            style='label', palette='flare', ax=ax)
        # ax.plot(theoretical_ct_x, theoretical_ct_y)
        ax.grid(True)
        ax.set_title(f'Batch size m={bs[i]}')
        ax.set_xlim(60, 86400)
        ax.set_xscale('log')
        ax.set_xticks([60, 600, 3600, 3600 * 4, 86400], ['1m', '10m', '1h', '4h', '1d'])
        ax.set_xlabel('Time')

        ax.set_ylim(0, 100)
        ax.set_yticks([0, 25, 50, 75, 100], ['0', '25%', '50%', '75%', '100%'])
        ax.set_ylabel('Time of cross-testing')

        try:
            a = tt_by_batch[tt_by_batch['label'] == 'w/ opt'].filter(
                items=['time_step', 'percentage'])
            a = a[a['time_step'] == 3600.0 *  4]
            a_x, a_y = a['time_step'].values[0], a['percentage'].values[0]
            print(a_x, a_y, round(a_y))
            # ax.text(a_x, a_y, str(f'{round(a_y)}%'), ha='center', va='bottom')
            a = tt_by_batch[tt_by_batch['label'] == 'w/o opt'].filter(
                items=['time_step', 'percentage'])
            a = a[a['time_step'] == 3600.0 *  4]
            a_x, a_y = a['time_step'].values[0], a['percentage'].values[0]
            # ax.text(a_x, a_y, str(f'{round(a_y)}%'), ha='center', va='bottom')
            print(a_x, a_y, round(a_y))
        except IndexError as ax:
            print('adding text', ax)

        try:
            a = tt_by_batch[tt_by_batch['label'] == 'w/o opt'].iloc[-1]['snapshots']
            b = tt_by_batch[tt_by_batch['label'] == 'w/ opt'].iloc[-1]['snapshots']
            labels = [str(round(a, 2)), str(round(b, 2))]
            handles, _ = ax.get_legend_handles_labels()
            ax.legend(handles, labels)
            if not show_snapshots:
                ax.legend().remove()
        except IndexError as ax:
            print('updating legends', ax)

    fig.legend(reversed(handles), reversed(['Optimizations = None', 'Optimizations = All']),
               loc='outside lower center', ncols=2)
    print(f'Saving {pathname}')
    try:
        plt.savefig(f'{pathname}.png')
        plt.savefig(f'{pathname}.pdf')
    except ValueError as ex:
        print(ex)

# for i in feval.all_experiments:
    # print('Loaded', i)
df = feval.df_crosstest

# theoretical_ct_x = [i for i in range(1, 86400)]
# theoretical_ct_y = [np.square(np.log10(i)) / i * 100 for i in theoretical_ct_x]

df['percentage'] = df.apply(calculate_percentage, axis=1)
df = df.filter(items=[
    'time_step', 'time_elapsed', 'time_crosstest', 'percentage', 'snapshots'])

# average
tt = df.groupby(cs).agg({'percentage': 'mean', 'snapshots': 'mean'}).reset_index().groupby(
    cs2).agg({'percentage': 'median', 'snapshots': 'median'}).reset_index()
ploooooooot(tt, '../TangoFuzz-paper/media/time-average', show_snapshots=False)

# by targets
targets = df.index.get_level_values('target').unique()
for target in targets:
    # get data of each target
    tt = df.iloc[df.index.get_level_values('target') == target].filter(
        items=['time_step', 'time_elapsed', 'time_crosstest', 'percentage', 'snapshots'])
    # calculate the average percentage of 3 runs
    tt = tt.groupby(cs).agg({'percentage': 'mean', 'snapshots': 'mean'}).reset_index()
    ploooooooot(tt, f'../TangoFuzz-paper/media/time-{target}')
