from django.http import Http404
from django.views.generic import (
    ListView,
    DetailView,
    ArchiveIndexView,
    YearArchiveView
)
from calaccess_raw import get_model_list
from django.template.defaultfilters import slugify
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
    """
    A detail page with everything we know about the provided raw data file.
    """
    template_name = 'calaccess_website/rawdatafile_detail.html'

    def get_object_list(self):
        """
        Returns a list of the raw data files as a key dictionary
        with the URL slug as the keys.
        """
        return dict((slugify(m().get_tsv_name()), m) for m in get_model_list())

    def get_object(self):
        """
        Returns the file model from the CAL-ACCESS raw data app that
        matches the provided slug.

        Raises a 404 error if one is not found
        """
        key = self.kwargs['file_name'] + 'tsv'
        try:
            return self.get_object_list()[key]
        except KeyError:
            raise Http404

    def get_context_data(self, **kwargs):
        """
        Add some extra bits to the template's context
        """
        context = super(RawDataFileDetail, self).get_context_data(**kwargs)
        # Pull all previous versions of the provided file 
        context['version_list'] = RawDataFile.objects.filter(
            file_name=self.kwargs['file_name'].upper()
        ).order_by('-version__release_datetime')
        return context
