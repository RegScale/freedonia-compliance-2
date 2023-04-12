#!/usr/bin/env python3

# import python packages
import rtyaml
import json
import os
import glob
import uuid
import requests
import datetime
from collections import defaultdict
from itertools import groupby
from natsort import natsorted
from dataclasses import dataclass, field

def slugify(name):
    """Return a slugified value for name"""
    return name.replace("/","").replace(" ","_").lower()

def ensure_dir(path):
    """Ensure a directory exists"""
    if not os.path.exists(path):
        os.makedirs(path)