from os.path import join, dirname

with open(join(dirname(__file__), "VERSION")) as f:
    __version__ = f.read().strip()

from .utils import index  # noqa: F401

from .tensor import Tensor  # noqa: F401
from .tensor import PyTorchTensor  # noqa: F401
from .tensor import TensorFlowTensor  # noqa: F401
from .tensor import NumPyTensor  # noqa: F401
from .tensor import JAXTensor  # noqa: F401

from .tensor.base import istensor  # noqa: F401
from .astensor import astensor  # noqa: F401

from .modules import torch  # noqa: F401
from .modules import tensorflow  # noqa: F401
from .modules import jax  # noqa: F401
from .modules import numpy  # noqa: F401

from .framework import *  # noqa: F401,F403

from . import norms  # noqa: F401

from .lib import *  # noqa: F401,F403
