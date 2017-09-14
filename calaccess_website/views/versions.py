from datetime import datetime
from django.http import Http404
from django.utils import timezone
from .base import CalAccessModelListMixin
from django.core.urlresolvers import reverse
from calaccess_raw.models import RawDataVersion
from calaccess_processed.models import ProcessedDataVersion
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
    queryset = RawDataVersion.objects.complete().exclude(release_datetime__lte='2016-07-27')
    date_field = "release_datetime"
    template_name = "calaccess_website/version_archive.html"
    build_path = "downloads/index.html"


class VersionYearArchiveList(BuildableYearArchiveView):
    """
    A list of all versions of CAL-ACCESS in a given year
    """
    queryset = RawDataVersion.objects.complete().exclude(release_datetime__lte='2016-07-27')
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
    queryset = RawDataVersion.objects.complete().exclude(release_datetime__lte='2016-07-27')
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
    queryset = RawDataVersion.objects.complete().exclude(release_datetime__lte='2016-07-27')
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
        context['raw_files'] = self.regroup_by_klass_group(
            self.object.files.all()
        )
        # include processed_files, if available
        try:
            processed_files = [
                i for i in self.object.processed_version.files.all()
                if 'Form' not in i.file_name
            ]
        except ProcessedDataVersion.DoesNotExist:
            pass
        else:
            context['processed_file_count'] = len(processed_files)
            context['processed_files'] = self.regroup_by_klass_group(
                processed_files
            )

        if self.object.error_count:
            context['error_pct'] = 100 * self.object.error_count / float(self.object.download_record_count)
        else:
            context['error_pct'] = 0
        return context

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
            return self.get_queryset().latest("release_datetime")
        except self.queryset.model.DoesNotExist:
            raise Http404

    def get_context_data(self, **kwargs):
        """
        Add little extra bits that the standard detail page won't have.
        """
        context = super(LatestVersion, self).get_context_data(**kwargs)
        # A hint we can use in the template as a switch
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
