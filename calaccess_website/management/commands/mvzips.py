#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Move downloaded and cleaned zips to their proper place in the raw data archived dir.
"""
import boto3
from django.conf import settings
from calaccess_raw.management.commands import CalAccessCommand
from calaccess_raw.models.tracking import RawDataVersion
import logging
logger = logging.getLogger(__name__)


class Command(CalAccessCommand):
    """
    Move downloaded and cleaned zips to their proper place in the raw data archived dir.
    """
    help = 'Move downloaded and cleaned zips to their proper place in the raw data archived dir'

    def handle(self, *args, **options):
        """
        Make it happen.
        """
        super(Command, self).handle(*args, **options)

        # set up boto session
        self.session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        # and client
        self.client = self.session.client('s3')

        # loop over all the versions
        for v in RawDataVersion.objects.all():
            # if there's a download zip
            if v.download_zip_archive:
                # set the initial path
                initial_download_path = v.download_zip_archive.name
                # split datetime from file name and ext
                download_datetime, download_fullname = initial_download_path.split('/')
                # split file name and ext
                download_filename, download_ext = download_fullname.split('.')
                # set new path
                new_download_path = '{fn}_{dt}.{fx}'.format(
                    fn=download_filename,
                    dt=download_datetime,
                    fx=download_ext
                )
                # move
                logger.debug('Move {0} to {1}'.format(
                        initial_download_path,
                        new_download_path
                    )
                )
                self.client.copy_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=new_download_path,
                    CopySource={
                        'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                        'Key': initial_download_path,
                    },
                )
                # reset file name
                v.download_zip_archive.name = new_download_path

            # repeat for clean zips
            if v.clean_zip_archive:
                # set the initial path
                initial_clean_path = v.clean_zip_archive.name
                # split datetime from file name and ext
                clean_datetime, clean_fullname = initial_clean_path.split('/')
                # split file name and ext
                clean_filename, clean_ext = clean_fullname.split('.')
                # set new path
                new_clean_path = 'clean_{dt}.{fx}'.format(
                    dt=clean_datetime,
                    fx=clean_ext
                )
                # move
                logger.debug('Move {0} to {1}'.format(
                        initial_clean_path,
                        new_clean_path
                    )
                )
                self.client.copy_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=new_clean_path,
                    CopySource={
                        'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                        'Key': initial_clean_path,
                    },
                )
                # reset file name
                v.clean_zip_archive.name = new_clean_path

                # save the version
                v.save()
