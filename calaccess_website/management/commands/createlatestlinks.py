#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Save copies of data files from the most recently completed update in a latest/
directory in the Django project's default file storage.
"""
import os
import logging
from django.conf import settings
from boto.s3.connection import S3Connection, OrdinaryCallingFormat
from calaccess_raw.models import RawDataCommand
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
        # get the version of the most last completed update
        v = RawDataCommand.objects.filter(
            command='updatecalaccessrawdata',
            finish_datetime__isnull=False
        ).latest('version__release_datetime').version

        logger.debug(
            'Copying files for {:%m-%d-%Y %H:%M:%S} version to latest/'.format(
                v.release_datetime
            )
        )

        # convert the zip files path to the latest path
        latest_zip_path = self.get_latest_path(v.download_zip_archive.name)

        # save zip to the latest directory
        logger.debug('Saving copy of zip file')
        self.copy_key(latest_zip_path, v.download_zip_archive.name)

        # loop through all of the raw data files
        for f in v.files.all():
            # convert the downloaded file's path to the latest path
            latest_dl_path = self.get_latest_path(f.download_file_archive.name)
            # save downloaded file to the latest directory
            logger.debug('Saving copy of {0}.TSV'.format(f.file_name))
            self.copy_key(latest_dl_path, f.download_file_archive.name)

            if f.clean_file_archive:
                # convert the cleaned file's path to the latest path
                latest_cl_path = self.get_latest_path(f.clean_file_archive.name)
                # save cleaned file to the latest directory
                logger.debug('Saving copy of {0}.csv'.format(
                    f.file_name.lower()
                ))
                self.copy_key(latest_cl_path, f.clean_file_archive.name)

            if f.error_log_archive:
                # convert the error log file's path to the latest path
                latest_el_path = self.get_latest_path(f.error_log_archive.name)
                # save error log file to the latest directory
                logger.debug('Saving copy of {0}.errors.csv'.format(
                    f.file_name.lower()
                ))
                self.copy_key(latest_el_path, f.error_log_archive.name)

    def get_latest_path(self, old_path):
        """
        Convert the file path to a latest file path
        """
        base_name = os.path.basename(old_path)
        return os.path.join("latest", base_name)

    def get_bucket(self):
        """
        Returns an S3 bucket ready to rock.
        """
        conn = S3Connection(
            settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY,
            calling_format=OrdinaryCallingFormat(),
            host=settings.AWS_S3_HOST,
        )
        return conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)

    def copy_key(self, target, source):
        """
        Copies the provided source key to the provided target key
        """
        bucket = self.get_bucket()
        bucket.copy_key(
            target,
            settings.AWS_STORAGE_BUCKET_NAME,
            source,
            preserve_acl=True,
        )
