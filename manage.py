#!/usr/bin/env python
import os
import sys
import configparser

if __name__ == "__main__":
    # Allow invoking manage.py from any directory
    repo_dir = os.path.dirname(os.path.realpath(__file__))

    # Load env variables from .env config file
    cp = configparser.SafeConfigParser()
    cp.read(os.path.join(repo_dir, ".env"))

    # Default to DEV env
    os.environ.setdefault("CALACCESS_WEBSITE_ENV", "DEV")

    # Get the current env
    cp_sect = os.getenv("CALACCESS_WEBSITE_ENV").upper()

    # If the env doesn't exist, throw an error
    if not cp.has_section(cp_sect):
        raise EnvironmentError("No [{0}] section found in .env file (run "
            "`fab createconfig).".format(cp_sect))

    # Load the files variables into the environment
    for i in cp.items(os.getenv("CALACCESS_WEBSITE_ENV").upper()):
        os.environ[i[0]] = i[1]

    # Continue with the standard Django boot
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
