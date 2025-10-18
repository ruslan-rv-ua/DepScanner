"""Sample Python file with various import statements for testing."""

# Standard library imports
import os
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

# Third-party imports
import requests
import numpy as np
from flask import Flask, render_template
from django.http import HttpResponse

# Relative imports (will be ignored in our scanner)
# from .utils import helper
# from ..models import User

# Multiple imports on one line
import json, re, datetime

# Import with alias
import pandas as pd
from requests.exceptions import RequestException as ReqError

# Import *
from os.path import *

# Conditional imports
if True:
    import socket

try:
    import optional_package
except ImportError:
    pass


def main() -> None:
    """Sample function."""
    pass
