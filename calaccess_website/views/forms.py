from django.http import Http404
from .base import CalAccessModelListMixin
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from calaccess_raw.annotations.filing_forms import all_filing_forms
from bakery.views import BuildableDetailView, BuildableListView

class FormList(BuildableListView, CalAccessModelListMixin):
    template_name = 'calaccess_website/form_list.html'
    build_path = "forms/index.html"

    def get_queryset(self):
        """
        Returns a list of all forms.
        """
        print(all_filing_forms)
        return self.regroup_by_klass_group(all_filing_forms)

class FormDetail(BuildableDetailView):
    """
    A detail page with everything we know about the provided filing form.
    """
    template_name = 'calaccess_website/form_detail.html'
    context_object_name = 'form'

    def get_queryset(self):
        """
        Returns a list of the forms as a key dictionary
        with the URL slug as the keys.
        """
        return dict((slugify(m.id), m) for m in all_filing_forms)

    def set_kwargs(self, obj):
        self.kwargs = {
            'id': obj
        }

    def get_object(self):
        """
        Returns the form from the CAL-ACCESS raw data app that
        matches the provided id.

        Raises a 404 error if one is not found
        """
        key = self.kwargs['id']
        try:
            return self.get_queryset()[key.lower()]
        except KeyError:
            raise Http404

    def get_url(self, obj):
        return reverse('form_detail', kwargs=dict(id=obj))

    def build_queryset(self):
        [self.build_object(o) for o in self.get_queryset()]