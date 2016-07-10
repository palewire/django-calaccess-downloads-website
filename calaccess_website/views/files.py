from django.http import Http404
from calaccess_raw import get_model_list
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from calaccess_raw.models.tracking import RawDataFile
from bakery.views import BuildableDetailView, BuildableListView


class FileList(BuildableListView):
    queryset = get_model_list()
    template_name = 'calaccess_website/file_list.html'
    build_path = "files/index.html"


class FileDetail(BuildableDetailView):
    """
    A detail page with everything we know about the provided raw data file.
    """
    template_name = 'calaccess_website/file_detail.html'

    def get_queryset(self):
        """
        Returns a list of the raw data files as a key dictionary
        with the URL slug as the keys.
        """
        return dict((slugify(m().db_table), m) for m in get_model_list())

    def set_kwargs(self, obj):
        self.kwargs = {
            'file_name': obj
        }

    def get_object(self):
        """
        Returns the file model from the CAL-ACCESS raw data app that
        matches the provided slug.

        Raises a 404 error if one is not found
        """
        key = self.kwargs['file_name']
        try:
            return self.get_queryset()[key.lower()]
        except KeyError:
            raise Http404

    def get_url(self, obj):
        return reverse('file_detail', kwargs=dict(file_name=obj))

    def get_context_data(self, **kwargs):
        """
        Add some extra bits to the template's context
        """
        context = super(FileDetail, self).get_context_data(**kwargs)
        # Pull all previous versions of the provided file
        context['version_list'] = RawDataFile.objects.filter(
            file_name=self.kwargs['file_name'].upper()
        ).order_by('-version__release_datetime')
        return context

    def build_queryset(self):
        [self.build_object(o) for o in self.get_queryset()]
