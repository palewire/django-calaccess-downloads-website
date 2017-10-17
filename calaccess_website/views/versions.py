from datetime import datetime
from django.apps import apps
from django.http import Http404
from django.utils import timezone
from .base import CalAccessModelListMixin
from django.core.urlresolvers import reverse
from calaccess_raw.models import RawDataVersion
from calaccess_processed.models import (
    ProcessedDataZip,
    ProcessedDataFile,
)
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
    queryset = RawDataVersion.objects.complete().exclude(
        release_datetime__lte='2016-07-27'
    ).select_related()
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
    queryset = RawDataVersion.objects.complete().exclude(
        release_datetime__lte='2016-07-27'
    ).select_related()
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

        if self.processed_version:
            context['flat_zip'] = self.get_processed_zip('flat')
            context['relational_zip'] = self.get_processed_zip('relational')
            context['flat_files'] = self.get_flat_files()

        if self.object.error_count:
            context['raw_files_w_errors'] = self.get_raw_files_w_errors()
            context['error_pct'] = 100 * self.object.error_count / float(self.object.download_record_count)
        else:
            context['error_pct'] = 0
        return context

    def get_processed_zip(self, label):
        """
        Return a ProcessedDataZip instance with a name that includes label.

        If no instance exists for the version, return None.
        """
        if self.processed_version:
            try:
                obj = self.processed_version.zips.get(
                    zip_archive__icontains=label
                )
            except (ProcessedDataZip.DoesNotExist, AttributeError):
                obj = None
        else:
            obj = None
        return obj

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
        if self.processed_version:
            flat_models = [
                m for m in apps.get_models()
                if getattr(m(), 'is_flat', False)
            ]
            for m in flat_models:
                flat_file = {'name': m().file_name, 'doc': m().doc}
                try:
                    file_obj = self.processed_version.files.get(
                        file_name=flat_file['name']
                    )
                except ProcessedDataFile.DoesNotExist:
                    flat_file['archive'] = None
                else:
                    flat_file['archive'] = file_obj.file_archive.name
                    if len(flat_file['archive']) == 0:
                        flat_file['archive'] = None
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

    @property
    def processed_version(self):
        """
        An ProcessedDataVersion instance, if one exists for the view
        """
        try:
            processed_version = self.object.processed_version
        except AttributeError:
            processed_version = None
        return processed_version


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
