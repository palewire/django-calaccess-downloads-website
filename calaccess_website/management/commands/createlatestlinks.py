import os
import logging
from django.conf import settings
from boto.s3.connection import S3Connection, OrdinaryCallingFormat
from calaccess_raw.models import RawDataVersion
from django.core.management.base import BaseCommand
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Copy the latest archived files to the permanent latest URLs"

    def handle(self, *args, **options):
        # Get the latest version
        obj = RawDataVersion.objects.latest('release_datetime')

        # Copy its zip file to the latest folder
        latest_zip_path = self.get_latest_path(obj.zip_file_archive.name)
        print "Copying {} to {}".format(
            obj.zip_file_archive.name,
            latest_zip_path
        )
        self.copy_key(obj.zip_file_archive.name, latest_zip_path)

        # Loop through all its files
        for f in obj.files.all():

            # Copy over the raw TSV to latest
            latest_tsv =  self.get_latest_path(f.download_file_archive.name)
            print "Copying {} to {}".format(
                f.download_file_archive.name,
                latest_tsv
            )
            self.copy_key(f.download_file_archive.name, latest_tsv)

            # If it has a clean csv do the same
            if f.clean_file_archive:
                latest_csv =  self.get_latest_path(f.clean_file_archive.name)
                print "Copying {} to {}".format(
                    f.clean_file_archive.name,
                    latest_csv
                )
                self.copy_key(f.clean_file_archive.name, latest_csv)

            # If it has an error log, do that too
            if f.error_log_archive:
                latest_error =  self.get_latest_path(f.error_log_archive.name)
                print "Copying {} to {}".format(
                    f.error_log_archive.name,
                    latest_error
                )
                self.copy_key(f.error_log_archive.name, latest_error)

    def get_latest_path(self, name):
        """
        Convert the file path to a latest file path
        """
        name = name.split("/")[1]
        return os.path.join("latest", name)

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

    def copy_key(self, source, target):
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
