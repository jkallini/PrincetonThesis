#!/usr/bin/env python
# benepar_download.py

# This script downloads the English model for benepar, benepar_en2.
# BEFORE running this script, and ensure that you have downloaded
# the requirements in requirments.txt.

import benepar
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

benepar.download('benepar_en2')