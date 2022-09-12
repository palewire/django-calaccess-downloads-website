from django.urls import reverse
from bakery.views import BuildableTemplateView


class LatestVersion(BuildableTemplateView):
    """
    Detail page of the latest CAL-ACCESS version
    """
    template_name = 'calaccess_website/version/detail_latest.html'
    build_path = "downloads/latest/index.html"

    def get_context_data(self, **kwargs):
        """
        Add little extra bits that the standard detail page won't have.
        """
        context = super(LatestVersion, self).get_context_data(**kwargs)
        # A hint we can use in the template as a switch
        context['title'] = 'Latest California campaign finance data'
        context['description'] = 'Download the most recent release of CAL-ACCESS, the government database that tracks campaign \
finance and lobbying activity in California politics.'
        context['is_latest'] = True
        return context

    def get_url(self, obj):
        """
        The never-changing latest URL.
        """
        return reverse('version_latest')
