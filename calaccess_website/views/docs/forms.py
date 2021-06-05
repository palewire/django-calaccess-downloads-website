from django.http import Http404
from django.urls import reverse
from calaccess_raw.annotations import FORMS
from django.template.defaultfilters import slugify
from calaccess_website.views.base import CalAccessModelListMixin
from django.views.generic import DetailView, ListView


class FormList(ListView, CalAccessModelListMixin):
    template_name = 'calaccess_website/docs/forms/form_list.html'

    def get_queryset(self):
        """
        Returns a list of all forms.
        """
        return self.regroup_by_klass_group(FORMS)

    def get_context_data(self, **kwargs):
        context = super(FormList, self).get_context_data(**kwargs)
        context['form_list'] = FORMS
        return context


class FormDetail(DetailView):
    """
    A detail page with everything we know about the provided filing form.
    """
    template_name = 'calaccess_website/docs/forms/form_detail.html'
    context_object_name = 'form'

    def get_queryset(self):
        """
        Returns a list of the forms as a key dictionary
        with the URL slug as the keys.
        """
        return dict((slugify(m.id), m) for m in FORMS)

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
