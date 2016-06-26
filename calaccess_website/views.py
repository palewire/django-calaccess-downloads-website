from django.http import Http404
from django.views.generic import (
    ListView,
    DetailView,
    ArchiveIndexView,
    YearArchiveView
)
from calaccess_raw import get_model_list
from calaccess_raw.models.tracking import RawDataVersion, RawDataFile


class VersionArchiveIndex(ArchiveIndexView):
    """
    A list of the latest versions of CAL-ACCESS in our archive
    """
    model = RawDataVersion
    date_field = "release_datetime"
    template_name = "calaccess_website/version_archive.html"


class VersionYearArchiveList(YearArchiveView):
    """
    A list of all versions of CAL-ACCESS in a given year
    """
    model = RawDataVersion
    date_field = "release_datetime"
    make_object_list = True
    template_name = "calaccess_website/version_archive_year.html"


class VersionDetail(DetailView):
    """
    A detail page with everything about an individual CAL-ACCESS version
    """
    model = RawDataVersion
    template_name = 'calaccess_website/version_detail.html'


class LatestVersion(VersionDetail):

    def get_object(self):
        try:
            object = RawDataVersion.objects.latest('release_datetime')
        except RawDataVersion.DoesNotExist:
            raise Http404("No versions found.")
        else:
            return object


class RawDataFileList(ListView):
    queryset = get_model_list()
    template_name = 'calaccess_website/raw_data_files_list.html'
    context_object_name = 'raw data files'


class RawDataFileDetail(DetailView):
    template_name = 'calaccess_website/raw_data_file.html'
    context_object_name = 'raw data file'

    def get_object(self):
        obj_search = [
            x for x in get_model_list()
            if x().get_tsv_name() == self.kwargs['file_name'].upper() + '.TSV'
        ]
        if len(obj_search) == 0:
            raise Http404("No versions found.")
        else:
            return obj_search[0]

    def get_context_data(self, **kwargs):
        context = super(RawDataFileDetail, self).get_context_data(**kwargs)

        context['file_versions'] = RawDataFile.objects.filter(
            file_name=self.kwargs['file_name'].upper()
        ).order_by('-version__release_datetime')

        return context
