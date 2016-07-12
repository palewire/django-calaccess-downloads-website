import time
from django.http import Http404
from django.core.urlresolvers import reverse
from calaccess_raw.models.tracking import RawDataVersion
from django.template.defaultfilters import date as dateformat
from bakery.views import (
    BuildableArchiveIndexView,
    BuildableYearArchiveView,
    BuildableMonthArchiveView,
    BuildableDetailView,
    BuildableRedirectView
)


class VersionArchiveIndex(BuildableArchiveIndexView):
    """
    A list of the latest versions of CAL-ACCESS in our archive
    """
    model = RawDataVersion
    date_field = "release_datetime"
    template_name = "calaccess_website/version_archive.html"
    build_path = "versions/index.html"


class VersionYearArchiveList(BuildableYearArchiveView):
    """
    A list of all versions of CAL-ACCESS in a given year
    """
    model = RawDataVersion
    date_field = "release_datetime"
    make_object_list = False
    template_name = "calaccess_website/version_archive_year.html"


class VersionMonthArchiveList(BuildableMonthArchiveView):
    """
    A list of all versions of CAL-ACCESS in a given year
    """
    model = RawDataVersion
    date_field = "release_datetime"
    make_object_list = True
    template_name = "calaccess_website/version_archive_month.html"


class VersionDetail(BuildableDetailView):
    """
    A detail page with everything about an individual CAL-ACCESS version
    """
    model = RawDataVersion
    template_name = 'calaccess_website/version_detail.html'

    def set_kwargs(self, obj):
        super(VersionDetail, self).set_kwargs(obj)
        self.kwargs.update({
            'year': obj.release_datetime.year,
            'month': obj.release_datetime.month,
            'release_epochtime': dateformat(obj.release_datetime, 'U'),
        })

    def get_object(self, **kwargs):
        dt = time.localtime(float(self.kwargs['release_epochtime']))
        dt = time.strftime('%Y-%m-%d %H:%M:%S', dt)
        try:
            return self.model.objects.get(release_datetime=dt)
        except self.model.DoesNotExist:
            raise Http404

    def get_context_data(self, **kwargs):
        """
        Add some extra bits to the template's context
        """
        context = super(VersionDetail, self).get_context_data(**kwargs)
        # Add the file's raw data model klass_group to the context
        context['files'] = []
        for file_ in self.object.files.all():
            values = file_.__dict__
            values['klass_group'] = file_.model().klass_group
            values['pretty_download_file_size'] = file_.pretty_download_file_size()
            values['pretty_clean_file_size'] = file_.pretty_clean_file_size()
            context['files'].append(values)
        return context

    def get_url(self, obj):
        return reverse(
            'version_detail',
            kwargs=dict(
                year=obj.release_datetime.year,
                month=obj.release_datetime.month,
                release_epochtime=dateformat(obj.release_datetime, 'U'),
            )
        )


class LatestVersion(BuildableRedirectView):
    """
    Redirect to the detail page of the latest CAL-ACCESS version
    """
    build_path = "versions/latest/index.html"
    pattern_name = 'version_detail'

    def get_redirect_url(self, *args, **kwargs):
        try:
            obj = RawDataVersion.objects.latest('release_datetime')
        except RawDataVersion.DoesNotExist:
            raise Http404
        return reverse(
            'version_detail',
            kwargs=dict(
                year=obj.release_datetime.year,
                month=obj.release_datetime.month,
                release_epochtime=dateformat(obj.release_datetime, 'U'),
            )
        )
