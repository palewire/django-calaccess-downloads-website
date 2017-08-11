from django.core.urlresolvers import reverse
from django.http import Http404
from calaccess_processed.models.tracking import ProcessedDataFile
from calaccess_website.views import CalAccessModelListMixin
from calaccess_website.templatetags.calaccess_website_tags import slugify
from bakery.views import BuildableDetailView, BuildableListView


class CcdcFileList(BuildableListView, CalAccessModelListMixin):
    template_name = 'calaccess_website/ccdc_file_list.html'
    build_path = "documentation/calaccess-files/index.html"

    def get_queryset(self):
        """
        Returns the CCDC model list with grouped by type.
        """
        return self.regroup_by_klass_group(get_model_list())

    def get_context_data(self, **kwargs):
        context = super(CcdcFileList, self).get_context_data(**kwargs)
        context['model_list'] = get_model_list()
        return context


class BaseFileDetailView(BuildableDetailView):
    """
    Base class for views providing information about a CCDC data file.
    """
    def get_queryset(self):
        """
        Returns a list of the raw data files as a key dictionary
        with the URL slug as the keys.
        """
        return dict((slugify(m().db_table), m) for m in get_model_list())

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
        file_name = self.kwargs['slug'].upper().replace("-", "_")
        context = super(BaseFileDetailView, self).get_context_data(**kwargs)
        # Pull all previous versions of the provided file
        context['version_list'] = ProcessedDataFile.objects.filter(
            file_name=file_name
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

    def build_queryset(self):
        [self.build_object(o) for o in self.get_queryset()]


class CcdcFileDownloadsList(BaseFileDetailView):
    """
    A detail page with links to all downloads for the provided CCDC data file.
    """
    template_name = 'calaccess_website/ccdc_file_downloads_list.html'

    def get_url(self, obj):
        return reverse('ccdc_file_downloads_list', kwargs=dict(slug=obj))


class CcdcFileDetail(BaseFileDetailView):
    """
    A detail page with all documentation for the provided CCDC data file.
    """
    template_name = 'calaccess_website/ccdc_file_detail.html'

    def get_url(self, obj):
        return reverse('raw_file_detail', kwargs=dict(slug=obj))

    def get_context_data(self, **kwargs):
        """
        Add some extra bits to the template's context
        """
        context = super(CcdcFileDetail, self).get_context_data(**kwargs)
        # Add list of choice fields to context
        context['choice_fields'] = self.get_choice_fields()
        return context

    def get_choice_fields(self):
        """
        Returns list of fields with choices and docs.
        """
        choice_fields = []
        for field in self.object._meta.fields:
            choice_fields.append(field)
        return choice_fields
