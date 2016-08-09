#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Update to the latest CAL-ACCESS snapshot and bake static website pages.
"""
import logging
from django.core.management import call_command
from calaccess_raw.management.commands.updatecalaccessrawdata import Command as updatecommand
logger = logging.getLogger(__name__)


class Command(updatecommand):
    """
    Update to the latest CAL-ACCESS snapshot and bake static website pages.
    """
    help = 'Update to the latest CAL-ACCESS snapshot and bake static website pages'

    def add_arguments(self, parser):
        """
        Adds custom arguments specific to this command.
        """
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "--publish",
            action="store_true",
            dest="publish",
            default=False,
            help="Publish baked content"
        )

    def handle(self, *args, **options):
        """
        Make it happen.
        """
        super(Command, self).handle(*args, **options)

        self.header('Creating latest file links')
        call_command('createlatestlinks')
        self.header('Baking downloads-website content')
        call_command('build')
        if options['publish']:
            self.header('Publishing baked content to S3 bucket.')
            call_command('publish')

        self.success("Done!")
