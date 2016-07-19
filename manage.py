#!/usr/bin/env python
import os
import sys
from backports import configparser

if __name__ == "__main__":
    # allow invoking manage.py from any directory
    repo_dir = os.path.dirname(os.path.realpath(__file__))
    # load env variables from .env config file
    cp = configparser.SafeConfigParser()
    cp.read(os.path.join(repo_dir, ".env"))
    # default to DEV env
    os.environ.setdefault("CALACCESS_WEBSITE_ENV", "DEV")
    cp_sect = os.getenv("CALACCESS_WEBSITE_ENV").upper()

    if not cp.has_section(cp_sect):
        raise EnvironmentError("No [{0}] section found in .env file (run "
            "`fab createconfig).".format(cp_sect))

    for i in cp.items(os.getenv("CALACCESS_WEBSITE_ENV").upper()):
        os.environ[i[0]] = i[1]
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
