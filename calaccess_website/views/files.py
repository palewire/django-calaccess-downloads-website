from django.http import Http404
from calaccess_raw import get_model_list
from .base import CalAccessModelListMixin
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from calaccess_raw.models.tracking import RawDataFile
from bakery.views import BuildableDetailView, BuildableListView


class FileList(BuildableListView, CalAccessModelListMixin):
    template_name = 'calaccess_website/file_list.html'
    build_path = "files/index.html"

    def get_queryset(self):
        """
        Returns the CAL-ACCESS model list with grouped by type.
        """
        return self.regroup_by_klass_group(get_model_list())


class FileDetail(BuildableDetailView):
    """
    Base class for views providing information about a raw data file.
    """
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


class FileDocumentation(FileDetail):
    """
    A detail page with all documentation for the provided raw data file.
    """
    template_name = 'calaccess_website/file_detail.html'

    def get_url(self, obj):
        return reverse('file_detail', kwargs=dict(file_name=obj))

    def get_context_data(self, **kwargs):
        """
        Add some extra bits to the template's context
        """
        context = super(FileDocumentation, self).get_context_data(**kwargs)
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


class FileDownloadsList(FileDetail):
    """
    A detail page with links to all downloads for the provided raw data file.
    """
    template_name = 'calaccess_website/file_downloads_list.html'

    def get_url(self, obj):
        return reverse('file_downloads_list', kwargs=dict(file_name=obj))
