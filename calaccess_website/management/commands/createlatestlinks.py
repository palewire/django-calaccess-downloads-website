#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Save copies of data files from the most recently completed update in a latest
directory in the default file storage of the Django project.
"""
import os
import re
import boto3
import random
import logging
from django.conf import settings
from calaccess_raw.models import RawDataVersion
from django.core.management.base import BaseCommand
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Save copies of data files from the most recently completed update in a latest
    directory in the default file storage of the Django project.
    """
    help = "Save copies of data files from the most recently completed update in \
a latest directory in the default file storage of the Django project"

    def handle(self, *args, **options):
        # set up boto session
        self.session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        # and clients
        self.s3 = self.session.client('s3')
        self.cloudfront = self.session.client('cloudfront')

        # Delete existing latest files
        latest_key_list = self.s3.list_objects_v2(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Prefix='latest/',
        )
        if latest_key_list['KeyCount'] > 0:
            self.delete_keys(latest_key_list)

        # get the version of last update that finished
        v = RawDataVersion.objects.exclude(update_finish_datetime=None).latest('update_finish_datetime')

        logger.debug(
            'Copying files for {:%m-%d-%Y %H:%M:%S} version to latest/'.format(
                v.release_datetime
            )
        )

        # save downloaded zip to the latest dir
        if v.download_zip_archive:
            # strip the datetime from the zip name
            zip_name = self.strip_datetime(
                os.path.basename(v.download_zip_archive.name),
            )
            self.copy(
                v.download_zip_archive.name,
                self.get_latest_path(zip_name),
            )
        # save cleaned zip to the latest dir
        if v.clean_zip_archive:
            # strip the datetime from the zip name
            zip_name = self.strip_datetime(
                os.path.basename(v.clean_zip_archive.name),
            )
            self.copy(
                v.clean_zip_archive.name,
                self.get_latest_path(zip_name),
            )

        # loop through all of the raw data files
        for f in v.files.all():
            # save downloaded file to the latest directory
            self.copy(
                f.download_file_archive.name,
                self.get_latest_path(f.download_file_archive.name)
            )

            if f.clean_file_archive:
                # save cleaned file to the latest directory
                self.copy(
                    f.clean_file_archive.name,
                    self.get_latest_path(f.clean_file_archive.name)
                )

            if f.error_log_archive:
                # save error log file to the latest directory
                self.copy(
                    f.error_log_archive.name,
                    self.get_latest_path(f.error_log_archive.name)
                )

        # Clear the cloudfront cache by sending an invalidation request
        if latest_key_list['KeyCount'] > 0:
            self.invalidate_keys(latest_key_list)

    def strip_datetime(self, filename):
        """
        Removes the datetime portion from filename.
        """
        return re.sub(
            r'_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}',
            '',
            filename,
        )

    def get_latest_path(self, old_path):
        """
        Convert the file path to a latest file path
        """
        base_name = os.path.basename(old_path)
        return os.path.join("latest", base_name)

    def copy(self, source, target):
        """
        Copies the provided source key to the provided target key
        """
        logger.debug('Saving copy of %s' % os.path.basename(source))
        copy_source = {
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': source
        }
        self.s3.copy(
            copy_source,
            settings.AWS_STORAGE_BUCKET_NAME,
            target,
        )

    def delete_keys(self, key_list):
        """
        Delete all the provided s3 keys.
        """
        logger.debug(
            'Deleting %s keys currently under latest/' % key_list['KeyCount']
        )
        # format
        objects = [{'Key': o['Key']} for o in key_list['Contents']]
        # delete
        self.s3.delete_objects(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Delete={
                'Objects': objects,
            }
        )

    def invalidate_keys(self, key_list):
        """
        Send CloudFront an invalidation request to clear.
        """
        logger.debug(
            "Sending invalidation request for %s keys under latest/" % key_list['KeyCount']
        )
        items = ["/{}".format(o['Key']) for o in key_list['Contents']]
        self.cloudfront.create_invalidation(
            DistributionId=settings.CLOUDFRONT_ARCHIVED_DATA_DISTRIBUTION,
            InvalidationBatch={
                # What to invalidate
                'Paths': {
                    'Quantity': key_list['KeyCount'],
                    'Items': items
                },
                # A random name for the request
                'CallerReference': str(random.getrandbits(128))
            }
        )
