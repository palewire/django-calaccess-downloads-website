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
                name='Processed civic data files',
                description="Definitions, record layouts and data dictionaries for the \
processed data files released by the California Civic Data Coalition. These files are recommended for beginners and regular use.",
                url=reverse("ccdc_file_list"),
            ),
            dict(
                name='Raw CAL-ACCESS files',
                description="Definitions, record layouts and data dictionaries for the {} raw \
files released from the California Secretary of State's CAL-ACCESS database. These files are only for experts.".format(len(model_list)),
                url=reverse("calaccess_file_list"),
            ),
            dict(
                name='CAL-ACCESS forms',
                description="Descriptions, samples and other documentation for \
the {} forms that campaigns and lobbyists use to disclose activity to California's Secretary of State.".format(len(form_list)),
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
                name='Civic data technical documentation',
                description="Technical documentation for the collection of \
California Civic Data Coalition applications that power this site.",
                url="http://django-calaccess.californiacivicdata.org"
            ),
            dict(
                name="Frequently asked questions",
                description="Answers to common questions about this project and the underlying CAL-ACCESS database.",
                url=reverse("faq"),
            ),
        ]
        return {
            'object_list': object_list,
            'title': "Documentation",
            'description': "How to work with the data tracking campaign finance and lobbying activity in California politics."
        }


class FAQ(BuildableTemplateView):
    """
    Frequently asked questions.
    """
    build_path = "documentation/frequently-asked-questions/index.html"
    template_name = "calaccess_website/faq_detail.html"
