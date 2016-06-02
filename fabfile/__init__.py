from fabric.colors import green
from fabric.api import env, local, task
import yaml

from configure import configure, loadconfig
from configure import ConfigTask
from amazon import createrds

__all__ = (
    'configure',
    'loadconfig',
    'createrds',
    'pipinstall',
    'manage',
    'migrate',
)