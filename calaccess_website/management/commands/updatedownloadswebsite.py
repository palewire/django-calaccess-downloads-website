#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Update to the latest CAL-ACCESS snapshot.
"""
from django.core.management import call_command
from calaccess_raw.management.commands.updatecalaccessrawdata import Command as UpdateCommand


class Command(UpdateCommand):
    """
    Update to the latest CAL-ACCESS snapshot and bake static website pages.
    """
    help = 'Update to the latest CAL-ACCESS snapshot'

    def handle(self, *args, **options):
        """
        Make it happen.
        """
        # Run the raw data loading command.
        super(Command, self).handle(*args, **options)

        # Process it.
        call_command('processcalaccessdata')

        # We're out.
        self.success("Done!")
