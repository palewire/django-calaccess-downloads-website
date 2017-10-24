from datetime import datetime
from django.apps import apps
from django.http import Http404
from django.utils import timezone
from .base import CalAccessModelListMixin
from django.core.urlresolvers import reverse
from calaccess_website.models import RawDataVersionProxy
from django.template.defaultfilters import date as dateformat
from bakery.views import (
    BuildableArchiveIndexView,
    BuildableYearArchiveView,
    BuildableMonthArchiveView,
    BuildableDetailView
)


class VersionArchiveIndex(BuildableArchiveIndexView):
    """
    A list of the latest versions of CAL-ACCESS in our archive
    """
    model = RawDataVersionProxy
    date_field = "release_datetime"
    template_name = "calaccess_website/version_archive.html"
    build_path = "downloads/index.html"


class VersionYearArchiveList(BuildableYearArchiveView):
    """
    A list of all versions of CAL-ACCESS in a given year
    """
    model = RawDataVersionProxy
    date_field = "release_datetime"
    make_object_list = False
    template_name = "calaccess_website/version_archive_year.html"

    def get_url(self):
        return reverse(
            'version_archive_year',
            kwargs=dict(year=self.get_year())
        )


class VersionMonthArchiveList(BuildableMonthArchiveView):
    """
    A list of all versions of CAL-ACCESS in a given year
    """
    model = RawDataVersionProxy
    date_field = "release_datetime"
    month_format = "%m"
    make_object_list = True
    template_name = "calaccess_website/version_archive_month.html"

    def get_url(self):
        return reverse(
            'version_archive_month',
            kwargs=dict(
                year=self.get_year(),
                month=self.get_month()
            )
        )


class VersionDetail(BuildableDetailView, CalAccessModelListMixin):
    """
    A detail page with everything about an individual CAL-ACCESS version
    """
    model = RawDataVersionProxy
    template_name = 'calaccess_website/version_detail_archived.html'

    def set_kwargs(self, obj):
        super(VersionDetail, self).set_kwargs(obj)
        self.kwargs.update({
            'year': obj.release_datetime.year,
            'month': dateformat(obj.release_datetime, 'm'),
            'day': dateformat(obj.release_datetime, 'd'),
            'time': dateformat(obj.release_datetime, 'His'),
        })

    def get_object(self, **kwargs):
        date_parts = map(int, [
            self.kwargs['year'],
            self.kwargs['month'],
            self.kwargs['day'],
            self.kwargs['time'][:2],
            self.kwargs['time'][2:4],
            self.kwargs['time'][-2:]
        ])
        dt = datetime(*date_parts)
        dt = timezone.utc.localize(dt)
        try:
            return self.get_queryset().get(release_datetime=dt)
        except self.get_queryset().model.DoesNotExist:
            raise Http404

    def get_context_data(self, **kwargs):
        """
        Add some extra bits to the template's context
        """
        context = super(VersionDetail, self).get_context_data(**kwargs)
        context['date_string'] = dateformat(self.object.release_datetime, "N j, Y")
        context['description'] = "The {} release of CAL-ACCESS database, the government database that tracks \
campaign finance and lobbying activity in California politics.".format(context['date_string'])
        context['has_processed_version'] = self.object.has_processed_version
        context['processed_version_completed'] = self.object.processed_version_completed

        if context['has_processed_version']:
            context['flat_zip'] = self.object.flat_zip
            context['relational_zip'] = self.object.relational_zip
            context['flat_files'] = self.get_flat_files()

        if self.object.error_count:
            context['raw_files_w_errors'] = self.get_raw_files_w_errors()
            context['error_pct'] = 100 * self.object.error_count / float(self.object.download_record_count)
        else:
            context['error_pct'] = 0
        return context

    def get_raw_files_w_errors(self):
        """
        Return an iterable of RawDataFile instances with logged errors.
        """
        return [
            f for f in self.object.files.all() if f.error_count > 0
        ]

    def get_flat_files(self):
        """
        Return an iterable of dicts with info about the processed flat files.
        """
        flat_files = []
        if self.object.has_processed_version:
            flat_models = [
                m for m in apps.get_models()
                if getattr(m(), 'is_flat', False)
            ]
            for m in flat_models:
                flat_file = {
                    'name': m().file_name,
                    'doc': m().doc,
                    'is_processed': self.object.processed_version.check_processed_model(m),
                    'coming_soon': False
                }
                flat_files.append(flat_file)
            # append coming soon files
            for i in ['Committees', 'Filings', 'Contributions', 'Expenditures']:
                flat_file = {
                    'name': i,
                    'doc': 'Every campaign finance %s.' % i.strip('s').lower(),
                    'is_processed': False,
                    'coming_soon': True
                }
                flat_files.append(flat_file)

        return flat_files

    def get_url(self, obj):
        return reverse(
            'version_detail',
            kwargs=dict(
                year=obj.release_datetime.year,
                month=dateformat(obj.release_datetime, 'm'),
                day=dateformat(obj.release_datetime, 'd'),
                time=dateformat(obj.release_datetime, 'His'),
            )
        )


class LatestVersion(VersionDetail):
    """
    Detail page of the latest CAL-ACCESS version
    """
    template_name = 'calaccess_website/version_detail_latest.html'

    def get_object(self, **kwargs):
        """
        Return the latest object from the queryset every time.
        """
        try:
            return self.get_queryset().complete().latest("release_datetime")
        except self.model.DoesNotExist:
            raise Http404

    def get_context_data(self, **kwargs):
        """
        Add little extra bits that the standard detail page won't have.
        """
        context = super(LatestVersion, self).get_context_data(**kwargs)
        # A hint we can use in the template as a switch
        context['title'] = 'Latest download'
        context['description'] = 'The most recent release of CAL-ACCESS, the government database that tracks campaign \
finance and lobbying activity in California politics.'
        context['is_latest'] = True
        return context

    def get_url(self, obj):
        """
        The never-changing latest URL.
        """
        return reverse('version_latest')

    def build_queryset(self):
        """
        Only build this view for one object, the latest one.
        """
        return self.build_object(self.get_object())
