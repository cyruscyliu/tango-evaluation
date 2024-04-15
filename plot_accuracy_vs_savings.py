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
    'tango_inference_control',
    'tango_inference_all',
    'tango_inference_extend_on_groups_50',
    'tango_inference_dt_predict_50',
    'tango_inference_dt_extrapolate_50',
    'tango_inference_validate_all_10/dcmtk', # no data
    'tango_inference_validate_all_20/dcmtk', # no data
    'tango_inference_validate_all_50/dcmtk', # no data
    'tango_inference_validate_all_100/dcmtk', # no data
    'tango_inference_validate_all_20/llhttp/parse/0', # no data
    'tango_inference_validate_all_50/llhttp/parse/2', # no data
    'tango_inference_validate_all_100/llhttp', # no data
    'tango_inference_validate_all_50/openssl', # no data
    'tango_inference_validate_all_100/openssl', # no data
    'tango_inference_validate_all_50/tinydtls/dtls/0', # no data
    'tango_inference_validate_all_50/tinydtls/dtls/2', # no data
    'tango_inference_validate_all_100/tinydtls/dtls/2', # no data
    'tango_inference_validate_all_50/live555', # no data
    'tango_inference_validate_all_100/live555', # no data
    'tango_inference_validate_all_100/bftpd', # no data
    'tango_inference_validate_all_100/expat/xmlwf/2', # no data
    'tango_inference_validate_all_100/expat/xmlwf/1', # no data
    'tango_inference_validate_all_100/openssh/sshd/2', # no data
    'tango_inference_validate_all_100/pureftpd/pureftpd', # no data
    'tango_inference_validate_all_100/lightftp/lightftp/0', # no data
    'tango_inference_validate_extend_on_groups_50/live555', # no data
    'tango_inference_validate_extend_on_groups_50/llhttp/parse/0', # no data
    'tango_inference_validate_extend_on_groups_50/llhttp/parse/2', # no data
    'tango_inference_validate_extend_on_groups_50/lightftp/lightftp/1', # no data
    'tango_inference_validate_extend_on_groups_50/tinydtls/dtls/0', # no data
    'tango_inference_validate_extend_on_groups_50/tinydtls/dtls/2', # no data
    'tango_inference_validate_extend_on_groups_50/dcmtk', # no data
    'tango_inference_validate_extend_on_groups_50/openssl', # no data
    'tango_inference_validate_dt_predict_50/live555', # no data
    'tango_inference_validate_dt_predict_50/dcmtk', # no data
    'tango_inference_validate_dt_predict_50/llhttp/parse/2', # no data
    'tango_inference_validate_dt_predict_50/openssl', # no data
    'tango_inference_validate_dt_predict_50/tinydtls/dtls/0', # no data
    'tango_inference_validate_dt_predict_50/tinydtls/dtls/1', # no data
    'tango_inference_validate_dt_predict_50/lightftp/lightftp/0', # no data
    'tango_inference_validate_dt_extrapolate_50/live555', # no data
    'tango_inference_validate_dt_extrapolate_50/dcmtk', # no data
    'tango_inference_validate_dt_extrapolate_50/llhttp/parse/1', # no data
    'tango_inference_validate_dt_extrapolate_50/daapd', # no data
]

args.exclude_runs = ['3', '4']
args.include_targets = [
    'expat', 'exim', 'dcmtk', 'openssh',
    'openssl', 'dnsmasq', 'llhttp', 'live555',
    'kamailio', 'tinydtls',
    'lightftp', 'pureftpd', 'bftpd', 'proftpd',
    'yajl', 'daapd',
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

cs = ['type', 'batch_size',
      'extend_on_groups', 'dt_predict', 'dt_extrapolate',
      'target', 'program', 'validate', 'time_step']

def calculate_accuracy(row):
    s = row['total_misses'] + row['total_hits']
    if s == 0.0:
        return np.nan # invalid data
    else:
        return row['total_hits'] / s * 100

def to_label(row):
    label = ''
    if row['type'] == 'inference' and row['validate'] == True:
        if row['extend_on_groups'] == False and \
                row['dt_predict'] == False and \
                row['dt_extrapolate'] == False:
            label += 'None'
        elif row['extend_on_groups'] == True and \
                row['dt_predict'] == True and \
                row['dt_extrapolate'] == True :
            label += 'BCD'
        elif row['extend_on_groups'] == False and \
                row['dt_predict'] == True and \
                row['dt_extrapolate'] == False:
            label += 'C'
        elif row['extend_on_groups'] == True and \
                row['dt_predict'] == False and \
                row['dt_extrapolate'] == False:
            label += 'B'
        elif row['extend_on_groups'] == False and \
                row['dt_predict'] == True and \
                row['dt_extrapolate'] == True:
            label += 'CD'
        else:
            print('double check')
            print(row)
    return label

marker_dict = {
    'expat': 'o', 'exim': 'v', 'dcmtk': '^', 'openssh': '<', 'openssl': '>',
    'dnsmasq': 's', 'llhttp': 'p', 'live555': '*', 'kamailio': 'h', 'tinydtls': 'D',
    'lightftp': 'd', 'pureftpd': 'P', 'bftpd': 'X', 'proftpd': '8', 'yajl': 'H'
}
color_dict = {
    'expat': 'blue', 'exim': 'green', 'dcmtk': 'red', 'openssh': 'cyan', 'openssl': 'magenta',
    'dnsmasq': 'goldenrod', 'llhttp': 'black', 'live555': 'orange', 'kamailio': 'pink', 'tinydtls': 'purple',
    'lightftp': 'brown', 'pureftpd': 'grey', 'bftpd': 'lime', 'proftpd': 'olive', 'yajl': 'plum'}
batch_size_color_dict = {10: 'red', 20: 'orange', 50: 'green', 100: 'blue'}

def ploooooooot_batch_size_50(tt, pathname):
    tt = tt[tt['batch_size'] == 50]

    fig, axes = plt.subplots(2, 2, sharex=True, sharey=True, layout='constrained')
    axes = axes.flatten()
    opts = ['B', 'C', 'CD', 'BCD']
    handles, labels = None, None
    for i, ax in enumerate(axes):
        tt_by_batch = tt[tt['label'] == opts[i]]
        print(tt_by_batch)
        g = sns.scatterplot(
            data=tt_by_batch, x='savings', y='accuracy', hue='target',
            style='target', markers=marker_dict, palette=color_dict, ax=ax)
        ax.grid(True)
        ax.set_title(f'Optimization: {opts[i]}')
        ax.set_xlim(-5, 105)
        ax.set_xticks([0, 50, 100], ['0', '50%', '100%'])
        ax.set_xlabel('Savings')

        ax.set_ylim(-5, 105)
        ax.set_yticks([0, 25, 50, 75, 100], ['0', '25%', '50%', '75%', '100%'])
        ax.set_ylabel('Accuracy')

        _handles, _labels = ax.get_legend_handles_labels()
        if handles is None or (handles is not None and len(_handles) >= len(handles)):
            handles, labels = _handles, _labels
        ax.legend().remove()

    fig.legend(handles, labels, loc='outside lower center', ncols=3)

    print(f'Saving {pathname}')
    try:
        plt.savefig(f'{pathname}.png')
        plt.savefig(f'{pathname}.pdf')
    except ValueError as ex:
        print(ex)

def ploooooooot_optimization_bcd(tt, pathname):
    tt = tt[tt['label'] == 'BCD']

    fig, axes = plt.subplots(2, 2, sharex=True, sharey=True, layout='constrained')
    axes = axes.flatten()
    bs = [10, 20, 50, 100]
    handles, labels = None, None
    for i, ax in enumerate(axes):
        tt_by_batch = tt[tt['batch_size'] == bs[i]]
        print(tt_by_batch)
        g = sns.scatterplot(
            data=tt_by_batch, x='savings', y='accuracy', hue='target',
            style='target', markers=marker_dict, palette=color_dict, ax=ax)
        ax.grid(True)
        ax.set_title(f'Batch size: {bs[i]}')
        ax.set_xlim(-5, 105)
        ax.set_xticks([0, 50, 100], ['0', '50%', '100%'])
        ax.set_xlabel('Savings')

        ax.set_ylim(-5, 105)
        ax.set_yticks([0, 25, 50, 75, 100], ['0', '25%', '50%', '75%', '100%'])
        ax.set_ylabel('Accuracy')

        _handles, _labels = ax.get_legend_handles_labels()
        if handles is None or (handles is not None and len(_handles) >= len(handles)):
            handles, labels = _handles, _labels
        ax.legend().remove()

    fig.legend(handles, labels, loc='outside lower center', ncols=3)

    print(f'Saving {pathname}')
    try:
        plt.savefig(f'{pathname}.png')
        plt.savefig(f'{pathname}.pdf')
    except ValueError as ex:
        print(ex)

# for i in feval.all_experiments:
#     print('Loaded', i)
df = feval.df_crosstest

# choose the last line
df = df.loc[df['time_step'] == 86340.0]

# calculate savings and accuracy
df = df.rename(columns={'total_savings': 'savings'})
df['accuracy'] = df.apply(calculate_accuracy, axis=1)
df = df.filter(items=['time_step', 'savings', 'accuracy', 'snapshots'])
df = df.groupby(cs).agg({'savings': 'mean', 'accuracy': 'mean', 'snapshots': 'mean'}).reset_index()

# add labels
df['label'] = df.apply(to_label, axis=1)
df = df.filter(items=['batch_size', 'label', 'target', 'program', 'savings', 'accuracy', 'snapshots'])

# get the last record
tt = df.groupby(['batch_size', 'target', 'program', 'label']).tail(1)
ploooooooot_batch_size_50(tt, '../TangoFuzz-paper/media/accuracy_vs_savings-50')
ploooooooot_optimization_bcd(tt, '../TangoFuzz-paper/media/accuracy_vs_savings-bcd')
