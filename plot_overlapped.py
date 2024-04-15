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

exclude_runs = ['3', '4']
include_targets = [
    'lightftp', 'bftpd', 'exim', 'dcmtk',
    'openssh', 'openssl', 'dnsmasq', 'pureftpd',
    'proftpd', 'tinydtls', 'live555', 'kamailio',
    'llhttp', 'yajl', 'expat'
]

import os
import json

data = {
    'summary': [],
    'snapshots': []
}
for _root, _, _files in os.walk('../eurosp_data/workdir_tango_inference'):
    for _fuzzer in ['afl_nyx', 'tango_afl_nyx', 'nyxnet', 'tango_nyxnet']:
        if _root.find(_fuzzer) != -1:
            break
    else:
        continue
    for _file in _files:
        if _file != 'snapshots.json':
            continue
        data['summary'].append(_root)
        with open(os.path.join(_root, _file)) as f:
            snapshots = json.load(f)
        data['snapshots'].append(json.dumps(snapshots))

df = pd.DataFrame(data)

# Plotting part:
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import seaborn.objects as so
import numpy as np

# afl_nyx/llhttp/parse/1/workdir
df['run'] = df.apply(lambda row: row['summary'].split('/')[-2], axis=1)
df['target'] = df.apply(lambda row: row['summary'].split('/')[-4], axis=1)
df['fuzzer'] = df.apply(lambda row: row['summary'].split('/')[-5], axis=1)
df.set_index(['run', 'target', 'fuzzer'], inplace=True)

def calculate_a_unique(a, b):
    unique = []
    for k, v in a.items():
        for kk, vv in b.items():
            v_set = set(v)
            vv_set = set(vv)
            # same sets are duplicated
            if vv_set <= v_set:
                unique.append(k)
    return unique

new_data = {
    'target': [],
    'run': [],
    'w/o inference': [],
    'w/ inference': [],
    'overlapping': [],
}
for name, group in df.groupby(['target', 'run']):
    f_json = json.loads(group.iloc[0]['snapshots'])
    try:
        g_json = json.loads(group.iloc[1]['snapshots'])
        unique_a = len(calculate_a_unique(f_json, g_json))
        unique_b = len(calculate_a_unique(g_json, f_json))
        overlapped = len(f_json) - unique_a + len(g_json) - unique_b
        new_data['target'].append(group.index.get_level_values('target')[0])
        new_data['run'].append(group.index.get_level_values('run')[0])
        if group.index.get_level_values('fuzzer')[1].find('tango') == -1:
            new_data['w/o inference'].append(unique_a)
            new_data['w/ inference'].append(unique_b)
        else:
            new_data['w/ inference'].append(unique_a)
            new_data['w/o inference'].append(unique_b)
        new_data['overlapping'].append(overlapped)

    except IndexError:
        continue

df = pd.DataFrame(new_data)
def calculate_percentage(row):
    a = row['w/o inference']
    b = row['w/ inference']
    c = row['overlapping']
    row['w/o inference'] = a / (a + b + c) * 100
    row['w/ inference'] = b / (a + b + c) * 100
    row['overlapping'] = c / (a + b + c) * 100
    return row
df = df.apply(calculate_percentage, axis=1)
df = df.groupby('target').agg({'w/o inference': 'mean', 'overlapping': 'mean', 'w/ inference': 'mean'}).reset_index()
df = df.sort_values(by='target', ascending=False)
print(df)

fig, ax = plt.subplots(1, 1, sharex=True, sharey=True, layout='constrained')
df.plot(x='target', kind='barh', stacked=True,
        color=['goldenrod', 'firebrick', 'indigo'], ax=ax, width=0.8)
ax.set_ylabel('')
ax.set_xlabel('Percentage of infered stats')
handles, labels = ax.get_legend_handles_labels()
ax.legend().remove()
fig.legend(handles, labels, loc='outside upper right', ncols=3)
pathname = '../TangoFuzz-paper/media/cross_inference'
plt.savefig(f'{pathname}.png', bbox_inches='tight')
plt.savefig(f'{pathname}.pdf', bbox_inches='tight')


