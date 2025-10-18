"""Sample Python file with various import statements for testing."""

# Standard library imports
import os
import sys
import json
from pathlib import Path

# Third-party imports
import requests
import numpy as np
from flask import Flask

# Relative imports (will be ignored in our scanner)
# from .utils import helper
# from ..models import User

# Multiple imports on one line
import random, string, time

# Import with alias
import pandas as pd

# Import *
from os.path import *

# Conditional imports
if True:
    import asyncio

try:
    import optional_package
except ImportError:
    pass


def main() -> None:
    """Sample function."""
    pass
