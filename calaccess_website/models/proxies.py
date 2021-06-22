#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Proxy models for augmenting models from other apps.
"""
from calaccess_raw.models import RawDataVersion
from calaccess_processed.models import ProcessedDataZip
from calaccess_processed.models import ProcessedDataVersion


class ProcessedDataVersionProxy(ProcessedDataVersion):
    """
    Proxy model of the ProcessedDataVersion.
    """
    def get_processed_zip(self, label):
        """
        Return a ProcessedDataZip instance with a name that includes label.

        If no instance exists for the version, return None.
        """
        try:
            return self.zips.get(zip_archive__icontains=label)
        except ProcessedDataZip.DoesNotExist:
            return None

    @property
    def flat_zip(self):
        """
        ProcessedDataZip instance of flat files for this version (if it exists).
        """
        return self.get_processed_zip('flat')

    @property
    def relational_zip(self):
        """
        ProcessedDataZip instance of relational files for this version (if it exists).
        """
        return self.get_processed_zip('relational')

    class Meta:
        proxy = True


class RawDataVersionProxy(RawDataVersion):
    """
    Proxy model of the RawDataVersion.
    """
    def get_processed_zip(self, label):
        """
        Return a ProcessedDataZip instance with a name that includes label.

        If no instance exists for the version, return None.
        """
        if self.has_processed_version:
            try:
                obj = self.processed_version.zips.get(
                    zip_archive__icontains=label
                )
            except ProcessedDataZip.DoesNotExist:
                obj = None
        else:
            obj = None
        return obj

    @property
    def flat_zip(self):
        """
        ProcessedDataZip instance of flat files for this version (if it exists).
        """
        if self.has_processed_version:
            obj = self.get_processed_zip('flat')
        else:
            obj = None
        return obj

    @property
    def relational_zip(self):
        """
        ProcessedDataZip instance of relational files for this version (if it exists).
        """
        if self.has_processed_version:
            obj = self.get_processed_zip('relational')
        else:
            obj = None
        return obj

    @property
    def has_processed_version(self):
        """
        Check if the raw version is linked a ProcessedDataVersion instance.
        """
        try:
            self.processed_version
        except AttributeError:
            return False
        else:
            return True

    @property
    def processed_version_completed(self):
        """
        Check if the processed version completed.
        """
        if self.has_processed_version:
            return self.processed_version.update_completed
        else:
            return False

    class Meta:
        proxy = True
