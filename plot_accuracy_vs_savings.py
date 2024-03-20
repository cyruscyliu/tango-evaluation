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
    'tango_inference_control',
    'tango_inference_all',
    'tango_inference_validate_all_20/dnsmasq',
    'tango_inference_validate_all_20/expat',
    'tango_inference_validate_all_20/openssh/sshd/2',
    'tango_inference_validate_all_20/openssh/sshd/1',
    'tango_inference_validate_all_20/openssl/openssl/1',
    'tango_inference_validate_all_20/rtsp/live555',
    'tango_inference_validate_all_20/exim/exim',
    'tango_inference_validate_all_100/dnsmasq/dnsmasq/2',
    'tango_inference_validate_all_100/dnsmasq/dnsmasq/1',
    'tango_inference_validate_all_100/expat/xmlwf',
    'tango_inference_validate_dt_extrapolate_50/dnsmasq/dnsmasq',
    'tango_inference_validate_dt_extrapolate_50/expat/xmlwf',
    'tango_inference_validate_dt_extrapolate_50/exim/exim',
    'tango_inference_validate_extend_on_groups_50/dnsmasq/dnsmasq/0',
    'tango_inference_validate_extend_on_groups_50/dnsmasq/dnsmasq/2',
    'tango_inference_validate_all_50/dnsmasq/dnsmasq',
    'tango_inference_validate_all_50/expat/xmlwf',
    'tango_inference_validate_all_50/openssh/sshd/1',
    'tango_inference_validate_all_50/exim/exim/2',
    'tango_inference_validate_dt_predict_50/dnsmasq/dnsmasq/2',
    'tango_inference_validate_dt_predict_50/dnsmasq/dnsmasq/1',
    'tango_inference_validate_dt_predict_50/expat/xmlwf',
    'tango_inference_validate_dt_predict_50/openssh/sshd/0',
    'tango_inference_validate_dt_predict_50/openssh/sshd/1',
    'tango_inference_validate_dt_predict_50/exim/exim',
    'tango_inference_validate_all_10/dcmtk/dcmqrscp/0',
    'tango_inference_validate_all_10/dcmtk/dcmqrscp/1',
    'tango_inference_validate_all_10/dnsmasq/dnsmasq',
    'tango_inference_validate_all_10/expat/xmlwf',
    'tango_inference_validate_all_10/openssh/sshd',
    'tango_inference_validate_all_10/openssl/openssl',
    'tango_inference_validate_all_10/rtsp/live555',
    'tango_inference_validate_all_10/exim/exim',
    'tango_inference_extend_on_groups_50',
    'tango_inference_dt_predict_50',
    'tango_inference_dt_extrapolate_50',
    'all_20/sip', 'all_50/sip', 'all_100/sip', 'dt_predict_50/sip', 'dt_extrapolate_50/sip',
    '20/dtls', '50/dtls', '100/dtls', 'dt_predict_50/dtls', 'dt_extrapolate_50/dtls',
    '20/lightftp', '50/lightftp', '100/lightftp', 'dt_predict_50/lightftp', 'dt_extrapolate_50/lightftp',
    '20/pureftpd', '50/pureftpd', '100/pureftpd', 'dt_predict_50/pureftpd', 'dt_extrapolate_50/pureftpd',
    '20/yajl', '50/yajl', '100/yajl', 'dt_predict_50/yajl', 'dt_extrapolate_50/yajl',
    '20/bftpd', '50/bftpd', '100/bftpd', 'dt_predict_50/bftpd', 'dt_extrapolate_50/bftpd',
    '20/daap', '50/daap', '100/daap', 'dt_predict_50/daap', 'dt_extrapolate_50/daap',
    '20/proftdp', '50/proftdp', '100/proftdp' 'dt_predict_50/proftpd', 'dt_extrapolate_50/proftpd',
]

args.exclude_runs = ['3', '4']
args.include_targets = [
    'expat', 'exim', 'dcmtk', 'openssh',
    'openssl', 'dnsmasq', 'llhttp', 'rtsp',
    'sip', 'dtls',
    'lightftp', 'pureftpd', 'yajl', 'bftpd', 'daap', 'proftdp'
]
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
        # no cross-testing -> no validation
        if row['snapshots'] < row.name[cs.index('batch_size')]:
            return 100
        elif row['savings'] == 0.0:
            return 100
        else:
            return np.nan
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

def ploooooooot_batch_size_50(tt, pathname):
    tt = tt[tt['batch_size'] == 50]

    fig, axes = plt.subplots(2, 2, sharex=True, sharey=True, layout='constrained')
    axes = axes.flatten()
    opts = ['B', 'C', 'CD', 'BCD']
    handles, labels = None, None
    for i, ax in enumerate(axes):
        tt_by_batch = tt[tt['label'] == opts[i]]
        markers = ['${:x}$'.format(i) for i in range(0, 16)]
        palette = ['black' for i in range(0, 16)]
        print(tt_by_batch)
        g = sns.scatterplot(
            data=tt_by_batch, x='savings', y='accuracy',
            hue='target', style='target', ax=ax, sizes=[20])
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

    fig.legend(handles, labels, loc='outside lower center', ncols=4)

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
        markers = ['${:x}$'.format(i) for i in range(0, 16)]
        palette = ['black' for i in range(0, 16)]
        print(tt_by_batch)
        g = sns.scatterplot(
            data=tt_by_batch, x='savings', y='accuracy', hue='target',
            style='target', ax=ax, sizes=[20])
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

    fig.legend(handles, labels, loc='outside lower center', ncols=4)

    print(f'Saving {pathname}')
    try:
        plt.savefig(f'{pathname}.png')
        plt.savefig(f'{pathname}.pdf')
    except ValueError as ex:
        print(ex)


# for i in feval.all_experiments:
#     print('Loaded', i)
df = feval.df_crosstest

# remove the rows where the snapshot is less than batch_size
# no cross-testing is executed then no validation is performed
# df = df.loc[df['snapshots'] >= df.index.get_level_values('batch_size')]

# calculate savings and accuracy
df['savings'] = df['total_savings']
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
