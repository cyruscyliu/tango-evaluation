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
args.ar = Path('../eurosp_data/old_data_for_cov_ahmad')
args.duration = 24*3600
args.step = 60
args.verbose = 1
args.exclude_dirs = [
    'pfb',
    'workdir_tango_inference',
    'test',
    'pfb-eval-afl-24h',
    'pfb-eval-nyx-24h',
    'pfb-eval-nyxloosen-24h',
    'pfb-eval-sgfuzz-24h',
    'new_data_for_cov_qiang',
    'old_data_for_cov_qiang',
    'nyxnet_with_inference',
    'nyxnet_without_inference',
]

args.exclude_runs = [str(i) for i in range(3, 20)]
args.include_targets = [
    'expat', 'dcmtk', 'openssh', 'openssl',
    'dnsmasq', 'llhttp', 'rtsp', 'sip', 'dtls',
    'lightftp', 'pureftpd', 'yajl', 'bftpd', 'proftpd'
]
args.mission = 'coverage'
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
    if row['time_elapsed'] == 0.0:
        return np.nan
    else:
        return row['time_crosstest'] / row['time_elapsed'] * 100

def ploooooooot(tt, pathname, show_snapshots=True):
    fig, ax = plt.subplots(1, 1, sharex=True, sharey=True, layout='constrained')
    g = sns.lineplot(
        data=tt, x='time_step', y='pc_cov_cnt', hue='fuzzer',
        style='fuzzer', palette='flare', ax=ax)
    ax.grid(True)
    ax.set_xlim(60, 86400)
    ax.set_xscale('log')
    ax.set_xticks([60, 3600, 3600 * 4, 86400], ['1m', '1h', '4h', '1d'])
    ax.get_yaxis().get_major_formatter().set_scientific(False)
    ax.set_xlabel('Time')
    ax.set_yscale('log')
    ax.set_ylabel('# of Edges')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend().remove()
    fig.legend(handles, labels, loc='outside lower center', ncols=2)
    print(f'Saving {pathname}')
    try:
        plt.savefig(f'{pathname}.png')
        plt.savefig(f'{pathname}.pdf')
    except ValueError as ex:
        print(ex)

# for i in feval.all_experiments:
    # print('Loaded', i)
df = feval.df_coverage

cs = ['fuzzer', 'target', 'program', 'time_step']
# by targets
targets = df.index.get_level_values('target').unique()
for target in targets:
    # get data of each target
    tt = df.iloc[df.index.get_level_values('target') == target]
    # calculate the average percentage of 3 runs
    tt = tt.groupby(cs).agg({'pc_cov_cnt': 'mean'}).reset_index()
    ploooooooot(tt, f'../TangoFuzz-paper/media/coverage-{target}')
