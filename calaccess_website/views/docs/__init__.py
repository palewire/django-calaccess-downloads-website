from .calaccess_files import FileList, FileDetail, FileDownloadsList

import calaccess_raw
from django.urls import reverse
from bakery.views import BuildableTemplateView


class DocumentationIndex(BuildableTemplateView):
    """
    An index page for linking to all of our documentation sections
    """
    build_path = "documentation/index.html"
    template_name = "calaccess_website/documentation_index.html"

    def get_context_data(self):
        model_list = calaccess_raw.get_model_list()
        object_list = [
            dict(
                name='CAL-ACCESS files',
                description="Definitions, record layouts and data dictionaries for the {} \
files released from CAL-ACCESS, the California Secretary of State's database \
tracking campaign finance and lobbying activity in state politics.".format(len(model_list)),
                url=reverse("file_list"),
            ),
            dict(
                name='CAL-ACCESS forms',
                description="",
                url=""
            ),
            dict(
                name='Technical documentation',
                description="",
                url=""
            ),
            dict(
                name='References',
                description="",
                url=""
            ),
        ]
        return {
            'object_list': object_list
        }
