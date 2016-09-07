from .calaccess_forms import FormList, FormDetail
from .calaccess_official import OfficialDocumentation
from .calaccess_files import FileList, FileDetail, FileDownloadsList
import calaccess_raw
from django.urls import reverse
from bakery.views import BuildableTemplateView
from calaccess_raw.annotations.filing_forms import all_filing_forms


class DocumentationIndex(BuildableTemplateView):
    """
    An index page for linking to all of our documentation sections
    """
    build_path = "documentation/index.html"
    template_name = "calaccess_website/documentation_index.html"

    def get_context_data(self):
        model_list = calaccess_raw.get_model_list()
        form_list = all_filing_forms
        object_list = [
            dict(
                name='CAL-ACCESS files',
                description="Definitions, record layouts and data dictionaries for the {} \
CAL-ACCESS files released by the state.".format(len(model_list)),
                url=reverse("file_list"),
            ),
            dict(
                name='CAL-ACCESS forms',
                description="Descriptions, samples and other documentation for \
the {} forms that campaigns and lobbyists use to disclose activity to the state.".format(len(form_list)),
                url=reverse("form_list"),
            ),
            dict(
                name='CAL-ACCESS official documentation',
                description="The jumbled, fragmentary and unreliable documentation \
for the CAL-ACCESS database provided by California's Secretary of State. For more authoritative \
information, refer to our materials.",
                url=reverse("official_documentation"),
            ),
            dict(
                name='CCDC technical documentation',
                description="Technical documentation for the collection of \
California Civic Data Coalition applications that power this site.",
                url="http://django-calaccess.californiacivicdata.org"
            ),
        ]
        return {
            'object_list': object_list
        }


__all__ = (
    'DocumentationIndex',
    'FormList',
    'FormDetail',
    'FileList',
    'FileDetail',
    'FileDownloadsList',
    'OfficialDocumentation',
)
