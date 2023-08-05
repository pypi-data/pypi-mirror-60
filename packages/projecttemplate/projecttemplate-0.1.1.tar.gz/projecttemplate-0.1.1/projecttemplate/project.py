# -*- coding: utf-8 -*-
"""ProjectTemplate

Class to describe project templates and create projects from them
"""
from pathlib import Path
from typing import Callable, Dict

import pandas as pd  # type: ignore

from .util import AttrDict


class Project:

    _readers: Dict[str, Callable[[Path, str, "Project"], None]] = {}

    def __init__(self, projdir: Path = Path()) -> None:
        self.projdir = Path(projdir)

        self.data = AttrDict()
        self.lib = AttrDict()

    @property
    def datadir(self) -> Path:
        return self.projdir / "data"

    @property
    def mungedir(self) -> Path:
        return self.projdir / "munge"

    @property
    def libdir(self) -> Path:
        return self.projdir / "lib"

    @classmethod
    def register_reader(
        cls,
        extension: str,
        reader: Callable[[Path, str, "Project"], None],
        overwrite: bool = False,
    ) -> None:
        if extension in cls._readers and not overwrite:
            raise ValueError(
                (
                    "Reader for extension {ext!r} already registered,"
                    " use overwite=True to replace the current reader"
                ).format(ext=extension)
            )
        cls._readers[extension] = reader

    def load_libs(self) -> None:
        from runpy import run_path

        print("Loading library functions")
        libs = []
        for f in self.libdir.iterdir():
            if f.suffix != ".py":
                continue
            print("\tLoading", repr(f.stem))
            file = run_path(str(f), run_name=f.stem)
            if f.stem in file:
                libs.append((f.stem, file[f.stem]))
        self.lib = AttrDict(libs)

    def list_data(self) -> pd.DataFrame:
        """
        list_data Lists all the datasets in the current project

        Lists the files with the corresponding variable name and reader
        to load the dataset.

        Returns
        -------
        pandas.DataFrame
            DataFrame with the files in the 'data' directory, the corresponding
            variable name and the reader function to load the data.
        """
        data = pd.DataFrame(
            [
                {
                    "file": f.name,
                    "variable": f.stem,
                    "reader": self._readers.get(f.suffix, None),
                }
                for f in self.datadir.iterdir()
            ]
        )
        data.loc[data["reader"].isnull(), "variable"] = None
        return data

    def load_data(self) -> None:
        print("Loading data from disk")
        for _, (file, variable, reader) in self.list_data().iterrows():
            if pd.isnull(reader):
                continue
            print("\tLoading", repr(file))
            reader(self.datadir / file, variable, self)

    def munge_data(self) -> None:
        from runpy import run_path

        print("Running munge scripts on data")
        for f in self.mungedir.iterdir():
            if f.suffix != ".py":
                continue
            print("\tRunning", repr(f.stem), "...")
            run_path(str(f), init_globals={"project": self})

    def load_project(self) -> None:
        self.load_libs()
        self.load_data()
        self.munge_data()
