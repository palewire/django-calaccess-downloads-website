import os
from github import Github
from github.InputFileContent import InputFileContent
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Update the gist with sample data files'

    def handle(self, *args, **options):
        self.gh = Github(os.getenv('GITHUB_TOKEN'))
        self.org = self.gh.get_organization("california-civic-data-coalition")
        self.repo = self.org.get_repo("django-calaccess-raw-data")
        self.gist = self.gh.get_gist('66bed097ddca855c36506da4b7c0d349')

        sample_data_dir = self.repo.get_dir_contents('/example/test-data/tsv/')

        files = {}

        for file in sample_data_dir:
            lines = file.decoded_content.splitlines()

            # can't add empty files to gist, so skip
            if len(lines) > 0:
                # we want the header + the first five lines without illegal chars
                top_lines = []

                for line in lines:
                    if '"' not in line:
                        top_lines.append(line)
                    if len(top_lines) == 6:
                        break

                # recombine the split lines into a single string
                joined_lines = '\r\n'.join(top_lines)

            files[file.name] = InputFileContent(content=joined_lines)

        # now save
        self.gist.edit(
            description='Updating sample files',
            files=files,
        )
