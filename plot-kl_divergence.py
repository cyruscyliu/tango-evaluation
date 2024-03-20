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

def pp_time(time):
    if np.isnan(time) :
        return time
    if time < 60:
        return '%gs' % time
    if time < (60 * 60):
        return '%gm' % (time / 60)
    if time < (24 * 60 * 60):
        return '%gh' % (time / (60 * 60))
    if time < (7 * 24 * 60 * 60):
        return '%gd' % (time / (24 * 60 * 60))
    if time < (30 * 24 * 60 * 60):
        return '%gw' % (time / (7 * 24 * 60 * 60))
    return '%gM' % (time / (30 * 24 * 60 * 60))

def list_ticks(bound, *, logfactor=None, linterval=None):
    if logfactor is not None:
        DENOMINATIONS = [
            1 * 60, # minutes
#             15 * 60, # quarter-hour
#             30 * 60, # half-hour
            60 * 60, # hour
#             12 * 60 * 60, # half-day
            24 * 60 * 60, # day
            7 * 24 * 60 * 60, # week
            30 * 24 * 60 * 60, # month
        ]
        current_denom = 0
        last_tick = min(DENOMINATIONS[current_denom], bound)
        ticks = [last_tick]
        while last_tick < bound:
            last_tick *= logfactor
            if (current_denom + 1) < len(DENOMINATIONS) \
                and last_tick >= DENOMINATIONS[current_denom + 1]:
                current_denom += 1
                last_tick = DENOMINATIONS[current_denom]
            ticks.append(last_tick)
    elif linterval is not None:
        if linterval <= 0:
            linterval = bound // 10
        last_tick = min(linterval, bound)
        ticks = [last_tick]
        while last_tick < bound:
            last_tick += linterval
            ticks.append(last_tick)
    else:
        raise ValueError("One of logfactor or linterval must be specified")
    return ticks

args = Namespace()
args.ar = Path('../eurosp_data/workdir_tango_inference')
args.duration = 24*3600
args.step = 60
args.verbose = 0
args.exclude_dirs = [
    'tango_inference_control_50/dcmtk/dcmqrscp/0', # didn't complete
    'tango_inference_extend_on_groups_50',
    'tango_inference_control',
    'tango_inference_all',
    'tango_inference_extend_on_groups_50',
    'tango_inference_dt_predict_50',
    'tango_inference_dt_extrapolate_50',
    'tango_inference_validate_dt_extrapolate_50',
    '100',
    'sip',
    'yajl'
]

args.exclude_runs = ['3', '4']
args.include_targets = [
    'lightftp', 'bftpd', 'exim', 'dcmtk',
    'openssh', 'openssl', 'dnsmasq', 'pureftpd',
    'dtls', 'rtsp', 'sip', 'llhttp', 'yajl', 'expat'
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
        name = 'AFLNet'
    elif 'nyx' in fuzzer:
        name = 'Nyx-Net'
    elif 'aflpp' in fuzzer:
        name = 'AFL++'
    elif 'tango' in fuzzer:
        name = r'\mbox{\textsc{Tango}}'
    df['name'] = name
    order = ['name'] + df.index.names
    df = df.set_index('name', append=True).reorder_levels(order)
    return df

df = feval.df_inference
df = df.iloc[df.index.get_level_values('fuzzer') != 'aflpp']
df = df.groupby(df.index.names).filter(lambda g: g.counts.sum() > 5)

df = df.groupby('fuzzer', group_keys=False).apply(add_fuzzer_name)
df = df.groupby(df.index.names).apply(calculate_diversity)
df['N'] = df['N'].groupby('target', group_keys=False).apply(lambda g: g / g.max())
df = df.reset_index(['name', 'fuzzer', 'target']).reset_index(drop=True)

ratios = df.groupby('name').apply(lambda g: g.groupby('target').ngroups).sort_values()

g = sns.catplot(data=df, y='target', x='value', # hue='type',
            color='white', linewidth=1, #linecolor='black',
            row='name', sharey=False, row_order=ratios.index.values,
            showfliers=False, shownotches=True, #margin_titles=True,
            kind='box', height=1.5, aspect=3,
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

g.set_axis_labels(x_var='Normalized Divergence', y_var='Target')
g.set(xlim=(-0.1,1))
g.set_titles(row_template=r'{row_name}')
