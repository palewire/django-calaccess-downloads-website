#!/usr/bin/env python
import os
import sys
import ConfigParser

if __name__ == "__main__":
    # load env variables from .env config file
    cp = ConfigParser.SafeConfigParser()
    cp.read('.env')
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
