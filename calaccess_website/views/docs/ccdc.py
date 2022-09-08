#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Views for CCDC file documetnation pages.
"""
# Django tricks
from django.apps import apps
from django.http import Http404
from django.urls import reverse
from calaccess_website.templatetags.calaccess_website_tags import slugify

# Models
from calaccess_processed.models import ProcessedDataFile

# Views
from calaccess_website.views import CalAccessModelListMixin
from bakery.views import BuildableDetailView, BuildableListView


def get_ocd_proxy_models():
    """
    Return an iterable of all OCD proxy models from the processed_data app.
    """
    election_proxies = apps.get_app_config('calaccess_processed_elections').get_ocd_models_map().values()
    flat_proxies = apps.get_app_config("calaccess_processed_flatfiles").get_flat_proxy_list()
    return list(election_proxies) + list(flat_proxies)


def get_processed_data_files():
    """
    Return a tuple of ProcessedDataFile instances for published files.
    """
    file_list = [ProcessedDataFile(file_name=m().file_name) for m in get_ocd_proxy_models()]
    return sorted(file_list, key=lambda f: f.file_name)


class CcdcFileList(BuildableListView, CalAccessModelListMixin):
    template_name = 'calaccess_website/docs/ccdc/file_list.html'
    build_path = "documentation/processed-files/index.html"

    def get_queryset(self):
        """
        Returns the CCDC model list with grouped by type.
        """
        return self.regroup_by_klass_group(get_processed_data_files())

    def get_context_data(self, **kwargs):
        context = super(CcdcFileList, self).get_context_data(**kwargs)
        context['file_num'] = len(get_processed_data_files())
        context['title'] = 'Processed files'
        context['description'] = 'Definitions, record layouts and data dictionaries for the \
processed data files released by the California Civic Data Coalition. Recommended for beginners and regular use.'
        return context


class BaseFileDetailView(BuildableDetailView):
    """
    Base class for views providing information about a CCDC data file.
    """
    def get_queryset(self):
        """
        Returns a list of the ccdc data files as a key dictionary
        with the URL slug as the keys.
        """
        return dict((slugify(f.file_name), f) for f in get_processed_data_files())

    def build_queryset(self):
        [self.build_object(o) for o in self.get_queryset()]

    def set_kwargs(self, obj):
        self.kwargs = {
            'slug': obj
        }

    def get_object(self):
        """
        Returns the file model from the CAL-ACCESS processed data app that
        matches the provided slug.

        Raises a 404 error if one is not found
        """
        key = self.kwargs['slug']
        try:
            return self.get_queryset()[key.lower()]
        except KeyError:
            raise Http404

    def get_context_data(self, **kwargs):
        """
        Add some extra bits to the template's context
        """
        file_name = self.kwargs['slug'].replace("-", "")
        context = super(BaseFileDetailView, self).get_context_data(**kwargs)

        # Pull all previous versions of the provided file
        context['version_list'] = ProcessedDataFile.objects.filter(
            file_name__icontains=file_name
        ).order_by(
            '-version__raw_version__release_datetime'
        ).exclude(
            version__raw_version__release_datetime__lte='2016-07-27'
        )

        # note if the most recent version of the file is empty
        try:
            context['empty'] = context['version_list'][0].records_count == 0
        except IndexError:
            context['empty'] = True

        return context


class CcdcFileDownloadsList(BaseFileDetailView):
    """
    A detail page with links to all downloads for the provided CCDC data file.
    """
    template_name = 'calaccess_website/docs/ccdc/download_list.html'

    def get_url(self, obj):
        return reverse('ccdc_file_downloads_list', kwargs=dict(slug=obj))


class CcdcFileDetail(BaseFileDetailView):
    """
    A detail page with all documentation for the provided CCDC data file.
    """
    template_name = 'calaccess_website/docs/ccdc/file_detail.html'

    def get_url(self, obj):
        return reverse('ccdc_file_detail', kwargs=dict(slug=obj))

    def get_context_data(self, **kwargs):
        """
        Add some extra bits to the template's context
        """
        context = super(CcdcFileDetail, self).get_context_data(**kwargs)
        # Add list of fields to context
        context['fields'] = self.get_sorted_fields()
        return context

    def get_sorted_fields(self):
        """
        Return a list of fields (dicts) sorted by name.
        """
        field_list = []
        for field in self.object.model().get_field_list():
            field_data = {
                'column': field.name,
                'description': field.description,
                'help_text': field.help_text,
            }
            if field.choices and len(field.choices) > 0:
                field_data['choices'] = [c for c in field.choices]
            else:
                field_data['choices'] = None

            field_list.append(field_data)

        return sorted(field_list, key=lambda k: k['column'])
