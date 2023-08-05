"""
Create templates for project directories

Projects can be created from a script or from a directory
"""
from abc import ABC, abstractmethod
from pathlib import Path


class Template(ABC):
    def __init__(self, name, description):
        self.name = name
        self.description = description

    @abstractmethod
    def create_project(self, location, allow_existing=False):
        pass


class DefaultTemplate(Template):
    def __init__(self):
        super().__init__("Default", "Builtin default template")

    def create_project(self, location, allow_existing=False):
        location = Path(location).resolve()
        if not location.parent.exists():
            raise ValueError("Parent directory for new project must exist")
        if not allow_existing and location.exists():
            raise ValueError(
                "Project directory exists, use 'allow_existing=True' to create anyway."
            )
        datadir = location / "data"
        libdir = location / "lib"
        mungedir = location / "munge"
        datadir.mkdir(exist_ok=True)
        libdir.mkdir(exist_ok=True)
        mungedir.mkdir(exist_ok=True)
        with (datadir / "README.md").open("w") as f:
            f.write(
                """This directory contains the datafiles for your project\n
                These files will be loaded by calling load_project if the
                file extension is registered with a corresponding reader.
                The data can then be accessed using the Project.data attribute."""
            )
        with (libdir / "README.md").open("w") as f:
            f.write(
                """This directory contains library functions for your project\n
                These files will be ran before loading the data, allowing you
                to register additional data readers. Objects defined in the file
                with a name matching the filename will be made available in the
                Project.lib attribute."""
            )
        with (mungedir / "README.md").open("w") as f:
            f.write(
                """This project contains preprocessing scripts\n
                These files will be run after the data files are loaded, and
                have access to the current Project object using the global
                variable `project`."""
            )
