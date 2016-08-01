#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Zip up cleaned raw data files (and error logs) and archive zip files.
"""
import os
import boto3
import logging
import shutil
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile
from django.conf import settings
from django.core.files import File
from calaccess_raw import get_download_directory
from calaccess_raw.management.commands import CalAccessCommand
from calaccess_raw.models.tracking import RawDataVersion
logger = logging.getLogger(__name__)


class Command(CalAccessCommand):
    """
    Zip up cleaned raw data files (and error logs) and archive zip files.
    """
    help = 'Zip up cleaned raw data files (and error logs) and archive zip files'

    def handle(self, *args, **options):
        """
        Make it happen.
        """
        super(Command, self).handle(*args, **options)
        self.clean_zip_path = os.path.join(
            get_download_directory(),
            'calaccess_cleaned.zip'
        )

        self.data_dir = get_download_directory()

        if os.path.exists(self.data_dir):
            shutil.rmtree(self.data_dir)

        os.makedirs(self.data_dir)

        versions = RawDataVersion.objects.filter(clean_zip_archive='')

        if versions:
            for version in versions:
                logger.debug(
                    'Creating zip file for {:%Y-%m-%d_%H-%M-%S} version'.format(
                        version.release_datetime
                    )
                )

                self.download_clean_files(version)
                self.create_zip_file(version)
                self.archive_zip_file(version)

    def download_clean_files(self, version):
        # set up boto session
        boto_session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        # and client
        s3_client = boto_session.client('s3')

        for raw_file in version.files.all():
            if raw_file.clean_file_archive:
                logger.debug(
                    'Downloading {0}'.format(os.path.basename(
                            raw_file.clean_file_archive.name
                        )
                    )
                )
                # set up local file path
                local_clean_file_path = os.path.join(
                    self.data_dir,
                    os.path.basename(raw_file.clean_file_archive.name),
                )
                # download
                s3_client.download_file(
                    settings.AWS_STORAGE_BUCKET_NAME,
                    raw_file.clean_file_archive.name,
                    local_clean_file_path,
                )
            if raw_file.error_log_archive:
                logger.debug(
                    'Downloading {0}'.format(os.path.basename(
                            raw_file.error_log_archive.name
                        )
                    )
                )
                # set up local file path
                local_error_file_path = os.path.join(
                    self.data_dir,
                    os.path.basename(raw_file.error_log_archive.name),
                )
                # download
                s3_client.download_file(
                    settings.AWS_STORAGE_BUCKET_NAME,
                    raw_file.error_log_archive.name,
                    local_error_file_path,
                )

    def create_zip_file(self, version):
        logger.debug('Creating zip file')
        compression = ZIP_DEFLATED
        try:
            zf = ZipFile(self.clean_zip_path, 'w', compression, allowZip64=True)
        except RuntimeError:
            logger.error('Zip file cannot be compressed (check zlib module).')
            compression = ZIP_STORED
            zf = ZipFile(self.clean_zip_path, 'w', compression, allowZip64=True)

        csv_files = [f for f in os.listdir(self.data_dir) if '.csv' in f]

        for f in csv_files:
            logger.debug('Writing %s to zip file' % os.path.basename(f))
            file_path = os.path.join(self.data_dir, f)
            zf.write(file_path, f)
            os.remove(file_path)

        zf.close()

    def archive_zip_file(self, version):
        version.clean_zip_archive.delete()
        logger.debug('Archiving zip file')
        with open(self.clean_zip_path) as zf:
            # Save the zip on the raw data version
            version.clean_zip_archive.save(
                os.path.basename(self.clean_zip_path), File(zf)
            )
