import os
import requests
from calaccess_raw import get_model_list
from calaccess_website.views.docs.ccdc_files import get_ocd_proxy_models
from calaccess_website.templatetags.calaccess_website_tags import archive_url
from github import Github
from github.InputFileContent import InputFileContent
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Update the gist with sample data files'

    def handle(self, *args, **options):
        self.gh = Github(os.getenv('github_token'))
        self.gist = self.gh.get_gist('66bed097ddca855c36506da4b7c0d349')
        self.files = {}

        print('  getting raw data...')
        for m in get_model_list():
            file_name = m().get_csv_name()
            self.get_file_data(file_name)

        print('  getting processed data...')
        for m in get_ocd_proxy_models():
            file_name = u'%s.csv' % m().file_name
            self.get_file_data(file_name)

        # now save
        self.gist.edit(
            description='Updating sample files',
            files=self.files,
        )

    def get_file_data(self, file_name):
        """
        Get header and top five lines from the latest version of file_name.
        """
        file_url = archive_url(file_name, is_latest=True)
        top_lines = []

        with requests.get(file_url, stream=True) as r:
            try:
                r.raise_for_status()
            except Exception as e:
                print(e)
                # not sure why deleting files is no longer working...
                # self.files[file_name] = None
            else:
                # read the first five lines
                for line in r.iter_lines():
                    if len(top_lines) == 6:
                        break
                    else:
                        top_lines.append(line)
                joined_lines = '\r\n'.join(top_lines)
                file_content = InputFileContent(joined_lines)
                self.files[file_name] = file_content
