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
args.verbose = 0
args.exclude_dirs = [
    'tango_inference_control_50/dcmtk/dcmqrscp/0', # didn't complete
    'tango_inference_extend_on_groups_50',
    'tango_inference_control',
    'tango_inference_all_10',
    'tango_inference_all_20',
    'tango_inference_all_100',
    'tango_inference_extend_on_groups_50',
    'tango_inference_dt_predict_50',
    'tango_inference_dt_extrapolate_50',
    'tango_inference_validate',
    'tango_afl_nyx',
    'tango_nyxnet',
]

args.exclude_runs = ['3', '4']
args.include_targets = [
    'lightftp', 'bftpd', 'exim', 'dcmtk',
    'openssh', 'openssl', 'dnsmasq', 'pureftpd',
    'proftpd', 'tinydtls', 'live555', 'kamailio',
    'llhttp', 'yajl', 'expat'
]
args.mission = 'snapshots'
configure_verbosity(args.verbose)

feval = Evaluation(args)

# Plotting part:
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import seaborn.objects as so
import numpy as np
from matplotlib.colors import Normalize

def calculate_diversity(df):
    p = df.counts / df.counts.sum()
    N = df.counts.size
    parts = p * np.log(N * p)
    kl = parts.sum()
    if N > 1:
        kl /= np.log(N)

    u = 1 / N
    D = (p ** 2).sum()
    div = (D - u)
    if N > 1:
        div /= (1 - u)
    return pd.DataFrame([
        ['kl', kl, N],
        ], columns=['type', 'value', 'N'])

def add_fuzzer_name(df):
    fuzzer = df.index.get_level_values('fuzzer')[0]
    if 'aflnet' in fuzzer:
        name = 'fuzzer'
    elif 'nyx' in fuzzer:
        name = 'fuzzer'
    elif 'aflpp' in fuzzer:
        name = 'fuzzer'
    elif 'tango' in fuzzer:
        name = 'fuzzer' # r'\mbox{\textsc{Tango}}'
    df['name'] = name
    order = ['name'] + df.index.names
    df = df.set_index('name', append=True).reorder_levels(order)
    return df

df = feval.df_snapshots
df = df.iloc[df.index.get_level_values('fuzzer') != 'aflpp']
df = df.groupby(df.index.names).filter(lambda g: g.counts.sum() > 5)

df = df.groupby('fuzzer', group_keys=False).apply(add_fuzzer_name)
df = df.groupby(df.index.names).apply(calculate_diversity)
df['N'] = df['N'].groupby('target', group_keys=False).apply(lambda g: g / g.max())
df = df.reset_index(['name', 'fuzzer', 'target']).reset_index(drop=True)

ratios = df.groupby('name').apply(lambda g: g.groupby('target').ngroups).sort_values()

df = df.sort_values(by='target')
print(df.to_string())
g = sns.catplot(data=df, y='target', x='value', # hue='type',
            color='white', linewidth=1, # linecolor='black',
            row='name', sharey=False, row_order=ratios.index.values,
            showfliers=False, # shownotches=True, # margin_titles=True,
            kind='box', height=3, aspect=2.5,
            facet_kws=dict(gridspec_kws=dict(height_ratios=ratios, hspace=0.4)))

size_norm = Normalize(0, 1)
def plot_datapoints(name, target, **kwargs):
    ax = plt.gca()
    my_df = df.set_index(['name']).xs(name.unique()[0]).reset_index()
    (
        so.Plot(data=my_df, y='target', x='value', pointsize='N')
        .add(
            so.Dots(artist_kws=dict(zorder=2)),
            so.Jitter(x=0, y=0.2),
            legend=False,
        )
        .scale(pointsize=(2, 8))
        .on(ax)
        .plot()
    )

g.map(plot_datapoints, 'name', 'target')

plt.xlim(-0.1, 1.1)
plt.xlabel('Normalized Divergence')
plt.ylabel('')
pathname = '../TangoFuzz-paper/media/divergence'
plt.savefig(f'{pathname}.png', bbox_inches='tight')
plt.savefig(f'{pathname}.pdf', bbox_inches='tight')
