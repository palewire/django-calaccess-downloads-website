#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Update to the latest available CAL-ACCESS snapshot and publish the files to the
website.
"""
import logging
from django.core.management import call_command
from calaccess_raw.management.commands.updatecalaccessrawdata import Command as updatecommand
logger = logging.getLogger(__name__)


class Command(updatecommand):
    """
    Update to the latest available CAL-ACCESS snapshot and publish the files to
    the website.
    """
    help = 'Update to the latest available CAL-ACCESS snapshot and publish the\
files to the website.'

    def handle(self, *args, **options):
        """
        Make it happen.
        """
        super(Command, self).handle(*args, **options)

        self.header('Creating latest file links')
        call_command('createlatestlinks')
        self.header('Baking downloads-website content')
        call_command('build')
        self.header('Publishing backed content to S3 bucket.')
        call_command('publish')

        self.success("Done!")
