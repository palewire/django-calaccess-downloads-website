from django.http import Http404
from django.urls import reverse
from calaccess_raw import get_model_list
from calaccess_raw.models.tracking import RawDataFile
from calaccess_website.views import CalAccessModelListMixin
from bakery.views import BuildableDetailView, BuildableListView
from calaccess_website.templatetags.calaccess_website_tags import slugify


class CalAccessFileList(BuildableListView, CalAccessModelListMixin):
    template_name = 'calaccess_website/docs/calaccess/file_list.html'
    build_path = "documentation/raw-files/index.html"

    def get_queryset(self):
        """
        Returns the CAL-ACCESS model list with grouped by type.
        """
        return self.regroup_by_klass_group(get_model_list())

    def get_context_data(self, **kwargs):
        context = super(CalAccessFileList, self).get_context_data(**kwargs)
        model_list = get_model_list()
        context['model_list'] = model_list
        context['title'] = 'Raw files'
        context['description'] = "Definitions, record layouts and data dictionaries for the {} raw \
files released from the California Secretary of State's CAL-ACCESS database. For experts only.".format(len(model_list))
        return context


class BaseFileDetailView(BuildableDetailView):
    """
    Base class for views providing information about a raw data file.
    """
    def get_queryset(self):
        """
        Returns a list of the raw data files as a key dictionary
        with the URL slug as the keys.
        """
        return dict(
            (slugify(m().db_table), m) for m in get_model_list()
        )

    def set_kwargs(self, obj):
        self.kwargs = {
            'slug': obj
        }

    def get_object(self):
        """
        Returns the file model from the CAL-ACCESS raw data app that
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
        context['version_list'] = RawDataFile.objects.filter(
            file_name=file_name
        ).order_by('-version__release_datetime').exclude(version__release_datetime__lte='2016-07-27')
        # note if the most recent version of the file is empty
        try:
            context['empty'] = context['version_list'][0].download_records_count == 0
        except IndexError:
            context['empty'] = True
        return context

    def build_queryset(self):
        [self.build_object(o) for o in self.get_queryset()]


class CalAccessFileDownloadsList(BaseFileDetailView):
    """
    A detail page with links to all downloads for the provided raw data file.
    """
    template_name = 'calaccess_website/docs/calaccess/download_list.html'

    def get_url(self, obj):
        return reverse('calaccess_file_downloads_list', kwargs=dict(slug=obj))


class CalAccessFileDetail(BaseFileDetailView):
    """
    A detail page with all documentation for the provided raw data file.
    """
    template_name = 'calaccess_website/docs/calaccess/file_detail.html'

    def get_url(self, obj):
        return reverse('calaccess_file_detail', kwargs=dict(slug=obj))

    def get_context_data(self, **kwargs):
        """
        Add some extra bits to the template's context
        """
        context = super(CalAccessFileDetail, self).get_context_data(**kwargs)
        # Add list of choice fields to context
        context['choice_fields'] = self.get_choice_fields()
        # Add dict of docs to context
        context['docs'] = self.get_docs()
        return context

    def get_choice_fields(self):
        """
        Returns list of fields with choices and docs.
        """
        choice_fields = []
        for field in self.object._meta.fields:
            if len(field.choices) > 0:
                # add doc title, page_url list to each choice field
                field.docs = {}
                for doc in sorted(
                    field.documentcloud_pages,
                    key=lambda x: x.start_page
                ):
                    """if self.refresh_dc_cache and doc.id not in self.docs_cached:
                        doc._cache_metadata()
                        self.docs_cached.append(doc.id)"""
                    try:
                        field.docs[doc.title].append(doc)
                    except KeyError:
                        field.docs[doc.title] = [doc]
            choice_fields.append(field)
        return choice_fields

    def get_docs(self):
        """
        Returns dict of { doc_title: list of documentcloud objects }.
        """
        docs = {}
        for doc in sorted(
            self.object.DOCUMENTCLOUD_PAGES,
            key=lambda x: x.start_page
        ):
            """if self.refresh_dc_cache and doc.id not in self.docs_cached:
                doc._cache_metadata()
                self.docs_cached.append(doc.id)"""
            try:
                docs[doc.title].append(doc)
            except KeyError:
                docs[doc.title] = [doc]
        return docs
