from datetime import datetime
from django.apps import apps
from django.http import Http404
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import redirect
from .base import CalAccessModelListMixin
from calaccess_website.models import ProcessedDataVersionProxy
from django.template.defaultfilters import date as dateformat
from django.views.generic import (
    ArchiveIndexView,
    YearArchiveView,
    MonthArchiveView,
    DetailView
)


def redirect_latest_processed(request, slug):
    queryset = ProcessedDataVersionProxy.objects.exclude(process_finish_datetime=None)
    try:
        obj = queryset.latest("process_finish_datetime")
    except queryset.model.DoesNotExist:
        raise Http404
    fobj = obj.files.all()[0]
    name = fobj.file_archive.name.split("/")[0]
    url = f"https://archive.org/download/{name}/{slug}"
    return redirect(url)


def redirect_latest_raw(request, slug):
    queryset = ProcessedDataVersionProxy.objects.exclude(process_finish_datetime=None)
    try:
        obj = queryset.latest("process_finish_datetime").raw_version
    except queryset.model.DoesNotExist:
        raise Http404
    fobj = obj.files.all()[0]
    name = fobj.clean_file_archive.name.split("/")[0]
    url = f"https://archive.org/download/{name}/{slug}"
    return redirect(url)


class VersionArchiveIndex(ArchiveIndexView):
    """
    A list of the latest versions of CAL-ACCESS in our archive
    """
    queryset = ProcessedDataVersionProxy.objects.exclude(process_finish_datetime=None)
    date_field = "process_finish_datetime"
    template_name = "calaccess_website/version/archive.html"


class VersionYearArchiveList(YearArchiveView):
    """
    A list of all versions of CAL-ACCESS in a given year
    """
    queryset = ProcessedDataVersionProxy.objects.exclude(process_finish_datetime=None)
    date_field = "process_finish_datetime"
    make_object_list = False
    template_name = "calaccess_website/version/archive_year.html"

    def get_url(self):
        return reverse(
            'version_archive_year',
            kwargs=dict(year=self.get_year())
        )


class VersionMonthArchiveList(MonthArchiveView):
    """
    A list of all versions of CAL-ACCESS in a given year
    """
    queryset = ProcessedDataVersionProxy.objects.exclude(process_finish_datetime=None)
    date_field = "process_finish_datetime"
    month_format = "%m"
    make_object_list = True
    template_name = "calaccess_website/version/archive_month.html"

    def get_url(self):
        return reverse(
            'version_archive_month',
            kwargs=dict(
                year=self.get_year(),
                month=self.get_month()
            )
        )


class VersionDetail(DetailView, CalAccessModelListMixin):
    """
    A detail page with everything about an individual CAL-ACCESS version
    """
    queryset = ProcessedDataVersionProxy.objects.exclude(process_finish_datetime=None)
    template_name = 'calaccess_website/version/detail_archived.html'

    def set_kwargs(self, obj):
        super(VersionDetail, self).set_kwargs(obj)
        self.kwargs.update({
            'year': obj.raw_version.release_datetime.year,
            'month': dateformat(obj.raw_version.release_datetime, 'm'),
            'day': dateformat(obj.raw_version.release_datetime, 'd'),
            'time': dateformat(obj.raw_version.release_datetime, 'His'),
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
            return self.get_queryset().get(raw_version__release_datetime=dt)
        except self.get_queryset().model.DoesNotExist:
            raise Http404

    def get_context_data(self, **kwargs):
        """
        Add some extra bits to the template's context
        """
        context = super(VersionDetail, self).get_context_data(**kwargs)
        context['date_string'] = dateformat(self.object.raw_version.release_datetime, "N j, Y")
        context['description'] = "The {} release of CAL-ACCESS database, the government database that tracks \
campaign finance and lobbying activity in California politics.".format(context['date_string'])
        context['has_processed_version'] = True
        context['processed_version_completed'] = True

        if context['has_processed_version']:
            context['flat_zip'] = self.object.flat_zip
            context['relational_zip'] = self.object.relational_zip
            context['flat_files'] = self.get_flat_files()

        if self.object.raw_version.error_count:
            context['raw_files_w_errors'] = self.get_raw_files_w_errors()
            context['error_pct'] = (
                100 * self.object.raw_version.error_count / float(self.object.raw_version.download_record_count)
            )
        else:
            context['error_pct'] = 0
        return context

    def get_raw_files_w_errors(self):
        """
        Return an iterable of RawDataFile instances with logged errors.
        """
        return [
            f for f in self.object.raw_version.files.all() if f.error_count > 0
        ]

    def get_flat_files(self):
        """
        Return an iterable of dicts with info about the processed flat files.
        """
        flat_files = []
        flat_models = apps.get_app_config("calaccess_processed_flatfiles").get_flat_proxy_list()
        for m in flat_models:
            flat_file = {
                'name': m()._meta.verbose_name_plural,
                'doc': m().doc.replace(".", ""),
                'is_processed': self.object.check_processed_model(m),
                'coming_soon': False
            }
            flat_files.append(flat_file)
        # append coming soon files
        for i in ['Committees', 'Filings', 'Contributions', 'Expenditures']:
            flat_file = {
                'name': i,
                'doc': 'Every campaign %s' % i.strip('s').lower(),
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
    template_name = 'calaccess_website/version/detail_latest.html'

    def get_object(self, **kwargs):
        """
        Return the latest object from the queryset every time.
        """
        try:
            return self.get_queryset().latest("process_finish_datetime")
        except self.model.DoesNotExist:
            raise Http404

    def get_context_data(self, **kwargs):
        """
        Add little extra bits that the standard detail page won't have.
        """
        context = super(LatestVersion, self).get_context_data(**kwargs)
        # A hint we can use in the template as a switch
        context['title'] = 'Latest California campaign finance data'
        context['description'] = 'Download the most recent release of CAL-ACCESS, the government database that tracks campaign \
finance and lobbying activity in California politics.'
        context['is_latest'] = True
        return context

    def get_url(self, obj):
        """
        The never-changing latest URL.
        """
        return reverse('version_latest')
