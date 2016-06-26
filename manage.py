#!/usr/bin/env python
import os
import sys
import dotenv

if __name__ == "__main__":
    repo_dir = os.path.dirname(os.path.realpath(__file__))
    dotenv.read_dotenv(os.path.join(repo_dir, ".env"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
