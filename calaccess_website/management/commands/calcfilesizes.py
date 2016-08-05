#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backfill zip and file size columns.
"""
from boto3.exceptions import botocore
from calaccess_raw.management.commands import CalAccessCommand
from calaccess_raw.models.tracking import RawDataVersion, RawDataFile
import logging
logger = logging.getLogger(__name__)


class Command(CalAccessCommand):
    """
    Backfill zip and file size columns.
    """
    help = 'Backfill zip and file size columns'

    def handle(self, *args, **options):
        """
        Make it happen.
        """
        super(Command, self).handle(*args, **options)

        logger.debug('Back-filling sizes for downloaded zips.')
        downloads = RawDataVersion.objects.exclude(download_zip_archive='')
        for v in downloads:
            try:
                v.download_zip_size = v.download_zip_archive.size
            except botocore.exceptions.ClientError:
                pass
            else:
                v.save()

        logger.debug('Back-filling sizes for cleaned zips.')
        cleans = RawDataVersion.objects.exclude(clean_zip_archive='')
        for v in cleans:
            try:
                v.clean_zip_size = v.clean_zip_archive.size
            except botocore.exceptions.ClientError:
                pass
            else:
                v.save()

        logger.debug('Back-filling sizes for cleaned raw data files.')
        raw_files = RawDataFile.objects.exclude(clean_file_archive='')
        for f in raw_files:
            try:
                f.clean_file_size = f.clean_file_archive.size
            except botocore.exceptions.ClientError:
                pass
            else:
                f.save()
