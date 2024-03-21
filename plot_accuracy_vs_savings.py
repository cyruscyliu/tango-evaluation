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
    'tango_inference_extend_on_groups_50',
    'tango_inference_dt_predict_50',
    'tango_inference_dt_extrapolate_50',
    'tango_inference_validate_all_20/dnsmasq/dnsmasq/0', # 540.367671 DATA MISSING!!!
    'tango_inference_validate_all_20/dnsmasq/dnsmasq/2', # 60.179238 DATA MISSING!!!
    'tango_inference_validate_all_20/dnsmasq/dnsmasq/1', # 120.104876 DATA MISSING!!!
    'tango_inference_validate_all_20/bftpd/bftpd/0', # 1320.289727 DATA MISSING!!!
    'tango_inference_validate_all_20/bftpd/bftpd/2', # 180.131102 DATA MISSING!!!
    'tango_inference_validate_all_20/bftpd/bftpd/1', # 360.12788 DATA MISSING!!!
    'tango_inference_validate_all_20/expat/xmlwf/0', # 81.246044 DATA MISSING!!!
    'tango_inference_validate_all_20/expat/xmlwf/2', # 82.455139 DATA MISSING!!!
    'tango_inference_validate_all_20/expat/xmlwf/1', # 47.665807 DATA MISSING!!!
    'tango_inference_validate_all_20/openssh/sshd/2', # 120.185594 DATA MISSING!!!
    'tango_inference_validate_all_20/openssh/sshd/1', # 120.100545 DATA MISSING!!!
    'tango_inference_validate_all_20/openssl/openssl/1', # 840.616442 DATA MISSING!!!
    'tango_inference_validate_all_20/lightftp/lightftp/0', # 2880.370138 DATA MISSING!!!
    'tango_inference_validate_all_20/lightftp/lightftp/2', # 120.117279 DATA MISSING!!!
    'tango_inference_validate_all_20/lightftp/lightftp/1', # 120.171241 DATA MISSING!!!
    'tango_inference_validate_all_20/rtsp/live555/0', # 143.995341 DATA MISSING!!!
    'tango_inference_validate_all_20/rtsp/live555/2', # 19.866367 DATA MISSING!!!
    'tango_inference_validate_all_20/rtsp/live555/1', # 125.460986 DATA MISSING!!!
    'tango_inference_validate_all_20/exim/exim/0', # 60.196857 DATA MISSING!!!
    'tango_inference_validate_all_20/exim/exim/2', # 1140.54799 DATA MISSING!!!
    'tango_inference_validate_all_20/exim/exim/1', # 840.345548 DATA MISSING!!!
    'tango_inference_validate_all_100/dnsmasq/dnsmasq/0', # 10924.584836 DATA MISSING!!!
    'tango_inference_validate_all_100/dnsmasq/dnsmasq/2', # 2521.114595 DATA MISSING!!!
    'tango_inference_validate_all_100/dnsmasq/dnsmasq/1', # 600.383692 DATA MISSING!!!
    'tango_inference_validate_all_100/expat/xmlwf/0', # 1020.547552 DATA MISSING!!!
    'tango_inference_validate_all_100/expat/xmlwf/2', # 600.301337 DATA MISSING!!!
    'tango_inference_validate_all_100/expat/xmlwf/1', # 840.49502 DATA MISSING!!!
    'tango_inference_validate_dt_extrapolate_50/dnsmasq/dnsmasq/0', # 240.223824 DATA MISSING!!!
    'tango_inference_validate_dt_extrapolate_50/dnsmasq/dnsmasq/2', # 2881.250844 DATA MISSING!!!
    'tango_inference_validate_dt_extrapolate_50/dnsmasq/dnsmasq/1', # 240.167417 DATA MISSING!!!
    'tango_inference_validate_dt_extrapolate_50/bftpd/bftpd/0', # 600.217067 DATA MISSING!!!
    'tango_inference_validate_dt_extrapolate_50/bftpd/bftpd/2', # 2100.447888 DATA MISSING!!!
    'tango_inference_validate_dt_extrapolate_50/expat/xmlwf/0', # 360.257795 DATA MISSING!!!
    'tango_inference_validate_dt_extrapolate_50/expat/xmlwf/2', # 420.265998 DATA MISSING!!!
    'tango_inference_validate_dt_extrapolate_50/expat/xmlwf/1', # 480.31497 DATA MISSING!!!
    'tango_inference_validate_dt_extrapolate_50/lightftp/lightftp/2', # 4680.727698 DATA MISSING!!!
    'tango_inference_validate_dt_extrapolate_50/lightftp/lightftp/1', # 780.205447 DATA MISSING!!!
    'tango_inference_validate_dt_extrapolate_50/exim/exim/0', # 3481.497332 DATA MISSING!!!
    'tango_inference_validate_dt_extrapolate_50/exim/exim/2', # 1440.726728 DATA MISSING!!!
    'tango_inference_validate_dt_extrapolate_50/exim/exim/1', # 960.446341 DATA MISSING!!!
    'tango_inference_validate_extend_on_groups_50/dnsmasq/dnsmasq/0', # 1020.571373 DATA MISSING!!!
    'tango_inference_validate_extend_on_groups_50/dnsmasq/dnsmasq/2', # 840.468338 DATA MISSING!!!
    'tango_inference_validate_extend_on_groups_50/bftpd/bftpd/1', # 6361.299155 DATA MISSING!!!
    'tango_inference_validate_all_50/dnsmasq/dnsmasq/0', # 1200.645891 DATA MISSING!!!
    'tango_inference_validate_all_50/dnsmasq/dnsmasq/2', # 900.447683 DATA MISSING!!!
    'tango_inference_validate_all_50/dnsmasq/dnsmasq/1', # 1260.616751 DATA MISSING!!!
    'tango_inference_validate_all_50/bftpd/bftpd/1', # 6001.268101 DATA MISSING!!!
    'tango_inference_validate_all_50/expat/xmlwf/0', # 240.164633 DATA MISSING!!!
    'tango_inference_validate_all_50/expat/xmlwf/2', # 180.192323 DATA MISSING!!!
    'tango_inference_validate_all_50/expat/xmlwf/1', # 360.299037 DATA MISSING!!!
    'tango_inference_validate_all_50/openssh/sshd/1', # 6200.328545 DATA MISSING!!!
    'tango_inference_validate_all_50/lightftp/lightftp/2', # 2760.410002 DATA MISSING!!!
    'tango_inference_validate_all_50/lightftp/lightftp/1', # 1680.304508 DATA MISSING!!!
    'tango_inference_validate_all_50/exim/exim/2', # 1320.54144 DATA MISSING!!!
    'tango_inference_validate_dt_predict_50/dnsmasq/dnsmasq/2', # 2401.189135 DATA MISSING!!!
    'tango_inference_validate_dt_predict_50/dnsmasq/dnsmasq/1', # 4562.039682 DATA MISSING!!!
    'tango_inference_validate_dt_predict_50/expat/xmlwf/0', # 480.302481 DATA MISSING!!!
    'tango_inference_validate_dt_predict_50/expat/xmlwf/2', # 240.151617 DATA MISSING!!!
    'tango_inference_validate_dt_predict_50/expat/xmlwf/1', # 240.211075 DATA MISSING!!!
    'tango_inference_validate_dt_predict_50/openssh/sshd/0', # 3241.476018 DATA MISSING!!!
    'tango_inference_validate_dt_predict_50/openssh/sshd/1', # 3301.676492 DATA MISSING!!!
    'tango_inference_validate_dt_predict_50/lightftp/lightftp/2', # 7741.889433 DATA MISSING!!!
    'tango_inference_validate_dt_predict_50/exim/exim/2', # 1260.902727 DATA MISSING!!!
    'tango_inference_validate_dt_predict_50/exim/exim/1', # 2040.987691 DATA MISSING!!!
    'tango_inference_validate_all_10/dcmtk/dcmqrscp/0', # 60.179329 DATA MISSING!!!
    'tango_inference_validate_all_10/dcmtk/dcmqrscp/1', # 60.14613 DATA MISSING!!!
    'tango_inference_validate_all_10/dnsmasq/dnsmasq/0', # 120.111658 DATA MISSING!!!
    'tango_inference_validate_all_10/dnsmasq/dnsmasq/2', # 8.164779 DATA MISSING!!!
    'tango_inference_validate_all_10/dnsmasq/dnsmasq/1', # 60.134849 DATA MISSING!!!
    'tango_inference_validate_all_10/bftpd/bftpd/0', # 69.65985 DATA MISSING!!!
    'tango_inference_validate_all_10/bftpd/bftpd/2', # 5.90795 DATA MISSING!!!
    'tango_inference_validate_all_10/expat/xmlwf/0', # 60.08609 DATA MISSING!!!
    'tango_inference_validate_all_10/expat/xmlwf/2', # 69.761319 DATA MISSING!!!
    'tango_inference_validate_all_10/expat/xmlwf/1', # 66.956375 DATA MISSING!!!
    'tango_inference_validate_all_10/openssh/sshd/0', # 19.422725 DATA MISSING!!!
    'tango_inference_validate_all_10/openssh/sshd/2', # 20.616002 DATA MISSING!!!
    'tango_inference_validate_all_10/openssh/sshd/1', # 20.907295 DATA MISSING!!!
    'tango_inference_validate_all_10/openssl/openssl/0', # 720.480112 DATA MISSING!!!
    'tango_inference_validate_all_10/openssl/openssl/2', # 4682.537544 DATA MISSING!!!
    'tango_inference_validate_all_10/openssl/openssl/1', # 60.177844 DATA MISSING!!!
    'tango_inference_validate_all_10/lightftp/lightftp/0', # 2.562111 DATA MISSING!!!
    'tango_inference_validate_all_10/lightftp/lightftp/2', # 660.199362 DATA MISSING!!!
    'tango_inference_validate_all_10/lightftp/lightftp/1', # 2.533536 DATA MISSING!!!
    'tango_inference_validate_all_10/rtsp/live555/0', # 360.281896 DATA MISSING!!!
    'tango_inference_validate_all_10/rtsp/live555/2', # 240.20792 DATA MISSING!!!
    'tango_inference_validate_all_10/rtsp/live555/1', # 13.470424 DATA MISSING!!!
    'tango_inference_validate_all_10/exim/exim/0', # 900.461629 DATA MISSING!!!
    'tango_inference_validate_all_10/exim/exim/2', # 34.32229 DATA MISSING!!!
    'tango_inference_validate_all_10/exim/exim/1', # 33.59406 DATA MISSING!!!
    'yajl', 'daap'
]

args.exclude_runs = ['3', '4']
args.include_targets = [
    'expat', 'exim', 'dcmtk', 'openssh',
    'openssl', 'dnsmasq', 'llhttp', 'rtsp',
    'sip', 'dtls',
    'lightftp', 'pureftpd', 'bftpd', 'proftdp'
    # 'yajl', 'daap',
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
    'dnsmasq': 's', 'llhttp': 'p', 'rtsp': '*', 'sip': 'h', 'dtls': 'D',
    'lightftp': 'd', 'pureftpd': 'P', 'bftpd': 'X', 'proftdp': '8'
}
color_dict = {
    'expat': 'blue', 'exim': 'green', 'dcmtk': 'red', 'openssh': 'cyan', 'openssl': 'magenta',
    'dnsmasq': 'yellow', 'llhttp': 'black', 'rtsp': 'orange', 'sip': 'pink', 'dtls': 'purple',
    'lightftp': 'brown', 'pureftpd': 'grey', 'bftpd': 'lime', 'proftpd': 'olive'}

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
            style='target', markers=marker_dict, palette=color_dict, ax=ax, sizes=[20])
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
        print(tt_by_batch)
        g = sns.scatterplot(
            data=tt_by_batch, x='savings', y='accuracy', hue='target',
            style='target', markers=marker_dict, palette=color_dict, ax=ax, sizes=[20])
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
df = df.loc[df['snapshots'] >= df.index.get_level_values('batch_size')]
# remove the rows where the total savings is zero, which may be due to
# the bug in Tango validation
df = df.loc[df['total_savings'] != 0.0]

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
