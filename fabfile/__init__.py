#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fabric.colors import green
from fabric.api import env, local, task
import yaml

from configure import configure, loadconfig
from configure import ConfigTask
from amazon import createrds, createserver

__all__ = (
    'configure',
    'loadconfig',
    'createrds',
    'createserver',
    'pipinstall',
    'manage',
    'migrate',
)
