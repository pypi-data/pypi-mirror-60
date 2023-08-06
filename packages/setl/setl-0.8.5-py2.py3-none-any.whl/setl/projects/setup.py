__all__ = ["ProjectSetupMixin"]

import os
import pathlib
import subprocess

from typing import Sequence

from .base import BaseProject
from .build import BuildEnv


def _get_setuppy_args(root: pathlib.Path) -> Sequence[str]:
    if root.joinpath("setup.py").exists():
        return ["setup.py"]
    if not root.joinpath("setup.cfg").is_file():
        raise FileNotFoundError("setup.py")
    return ["-c", "from setuptools import setup; setup()"]


class ProjectSetupMixin(BaseProject):
    def setuppy(self, env: BuildEnv, *args: str):
        subprocess.check_call(
            [
                os.fspath(env.interpreter),
                *_get_setuppy_args(self.root),
                *args,
            ],
            cwd=self.root,
        )
