import calaccess_raw
from django.urls import reverse
from calaccess_raw.annotations import FORMS
from bakery.views import BuildableTemplateView


class DocumentationIndex(BuildableTemplateView):
    """
    An index page for linking to all of our documentation sections
    """
    template_name = "calaccess_website/docs/index.html"
    build_path = "documentation/index.html"

    def get_context_data(self):
        model_list = calaccess_raw.get_model_list()
        form_list = FORMS
        object_list = [
            dict(
                name='Processed files from the California Civic Data Coalition',
                description="Definitions, record layouts and data dictionaries for the \
processed data files released by the California Civic Data Coalition. Recommended for beginners and regular use.",
                url=reverse("ccdc_file_list"),
            ),
            dict(
                name='Raw files from CAL-ACCESS',
                description="Definitions, record layouts and data dictionaries for the {} raw \
files released from the California Secretary of State's CAL-ACCESS database. For experts only.".format(len(model_list)),
                url=reverse("calaccess_file_list"),
            ),
            dict(
                name='Official CAL-ACCESS forms',
                description="Descriptions, samples and other documentation for \
the {} forms that campaigns and lobbyists use to disclose activity to California's Secretary of \
State.".format(len(form_list)),
                url=reverse("form_list"),
            ),
            dict(
                name='Official CAL-ACCESS documentation',
                description="The jumbled, fragmentary and unreliable documentation \
for the CAL-ACCESS database provided by California's Secretary of State. For more authoritative \
information refer to the materials above.",
                url=reverse("official_documentation"),
            ),
            dict(
                name='Technical documentation',
                description="A user manual for the collection of \
California Civic Data Coalition applications that power this site. For developers only.",
                url="//django-calaccess.californiacivicdata.org"
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
            'description': "How to work with our data tracking campaign finance and lobbying activity in \
California politics."
        }


class FAQ(BuildableTemplateView):
    """
    Frequently asked questions.
    """
    template_name = "calaccess_website/docs/faq/question_list.html"
    build_path = "documentation/frequently-asked-questions/index.html"
