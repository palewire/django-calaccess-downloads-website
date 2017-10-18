#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Proxy models for augmenting models from other apps.
"""
from calaccess_raw.managers import RawDataVersionQuerySet


class RawDataVersionManager(RawDataVersionQuerySet):
    """
    Custom manager for filtering RawDataVersions to those we want to surface.
    """
    def get_queryset(self):
        """
        Returns the custom QuerySet for this manager.
        """
        return super(
            RawDataVersionManager, self
        ).get_queryset().complete().exclude(
            release_datetime__lte='2016-07-27'
        )
