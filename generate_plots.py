from __future__ import annotations
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

import argparse
import logging
from pathlib import Path
from collections import namedtuple
from typing import Iterable, Optional, Type
from dataclasses import dataclass

import pandas as pd
import numpy as np
from pandas import DataFrame
from os import PathLike
import json

Params = namedtuple("Params", ("fuzzer", "target", "program", "experiment"))


def main():
    args = parse_args()
    configure_verbosity(args.verbose)

    feval = Evaluation(args)


def parse_args():
    parser = argparse.ArgumentParser(
        description=("Generate plots from Tango's state inference statistics.")
    )
    parser.add_argument(
        "ar",
        type=Path,
        help="The path to the root directory containing all experiments.",
    )
    parser.add_argument(
        "duration",
        type=int,
        default=(24 * 60 * 60),
        help="The time duration of the campaign, in seconds.",
    )
    parser.add_argument(
        "step",
        type=int,
        default=60,
        help="The time step to use when resampling data, in seconds.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help=(
            "Controls the verbosity of messages. "
            "-v prints info. -vv prints debug. Default: warnings and higher."
        ),
    )
    return parser.parse_args()


def configure_verbosity(level):
    mapping = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
    # will raise exception when level is invalid
    numeric_level = mapping[level]
    logging.getLogger().setLevel(numeric_level)


@dataclass
class Evaluation:
    args: argparse.Namespace

    def __post_init__(self):
        self.all_experiments = list(
            map(Experiment, self.find_experiments(self.args.ar))
        )
        logging.info(f"Found {len(self.all_experiments)} experiments")
        if self.args.mission == 'crosstesting':
            self.df_crosstest = self.get_master_df(
                filename="crosstest_0.csv",
                upper_bound=self.args.duration,
                time_step=self.args.step,
            )
        # self.df_inference = self.get_master_df(
        #     filename='inference.json')
        if self.args.mission == 'coverage':
            self.df_coverage = self.get_master_df(
                filename="pc_cov_cnts.csv",
                upper_bound=self.args.duration,
                time_step=self.args.step,
            )

    def find_experiments(self, path) -> Iterable[Path]:
        logging.info("Finding experiments ...")
        rs = []
        for p in path.rglob("workdir/"):
            wanted = False
            for target in self.args.include_targets:
                if p.as_posix().find(target) != -1:
                    wanted = True
            for ed in self.args.exclude_dirs:
                if p.as_posix().find(ed) != -1:
                    wanted = False
            for er in self.args.exclude_runs:
                if p.parent.as_posix().endswith(er):
                    wanted = False
            if wanted:
                rs.append(p.parent)
        return rs

    def get_all_recordings(self, *args, **kwargs) -> Iterable[Recording]:
        for e in self.all_experiments:
            try:
                yield e.read_recording(*args, **kwargs)
            except FileNotFoundError:
                continue

    def get_annotated_dfs(self, *args, **kwargs) -> Iterable[DataFrame]:
        logging.info("Getting all recordings ...")
        recordings = self.get_all_recordings(*args, **kwargs)
        return map(lambda r: r.annotate(inplace=True), recordings)

    def get_master_df(self, *args, **kwargs) -> DataFrame:
        logging.info("Getting annotated dfs ...")
        dfs = self.get_annotated_dfs(*args, **kwargs)
        return pd.concat(dfs)

    def generate_time_overhead(self) -> DataFrame:
        pass


@dataclass
class Experiment:
    path: PathLike

    def __post_init__(self):
        logging.debug("%s", self.path)

    @property
    def parameters(self) -> Params:
        return Params._make(self.path.parts[-len(Params._fields) :])

    def get_recordings(self) -> Iterable[Recording]:
        for file in Recording.handlers:
            path = self.path / "workdir" / file
            if not path.is_file():
                continue
            try:
                record = self.read_recording(path.stem)
                print(record)
                yield record
                logging.info(f"Manage to read {path}")
            except KeyError as ex:
                pass

    def read_recording(self, filename: str, **kwargs) -> Recording:
        path = self.path / "workdir" / filename
        logging.info(f"Loading {path}")
        return Recording(filename=filename, path=path, experiment=self, **kwargs)

    def annotate(self, df: DataFrame, inplace=False) -> DataFrame:
        logging.info("Annotating in Experiment")
        if not inplace:
            df = df.copy()
        append = False
        for param in self.parameters._fields:
            df[param] = getattr(self.parameters, param)
            logging.info(f"Indexing (row labels) {param} -> {getattr(self.parameters, param)}")
            df.set_index(param, append=append, inplace=True)
            append = True
        logging.info("Annotating in Experiment: Done")
        return df

# 86357

class Measurement:
    def __init__(self, *, filename: str, df: DataFrame, **kwargs):
        self.filename = filename
        self.df = df
        if kwargs:
            logging.warning("Unused parameters for %s: %s", self.__class__, kwargs)


class Recording(Measurement):
    handlers: dict[str, Type] = {}

    def __init_subclass__(cls, *, filename: str, **kwargs):
        super().__init_subclass__(**kwargs)
        handler = cls.handlers.setdefault(filename, cls)

    def __new__(cls, filename: str, **kwargs):
        handler = cls.handlers[filename]
        return super(__class__, handler).__new__(handler)

    def __init__(self, *, experiment: Experiment, **kwargs):
        super().__init__(**kwargs)
        self.experiment = experiment

    def annotate(self, **kwargs) -> DataFrame:
        logging.info("Annotating in Recording")
        df = self.experiment.annotate(self.df, **kwargs)
        df["recording"] = self.filename
        logging.info(f"Indexing (row labels) recording -> {self.filename}")
        rv = df.set_index(
            "recording", append=True, inplace=kwargs.get("inplace", False)
        )
        logging.info("Annotating in Recording: Done")
        return rv or df


class TimeSeriesResamplerMixin:
    def __init__(
        self,
        *,
        time_column: str,
        time_step: float,
        upper_bound: Optional[float] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.time_column = time_column
        self.time_step = time_step
        self.upper_bound = upper_bound

    def resample(self) -> DataFrame:
        self.df.at[0, self.time_column] = 0
        df = self.df.set_index(self.time_column, drop=False)
        df.index = pd.to_timedelta(df.index, unit="s")
        df = df.resample(f"{self.time_step}S").ffill()

        if self.upper_bound:
            time_grid = np.arange(0, self.upper_bound, self.time_step)
            df_bounded = pd.DataFrame(
                index=pd.to_timedelta(time_grid, unit="s"), columns=df.columns
            )
            df = df.reindex_like(df_bounded, method="ffill", copy=False)
        df.index = df.index.total_seconds()
        df = df.rename_axis("time_step").reset_index()
        return df

class Coverage(TimeSeriesResamplerMixin, Recording, filename="pc_cov_cnts.csv"):
    def __init__(self, *, path: Path, delimiter: str = ",", **kwargs):
        df = pd.read_csv(path, delimiter=delimiter)
        time_elapsed = df.iloc[-1]['time_elapsed']
        if time_elapsed < 80000:
            logging.warning(f'{path} {time_elapsed} DATA MISSING!!!')
        super().__init__(df=df, time_column="time_elapsed", **kwargs)
        df = self.resample()
        # interpolate initial time and counter stats
        interp_linear = ["time_elapsed", "pc_cov_cnt"]
        interp_pad = df.columns.difference([*interp_linear, "time_step"])
        interp_all = [*interp_linear, *interp_pad]
        # df = df.groupby(df.index.names, as_index=False).apply(
        # self._interpolate, interp_linear, interp_pad, interp_all)
        try:
            _df = self._interpolate(df, interp_linear, interp_pad, interp_all)
            self.df = _df
        except TypeError:
            self.df = df
        logging.info(f"Loaded {path}")

    def _interpolate(self, df, interp_linear, interp_pad, interp_all):
        df.loc[df[interp_all].duplicated(), interp_all] = np.nan
        df.loc[df["time_step"] == 0.0, interp_all] = 0
        df[interp_linear] = df[interp_linear].interpolate("linear")
        df[interp_pad] = df[interp_pad].interpolate("pad")
        return df

    def annotate(self, **kwargs) -> DataFrame:
        logging.info("Annotating in Crosstest")
        df = super().annotate(**kwargs)
        fuzzer = self.experiment.parameters.fuzzer
        parameters = self.FUZZER_PARAMETERS[fuzzer]
        logging.info(f"Droping index (row labels) fuzzer -> {fuzzer}")
        df = df.droplevel("fuzzer")
        old_index = df.index.copy()
        for param, value in parameters.items():
            df[param] = value
            logging.info(f"Indexing (row labels) {param} -> {value}")
            df = (
                df.set_index(param, append=True, inplace=kwargs.get("inplace", False))
                or df
            )
        df = df.reorder_levels(list(parameters.keys()) + old_index.names)
        logging.info("Annotating in Crosstest: Done")
        return df

class Crosstest(TimeSeriesResamplerMixin, Recording, filename="crosstest_0.csv"):
    FUZZER_PARAMETERS = {
        "tango_inference_validate_extend_on_groups_50": {
            "type": "inference",
            "batch_size": 50,
            "extend_on_groups": True,
            "dt_predict": False,
            "dt_extrapolate": False,
            "validate": True,
        },
        "tango_inference_validate_dt_predict_50": {
            "type": "inference",
            "batch_size": 50,
            "extend_on_groups": False,
            "dt_predict": True,
            "dt_extrapolate": False,
            "validate": True,
        },
        "tango_inference_validate_dt_extrapolate_50": {
            "type": "inference",
            "batch_size": 50,
            "extend_on_groups": False,
            "dt_predict": True,
            "dt_extrapolate": True,
            "validate": True,
        },
        "tango_inference_validate_all_10": {
            "type": "inference",
            "batch_size": 10,
            "extend_on_groups": True,
            "dt_predict": True,
            "dt_extrapolate": True,
            "validate": True,
        },
        "tango_inference_validate_all_20": {
            "type": "inference",
            "batch_size": 20,
            "extend_on_groups": True,
            "dt_predict": True,
            "dt_extrapolate": True,
            "validate": True,
        },
        "tango_inference_validate_all_50": {
            "type": "inference",
            "batch_size": 50,
            "extend_on_groups": True,
            "dt_predict": True,
            "dt_extrapolate": True,
            "validate": True,
        },
        "tango_inference_validate_all_100": {
            "type": "inference",
            "batch_size": 100,
            "extend_on_groups": True,
            "dt_predict": True,
            "dt_extrapolate": True,
            "validate": True,
        },
        "tango_inference_extend_on_groups_50": {
            "type": "inference",
            "batch_size": 50,
            "extend_on_groups": True,
            "dt_predict": False,
            "dt_extrapolate": False,
            "validate": False,
        },
        "tango_inference_dt_predict_50": {
            "type": "inference",
            "batch_size": 50,
            "extend_on_groups": False,
            "dt_predict": True,
            "dt_extrapolate": False,
            "validate": False,
        },
        "tango_inference_dt_extrapolate_50": {
            "type": "inference",
            "batch_size": 50,
            "extend_on_groups": False,
            "dt_predict": True,
            "dt_extrapolate": True,
            "validate": False,
        },
        "tango_inference_all_10": {
            "type": "inference",
            "batch_size": 10,
            "extend_on_groups": True,
            "dt_predict": True,
            "dt_extrapolate": True,
            "validate": False,
        },
        "tango_inference_all_20": {
            "type": "inference",
            "batch_size": 20,
            "extend_on_groups": True,
            "dt_predict": True,
            "dt_extrapolate": True,
            "validate": False,
        },
        "tango_inference_all_50": {
            "type": "inference",
            "batch_size": 50,
            "extend_on_groups": True,
            "dt_predict": True,
            "dt_extrapolate": True,
            "validate": False,
        },
        "tango_inference_all_100": {
            "type": "inference",
            "batch_size": 100,
            "extend_on_groups": True,
            "dt_predict": True,
            "dt_extrapolate": True,
            "validate": False,
        },
        "tango_inference_control_10": {
            "type": "inference",
            "batch_size": 10,
            "extend_on_groups": False,
            "dt_predict": False,
            "dt_extrapolate": False,
            "validate": False,
        },
        "tango_inference_control_20": {
            "type": "inference",
            "batch_size": 20,
            "extend_on_groups": False,
            "dt_predict": False,
            "dt_extrapolate": False,
            "validate": False,
        },
        "tango_inference_control_50": {
            "type": "inference",
            "batch_size": 50,
            "extend_on_groups": False,
            "dt_predict": False,
            "dt_extrapolate": False,
            "validate": False,
        },
        "tango_inference_control_100": {
            "type": "inference",
            "batch_size": 100,
            "extend_on_groups": False,
            "dt_predict": False,
            "dt_extrapolate": False,
            "validate": False,
        },
    }

    def __init__(self, *, path: Path, delimiter: str = ",", **kwargs):
        df = pd.read_csv(path, delimiter=delimiter)
        time_elapsed = df.iloc[-1]['time_elapsed']
        if time_elapsed < 80000:
            logging.warning(f'{path} {time_elapsed} DATA MISSING!!!')
        super().__init__(df=df, time_column="time_elapsed", **kwargs)
        df = self.resample()
        # interpolate initial time and counter stats
        interp_linear = ["time_elapsed", "time_crosstest"]
        interp_pad = df.columns.difference([*interp_linear, "time_step"])
        interp_all = [*interp_linear, *interp_pad]
        # df = df.groupby(df.index.names, as_index=False).apply(
        # self._interpolate, interp_linear, interp_pad, interp_all)
        try:
            _df = self._interpolate(df, interp_linear, interp_pad, interp_all)
            self.df = _df
        except TypeError:
            self.df = df
        logging.info(f"Loaded {path}")

    def _interpolate(self, df, interp_linear, interp_pad, interp_all):
        df.loc[df[interp_all].duplicated(), interp_all] = np.nan
        df.loc[df["time_step"] == 0.0, interp_all] = 0
        df[interp_linear] = df[interp_linear].interpolate("linear")
        df[interp_pad] = df[interp_pad].interpolate("pad")
        return df

    def get_overhead_time(self):
        df = self.df.set_index(self.time_column)
        df_overhead = df["time_crosstest"] / df.index
        df_overhead.fillna(1, inplace=True)
        df_savings = df["total_savings"]
        df_savings.fillna(0, inplace=True)
        df = pd.concat((df_overhead, df_savings), axis=1)
        return CrosstestOverhead(df=df)

    def get_inference_ratio(self):
        df = self.df.set_index(self.time_column)
        df = df[["snapshots", "states"]]
        df["ratio"] = df["states"] / df["snapshots"]
        df = df.fillna(1)
        return StateInferenceRatio(df=df)

    def get_measurements(self) -> Iterable[Measurement]:
        return self.get_overhead_time(), self.get_inference_ratio()

    def annotate(self, **kwargs) -> DataFrame:
        logging.info("Annotating in Crosstest")
        df = super().annotate(**kwargs)
        fuzzer = self.experiment.parameters.fuzzer
        parameters = self.FUZZER_PARAMETERS[fuzzer]
        logging.info(f"Droping index (row labels) fuzzer -> {fuzzer}")
        df = df.droplevel("fuzzer")
        old_index = df.index.copy()
        for param, value in parameters.items():
            df[param] = value
            logging.info(f"Indexing (row labels) {param} -> {value}")
            df = (
                df.set_index(param, append=True, inplace=kwargs.get("inplace", False))
                or df
            )
        df = df.reorder_levels(list(parameters.keys()) + old_index.names)
        logging.info("Annotating in Crosstest: Done")
        return df

class InferenceEntropy(Recording, filename="inference.json"):
    def __init__(self, *, path: Path, **kwargs):
        with path.open() as f:
            data = json.load(f)
        counts = [len(v) for v in data.values()]
        df = pd.DataFrame({"counts": counts})
        super().__init__(df=df, **kwargs)