#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Save copies of data files from the most recently completed update in a latest/
directory in the Django project's default file storage.
"""
import os
import logging
from django.conf import settings
import boto3
from calaccess_raw.models import RawDataVersion
from django.core.management.base import BaseCommand
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Save copies of data files from the most recently completed update in a latest/
    directory in the Django project's default file storage.
    """
    help = "Save copies of data files from the most recently completed update\
in a latest directory in the Django project's default file storage."

    def handle(self, *args, **options):
        # set up boto session
        self.session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        # and client
        self.client = self.session.client('s3')

        # get the version of last update that finished
        v = RawDataVersion.objects.latest('update_finish_datetime')

        logger.debug(
            'Copying files for {:%m-%d-%Y %H:%M:%S} version to latest/'.format(
                v.release_datetime
            )
        )

        # save zips to the latest directory
        if v.download_zip_archive:
            self.copy_to_latest(v.download_zip_archive.name)
        if v.clean_zip_archive:
            self.copy_to_latest(v.clean_zip_archive.name)

        # loop through all of the raw data files
        for f in v.files.all():
            # save downloaded file to the latest directory
            self.copy_to_latest(f.download_file_archive.name)

            if f.clean_file_archive:
                # save cleaned file to the latest directory
                self.copy_to_latest(f.clean_file_archive.name)

            if f.error_log_archive:
                # save error log file to the latest directory
                self.copy_to_latest(f.error_log_archive.name)

    def get_latest_path(self, old_path):
        """
        Convert the file path to a latest file path
        """
        base_name = os.path.basename(old_path)
        return os.path.join("latest", base_name)

    def copy_to_latest(self, source):
        """
        Copies the provided source key to the provided target key
        """
        logger.debug('Saving copy of %s' % os.path.basename(source))
        self.client.copy_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=self.get_latest_path(source),
            CopySource={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': source,
            },
        )
