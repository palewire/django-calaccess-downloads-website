#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Update to the latest CAL-ACCESS snapshot and bake static website pages.
"""
from django.core.management import call_command
from calaccess_raw.management.commands.updatecalaccessrawdata import Command as UpdateCommand


class Command(UpdateCommand):
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
        # Run the raw data loading command.
        super(Command, self).handle(*args, **options)

        # Process it.
        call_command('processcalaccessdata')

        # Sync it the with the CSV bucket.
        self.header('Creating latest file links')
        call_command('createlatestlinks')

        # Build it.
        self.header('Baking downloads-website content')
        call_command('build')

        # Publish it.
        if options['publish']:
            self.header('Publishing baked content to S3 bucket.')
            call_command('publish')

        # We're out.
        self.success("Done!")
